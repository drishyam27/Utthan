"""
Utthan - NSQF / NQR Course Catalog Ingestion CLI.
Parses official .xlsx workbooks, validates taxonomy, filters excluded sectors,
generates idempotent seed SQL, and optionally upserts to Supabase PostgreSQL.
"""

import argparse
import os
import sys
from pathlib import Path

# Add backend to sys.path so app modules can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

# Force utf-8 output for Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from app.services.nsqf_ingestion import (
    parse_all_courses,
    generate_seed_sql,
    find_dataset_directory,
    EXCLUDED_SECTORS,
)
from app.db.supabase import get_supabase_client
from app.core.config import settings


def main():
    parser = argparse.ArgumentParser(description="Ingest authoritative NSQF / NQR course dataset.")
    parser.add_argument("--dry-run", action="store_true", help="Parse and audit without writing files or database.")
    parser.add_argument("--generate-sql", type=str, default="supabase/seed_nsqf_catalog.sql", help="Output path for SQL seed file.")
    parser.add_argument("--upsert-db", action="store_true", help="Upsert parsed catalog directly into Supabase database.")
    args = parser.parse_args()

    print("==================================================")
    print("UTTHAN NSQF / NQR CATALOG INGESTION PIPELINE")
    print("==================================================")

    try:
        dataset_path = find_dataset_directory()
        print(f"Dataset Directory : {dataset_path}")
    except Exception as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    print("Parsing all sector workbooks...")
    sectors, qualifications, audit = parse_all_courses(dataset_path)

    print("\n--- AUDIT METRICS ---")
    print(f"Total Workbooks Processed : {audit['total_files']}")
    print(f"Total Source Rows         : {audit['total_source_rows']}")
    print(f"Valid Catalog Records     : {audit['valid_catalog_records']}")
    print(f"Excluded by Sector Policy : {audit['excluded_by_sector']}")
    print(f"Manual Review Needed      : {audit['manual_review_needed']}")
    print(f"Total Sectors Discovered  : {len(sectors)}")
    print(f"PwD Courses Found         : {audit['pwd_count']}")
    print(f"Duplicate Codes Resolved  : {len(audit['duplicate_codes'])}")

    print("\n--- LEVEL DISTRIBUTION ---")
    for lvl, count in sorted(audit["levels"].items(), key=lambda x: float(x[0])):
        print(f"  Level {lvl:4s}: {count:4d} courses")

    print("\n--- NOTIONAL HOURS DISTRIBUTION ---")
    for rng, count in sorted(audit["hour_ranges"].items()):
        print(f"  {rng:12s}: {count:4d} courses")

    if args.dry_run:
        print("\nDry run completed successfully. No changes written.")
        return

    # Generate SQL seed file
    if args.generate_sql:
        sql_out = Path(args.generate_sql)
        print(f"\nGenerating idempotent seed SQL to {sql_out}...")
        count = generate_seed_sql(sql_out)
        print(f"Wrote {count} qualification INSERT statements to {sql_out}")

    # Direct database upsert if requested
    if args.upsert_db:
        if not settings.is_supabase_configured:
            print("\nWARNING: Supabase is not configured in backend/.env. Skipping database upsert.")
            print("To seed the database, run the generated SQL script in the Supabase SQL editor:")
            print(f"  {args.generate_sql}")
            return

        print("\nConnecting to Supabase PostgreSQL...")
        try:
            client = get_supabase_client()
            
            # Upsert sectors in batches
            print(f"Upserting {len(sectors)} sectors...")
            client.table("nsqf_sectors").upsert(sectors, on_conflict="id").execute()
            print("Sectors upserted successfully.")

            # Upsert qualifications in batches of 100
            print(f"Upserting {len(qualifications)} qualifications in batches...")
            batch_size = 100
            for i in range(0, len(qualifications), batch_size):
                batch = qualifications[i:i + batch_size]
                # Format batch for PostgREST
                records = []
                for q in batch:
                    r = dict(q)
                    records.append(r)
                client.table("nsqf_qualifications").upsert(records, on_conflict="q_code,title").execute()
                print(f"  Upserted {min(i + batch_size, len(qualifications))}/{len(qualifications)} courses...")
            print("Database upsert completed successfully!")
        except Exception as exc:
            print(f"ERROR during Supabase upsert: {exc}")
            print("You can apply the seed file directly via Supabase SQL editor:")
            print(f"  {args.generate_sql}")
            sys.exit(1)

    print("\n==================================================")
    print("INGESTION PIPELINE COMPLETED SUCCESSFULLY")
    print("==================================================")


if __name__ == "__main__":
    main()
