-- Utthan: NSQF Catalog Column Types Patch
-- Migration: 20261003000002_nsqf_column_types.sql
-- Expands title and qualification_type to TEXT to support long titles and multi-category types.

ALTER TABLE nsqf_qualifications ALTER COLUMN title TYPE TEXT;
ALTER TABLE nsqf_qualifications ALTER COLUMN qualification_type TYPE TEXT;
