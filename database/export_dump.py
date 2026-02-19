#!/usr/bin/env python3
"""
NYC Taxi Trip Analyzer - Database Dump Export (PostgreSQL)
Member B: Database Design & Implementation

Generates a SQL dump file using pg_dump that can be used to recreate
the entire database on any PostgreSQL-compatible system.

Usage:
    cd database
    python export_dump.py
"""

import os
import subprocess
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DUMP_FILE  = os.path.join(SCRIPT_DIR, "taxi_db_dump.sql")

DB_NAME = "taxi_db"
DB_USER = "postgres"
DB_PASS = "Chris12"
DB_HOST = "localhost"
DB_PORT = "5432"


def main():
    print()
    print("=" * 70)
    print("  NYC TAXI TRIP ANALYZER — DATABASE DUMP EXPORT (PostgreSQL)")
    print("=" * 70)

    print(f"\n  Database    : {DB_NAME}")
    print(f"  Output dump : {DUMP_FILE}")

    start = time.time()

    # Set password via environment variable for pg_dump
    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASS

    print("  Running pg_dump...")

    try:
        result = subprocess.run(
            [
                "pg_dump",
                "-h", DB_HOST,
                "-p", DB_PORT,
                "-U", DB_USER,
                "-d", DB_NAME,
                "-f", DUMP_FILE,
                "--no-owner",
                "--no-privileges",
            ],
            env=env,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"\n  [ERROR] pg_dump failed:")
            print(f"  {result.stderr}")
            sys.exit(1)

    except FileNotFoundError:
        print("\n  [ERROR] pg_dump command not found.")
        print("  Make sure PostgreSQL bin directory is in your PATH.")
        print("  Typical locations:")
        print("    Windows: C:\\Program Files\\PostgreSQL\\<version>\\bin")
        print("    Mac:     /usr/local/pgsql/bin")
        print("    Linux:   /usr/bin")
        sys.exit(1)

    elapsed = time.time() - start
    file_size_mb = os.path.getsize(DUMP_FILE) / (1024 * 1024)

    print(f"\n  [OK] Dump complete!")
    print(f"  File size  : {file_size_mb:.1f} MB")
    print(f"  Time       : {elapsed:.1f}s")
    print(f"\n  To restore on another machine:")
    print(f"    createdb taxi_db")
    print(f"    psql -U postgres -d taxi_db -f taxi_db_dump.sql")
    print()


if __name__ == "__main__":
    main()
