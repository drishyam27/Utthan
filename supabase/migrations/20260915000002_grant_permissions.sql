-- ============================================================================
-- Utthan: Grant Privileges to PostgREST Roles & Reload Cache
--
-- This is an additive repair migration for existing Supabase projects where
-- the tables exist but PostgREST roles do not have the required privileges or
-- schema cache has not been refreshed. GRANT and NOTIFY are idempotent.
-- The broad grants are intentionally retained for Phase 2A compatibility;
-- least-privilege tightening belongs to a later security phase.
-- ============================================================================

GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;

GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL ROUTINES IN SCHEMA public TO anon, authenticated, service_role;

-- Explicit grants on all Phase 1 tables
GRANT ALL PRIVILEGES ON TABLE public.states, public.districts, public.skills, public.opportunities, public.opportunity_skills, public.beneficiaries, public.interview_sessions, public.applications TO anon, authenticated, service_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON ROUTINES TO anon, authenticated, service_role;

-- Reload PostgREST schema cache immediately
NOTIFY pgrst, 'reload schema';
