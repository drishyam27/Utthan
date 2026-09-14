"""
Utthan National Location Foundation Generator
Source: data/raw/lgd_districts.xls.xlsx (Ministry of Panchayati Raj, Govt of India)
Generates:
1. src/data/canonicalLocations.json (Single Source of Truth)
2. src/data/locations.js (Application-compatible JS module)
3. supabase/seed/02_all_india_districts.sql (Supabase 784-district seed)
4. supabase/verify/verify_location_master.sql (Supabase verification script)
"""

import os
import re
import json
import pandas as pd

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
EXCEL_PATH = os.path.join(ROOT_DIR, 'data', 'raw', 'lgd_districts.xls.xlsx')
CANONICAL_JSON_PATH = os.path.join(ROOT_DIR, 'src', 'data', 'canonicalLocations.json')
LOCATIONS_JS_PATH = os.path.join(ROOT_DIR, 'src', 'data', 'locations.js')
SEED_SQL_PATH = os.path.join(ROOT_DIR, 'supabase', 'seed', '02_all_india_districts.sql')
VERIFY_SQL_PATH = os.path.join(ROOT_DIR, 'supabase', 'verify', 'verify_location_master.sql')

# Authoritative State Mapping
STATE_DEFINITIONS = {
    1: {'code': 'JK', 'id': 'ut-jk', 'name': 'Jammu and Kashmir', 'type': 'UT'},
    2: {'code': 'HP', 'id': 'state-hp', 'name': 'Himachal Pradesh', 'type': 'STATE'},
    3: {'code': 'PB', 'id': 'state-pb', 'name': 'Punjab', 'type': 'STATE'},
    4: {'code': 'CH', 'id': 'ut-ch', 'name': 'Chandigarh', 'type': 'UT'},
    5: {'code': 'UT', 'id': 'state-ut', 'name': 'Uttarakhand', 'type': 'STATE'},
    6: {'code': 'HR', 'id': 'state-hr', 'name': 'Haryana', 'type': 'STATE'},
    7: {'code': 'DL', 'id': 'ut-dl', 'name': 'Delhi (NCT)', 'type': 'UT'},
    8: {'code': 'RJ', 'id': 'state-rj', 'name': 'Rajasthan', 'type': 'STATE'},
    9: {'code': 'UP', 'id': 'state-up', 'name': 'Uttar Pradesh', 'type': 'STATE'},
    10: {'code': 'BR', 'id': 'state-br', 'name': 'Bihar', 'type': 'STATE'},
    11: {'code': 'SK', 'id': 'state-sk', 'name': 'Sikkim', 'type': 'STATE'},
    12: {'code': 'AR', 'id': 'state-ar', 'name': 'Arunachal Pradesh', 'type': 'STATE'},
    13: {'code': 'NL', 'id': 'state-nl', 'name': 'Nagaland', 'type': 'STATE'},
    14: {'code': 'MN', 'id': 'state-mn', 'name': 'Manipur', 'type': 'STATE'},
    15: {'code': 'MZ', 'id': 'state-mz', 'name': 'Mizoram', 'type': 'STATE'},
    16: {'code': 'TR', 'id': 'state-tr', 'name': 'Tripura', 'type': 'STATE'},
    17: {'code': 'ML', 'id': 'state-ml', 'name': 'Meghalaya', 'type': 'STATE'},
    18: {'code': 'AS', 'id': 'state-as', 'name': 'Assam', 'type': 'STATE'},
    19: {'code': 'WB', 'id': 'state-wb', 'name': 'West Bengal', 'type': 'STATE'},
    20: {'code': 'JH', 'id': 'state-jh', 'name': 'Jharkhand', 'type': 'STATE'},
    21: {'code': 'OD', 'id': 'state-od', 'name': 'Odisha', 'type': 'STATE'},
    22: {'code': 'CT', 'id': 'state-ct', 'name': 'Chhattisgarh', 'type': 'STATE'},
    23: {'code': 'MP', 'id': 'state-mp', 'name': 'Madhya Pradesh', 'type': 'STATE'},
    24: {'code': 'GJ', 'id': 'state-gj', 'name': 'Gujarat', 'type': 'STATE'},
    27: {'code': 'MH', 'id': 'state-mh', 'name': 'Maharashtra', 'type': 'STATE'},
    28: {'code': 'AP', 'id': 'state-ap', 'name': 'Andhra Pradesh', 'type': 'STATE'},
    29: {'code': 'KA', 'id': 'state-ka', 'name': 'Karnataka', 'type': 'STATE'},
    30: {'code': 'GA', 'id': 'state-ga', 'name': 'Goa', 'type': 'STATE'},
    31: {'code': 'LD', 'id': 'ut-ld', 'name': 'Lakshadweep', 'type': 'UT'},
    32: {'code': 'KL', 'id': 'state-kl', 'name': 'Kerala', 'type': 'STATE'},
    33: {'code': 'TN', 'id': 'state-tn', 'name': 'Tamil Nadu', 'type': 'STATE'},
    34: {'code': 'PY', 'id': 'ut-py', 'name': 'Puducherry', 'type': 'UT'},
    35: {'code': 'AN', 'id': 'ut-an', 'name': 'Andaman and Nicobar Islands', 'type': 'UT'},
    36: {'code': 'TG', 'id': 'state-tg', 'name': 'Telangana', 'type': 'STATE'},
    37: {'code': 'LA', 'id': 'ut-la', 'name': 'Ladakh', 'type': 'UT'},
    38: {'code': 'DN', 'id': 'ut-dn', 'name': 'Dadra and Nagar Haveli and Daman and Diu', 'type': 'UT'}
}

