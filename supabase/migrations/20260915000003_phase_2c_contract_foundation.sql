-- Utthan Phase 2C-1: Data Contract & Schema Foundation
-- Additive foundation for anonymous beneficiary persistence, interview
-- lifecycle tracking, and deterministic recommendation responses.
-- No API routes or frontend persistence are introduced by this migration.

-- ============================================================================
-- 1. Stable beneficiary categorical constraints
-- ============================================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'beneficiaries_education_level_check'
    ) THEN
        ALTER TABLE beneficiaries
            ADD CONSTRAINT beneficiaries_education_level_check
            CHECK (
                education_level IS NULL OR education_level IN
                ('no_formal', '8th_pass', '10th_pass', '12th_pass', 'iti_vocational', 'graduate')
            );
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'beneficiaries_mobility_preference_check'
    ) THEN
        ALTER TABLE beneficiaries
            ADD CONSTRAINT beneficiaries_mobility_preference_check
            CHECK (
                mobility_preference IS NULL OR mobility_preference IN
                ('village_block', 'within_15km', 'district_wide', 'relocate_hostel')
            );
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'beneficiaries_primary_goal_check'
    ) THEN
        ALTER TABLE beneficiaries
            ADD CONSTRAINT beneficiaries_primary_goal_check
            CHECK (
                primary_goal IS NULL OR primary_goal IN
                ('training_stipend', 'job_placement', 'micro_business')
            );
    END IF;
END
$$;

-- ============================================================================
-- 2. Interview lifecycle fields
-- ============================================================================

ALTER TABLE interview_sessions
    ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'draft',
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS completed_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS revision INTEGER NOT NULL DEFAULT 1,
    ADD COLUMN IF NOT EXISTS extracted_profile JSONB;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'interview_sessions_status_check'
    ) THEN
        ALTER TABLE interview_sessions
            ADD CONSTRAINT interview_sessions_status_check
            CHECK (status IN ('draft', 'completed'));
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'interview_sessions_revision_check'
    ) THEN
        ALTER TABLE interview_sessions
            ADD CONSTRAINT interview_sessions_revision_check
            CHECK (revision >= 1);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'interview_sessions_completion_state_check'
    ) THEN
        ALTER TABLE interview_sessions
            ADD CONSTRAINT interview_sessions_completion_state_check
            CHECK (
                (status = 'draft' AND completed_at IS NULL)
                OR (status = 'completed' AND completed_at IS NOT NULL)
            );
    END IF;
END
$$;

CREATE INDEX IF NOT EXISTS idx_interview_sessions_beneficiary_created
    ON interview_sessions(beneficiary_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_interview_sessions_status
    ON interview_sessions(status);

-- ============================================================================
-- 3. Anonymous capability sessions
-- ============================================================================

CREATE TABLE IF NOT EXISTS beneficiary_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    beneficiary_id UUID NOT NULL REFERENCES beneficiaries(id) ON DELETE CASCADE,
    token_hash CHAR(64) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_used_at TIMESTAMPTZ,
    rotated_at TIMESTAMPTZ,
    revoked_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_beneficiary_sessions_beneficiary
    ON beneficiary_sessions(beneficiary_id);

CREATE INDEX IF NOT EXISTS idx_beneficiary_sessions_expires
    ON beneficiary_sessions(expires_at)
    WHERE revoked_at IS NULL;

-- Only a server-side FastAPI service using service_role should access this
-- table. The raw capability token is never stored in PostgreSQL.
ALTER TABLE beneficiary_sessions ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- 4. Private persistence security boundary
-- ============================================================================

-- Remove the earlier compatibility policies from private citizen data. The
-- FastAPI service_role client bypasses RLS; anon/authenticated clients do not
-- need direct database access for Phase 2C persistence.
DROP POLICY IF EXISTS "Public insert beneficiaries" ON beneficiaries;
DROP POLICY IF EXISTS "Public select beneficiaries" ON beneficiaries;
DROP POLICY IF EXISTS "Public update beneficiaries" ON beneficiaries;
DROP POLICY IF EXISTS "Public insert interview_sessions" ON interview_sessions;
DROP POLICY IF EXISTS "Public select interview_sessions" ON interview_sessions;
DROP POLICY IF EXISTS "Public manage applications" ON applications;

REVOKE ALL PRIVILEGES ON TABLE beneficiaries, interview_sessions, beneficiary_sessions, applications
    FROM anon, authenticated;

GRANT ALL PRIVILEGES ON TABLE beneficiaries, interview_sessions, beneficiary_sessions, applications
    TO service_role;

-- Catalog reads remain available through the existing public policies:
-- states, districts, skills, opportunities, and opportunity_skills.
