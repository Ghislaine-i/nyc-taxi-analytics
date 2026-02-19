#!/usr/bin/env python3


import json
import os
import re
import sys

try:
    import psycopg2
except ImportError:
    print("\n   psycopg2 is not installed.")
    print("  Run: pip install psycopg2-binary")
    sys.exit(1)

# Paths & Connection
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
SQL_FILE    = os.path.join(SCRIPT_DIR, "insight_queries.sql")
OUTPUT_JSON = os.path.join(SCRIPT_DIR, "insight_results.json")

DB_NAME = "taxi_db"
DB_USER = "postgres"
DB_PASS = "Chris12"
DB_HOST = "localhost"
DB_PORT = "5432"


def parse_queries(sql_file):
    
    with open(sql_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Split on the query header pattern
    pattern = r'--\s*QUERY\s+(\d+):\s*(.+?)(?:\n)'
    parts = re.split(pattern, content)

    queries = []
    # parts: [preamble, num, title, sql_block, num, title, sql_block, ...]
    i = 1
    while i < len(parts) - 2:
        num   = parts[i].strip()
        title = parts[i + 1].strip()
        sql   = parts[i + 2].strip()

        # Extract just the SELECT statement (remove comment lines)
        lines = []
        for line in sql.split("\n"):
            stripped = line.strip()
            if stripped.startswith("--"):
                continue
            if stripped:
                lines.append(line)
        select_sql = "\n".join(lines).strip().rstrip(";") + ";"

        if select_sql.upper().startswith("SELECT"):
            queries.append({
                "number": int(num),
                "title": title,
                "sql": select_sql,
            })

        i += 3

    return queries


def run_query(cursor, sql):
    """Execute a query and return column names + rows."""
    cursor.execute(sql.rstrip(";"))
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    return columns, rows


def print_table(columns, rows, max_col_width=25):
    """Pretty-print a result set as a formatted table."""
    # Calculate column widths
    widths = [len(c) for c in columns]
    for row in rows:
        for i, val in enumerate(row):
            widths[i] = min(max(widths[i], len(str(val))), max_col_width)

    # Header
    header = " | ".join(c.ljust(widths[i]) for i, c in enumerate(columns))
    sep = "-+-".join("-" * widths[i] for i in range(len(columns)))
    print(f"  {header}")
    print(f"  {sep}")

    # Rows
    for row in rows:
        line = " | ".join(str(v).ljust(widths[i])[:max_col_width] for i, v in enumerate(row))
        print(f"  {line}")


def main():
    if not os.path.exists(SQL_FILE):
        print(f"[ERROR] SQL file not found: {SQL_FILE}")
        sys.exit(1)

    # Connect to PostgreSQL
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
    except psycopg2.OperationalError as e:
        print(f"Could not connect to PostgreSQL: {e}")
        print("  Make sure PostgreSQL is running and taxi_db exists.")
        print("  Run setup_database.py first.")
        sys.exit(1)

    cursor = conn.cursor()

    queries = parse_queries(SQL_FILE)
    if not queries:
        print(" No queries found in SQL file.")
        sys.exit(1)

    all_results = {}

    print()
    print("=" * 70)
    print("  NYC TAXI TRIP ANALYZER — INSIGHT QUERY RESULTS")
    print("=" * 70)

    for q in queries:
        print(f"\n{'─' * 70}")
        print(f"  QUERY {q['number']}: {q['title']}")
        print(f"{'─' * 70}")

        try:
            columns, rows = run_query(cursor, q["sql"])
            print_table(columns, rows)

            # Store for JSON export — convert Decimals to floats for JSON
            all_results[f"query_{q['number']}"] = {
                "title": q["title"],
                "columns": columns,
                "data": [
                    {col: (float(val) if hasattr(val, 'as_tuple') else val)
                     for col, val in zip(columns, row)}
                    for row in rows
                ],
            }
            print(f"  → {len(rows)} rows returned")

        except Exception as e:
            print(f"  [ERROR] {e}")

    cursor.close()
    conn.close()

    # Save to JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"\n{'=' * 70}")
    print(f"  Results saved to: {OUTPUT_JSON}")
    print(f"{'=' * 70}\n")


if __name__ == "__main__":
    main()
