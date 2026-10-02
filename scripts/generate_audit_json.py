import glob
import json
import os
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

# Force utf-8 output for Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def normalize_text(text: str) -> str:
    if not text:
        return ""
    # Normalize unicode ligatures (e.g. \ufb03 -> ffi)
    normalized = unicodedata.normalize('NFKD', text)
    # Remove control characters except newline and tab
    cleaned = "".join(ch for ch in normalized if unicodedata.category(ch)[0] != 'C' or ch in '\n\t')
    return cleaned.strip()

def read_xlsx(fpath: str):
    with zipfile.ZipFile(fpath) as z:
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            sst = ET.fromstring(z.read('xl/sharedStrings.xml'))
            ns = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            for si in sst.findall('ns:si', ns):
                text = ''.join([t.text or '' for t in si.findall('.//ns:t', ns)])
                strings.append(normalize_text(text))
        
        sheet = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
        ns = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        
        parsed_rows = []
        for row in sheet.findall('.//ns:row', ns):
            row_data = {}
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

EXCLUDED_SECTORS = {
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

def parse_hours(val):
    if not val:
        return None
    match = re.search(r'(\d+)', str(val))
    return int(match.group(1)) if match else None

def get_hour_range(h):
    if h is None:
        return "Unknown"
    if h <= 200:
        return "1–200"
    elif h <= 400:
        return "201–400"
    elif h <= 600:
        return "401–600"
    elif h <= 800:
        return "601–800"
    elif h <= 1000:
        return "801–1000"
    elif h <= 1200:
        return "1001–1200"
    elif h <= 2400:
        return "1201–2400"
    else:
        return "Above 2401"

def parse_level(val):
    if not val:
        return None
    match = re.search(r'([0-9]+(?:\.[0-9]+)?)', str(val))
    return float(match.group(1)) if match else None

def run_audit():
    dataset_dir = Path(r"NSQF-NQR Course Dataset")
    files = sorted(list(dataset_dir.glob("*.xlsx")))
    
    audit_data = {
        "total_files": len(files),
        "total_rows": 0,
        "header_columns": [],
        "files": [],
        "sectors": {},
        "excluded_sectors_found": {},
        "levels": Counter(),
        "notional_hour_ranges": Counter(),
        "pwd_count": 0,
        "pwd_categories": Counter(),
        "duplicate_codes": {},
        "duplicate_titles": {},
        "missing_fields": Counter(),
        "awarding_bodies": Counter(),
        "qualification_types": Counter(),
        "manual_review_needed": [],
    }
    
    all_codes = Counter()
    all_titles = Counter()
    courses_by_code = defaultdict(list)
    courses_by_title = defaultdict(list)
    
    for f in files:
        rows = read_xlsx(str(f))
        if len(rows) < 2:
            audit_data["manual_review_needed"].append({
                "file": f.name,
                "reason": "Workbook has less than 2 rows (empty or missing headers)"
            })
            continue
            
        header_row = rows[1]
        max_col = max(header_row.keys()) if header_row else 0
        headers = [header_row.get(i, "") for i in range(max_col + 1)]
        if not audit_data["header_columns"]:
            audit_data["header_columns"] = [h for h in headers if h]
            
        col_map = {name: i for i, name in enumerate(headers) if name}
        data_rows = rows[2:]
        
        file_sector = None
        file_courses = []
        
        for r_i, r in enumerate(data_rows):
            audit_data["total_rows"] += 1
            
            s_no = r.get(col_map.get("S No.", 0), "")
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
            
            if not sector and not file_sector:
                file_sector = f.stem
            elif sector:
                file_sector = sector
                
            if not title:
                audit_data["missing_fields"]["title"] += 1
            if not code:
                audit_data["missing_fields"]["code"] += 1
            if not level_str:
                audit_data["missing_fields"]["level"] += 1
            if not sector:
                audit_data["missing_fields"]["sector"] += 1
                
            all_codes[code] += 1
            all_titles[title] += 1
            courses_by_code[code].append({"file": f.name, "title": title, "row": r_i + 3})
            courses_by_title[title].append({"file": f.name, "code": code, "sector": sector})
            
            lvl = parse_level(level_str)
            if lvl is not None:
                audit_data["levels"][str(lvl)] += 1
            else:
                audit_data["levels"]["Unknown"] += 1
                
            min_h = parse_hours(min_h_str)
            max_h = parse_hours(max_h_str)
            effective_h = max_h if max_h is not None else min_h
            h_range = get_hour_range(effective_h)
            audit_data["notional_hour_ranges"][h_range] += 1
            
            if awarding:
                audit_data["awarding_bodies"][awarding] += 1
            if q_type:
                audit_data["qualification_types"][q_type] += 1
                
            # Check PwD applicability
            is_pwd = False
            pwd_tags = []
            if "disabilit" in sector.lower() or "pwd" in sector.lower() or "pwd" in title.lower() or "pwd" in desc.lower() or "disability" in desc.lower():
                is_pwd = True
            
            # Detect PwD disability type tags (e.g., LD, SHI, VI, ID)
            for tag in ["LD", "SHI", "VI", "ID", "MD", "ASD", "CP", "MR", "OH"]:
                pattern = rf'\b{tag}\b'
                if re.search(pattern, title) or re.search(pattern, desc):
                    is_pwd = True
                    pwd_tags.append(tag)
                    audit_data["pwd_categories"][tag] += 1
                    
            if is_pwd:
                audit_data["pwd_count"] += 1
                
            file_courses.append({
                "code": code,
                "title": title,
                "level": lvl,
                "hours": effective_h,
                "is_pwd": is_pwd
            })
            
        file_sector_normalized = file_sector.strip() if file_sector else f.stem
        audit_data["sectors"][file_sector_normalized] = audit_data["sectors"].get(file_sector_normalized, 0) + len(data_rows)
        
        # Check excluded sectors
        for ex in EXCLUDED_SECTORS:
            if ex.lower() == file_sector_normalized.lower():
                audit_data["excluded_sectors_found"][ex] = audit_data["excluded_sectors_found"].get(ex, 0) + len(data_rows)
                
        audit_data["files"].append({
            "filename": f.name,
            "sector": file_sector_normalized,
            "row_count": len(data_rows),
            "headers": headers[:5]
        })

    # Duplicates analysis
    for code, count in all_codes.items():
        if count > 1 and code:
            audit_data["duplicate_codes"][code] = courses_by_code[code]
            
    for title, count in all_titles.items():
        if count > 1 and title:
            audit_data["duplicate_titles"][title] = courses_by_title[title]
            
    # Convert counters to regular dicts for JSON serialization
    audit_data["levels"] = dict(sorted(audit_data["levels"].items(), key=lambda x: (float(x[0]) if x[0] != "Unknown" else -1)))
    audit_data["notional_hour_ranges"] = dict(audit_data["notional_hour_ranges"])
    audit_data["missing_fields"] = dict(audit_data["missing_fields"])
    audit_data["pwd_categories"] = dict(audit_data["pwd_categories"])
    audit_data["awarding_bodies"] = dict(audit_data["awarding_bodies"].most_common(20))
    audit_data["qualification_types"] = dict(audit_data["qualification_types"])
    
    out_dir = Path("docs")
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "nsqf_dataset_audit.json"
    with open(out_file, "w", encoding="utf-8") as fp:
        json.dump(audit_data, fp, indent=2, ensure_ascii=False)
        
    print(f"Audit completed successfully!")
    print(f"Total Files: {audit_data['total_files']}")
    print(f"Total Course Rows: {audit_data['total_rows']}")
    print(f"Total Sectors: {len(audit_data['sectors'])}")
    print(f"Excluded Sectors Present: {len(audit_data['excluded_sectors_found'])}")
    print(f"Duplicate Codes: {len(audit_data['duplicate_codes'])}")
    print(f"PwD Courses: {audit_data['pwd_count']}")
    print(f"Audit report saved to: {out_file}")

if __name__ == "__main__":
    run_audit()
