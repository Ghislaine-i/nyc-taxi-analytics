#!/usr/bin/env python3


import csv
import os
import sys
import time

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("\n  [ERROR] psycopg2 is not installed.")
    print("  Run: pip install psycopg2-binary")
    sys.exit(1)

#  Configuration 
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

DB_NAME  = "taxi_db"
DB_USER  = "postgres"
DB_PASS  = "Chris12"
DB_HOST  = "localhost"
DB_PORT  = "5432"

CONNECTION_STRING = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

SCHEMA_FILE      = os.path.join(SCRIPT_DIR, "schema.sql")
ZONE_LOOKUP_FILE = os.path.join(PROJECT_ROOT, "data", "taxi_zone_lookup.csv")
CSV_FILE         = os.path.join(PROJECT_ROOT, "shared", "cleaned_taxi_data.csv")

# If shared CSV not found, fall back to backend copy
if not os.path.exists(CSV_FILE):
    CSV_FILE = os.path.join(PROJECT_ROOT, "backend", "cleaned_taxi_data.csv")


# Helpers
def banner(text):
    width = 70
    print("\n" + "=" * width)
    print(f"  {text}")
    print("=" * width)


def success(msg):
    print(f"  [OK] {msg}")


def fail(msg):
    print(f"  [FAIL] {msg}")
    sys.exit(1)


#  Step 0: Create database if it doesn't exist

def create_database_if_needed():
    banner("STEP 0: CHECKING / CREATING DATABASE")

    try:
        # Connect to default 'postgres' database to create taxi_db
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        exists = cursor.fetchone()

        if exists:
            print(f"  Database '{DB_NAME}' already exists.")
            # Drop and recreate for clean slate
            cursor.execute(f"DROP DATABASE {DB_NAME}")
            print(f"  Dropped existing database for clean rebuild.")

        cursor.execute(f"CREATE DATABASE {DB_NAME}")
        success(f"Database '{DB_NAME}' created")

        cursor.close()
        conn.close()

    except psycopg2.OperationalError as e:
        fail(
            f"Could not connect to PostgreSQL.\n"
            f"  Error: {e}\n"
            f"  Make sure PostgreSQL is running and credentials are correct:\n"
            f"    User: {DB_USER}\n"
            f"    Password: {DB_PASS}\n"
            f"    Host: {DB_HOST}:{DB_PORT}"
        )


# Step 1: Apply schema

def apply_schema(conn):
    banner("STEP 1: APPLYING SCHEMA")

    if not os.path.exists(SCHEMA_FILE):
        fail(f"Schema file not found: {SCHEMA_FILE}")

    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    cursor = conn.cursor()
    cursor.execute(schema_sql)
    conn.commit()
    cursor.close()

    success("Schema applied (locations + trips tables, indexes)")


#  Step 2: Import locations from taxi_zone_lookup.csv

