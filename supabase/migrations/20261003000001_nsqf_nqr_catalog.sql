-- Utthan: Authoritative NSQF / NQR Course Catalog Migration
-- Migration: 20261003000001_nsqf_nqr_catalog.sql
-- Additive relational schema for official NQR qualifications & sector taxonomy.

-- ============================================================================
-- 1. NSQF SECTORS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS nsqf_sectors (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE,
    course_count INTEGER NOT NULL DEFAULT 0,
    is_excluded BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_nsqf_sectors_excluded ON nsqf_sectors(is_excluded);

-- ============================================================================
-- 2. NSQF QUALIFICATIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS nsqf_qualifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    q_code VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    sector_id VARCHAR(64) NOT NULL REFERENCES nsqf_sectors(id) ON DELETE RESTRICT,
    sector_name VARCHAR(150) NOT NULL,
    nsqf_level NUMERIC(3, 1) NOT NULL,
    description TEXT,
    min_notional_hours INTEGER,
    max_notional_hours INTEGER,
    notional_hours_range VARCHAR(50),
    version VARCHAR(50),
    originally_approved VARCHAR(50),
    valid_till VARCHAR(50),
    awarding_body TEXT,
    certifying_bodies TEXT,
    proposed_occupation TEXT,
    progression_pathway TEXT,
    qualification_type VARCHAR(100),
    adopted_qualification TEXT,
    training_delivery_hours TEXT,
    is_pwd BOOLEAN NOT NULL DEFAULT FALSE,
    pwd_categories TEXT[] DEFAULT '{}',
    raw_metadata JSONB DEFAULT '{}'::jsonb,
    source_file VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_nsqf_q_code_title UNIQUE (q_code, title)
);

-- Query performance indexes
CREATE INDEX IF NOT EXISTS idx_nsqf_qualifications_sector_id ON nsqf_qualifications(sector_id);
CREATE INDEX IF NOT EXISTS idx_nsqf_qualifications_nsqf_level ON nsqf_qualifications(nsqf_level);
CREATE INDEX IF NOT EXISTS idx_nsqf_qualifications_is_pwd ON nsqf_qualifications(is_pwd);
CREATE INDEX IF NOT EXISTS idx_nsqf_qualifications_q_code ON nsqf_qualifications(q_code);
CREATE INDEX IF NOT EXISTS idx_nsqf_qualifications_hours_range ON nsqf_qualifications(notional_hours_range);
CREATE INDEX IF NOT EXISTS idx_nsqf_qualifications_is_active ON nsqf_qualifications(is_active);

-- ============================================================================
-- 3. ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================
ALTER TABLE nsqf_sectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE nsqf_qualifications ENABLE ROW LEVEL SECURITY;

-- Catalog reads are public
DROP POLICY IF EXISTS "Public select nsqf_sectors" ON nsqf_sectors;
CREATE POLICY "Public select nsqf_sectors" ON nsqf_sectors
    FOR SELECT USING (true);

DROP POLICY IF EXISTS "Public select nsqf_qualifications" ON nsqf_qualifications;
CREATE POLICY "Public select nsqf_qualifications" ON nsqf_qualifications
    FOR SELECT USING (true);

-- Permissions for anon, authenticated, service_role
GRANT SELECT ON TABLE nsqf_sectors TO anon, authenticated;
GRANT SELECT ON TABLE nsqf_qualifications TO anon, authenticated;

GRANT ALL PRIVILEGES ON TABLE nsqf_sectors TO service_role;
GRANT ALL PRIVILEGES ON TABLE nsqf_qualifications TO service_role;
