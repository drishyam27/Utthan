"""
Phase 4 Verification Script: Database & NSQF Catalog Audit + Scenarios A-G
Audits live catalog counts, schema integrity, excluded sectors, decimal levels,
PwD qualifications, and tests Scenarios A through G deterministically.
"""

import sys
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

# Force utf-8 output for Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from app.core.config import settings
from app.db.supabase import get_supabase_client
from app.services.nsqf_ingestion import EXCLUDED_SECTORS, slugify
from app.services.nsqf_service import _get_in_memory_catalog
from app.services.nsqf_recommendation_service import (
    evaluate_nsqf_eligibility,
    generate_nsqf_recommendations,
    check_insufficient_profile,
    NSQFEligibilityStatus,
)
from app.schemas.adaptive_interview import (
    StructuredBeneficiaryProfile,
    NSQFCompetencyEvidence,
)


def run_catalog_audit():
    print("==================================================")
    print("1. NSQF CATALOG & DATABASE AUDIT")
    print("==================================================")

    client = None
    if settings.is_supabase_configured:
        try:
            client = get_supabase_client()
            print("Connected to Supabase PostgreSQL.")
        except Exception as e:
            print(f"Supabase connection error: {e}")
            client = None
    else:
        print("Supabase credentials not configured in backend/.env; using in-memory catalog.")

    # 1. Check Sectors
    sectors_count = 0
    sectors_list = []
    if client:
        try:
            res_sec = client.table("nsqf_sectors").select("id, name").execute()
            sectors_list = getattr(res_sec, "data", []) or []
            sectors_count = len(sectors_list)
        except Exception as e:
            print(f"Error querying nsqf_sectors: {e}")
    if sectors_count == 0:
        # Check in-memory catalog
        raw_sectors, raw_courses, raw_stats = _get_in_memory_catalog()
        sectors_set = {c.get("sector_name") for c in raw_courses if c.get("sector_name")}
        sectors_count = len(sectors_set)
        sectors_list = [{"name": s, "id": slugify(s)} for s in sectors_set]

    print(f"Sectors Count: {sectors_count}")
    print("All 44 Active Sectors:")
    for s in sorted(sectors_list, key=lambda x: x["name"]):
        print(f"  - {s['name']} (slug: {s['id']})")

    # 2. Check Excluded Sectors in Sectors List
    leak_sectors = [s["name"] for s in sectors_list if s["name"] in EXCLUDED_SECTORS]
    print(f"Excluded Sectors Present in Catalog Sectors: {leak_sectors} (Expected: None)")

    # 3. Check Qualifications
    quals = []
    if client:
        try:
            # Query all qualifications in batches of 1000
            offset = 0
            while True:
                res_q = client.table("nsqf_qualifications").select(
                    "q_code, title, sector_name, sector_id, nsqf_level, notional_hours_range, is_pwd, pwd_categories"
                ).range(offset, offset + 999).execute()
                batch = getattr(res_q, "data", []) or []
                if not batch:
                    break
                quals.extend(batch)
                offset += len(batch)
                if len(batch) < 1000:
                    break
        except Exception as e:
            print(f"Error querying nsqf_qualifications from DB: {e}")

    if not quals:
        _, quals, _ = _get_in_memory_catalog()

    print(f"Qualifications Count: {len(quals)} (Expected: ~2,810)")

    # 4. Check for duplicate (q_code, title)
    unique_pairs = set()
    duplicates = []
    for q in quals:
        pair = (q.get("q_code"), q.get("title"))
        if pair in unique_pairs:
            duplicates.append(pair)
        else:
            unique_pairs.add(pair)
    print(f"Unique (q_code, title) Pairs: {len(unique_pairs)}")
    print(f"Duplicate (q_code, title) Pairs: {len(duplicates)}")

    # 5. Check Excluded Sectors in Qualifications
    leak_quals = [q for q in quals if q.get("sector_name") in EXCLUDED_SECTORS]
    print(f"Qualifications in Excluded Sectors: {len(leak_quals)} (Expected: 0)")

    # 6. Decimal NSQF Levels
    decimal_levels = [q for q in quals if q.get("nsqf_level") and float(q["nsqf_level"]) % 1 != 0]
    decimal_vals = sorted(list({float(q["nsqf_level"]) for q in decimal_levels}))
    print(f"Decimal NSQF Levels Found: {decimal_vals}")
    print(f"Count of Courses with Decimal Levels: {len(decimal_levels)}")

    # 7. Notional Hours Ranges
    hour_buckets = {}
    for q in quals:
        b = q.get("notional_hours_range") or "Unspecified"
        hour_buckets[b] = hour_buckets.get(b, 0) + 1
    print("\nNotional Hours Distribution:")
    for b, c in sorted(hour_buckets.items()):
        print(f"  {b:15s}: {c} courses")

    # 8. PwD Qualifications
    pwd_quals = [q for q in quals if q.get("is_pwd")]
    print(f"\nTotal PwD Tailored Qualifications: {len(pwd_quals)}")
    pwd_cats = {}
    for q in pwd_quals:
        for cat in (q.get("pwd_categories") or []):
            pwd_cats[cat] = pwd_cats.get(cat, 0) + 1
    print(f"PwD Category Counts: {pwd_cats}")

    return quals, client