def import_locations(conn):
    banner("STEP 2: IMPORTING LOCATIONS (taxi_zone_lookup.csv)")

    if not os.path.exists(ZONE_LOOKUP_FILE):
        fail(
            f"Taxi zone lookup file not found.\n"
            f"  Expected at: {ZONE_LOOKUP_FILE}\n"
            f"  Please ensure data/taxi_zone_lookup.csv exists."
        )

    print(f"  Reading: {ZONE_LOOKUP_FILE}")

    cursor = conn.cursor()
    count = 0

    with open(ZONE_LOOKUP_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            location_id  = int(row["LocationID"])
            borough      = row.get("Borough", "Unknown").strip()
            zone         = row.get("Zone", "Unknown").strip()
            service_zone = row.get("service_zone", "").strip() or None

            cursor.execute(
                "INSERT INTO locations "
                "(location_id, borough, zone, service_zone) VALUES (%s, %s, %s, %s) "
                "ON CONFLICT (location_id) DO NOTHING",
                (location_id, borough, zone, service_zone),
            )
            count += 1

    conn.commit()
    cursor.close()
    success(f"Imported {count} locations from official NYC TLC zone lookup")
    return count


#  Step 3: Import trip records 

def import_trips(conn):
    banner("STEP 3: IMPORTING TRIP RECORDS")

    if not os.path.exists(CSV_FILE):
        fail(f"CSV file not found: {CSV_FILE}")

    print(f"  Reading: {CSV_FILE}")
    start = time.time()

    # Column order must match the CSV header
    csv_columns = [
        "VendorID",
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime",
        "passenger_count",
        "trip_distance",
        "RatecodeID",
        "store_and_fwd_flag",
        "PULocationID",
        "DOLocationID",
        "payment_type",
        "fare_amount",
        "extra",
        "mta_tax",
        "tip_amount",
        "tolls_amount",
        "improvement_surcharge",
        "total_amount",
        "congestion_surcharge",
        "trip_duration_minutes",
        "avg_speed_mph",
        "fare_per_mile",
        "pickup_hour",
        "pickup_day_of_week",
        "pickup_day_name",
        "pickup_month",
        "pickup_borough",
        "pickup_zone",
        "dropoff_borough",
        "dropoff_zone",
    ]

    col_names = ", ".join(c.lower() for c in csv_columns)
    placeholders = ", ".join(["%s"] * len(csv_columns))
    insert_sql = f'INSERT INTO trips ({col_names}) VALUES ({placeholders})'

    cursor = conn.cursor()
    batch = []
    total = 0
    batch_size = 5000

    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            values = []
            for col in csv_columns:
                val = row.get(col, "").strip()
                if val == "":
                    values.append(None)
                else:
                    values.append(val)
            batch.append(tuple(values))
            total += 1

            if len(batch) >= batch_size:
                cursor.executemany(insert_sql, batch)
                conn.commit()
                print(f"    ... {total:,} records imported", end="\r")
                batch = []

    # Insert remaining rows
    if batch:
        cursor.executemany(insert_sql, batch)
        conn.commit()

    elapsed = time.time() - start
    print()  # newline after \r
    cursor.close()
    success(f"Imported {total:,} trip records in {elapsed:.1f}s")
    return total


#  Step 4: Validate 

def validate(conn, expected_locations, expected_trips):
    banner("STEP 4: VALIDATION")

    cursor = conn.cursor()

    # Check counts
    cursor.execute("SELECT COUNT(*) FROM locations")
    loc_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM trips")
    trip_count = cursor.fetchone()[0]

    print(f"  Locations : {loc_count:,}  (expected ~{expected_locations})")
    print(f"  Trips     : {trip_count:,}  (expected {expected_trips:,})")

    # Date range
    cursor.execute(
        "SELECT MIN(tpep_pickup_datetime), MAX(tpep_pickup_datetime) FROM trips"
    )
    min_dt, max_dt = cursor.fetchone()
    print(f"  Date range: {min_dt} → {max_dt}")

    # Borough distribution
    cursor.execute(
        "SELECT pickup_borough, COUNT(*) AS cnt FROM trips "
        "GROUP BY pickup_borough ORDER BY cnt DESC LIMIT 5"
    )
    print("  Top pickup boroughs:")
    for borough, cnt in cursor.fetchall():
        print(f"    {borough or 'Unknown':20s} : {cnt:,}")

    # Derived features spot check
    cursor.execute(
        "SELECT AVG(trip_duration_minutes), AVG(avg_speed_mph), AVG(fare_per_mile) FROM trips"
    )
    avg_dur, avg_spd, avg_fpm = cursor.fetchone()
    print(f"  Avg duration  : {float(avg_dur):.1f} min")
    print(f"  Avg speed     : {float(avg_spd):.1f} mph")
    print(f"  Avg fare/mile : ${float(avg_fpm):.2f}")

    # NULLs in critical columns
    cursor.execute(
        "SELECT COUNT(*) FROM trips WHERE tpep_pickup_datetime IS NULL"
    )
    null_dt = cursor.fetchone()[0]
    print(f"  NULL pickup datetimes: {null_dt}")

    cursor.close()

    if trip_count == expected_trips and null_dt == 0:
        success("ALL VALIDATIONS PASSED")
    else:
        print("  [Counts may differ slightly; review above.")


#  Step 5: Print handoff info 

def print_handoff():
    banner("DONE ")

    print(f"""
  Database type   : PostgreSQL
  Connection URL  : {CONNECTION_STRING}

    Update backend/config.py:
      DATABASE_URL = "{CONNECTION_STRING}"
  
""")


#  Main 

def main():
    print(
        """
        NYC TAXI TRIP ANALYZER — DATABASE SETUP

"""
    )

    # Verify required files exist
    if not os.path.exists(ZONE_LOOKUP_FILE):
        fail(
            f"Taxi zone lookup not found.\n"
            f"  Expected at: {ZONE_LOOKUP_FILE}\n"
            f"  Please ensure data/taxi_zone_lookup.csv exists."
        )
    if not os.path.exists(CSV_FILE):
        fail(
            f"Cleaned data not found.\n"
            f"  Expected at: {CSV_FILE}\n"
            f"  Please ensure  cleaned_taxi_data.csv is in shared/ or backend/"
        )

    # Step 0: Create database
    create_database_if_needed()

    # Steps 1-4: Connect and populate
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )

    apply_schema(conn)
    loc_count = import_locations(conn)
    trip_count = import_trips(conn)
    validate(conn, loc_count, trip_count)

    conn.close()

    # Step 5
    print_handoff()


if __name__ == "__main__":
    main()
