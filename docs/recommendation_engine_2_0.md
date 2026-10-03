# Utthan — Recommendation Engine 2.0

## Authoritative NSQF/NQR Catalog + Deterministic Eligibility + Explainable Ranking

---

### 1. Architectural Authority Hierarchy

Recommendation Engine 2.0 establishes the live **NSQF/NQR catalog (`nsqf_qualifications`)** with 2,810 courses across 44 sectors as the sole authoritative source for qualification recommendations.

```text
Beneficiary Voice Dialogue
       ↓
Sarvam STT
       ↓
Phase 3B Adaptive State Machine / Groq Intent Classification
       ↓
StructuredBeneficiaryProfile (Canonicalized Profile + Competency Evidence)
       ↓
Recommendation Engine 2.0 (backend/app/services/nsqf_recommendation_service.py)
       ├── Hard Gate 1: Excluded Sectors Enforcement (15 statutory exclusions blocked strictly)
       ├── Hard Gate 2: Deterministic Eligibility Evaluation (evaluate_nsqf_eligibility)
       ├── Dimension Match: PwD Inclusive Accommodation (VI, SHI, LD, ID)
       ├── Dimension Match: Capacity & Notional Hours Fit (8 canonical buckets)
       ├── Dimension Match: Practical Competency Evidence (Keyword token overlap)
       ├── Dimension Match: Canonical Education & Vocational Alignment
       └── Dimension Match: NSQF Level Progression Fit
       ↓
Explainable Deterministic Relevance Scoring (0–100)
       ↓
Stable Deterministic Ranking (score DESC, nsqf_level DESC, q_code ASC)
       ↓
NSQFRecommendationResponse (Machine-readable match reasons, warnings, ranks)
```

---

### 2. Distinction: NSQF Qualifications vs Training Opportunities

| Dimension | `nsqf_qualifications` (Catalog Course) | `opportunities` (Local Batches) |
|---|---|---|
| **Concept** | Recognized national skill standard from NQR | Locally funded PM-AJAY training center or batch |
| **Authority** | Government NQR dataset (2,810 courses, 44 sectors) | Program administration / training partners |
| **Scope** | Pan-India curriculum standard, NSQF level, hours | Location-restricted (State, District), stipend |
| **Frontend UI** | Rendered as **Official NSQF Course** with code & level | Rendered as **Sponsored Batch** with center location |

---

### 3. Excluded Sectors (Server-Side Enforced Zero-Tolerance)

The following 15 sectors are hard-excluded at query and eligibility layers:
1. `Judiciary`
2. `Indian Defence Forces`
3. `Legal Activities`
4. `Legislators`
5. `Musical Instruments`
6. `Optical Products`
7. `Postal Services`
8. `Printing`
9. `Public Administration`
10. `Railways`
11. `Real Estate`
12. `Religious Professionals`
13. `Shipping`
14. `Tobacco Industry`
15. `Unorganised Sector`

Total count of excluded sector qualifications in recommendation output is guaranteed **0**.

---

### 4. Deterministic Eligibility & Ranking Rules

#### 4.1 Strict No-Guessing Rule
If catalog metadata does not specify an entry rule (e.g. minimum age, gender, mandatory ITI, or minimum education), the engine marks the requirement explicitly as `requirement_unavailable` rather than hallucinating eligibility gates.

#### 4.2 Dimension Coverage
* **Sector**: Match with `interested_sector_id` or `interested_sector_name` (+35 points max).
* **Competencies & Skills**: Practical evidence (tools, technical skills, core skills, occupation) matched deterministically against qualification title, proposed occupation, description, and progression (+25 points max).
* **Notional Hours**: 8 canonical buckets (`1–200`, `201–400`, `401–600`, `601–800`, `801–1000`, `1001–1200`, `1201–2400`, `Above 2401`) compared against citizen preference (+15 points max).
* **PwD Compatibility**: 233 PwD-tailored qualifications matched against citizen disability status and categories (VI, SHI, LD, ID) (+10 points max).
* **Education & Vocational**: Canonical 20-level hierarchy; minimum entry education satisfied deterministically (+10 points max).
* **NSQF Level Progression**: Aligned with years of practical experience without altering course decimal levels (+5 points max).
* **Stable Deterministic Tie-Breaker**: `(-score, -nsqf_level, q_code)`.

---

### 5. Edge Case Handling

* **`insufficient_profile`**: Returned when the profile lacks basic sector preference or trade skills (`completeness_percentage < 15`). Courses are never forced without citizen context.
* **`no_match`**: Returned when no catalog qualifications pass strict criteria for the chosen parameters, providing transparent diagnostic reasons.
* **Groq Isolation**: Groq is restricted to conversational speech understanding. It has zero authority to select courses, alter eligibility gates, or assign NSQF levels.

---

### 6. API Endpoints

1. `GET /api/beneficiaries/{beneficiary_id}/recommendations/nsqf`: Capability-protected authoritative NSQF recommendations.
2. `GET /api/adaptive-interview/{interview_id}/recommendations`: Capability-protected recommendations grounded in session profile.
3. `GET /api/beneficiaries/{beneficiary_id}/recommendations`: Preserved backward-compatible endpoint for local training opportunities.