def run_scenarios(quals, client):
    print("\n==================================================")
    print("2. DETERMINISTIC SCENARIO VALIDATION (A-G)")
    print("==================================================")

    # Helper to test evaluate_nsqf_eligibility on candidate courses
    # -------------------------------------------------------------
    # Scenario A: Beginner (No formal education, no experience, selected sector: Agriculture)
    # -------------------------------------------------------------
    profile_a = StructuredBeneficiaryProfile(
        beneficiary_id=uuid4(),
        interview_id=uuid4(),
        name="Sunita Devi",
        education="no_formal",
        education_label="No formal education",
        work_experience_years=0.0,
        interested_sector_name="Agriculture",
        interested_sector_id="agriculture",
        notional_hours_range="201–400",
        pwd_status=False,
    )
    agri_courses = [q for q in quals if q.get("sector_name") == "Agriculture"]
    eval_a_eligible = []
    for c in agri_courses:
        res = evaluate_nsqf_eligibility(profile_a, c)
        if res.eligible:
            eval_a_eligible.append((c, res))
    print(f"Scenario A (Beginner in Agriculture): {len(eval_a_eligible)} courses eligible out of {len(agri_courses)} Agriculture courses.")
    assert len(eval_a_eligible) > 0, "Scenario A should find entry-level Agriculture courses!"
    top_c_a, top_eval_a = eval_a_eligible[0]
    print(f"  Top Match Sample: {top_c_a.get('q_code')} - {top_c_a.get('title')} (Level {top_c_a.get('nsqf_level')})")
    print(f"  Matched Criteria: {top_eval_a.matched_requirements[:2]}")

    # -------------------------------------------------------------
    # Scenario B: Vocationally Qualified (10th + ITI, Electronics / Automotive)
    # -------------------------------------------------------------
    profile_b = StructuredBeneficiaryProfile(
        beneficiary_id=uuid4(),
        interview_id=uuid4(),
        name="Vikram Kumar",
        education="10th",
        education_label="10th Pass",
        vocational_training=True,
        vocational_training_type="ITI",
        work_experience_years=1.0,
        interested_sector_name="Electronics & HW",
        interested_sector_id="electronics-hw",
        notional_hours_range="401–600",
        pwd_status=False,
    )
    elec_courses = [q for q in quals if q.get("sector_name") == "Electronics & HW"]
    eval_b_eligible = []
    for c in elec_courses:
        res = evaluate_nsqf_eligibility(profile_b, c)
        if res.eligible:
            eval_b_eligible.append((c, res))
    print(f"\nScenario B (Vocationally Qualified in Electronics & HW): {len(eval_b_eligible)} eligible out of {len(elec_courses)} Electronics & HW courses.")
    assert len(eval_b_eligible) > 0, "Scenario B should find courses for 10th + ITI!"
    top_c_b, top_eval_b = eval_b_eligible[0]
    print(f"  Top Match Sample: {top_c_b.get('q_code')} - {top_c_b.get('title')} (Level {top_c_b.get('nsqf_level')})")

    # -------------------------------------------------------------
    # Scenario C: Experienced Beneficiary (12th + 5 years exp, Construction)
    # -------------------------------------------------------------
    profile_c = StructuredBeneficiaryProfile(
        beneficiary_id=uuid4(),
        interview_id=uuid4(),
        name="Rajesh Sharma",
        education="12th",
        education_label="12th Pass",
        work_experience_years=5.0,
        interested_sector_name="Construction",
        interested_sector_id="construction",
        competency_evidence=NSQFCompetencyEvidence(
            technical_skills=["bricklaying", "plastering", "scaffolding"],
            tools_familiarity=["trowel", "plumb bob", "spirit level"],
        ),
        notional_hours_range="401–600",
        pwd_status=False,
    )
    const_courses = [q for q in quals if q.get("sector_name") == "Construction"]
    eval_c_eligible = []
    for c in const_courses:
        res = evaluate_nsqf_eligibility(profile_c, c)
        if res.eligible:
            eval_c_eligible.append((c, res))
    print(f"\nScenario C (Experienced Construction Worker): {len(eval_c_eligible)} eligible out of {len(const_courses)} Construction courses.")
    assert len(eval_c_eligible) > 0, "Scenario C should find courses for experienced worker!"
    top_c_c, top_eval_c = eval_c_eligible[0]
    print(f"  Top Match Sample: {top_c_c.get('q_code')} - {top_c_c.get('title')} (Level {top_c_c.get('nsqf_level')})")

    # -------------------------------------------------------------
    # Scenario D: PwD (is_pwd = True, LD category)
    # -------------------------------------------------------------
    profile_d = StructuredBeneficiaryProfile(
        beneficiary_id=uuid4(),
        interview_id=uuid4(),
        name="Amina Khatun",
        education="10th",
        work_experience_years=0.0,
        pwd_status=True,
        pwd_checked=True,
        pwd_categories=["LD"],
        interested_sector_name="Persons with Disability",
        interested_sector_id="persons-with-disability",
        notional_hours_range="201–400",
    )
    pwd_sector_courses = [q for q in quals if q.get("sector_name") == "Persons with Disability"]
    eval_d_pwd_matches = []
    for c in pwd_sector_courses:
        res = evaluate_nsqf_eligibility(profile_d, c)
        if res.eligible and c.get("is_pwd"):
            eval_d_pwd_matches.append((c, res))
    print(f"\nScenario D (PwD Candidate in Persons with Disability Sector): Found {len(eval_d_pwd_matches)} PwD-tailored courses.")
    assert len(eval_d_pwd_matches) > 0, "Scenario D should find PwD tailored courses!"
    top_c_d, top_eval_d = eval_d_pwd_matches[0]
    print(f"  Top Match Sample: {top_c_d.get('q_code')} - {top_c_d.get('title')} (PwD categories: {top_c_d.get('pwd_categories')})")

    # Also test through generate_nsqf_recommendations
    rec_d = generate_nsqf_recommendations(client, profile_d, limit=5)
    print(f"  generate_nsqf_recommendations status: {rec_d.status} (returned {len(rec_d.recommendations)} courses)")
    assert rec_d.status == "eligible"
    assert len(rec_d.recommendations) > 0

    # -------------------------------------------------------------
    # Scenario E: Insufficient Profile (Missing education and sector)
    # -------------------------------------------------------------
    profile_e = StructuredBeneficiaryProfile(
        beneficiary_id=uuid4(),
        interview_id=uuid4(),
        name="Incomplete User",
        education=None,
        interested_sector_name=None,
        interested_sector_id=None,
    )
    is_insuf, missing_fields = check_insufficient_profile(profile_e)
    print(f"\nScenario E (Insufficient Profile): check_insufficient_profile -> {is_insuf}, missing: {missing_fields}")
    assert is_insuf, "Profile without education and sector must be flagged insufficient!"
    assert "education" in missing_fields and "interested_sector" in missing_fields

    rec_e = generate_nsqf_recommendations(client, profile_e)
    print(f"  generate_nsqf_recommendations status: {rec_e.status}")
    assert rec_e.status == "insufficient_profile"
    assert len(rec_e.recommendations) == 0

    # -------------------------------------------------------------
    # Scenario F: No Match (e.g. impossible criteria, e.g. PhD level requirement for no_formal)
    # -------------------------------------------------------------
    high_qual = {
        "q_code": "HIGH/Q01",
        "title": "Senior Research Scientist",
        "sector_name": "Healthcare",
        "sector_id": "healthcare",
        "nsqf_level": 8.0,
        "description": "Eligibility criteria: Graduate degree or higher required in relevant biological sciences.",
    }
    eval_f = evaluate_nsqf_eligibility(profile_a, high_qual)
    print(f"\nScenario F (No Match Candidate vs High Qualification):")
    print(f"  Eligible: {eval_f.eligible}")
    print(f"  Status: {eval_f.status.value}")
    print(f"  Hard Failures: {eval_f.hard_failures}")
    assert not eval_f.eligible, "Beginner should fail Senior Research Scientist eligibility!"

    # Also test generate_nsqf_recommendations no_match behavior for non-existent sector
    profile_f_nomatch = StructuredBeneficiaryProfile(
        beneficiary_id=uuid4(),
        interview_id=uuid4(),
        name="No Match User",
        education="10th",
        interested_sector_name="NonExistentFakeSector",
        interested_sector_id="non-existent-fake-sector",
    )
    rec_f = generate_nsqf_recommendations(client, profile_f_nomatch)
    print(f"  Non-existent sector recommendation status: {rec_f.status}")
    assert rec_f.status == "no_match"
    assert len(rec_f.recommendations) == 0

    # -------------------------------------------------------------
    # Scenario G: Excluded Sector (Attempting recommendations for each excluded sector)
    # -------------------------------------------------------------
    print("\nScenario G (Excluded Sector Enforcement):")
    excluded_violations = []
    for ex_sec in sorted(EXCLUDED_SECTORS):
        dummy_c = {
            "q_code": f"EX/{ex_sec[:3].upper()}",
            "title": f"Official {ex_sec} Role",
            "sector_name": ex_sec,
            "sector_id": slugify(ex_sec),
            "nsqf_level": 4.0,
        }
        res_ex = evaluate_nsqf_eligibility(profile_b, dummy_c)
        if res_ex.eligible:
            excluded_violations.append(ex_sec)

        # Test request for excluded sector in recommendations
        profile_ex = StructuredBeneficiaryProfile(
            beneficiary_id=uuid4(),
            interview_id=uuid4(),
            name=f"User in {ex_sec}",
            education="12th",
            interested_sector_name=ex_sec,
            interested_sector_id=slugify(ex_sec),
        )
        rec_ex = generate_nsqf_recommendations(client, profile_ex)
        for r in rec_ex.recommendations:
            if r.sector_name in EXCLUDED_SECTORS or r.sector_name == ex_sec:
                excluded_violations.append(f"LEAK: {r.sector_name} / {r.title}")

    assert len(excluded_violations) == 0, f"Excluded sectors leaked through: {excluded_violations}"
    print(f"All {len(EXCLUDED_SECTORS)} excluded sectors strictly rejected by recommendation engine!")

    print("\nAll Scenarios A through G passed with 100% adherence to deterministic rules!")


if __name__ == "__main__":
    quals, client = run_catalog_audit()
    run_scenarios(quals, client)
