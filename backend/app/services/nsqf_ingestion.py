"""
Utthan Backend - Authoritative NSQF / NQR Course Ingestion Service.
Parses, normalizes, audits, and ingests official NQR qualifications from the dataset.
"""

import json
import logging
import os
import re
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("utthan.nsqf_ingestion")

# Strict list of 15 excluded sectors per project requirements
EXCLUDED_SECTORS: Set[str] = {
    "Judiciary",
    "Indian Defence Forces",
    "Legal Activities",
    "Legislators",
    "Musical Instruments",
    "Optical Products",
    "Postal Services",
    "Printing",
    "Public Administration",
    "Railways",
    "Real Estate",
    "Religious Professionals",
    "Shipping",
    "Tobacco Industry",
    "Unorganised Sector",
}


def slugify(text: str) -> str:
    """Converts a display name to a clean, URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[\s&/\\]+', '-', text)
    text = re.sub(r'[^a-z0-9\-]', '', text)
    return text.strip('-')


def normalize_text(text: Optional[str]) -> str:
    """Normalizes text, strips whitespace and expands unicode ligatures."""
    if not text:
        return ""
    # Normalize ligatures (e.g. \ufb03 -> ffi, \ufb01 -> fi)
    normalized = unicodedata.normalize('NFKD', str(text))
    # Filter out unprintable control characters except newline and tab
    cleaned = "".join(ch for ch in normalized if unicodedata.category(ch)[0] != 'C' or ch in '\n\t')
    return cleaned.strip()


def parse_hours(val: Optional[str]) -> Optional[int]:
    """Extracts numeric training hours from string."""
    if not val:
        return None
    match = re.search(r'(\d+)', str(val))
    return int(match.group(1)) if match else None


def get_notional_hour_range(hours: Optional[int]) -> Optional[str]:
    """Buckets hours into official NQR categories."""
    if hours is None:
        return None
    if hours <= 200:
        return "1–200"
    elif hours <= 400:
        return "201–400"
    elif hours <= 600:
        return "401–600"
    elif hours <= 800:
        return "601–800"
    elif hours <= 1000:
        return "801–1000"
    elif hours <= 1200:
        return "1001–1200"
    elif hours <= 2400:
        return "1201–2400"
    else:
        return "Above 2401"


def parse_level(val: Optional[str]) -> Optional[float]:
    """Extracts NSQF level as float, supporting half-levels (e.g. 2.5, 4.5)."""
    if not val:
        return None
    match = re.search(r'([0-9]+(?:\.[0-9]+)?)', str(val))
    return float(match.group(1)) if match else None


def read_xlsx_cells(fpath: str) -> List[Dict[int, str]]:
    """
    Parses a single .xlsx file using standard library zipfile and xml.
    Returns list of rows, where each row is a dict of col_idx -> string.
    Zero external dependencies required.
    """
    with zipfile.ZipFile(fpath) as z:
        strings: List[str] = []
        if 'xl/sharedStrings.xml' in z.namelist():
            sst = ET.fromstring(z.read('xl/sharedStrings.xml'))
            ns = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            for si in sst.findall('ns:si', ns):
                text = ''.join([t.text or '' for t in si.findall('.//ns:t', ns)])
                strings.append(normalize_text(text))

        sheet = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
        ns = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

        parsed_rows: List[Dict[int, str]] = []
        for row in sheet.findall('.//ns:row', ns):
            row_data: Dict[int, str] = {}
            for c in row.findall('ns:c', ns):
                ref = c.get('r', '')
                m = re.match(r'([A-Z]+)', ref)
                col_idx = 0
                if m:
                    for ch in m.group(1):
                        col_idx = col_idx * 26 + (ord(ch) - ord('A') + 1)
                    col_idx -= 1

                t = c.get('t')
                val_el = c.find('ns:v', ns)
                val = val_el.text if val_el is not None else ''
                if t == 's' and val.isdigit():
                    idx = int(val)
                    val = strings[idx] if idx < len(strings) else ''
                elif t == 'inlineStr':
                    is_el = c.find('.//ns:t', ns)
                    val = is_el.text if is_el is not None else ''
                row_data[col_idx] = normalize_text(val)
            parsed_rows.append(row_data)
        return parsed_rows


def find_dataset_directory() -> Path:
    """Finds the NSQF-NQR Course Dataset directory."""
    candidates = [
        Path("NSQF-NQR Course Dataset"),
        Path("../NSQF-NQR Course Dataset"),
        Path("../../NSQF-NQR Course Dataset"),
        Path(__file__).resolve().parent.parent.parent.parent / "NSQF-NQR Course Dataset",
    ]
    for p in candidates:
        if p.exists() and p.is_dir():
            return p.resolve()
    raise FileNotFoundError("Could not find 'NSQF-NQR Course Dataset' directory.")


def parse_all_courses(dataset_path: Optional[Path] = None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    """
    Parses all 44 workbooks from the NSQF-NQR Course Dataset.
    Returns:
        (sectors, qualifications, audit_metrics)
    """
    if dataset_path is None:
        dataset_path = find_dataset_directory()

    files = sorted(list(dataset_path.glob("*.xlsx")))
    if not files:
        raise FileNotFoundError(f"No .xlsx files found in {dataset_path}")

    sectors_dict: Dict[str, Dict[str, Any]] = {}
    qualifications: List[Dict[str, Any]] = []
    
    audit_metrics: Dict[str, Any] = {
        "total_files": len(files),
        "total_source_rows": 0,
        "valid_catalog_records": 0,
        "excluded_by_sector": 0,
        "manual_review_needed": 0,
        "excluded_sectors_found": [],
        "levels": Counter(),
        "hour_ranges": Counter(),
        "pwd_count": 0,
        "pwd_categories": Counter(),
        "duplicate_codes": Counter(),
    }

    seen_codes: Counter = Counter()

    for f in files:
        rows = read_xlsx_cells(str(f))
        if len(rows) < 2:
            audit_metrics["manual_review_needed"] += 1
            logger.warning(f"File {f.name} has fewer than 2 rows; skipped.")
            continue

        header_row = rows[1]
        max_col = max(header_row.keys()) if header_row else 0
        headers = [header_row.get(i, "") for i in range(max_col + 1)]
        col_map = {name: i for i, name in enumerate(headers) if name}

        data_rows = rows[2:]
        file_sector_name = ""

        for r in data_rows:
            audit_metrics["total_source_rows"] += 1
            title = r.get(col_map.get("Title", 1), "")
            code = r.get(col_map.get("Code", 2), "")
            desc = r.get(col_map.get("Description", 3), "")
            sector = r.get(col_map.get("Sector Name", 4), "")
            level_str = r.get(col_map.get("Level", 5), "")
            max_h_str = r.get(col_map.get("Maximum Notational Hours", 6), "")
            min_h_str = r.get(col_map.get("Minimum Notational Hours", 7), "")
            version = r.get(col_map.get("Version", 8), "")
            approved = r.get(col_map.get("Originally Approved", 9), "")
            valid_till = r.get(col_map.get("Valid Till", 10), "")
            awarding = r.get(col_map.get("Awarding Body", 11), "")
            certifying = r.get(col_map.get("Certifying Bodies", 12), "")
            occupation = r.get(col_map.get("Proposed Occupation", 13), "")
            progression = r.get(col_map.get("Progression Pathway", 14), "")
            q_type = r.get(col_map.get("Qualifcation Type", 15), "")
            adopted = r.get(col_map.get("Adopted Qualifcation", 16), "")
            delivery_h = r.get(col_map.get("Training Delivery Hours", 17), "")

            if not sector:
                sector = f.stem
            file_sector_name = sector

            # Check excluded sectors
            if sector in EXCLUDED_SECTORS:
                audit_metrics["excluded_by_sector"] += 1
                if sector not in audit_metrics["excluded_sectors_found"]:
                    audit_metrics["excluded_sectors_found"].append(sector)
                continue

            if not title or not code:
                audit_metrics["manual_review_needed"] += 1
                continue

            sector_id = slugify(sector)
            if sector_id not in sectors_dict:
                sectors_dict[sector_id] = {
                    "id": sector_id,
                    "name": sector,
                    "course_count": 0,
                    "is_excluded": False,
                }
            sectors_dict[sector_id]["course_count"] += 1

            level = parse_level(level_str)
            if level is None:
                level = 1.0  # safe fallback if level omitted

            min_h = parse_hours(min_h_str)
            max_h = parse_hours(max_h_str)
            effective_h = max_h if max_h is not None else min_h
            h_range = get_notional_hour_range(effective_h)

            seen_codes[code] += 1

            # PwD detection
            is_pwd = False
            pwd_cats: List[str] = []
            if "disabilit" in sector.lower() or "pwd" in sector.lower() or "pwd" in title.lower() or "pwd" in desc.lower():
                is_pwd = True

            for tag in ["LD", "SHI", "VI", "ID", "MD", "ASD", "CP", "MR", "OH"]:
                pattern = rf'\b{tag}\b'
                if re.search(pattern, title) or re.search(pattern, desc):
                    is_pwd = True
                    pwd_cats.append(tag)
                    audit_metrics["pwd_categories"][tag] += 1

            if is_pwd:
                audit_metrics["pwd_count"] += 1

            audit_metrics["levels"][str(level)] += 1
            if h_range:
                audit_metrics["hour_ranges"][h_range] += 1

            qualifications.append({
                "q_code": code,
                "title": title,
                "sector_id": sector_id,
                "sector_name": sector,
                "nsqf_level": level,
                "description": desc,
                "min_notional_hours": min_h,
                "max_notional_hours": max_h,
                "notional_hours_range": h_range,
                "version": version,
                "originally_approved": approved,
                "valid_till": valid_till,
                "awarding_body": awarding,
                "certifying_bodies": certifying,
                "proposed_occupation": occupation,
                "progression_pathway": progression,
                "qualification_type": q_type,
                "adopted_qualification": adopted,
                "training_delivery_hours": delivery_h,
                "is_pwd": is_pwd,
                "pwd_categories": pwd_cats,
                "raw_metadata": {
                    "source_row": r.get(col_map.get("S No.", 0), ""),
                    "qualification_type": q_type,
                    "version": version,
                },
                "source_file": f.name,
                "is_active": True,
            })

    audit_metrics["valid_catalog_records"] = len(qualifications)
    for code, count in seen_codes.items():
        if count > 1:
            audit_metrics["duplicate_codes"][code] = count

    sectors = list(sectors_dict.values())
    return sectors, qualifications, audit_metrics


def generate_seed_sql(out_path: Path) -> int:
    """
    Generates a production-ready SQL seed file containing idempotent
    INSERT statements with ON CONFLICT DO UPDATE for all sectors and qualifications.
    """
    sectors, qualifications, _ = parse_all_courses()
    
    lines: List[str] = [
        "-- Utthan: Production Seed Data for NSQF / NQR Course Catalog",
        "-- Auto-generated from authoritative NSQF-NQR Course Dataset",
        "-- Idempotent execution safe with ON CONFLICT clauses.",
        "",
        "BEGIN;",
        "",
        "-- 1. Seed Sectors",
    ]

    for s in sectors:
        name_esc = s['name'].replace("'", "''")
        id_esc = s['id'].replace("'", "''")
        lines.append(
            f"INSERT INTO nsqf_sectors (id, name, course_count, is_excluded) "
            f"VALUES ('{id_esc}', '{name_esc}', {s['course_count']}, {str(s['is_excluded']).lower()}) "
            f"ON CONFLICT (id) DO UPDATE SET "
            f"name = EXCLUDED.name, course_count = EXCLUDED.course_count, updated_at = NOW();"
        )

    lines.append("")
    lines.append("-- 2. Seed Qualifications")

    def sql_str(val: Optional[str]) -> str:
        if val is None:
            return "NULL"
        escaped = str(val).replace("'", "''")
        return f"'{escaped}'"

    def sql_int(val: Optional[int]) -> str:
        return str(val) if val is not None else "NULL"

    def sql_arr(val: List[str]) -> str:
        if not val:
            return "'{}'::text[]"
        items = ",".join([f'"{x}"' for x in val])
        return f"'{{{items}}}'::text[]"

    for q in qualifications:
        q_code = sql_str(q['q_code'])
        title = sql_str(q['title'])
        sector_id = sql_str(q['sector_id'])
        sector_name = sql_str(q['sector_name'])
        nsqf_level = q['nsqf_level']
        description = sql_str(q['description'])
        min_h = sql_int(q['min_notional_hours'])
        max_h = sql_int(q['max_notional_hours'])
        h_range = sql_str(q['notional_hours_range'])
        version = sql_str(q['version'])
        orig_app = sql_str(q['originally_approved'])
        valid_till = sql_str(q['valid_till'])
        awarding = sql_str(q['awarding_body'])
        certifying = sql_str(q['certifying_bodies'])
        occupation = sql_str(q['proposed_occupation'])
        progression = sql_str(q['progression_pathway'])
        q_type = sql_str(q['qualification_type'])
        adopted = sql_str(q['adopted_qualification'])
        delivery_h = sql_str(q['training_delivery_hours'])
        is_pwd = str(q['is_pwd']).lower()
        pwd_cats = sql_arr(q['pwd_categories'])
        raw_meta = sql_str(json.dumps(q['raw_metadata']))
        source_file = sql_str(q['source_file'])

        lines.append(
            f"INSERT INTO nsqf_qualifications ("
            f"q_code, title, sector_id, sector_name, nsqf_level, description, "
            f"min_notional_hours, max_notional_hours, notional_hours_range, version, "
            f"originally_approved, valid_till, awarding_body, certifying_bodies, "
            f"proposed_occupation, progression_pathway, qualification_type, adopted_qualification, "
            f"training_delivery_hours, is_pwd, pwd_categories, raw_metadata, source_file, is_active"
            f") VALUES ("
            f"{q_code}, {title}, {sector_id}, {sector_name}, {nsqf_level}, {description}, "
            f"{min_h}, {max_h}, {h_range}, {version}, "
            f"{orig_app}, {valid_till}, {awarding}, {certifying}, "
            f"{occupation}, {progression}, {q_type}, {adopted}, "
            f"{delivery_h}, {is_pwd}, {pwd_cats}, {raw_meta}::jsonb, {source_file}, true"
            f") ON CONFLICT (q_code, title) DO UPDATE SET "
            f"sector_id = EXCLUDED.sector_id, "
            f"nsqf_level = EXCLUDED.nsqf_level, "
            f"description = EXCLUDED.description, "
            f"min_notional_hours = EXCLUDED.min_notional_hours, "
            f"max_notional_hours = EXCLUDED.max_notional_hours, "
            f"notional_hours_range = EXCLUDED.notional_hours_range, "
            f"is_pwd = EXCLUDED.is_pwd, "
            f"pwd_categories = EXCLUDED.pwd_categories, "
            f"updated_at = NOW();"
        )

    lines.append("")
    lines.append("COMMIT;")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fp:
        fp.write("\n".join(lines))

    return len(qualifications)
