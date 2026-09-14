-- ============================================================================
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