# Preserve legacy IDs and codes for the 76 prototype districts
LEGACY_ALIASES = {
    ('state-up', 'kanpur nagar'): ('dist-up-kanpur', 'UP-KNP'),
    ('state-mh', 'chhatrapati sambhajinagar'): ('dist-mh-aurangabad', 'MH-CSN'),
    ('state-ka', 'bengaluru urban'): ('dist-ka-bengaluru', 'KA-BLR'),
    ('state-ka', 'dharwad'): ('dist-ka-hubballi', 'KA-DHW'),
    ('state-wb', 'south 24 parganas'): ('dist-wb-s24pgs', 'WB-S24'),
    ('state-wb', 'north 24 parganas'): ('dist-wb-n24pgs', 'WB-N24'),
    ('state-od', 'kataka'): ('dist-od-cuttack', 'OD-CUT'),
    ('state-od', 'khordha'): ('dist-od-khordha', 'OD-KHO'),
    ('state-jh', 'east singhbum'): ('dist-jh-east-singhbhum', 'JH-ESB'),
    ('state-kl', 'ernakulam'): ('dist-kl-ernakulam', 'KL-ERN'),
    ('state-as', 'kamrup metro'): ('dist-as-kamrup-metro', 'AS-KAM')
}

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def main():
    print(f"Reading Excel: {EXCEL_PATH}")
    df = pd.read_excel(EXCEL_PATH, sheet_name='allDistrictofIndia', header=1)
    df.columns = ['s_no', 'state_code', 'state_name', 'district_code', 'district_name', 'c01', 'c11']
    print(f"Read {len(df)} rows from LGD spreadsheet.")

    # Read legacy locations.js to extract legacy matches
    with open(LOCATIONS_JS_PATH, 'r', encoding='utf-8') as f:
        loc_text = f.read()

    legacy_dists = re.findall(r"{\s*id:\s*'([^']+)',\s*stateId:\s*'([^']+)',\s*name:\s*'([^']+)',\s*code:\s*'([^']+)'\s*}", loc_text)
    legacy_by_state_name = {}
    for lid, lsid, lname, lcode in legacy_dists:
        legacy_by_state_name[(lsid, lname.lower())] = (lid, lcode)

    # Build States
    canonical_states = []
    for lgd_code in sorted(STATE_DEFINITIONS.keys()):
        s = STATE_DEFINITIONS[lgd_code]
        canonical_states.append({
            "id": s['id'],
            "code": s['code'],
            "name": s['name'],
            "lgdCode": lgd_code,
            "type": s['type']
        })

    # Build Districts
    canonical_districts = []
    for _, row in df.iterrows():
        lgd_state_code = int(row['state_code'])
        state_meta = STATE_DEFINITIONS[lgd_state_code]
        d_name = str(row['district_name']).strip()
        lgd_dist_code = int(row['district_code'])
        state_code = state_meta['code']
        state_id = state_meta['id']

        # Determine ID and Code
        legacy_match = legacy_by_state_name.get((state_id, d_name.lower()))
        if not legacy_match:
            legacy_match = LEGACY_ALIASES.get((state_id, d_name.lower()))

        if legacy_match:
            dist_id, dist_code = legacy_match
        else:
            dist_id = f"dist-{state_code.lower()}-{slugify(d_name)}"
            dist_code = f"{state_code}-{lgd_dist_code}"

        canonical_districts.append({
            "id": dist_id,
            "code": dist_code,
            "stateCode": state_code,
            "stateId": state_id,
            "lgdDistrictCode": lgd_dist_code,
            "name": d_name,
            "census2001Code": int(row['c01']),
            "census2011Code": int(row['c11'])
        })

    # Assertions
    assert len(canonical_states) == 36, f"Expected 36 states, got {len(canonical_states)}"
    assert len(canonical_districts) == 784, f"Expected 784 districts, got {len(canonical_districts)}"
    
    unique_ids = set(d['id'] for d in canonical_districts)
    assert len(unique_ids) == 784, f"Expected 784 unique district IDs, got {len(unique_ids)}"

    unique_lgd_dist = set(d['lgdDistrictCode'] for d in canonical_districts)
    assert len(unique_lgd_dist) == 784, f"Expected 784 unique LGD district codes, got {len(unique_lgd_dist)}"

    # Check zero duplicate names within state
    pairs = set(f"{d['stateId']}::{d['name'].lower()}" for d in canonical_districts)
    assert len(pairs) == 784, "Found duplicate district names within same state"

    # 1. Write src/data/canonicalLocations.json
    canonical_data = {
        "metadata": {
            "source": "Local Government Directory (LGD), Ministry of Panchayati Raj, Government of India",
            "sourceUrl": "https://lgdirectory.gov.in",
            "rawFile": "data/raw/lgd_districts.xls.xlsx",
            "stateCount": 36,
            "districtCount": 784,
            "extractedAt": "2026-09-15"
        },
        "states": canonical_states,
        "districts": canonical_districts
    }

    os.makedirs(os.path.dirname(CANONICAL_JSON_PATH), exist_ok=True)
    with open(CANONICAL_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(canonical_data, f, indent=2, ensure_ascii=False)
    print(f"[OK] Wrote canonical master: {CANONICAL_JSON_PATH} (36 states, 784 districts)")

    # 2. Write src/data/locations.js
    locations_js_content = f"""/**
 * Official Location Master Data for India
 * Authoritative Source: Local Government Directory (LGD), Ministry of Panchayati Raj, Govt of India (lgdirectory.gov.in)
 * Canonical Master: src/data/canonicalLocations.json
 * 28 States + 8 Union Territories = 36 Administrative Entities | 784 Total Districts
 * 
 * Auto-generated from canonicalLocations.json. Do not edit manually.
 */

import canonicalData from './canonicalLocations.json' with {{ type: 'json' }};

export const STATES = canonicalData.states.map(s => ({{
  id: s.id,
  code: s.code,
  name: s.name,
  type: s.type === 'UT' ? 'union_territory' : 'state',
  lgdCode: s.lgdCode,
  entityType: s.type
}}));

export const DISTRICTS = canonicalData.districts.map(d => ({{
  id: d.id,
  stateId: d.stateId,
  stateCode: d.stateCode,
  name: d.name,
  code: d.code,
  lgdDistrictCode: d.lgdDistrictCode,
  census2001Code: d.census2001Code,
  census2011Code: d.census2011Code
}}));

export function getStates() {{
  return STATES;
}}

export function getStateById(stateId) {{
  if (!stateId) return null;
  return STATES.find(s => s.id === stateId || s.code === stateId);
}}

export function getDistrictsByState(stateId) {{
  if (!stateId) return [];
  return DISTRICTS.filter(d => d.stateId === stateId || d.stateCode === stateId);
}}

export function getDistrictById(districtId) {{
  if (!districtId) return null;
  return DISTRICTS.find(
    d => d.id === districtId || 
         d.code === districtId || 
         d.lgdDistrictCode === Number(districtId)
  );
}}
"""
    with open(LOCATIONS_JS_PATH, 'w', encoding='utf-8') as f:
        f.write(locations_js_content)
    print(f"[OK] Wrote application locations module: {LOCATIONS_JS_PATH}")

    # 3. Write supabase/seed/02_all_india_districts.sql
    os.makedirs(os.path.dirname(SEED_SQL_PATH), exist_ok=True)
    
    sql_lines = [
        "-- ============================================================================",
        "-- Utthan National Location Master: Complete 784 Districts Seed",
        "-- Authoritative Source: Local Government Directory (LGD), Ministry of Panchayati Raj, Govt of India",
        "-- Safe to re-run: Uses ON CONFLICT (id) DO UPDATE",
        "-- Covers all 36 States/UTs and exactly 784 official districts",
        "-- ============================================================================\n",
        "-- Ensure lgd_code and lgd_district_code columns exist safely",
        "ALTER TABLE states ADD COLUMN IF NOT EXISTS lgd_code INTEGER;",
        "ALTER TABLE districts ADD COLUMN IF NOT EXISTS lgd_district_code INTEGER;\n",
        "-- Ensure states table has official LGD codes updated",
    ]

    for s in canonical_states:
        sql_lines.append(f"UPDATE states SET lgd_code = {s['lgdCode']} WHERE id = '{s['id']}';")
    sql_lines.append("")

    sql_lines.append("-- Seed All 784 Districts")
    sql_lines.append("INSERT INTO districts (id, state_id, name, code, lgd_district_code) VALUES")
    
    dist_values = []
    for d in canonical_districts:
        # Escape single quotes in district names if any
        escaped_name = d['name'].replace("'", "''")
        dist_values.append(
            f"('{d['id']}', '{d['stateId']}', '{escaped_name}', '{d['code']}', {d['lgdDistrictCode']})"
        )
    sql_lines.append(",\n".join(dist_values))
    sql_lines.append("""ON CONFLICT (id) DO UPDATE SET
    state_id = EXCLUDED.state_id,
    name = EXCLUDED.name,
    code = EXCLUDED.code,
    lgd_district_code = EXCLUDED.lgd_district_code;\n""")

    with open(SEED_SQL_PATH, 'w', encoding='utf-8') as f:
        f.write("\n".join(sql_lines))
    print(f"[OK] Wrote Supabase 784-district seed: {SEED_SQL_PATH}")

    # 4. Write supabase/verify/verify_location_master.sql
    os.makedirs(os.path.dirname(VERIFY_SQL_PATH), exist_ok=True)
    verify_sql_content = """-- ============================================================================
-- Utthan Location Master Verification Script
-- Execute in Supabase SQL Editor to verify complete national location foundation
-- ============================================================================

-- 1. States Count (Expected: 36)
SELECT 
    COUNT(*) AS total_states,
    COUNT(CASE WHEN type = 'state' THEN 1 END) AS states_count,
    COUNT(CASE WHEN type = 'union_territory' THEN 1 END) AS ut_count
FROM states;

-- 2. Districts Count (Expected: 784)
SELECT 
    COUNT(*) AS total_districts,
    COUNT(DISTINCT lgd_district_code) AS unique_lgd_district_codes,
    COUNT(DISTINCT id) AS unique_district_ids
FROM districts;

-- 3. Orphan Districts Check (Expected: 0)
SELECT COUNT(*) AS orphan_districts
FROM districts d
LEFT JOIN states s ON d.state_id = s.id
WHERE s.id IS NULL;

-- 4. Duplicate LGD District Codes Check (Expected: 0 rows)
SELECT lgd_district_code, COUNT(*) AS count
FROM districts
WHERE lgd_district_code IS NOT NULL
GROUP BY lgd_district_code
HAVING COUNT(*) > 1;

-- 5. Duplicate District Names within Same State (Expected: 0 rows)
SELECT state_id, name, COUNT(*) AS count
FROM districts
GROUP BY state_id, name
HAVING COUNT(*) > 1;

-- 6. District Count Grouped by State/UT (Total sum must equal 784)
SELECT 
    s.code AS state_code,
    s.name AS state_name,
    s.lgd_code,
    COUNT(d.id) AS district_count
FROM states s
LEFT JOIN districts d ON s.id = d.state_id
GROUP BY s.id, s.code, s.name, s.lgd_code
ORDER BY s.lgd_code;
"""
    with open(VERIFY_SQL_PATH, 'w', encoding='utf-8') as f:
        f.write(verify_sql_content)
    print(f"[OK] Wrote Supabase verification SQL: {VERIFY_SQL_PATH}")

if __name__ == '__main__':
    main()
