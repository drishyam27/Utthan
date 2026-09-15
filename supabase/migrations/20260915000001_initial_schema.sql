-- Utthan PostgreSQL Schema for Supabase
-- Phase 1 Migration: Foundation Data Layer, Locations, Opportunities, Skills, and Beneficiaries

-- Enable pgcrypto for UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- 1. STATES MASTER TABLE
-- Source: Local Government Directory (LGD), Ministry of Panchayati Raj, Govt of India
-- ============================================================================
CREATE TABLE IF NOT EXISTS states (
    id VARCHAR(32) PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL DEFAULT 'state' CHECK (type IN ('state', 'union_territory')),
    lgd_code INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- 2. DISTRICTS MASTER TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS districts (
    id VARCHAR(64) PRIMARY KEY,
    state_id VARCHAR(32) NOT NULL REFERENCES states(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20),
    lgd_district_code INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_state_district_name UNIQUE (state_id, name)
);

-- Index for fast lookup by state
CREATE INDEX IF NOT EXISTS idx_districts_state_id ON districts(state_id);

-- ============================================================================
-- 3. SKILLS MASTER TABLE
-- Standardized against Sector Skill Councils & NSQF Framework
-- ============================================================================
CREATE TABLE IF NOT EXISTS skills (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    sector VARCHAR(100),
    nsqf_level INTEGER CHECK (nsqf_level BETWEEN 1 AND 8),
    qp_code VARCHAR(50),
    source VARCHAR(150),
    source_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_skills_nsqf ON skills(nsqf_level);
CREATE INDEX IF NOT EXISTS idx_skills_sector ON skills(sector);

-- ============================================================================
-- 4. OPPORTUNITIES MASTER TABLE
-- Real Welfare Schemes, Subsidized Courses & Livelihood Tracks
-- ============================================================================
CREATE TABLE IF NOT EXISTS opportunities (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(250) NOT NULL,
    category VARCHAR(100) NOT NULL,
    provider VARCHAR(200) NOT NULL,
    source VARCHAR(200) NOT NULL,
    source_url TEXT,
    state_id VARCHAR(32) REFERENCES states(id) ON DELETE SET NULL,
    district_id VARCHAR(64) REFERENCES districts(id) ON DELETE SET NULL,
    education_min VARCHAR(50) NOT NULL DEFAULT 'no_formal' 
        CHECK (education_min IN ('no_formal', '8th_pass', '10th_pass', '12th_pass', 'iti_vocational', 'graduate')),
    age_min INTEGER DEFAULT 18 CHECK (age_min >= 14),
    age_max INTEGER CHECK (age_max IS NULL OR age_max >= age_min),
    mobility_requirement VARCHAR(50) DEFAULT 'within_15km'
        CHECK (mobility_requirement IN ('village_block', 'within_15km', 'district_wide', 'relocate_hostel')),
    stipend TEXT,
    expected_earnings TEXT,
    duration TEXT,
    nsqf_level INTEGER CHECK (nsqf_level IS NULL OR (nsqf_level BETWEEN 1 AND 8)),
    qp_code VARCHAR(50),
    overview TEXT,
    primary_goal_fit VARCHAR(50) DEFAULT 'training_stipend'
        CHECK (primary_goal_fit IN ('training_stipend', 'job_placement', 'micro_business')),
    target_trade_keywords TEXT[] DEFAULT '{}',
    eligibility_rules JSONB DEFAULT '{}'::jsonb,
    action_steps JSONB DEFAULT '[]'::jsonb,
    application_url TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_opportunities_location ON opportunities(state_id, district_id);
CREATE INDEX IF NOT EXISTS idx_opportunities_category ON opportunities(category);
CREATE INDEX IF NOT EXISTS idx_opportunities_nsqf ON opportunities(nsqf_level);
CREATE INDEX IF NOT EXISTS idx_opportunities_active ON opportunities(active);

-- ============================================================================
-- 5. OPPORTUNITY_SKILLS MAPPING (Many-to-Many)
-- ============================================================================
CREATE TABLE IF NOT EXISTS opportunity_skills (
    opportunity_id VARCHAR(64) NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
    skill_id VARCHAR(64) NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    is_taught BOOLEAN NOT NULL DEFAULT TRUE,
    priority INTEGER DEFAULT 1,
    PRIMARY KEY (opportunity_id, skill_id)
);

-- ============================================================================
-- 6. BENEFICIARIES TABLE
-- Anonymous or Citizen Self-Reported Onboarding Data
-- ============================================================================
CREATE TABLE IF NOT EXISTS beneficiaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(150),
    preferred_language VARCHAR(20) NOT NULL DEFAULT 'hi',
    state_id VARCHAR(32) REFERENCES states(id) ON DELETE SET NULL,
    district_id VARCHAR(64) REFERENCES districts(id) ON DELETE SET NULL,
    education_level VARCHAR(50) DEFAULT 'no_formal',
    current_occupation VARCHAR(150),
    mobility_preference VARCHAR(50) DEFAULT 'within_15km',
    primary_goal VARCHAR(50) DEFAULT 'training_stipend',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_beneficiaries_location ON beneficiaries(state_id, district_id);

-- ============================================================================
-- 7. INTERVIEW SESSIONS TABLE
-- Audio/Text Interview Responses & Transcript History
-- ============================================================================
CREATE TABLE IF NOT EXISTS interview_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    beneficiary_id UUID REFERENCES beneficiaries(id) ON DELETE CASCADE,
    language VARCHAR(20) NOT NULL DEFAULT 'hi',
    responses JSONB NOT NULL DEFAULT '{}'::jsonb,
    transcript_log TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- 8. APPLICATIONS / ROADMAP MILESTONES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    beneficiary_id UUID NOT NULL REFERENCES beneficiaries(id) ON DELETE CASCADE,
    opportunity_id VARCHAR(64) NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'saved' CHECK (status IN ('saved', 'enrolled', 'in_progress', 'completed')),
    current_step INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_beneficiary_opportunity UNIQUE (beneficiary_id, opportunity_id)
);

-- ============================================================================
-- 9. ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================
ALTER TABLE states ENABLE ROW LEVEL SECURITY;
ALTER TABLE districts ENABLE ROW LEVEL SECURITY;
ALTER TABLE skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE opportunities ENABLE ROW LEVEL SECURITY;
ALTER TABLE opportunity_skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE beneficiaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE interview_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE applications ENABLE ROW LEVEL SECURITY;

-- Public Read for Catalog & Locations
CREATE POLICY "Public read states" ON states FOR SELECT USING (true);
CREATE POLICY "Public read districts" ON districts FOR SELECT USING (true);
CREATE POLICY "Public read skills" ON skills FOR SELECT USING (true);
CREATE POLICY "Public read opportunities" ON opportunities FOR SELECT USING (active = true);
CREATE POLICY "Public read opportunity_skills" ON opportunity_skills FOR SELECT USING (true);

-- Self-Service Anonymous Insert/Select for Beneficiary Sessions
CREATE POLICY "Public insert beneficiaries" ON beneficiaries FOR INSERT WITH CHECK (true);
CREATE POLICY "Public select beneficiaries" ON beneficiaries FOR SELECT USING (true);
CREATE POLICY "Public update beneficiaries" ON beneficiaries FOR UPDATE USING (true);

CREATE POLICY "Public insert interview_sessions" ON interview_sessions FOR INSERT WITH CHECK (true);
CREATE POLICY "Public select interview_sessions" ON interview_sessions FOR SELECT USING (true);

CREATE POLICY "Public manage applications" ON applications FOR ALL USING (true);

-- ============================================================================
-- 10. ROLE PERMISSIONS FOR POSTGREST (service_role, anon, authenticated)
-- ============================================================================
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL ROUTINES IN SCHEMA public TO anon, authenticated, service_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON ROUTINES TO anon, authenticated, service_role;
