"""
Database Import Script - NYC Taxi Trip Analyzer
Member B - Use this script to import cleaned data into your database

This script imports:
1. Locations data from taxi_zone_lookup.csv
2. Cleaned trip data from cleaned_taxi_data.csv

Supports both PostgreSQL and SQLite
"""

import pandas as pd
from sqlalchemy import create_engine
import sys
import os

# ===================================================================
# CONFIGURATION - MEMBER B: UPDATE THIS SECTION!
# ===================================================================

print("""
╔══════════════════════════════════════════════════════════════════╗
║     NYC TAXI TRIP ANALYZER - DATABASE IMPORT SCRIPT              ║
║     Member B - Database Setup                                    ║
╚══════════════════════════════════════════════════════════════════╝
""")

print("\nSelect your database type:")
print("1. PostgreSQL (recommended)")
print("2. SQLite (simpler, no installation needed)")
choice = input("\nEnter 1 or 2: ").strip()

if choice == "1":
    # PostgreSQL Configuration
    print("\n" + "="*70)
    print("POSTGRESQL CONFIGURATION")
    print("="*70)
    
    db_user = input("Database username (default: postgres): ").strip() or "postgres"
    db_password = input("Database password: ").strip()
    db_host = input("Database host (default: localhost): ").strip() or "localhost"
    db_port = input("Database port (default: 5432): ").strip() or "5432"
    db_name = input("Database name (default: taxi_db): ").strip() or "taxi_db"
    
    DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
elif choice == "2":
    # SQLite Configuration
    print("\n" + "="*70)
    print("SQLITE CONFIGURATION")
    print("="*70)
    
    db_file = input("Database filename (default: taxi_db.sqlite): ").strip() or "taxi_db.sqlite"
    DATABASE_URL = f"sqlite:///{db_file}"
    
else:
    print("Invalid choice. Please run the script again.")
    sys.exit(1)

print(f"\nDatabase URL: {DATABASE_URL}")
confirm = input("\nProceed with this configuration? (yes/no): ").strip().lower()

if confirm not in ['yes', 'y']:
    print("Cancelled.")
    sys.exit(0)

# ===================================================================
# FILE PATHS
# ===================================================================

# Get the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Data files
LOCATIONS_FILE = os.path.join(script_dir, '../data/taxi_zone_lookup.csv')
TRIPS_FILE = os.path.join(script_dir, '../shared/cleaned_taxi_data.csv')

# Check if files exist
print("\n" + "="*70)
print("CHECKING FILES")
print("="*70)

if not os.path.exists(LOCATIONS_FILE):
    print(f"❌ ERROR: Locations file not found: {LOCATIONS_FILE}")
    print("   Make sure taxi_zone_lookup.csv is in the /data/ folder")
    sys.exit(1)
else:
    print(f"✓ Found locations file: {LOCATIONS_FILE}")

if not os.path.exists(TRIPS_FILE):
    print(f"❌ ERROR: Trips file not found: {TRIPS_FILE}")
    print("   Make sure cleaned_taxi_data.csv is in the /shared/ folder")
    print("   Member A should have created this file")
    sys.exit(1)
else:
    file_size_mb = os.path.getsize(TRIPS_FILE) / (1024 * 1024)
    print(f"✓ Found trips file: {TRIPS_FILE} ({file_size_mb:.2f} MB)")

# ===================================================================
# DATABASE CONNECTION
# ===================================================================

print("\n" + "="*70)
print("CONNECTING TO DATABASE")
print("="*70)

try:
    engine = create_engine(DATABASE_URL)
    
    # Test connection
    with engine.connect() as conn:
        result = conn.execute("SELECT 1")
        result.fetchone()
    
    print("✓ Database connection successful!")
    
except Exception as e:
    print(f"❌ ERROR: Could not connect to database")
    print(f"   Error message: {e}")
    print("\nTroubleshooting:")
    print("  - PostgreSQL: Make sure the database exists (createdb taxi_db)")
    print("  - PostgreSQL: Check username, password, and port")
    print("  - PostgreSQL: Make sure PostgreSQL service is running")
    print("  - SQLite: Make sure you have write permissions in this directory")
    sys.exit(1)

# ===================================================================
# IMPORT LOCATIONS DATA
# ===================================================================

print("\n" + "="*70)
print("IMPORTING LOCATIONS DATA")
print("="*70)

try:
    # Read locations CSV
    print(f"Reading {LOCATIONS_FILE}...")
    locations_df = pd.read_csv(LOCATIONS_FILE)
    
    # Rename columns to match database schema
    locations_df.columns = ['location_id', 'borough', 'zone', 'service_zone']
    
    print(f"   Loaded {len(locations_df)} location records")
    
    # Import to database
    print("Importing to 'locations' table...")
    locations_df.to_sql('locations', engine, if_exists='replace', index=False)
    
    print(f"✓ Successfully imported {len(locations_df)} locations")
    
except Exception as e:
    print(f"❌ ERROR: Failed to import locations")
    print(f"   Error message: {e}")
    sys.exit(1)

# ===================================================================
# IMPORT TRIPS DATA
# ===================================================================

print("\n" + "="*70)
print("IMPORTING TRIPS DATA")
print("="*70)
print("⚠️  This may take 1-2 minutes for 50,000 records...")

try:
    # Read trips CSV
    print(f"\nReading {TRIPS_FILE}...")
    trips_df = pd.read_csv(TRIPS_FILE)
    
    print(f"   Loaded {len(trips_df)} trip records")
    print(f"   Columns: {', '.join(trips_df.columns[:5])}... (and {len(trips_df.columns) - 5} more)")
    
    # Convert datetime columns
    print("Converting datetime columns...")
    if 'tpep_pickup_datetime' in trips_df.columns:
        trips_df['tpep_pickup_datetime'] = pd.to_datetime(trips_df['tpep_pickup_datetime'])
    if 'tpep_dropoff_datetime' in trips_df.columns:
        trips_df['tpep_dropoff_datetime'] = pd.to_datetime(trips_df['tpep_dropoff_datetime'])
    
    # Import to database (this is the slow part)
    print("Importing to 'trips' table... (please wait)")
    trips_df.to_sql('trips', engine, if_exists='replace', index=False, chunksize=1000)
    
    print(f"✓ Successfully imported {len(trips_df)} trips")
    
except Exception as e:
    print(f"❌ ERROR: Failed to import trips")
    print(f"   Error message: {e}")
    sys.exit(1)

# ===================================================================
# CREATE INDEXES
# ===================================================================

print("\n" + "="*70)
print("CREATING INDEXES (for faster queries)")
print("="*70)

indexes = [
    ("idx_pickup_datetime", "trips", "tpep_pickup_datetime"),
    ("idx_pickup_hour", "trips", "pickup_hour"),
    ("idx_pickup_borough", "trips", "pickup_borough"),
    ("idx_fare_amount", "trips", "fare_amount"),
    ("idx_trip_distance", "trips", "trip_distance"),
]

try:
    with engine.connect() as conn:
        for idx_name, table, column in indexes:
            try:
                # Check if this is SQLite or PostgreSQL
                if 'sqlite' in DATABASE_URL:
                    # SQLite syntax
                    conn.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({column})")
                else:
                    # PostgreSQL syntax
                    conn.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({column})")
                
                print(f"   ✓ Created index: {idx_name}")
            except Exception as e:
                print(f"   ⚠️  Warning: Could not create index {idx_name}: {e}")
    
    print("✓ Indexes created successfully")
    
except Exception as e:
    print(f"⚠️  Warning: Some indexes may not have been created: {e}")
    print("   Database will still work, but queries may be slower")

# ===================================================================
# VERIFICATION
# ===================================================================

print("\n" + "="*70)
print("VERIFICATION")
print("="*70)

try:
    # Count locations
    result = pd.read_sql("SELECT COUNT(*) as count FROM locations", engine)
    location_count = result['count'].iloc[0]
    print(f"\n✓ Locations table: {location_count} records")
    
    # Count trips
    result = pd.read_sql("SELECT COUNT(*) as count FROM trips", engine)
    trip_count = result['count'].iloc[0]
    print(f"✓ Trips table: {trip_count} records")
    
    # Date range
    result = pd.read_sql("""
        SELECT 
            MIN(tpep_pickup_datetime) as earliest,
            MAX(tpep_pickup_datetime) as latest
        FROM trips
    """, engine)
    print(f"\n✓ Date range: {result['earliest'].iloc[0]} to {result['latest'].iloc[0]}")
    
    # Sample record
    print("\n✓ Sample trip record:")
    sample = pd.read_sql("SELECT * FROM trips LIMIT 1", engine)
    for col in ['tpep_pickup_datetime', 'pickup_borough', 'fare_amount', 'trip_distance', 
                'trip_duration_minutes', 'avg_speed_mph', 'fare_per_mile']:
        if col in sample.columns:
            print(f"   {col}: {sample[col].iloc[0]}")
    
    # Borough distribution
    result = pd.read_sql("""
        SELECT pickup_borough, COUNT(*) as count 
        FROM trips 
        WHERE pickup_borough IS NOT NULL
        GROUP BY pickup_borough 
        ORDER BY count DESC
    """, engine)
    print("\n✓ Trips by borough:")
    for _, row in result.iterrows():
        print(f"   {row['pickup_borough']}: {row['count']:,} trips")
    
except Exception as e:
    print(f"⚠️  Warning: Verification query failed: {e}")

# ===================================================================
# SUCCESS - NEXT STEPS
# ===================================================================

print("\n" + "="*70)
print("✓ IMPORT COMPLETE!")
print("="*70)

print("\n📋 NEXT STEPS FOR MEMBER B:\n")
print("1. Copy your database connection string:")
print(f"   {DATABASE_URL}")
print("\n2. Give this connection string to Member A")
print("   • They need to update backend/config.py line 34")
print("   • Or create a .env file with DATABASE_URL")

print("\n3. Send Member A a confirmation message:")
print(f"""
   ✓ Database Type: {'PostgreSQL' if 'postgresql' in DATABASE_URL else 'SQLite'}
   ✓ Total Locations: {location_count if 'location_count' in locals() else 'N/A'}
   ✓ Total Trips: {trip_count if 'trip_count' in locals() else 'N/A'}
   ✓ All data imported successfully
   ✓ Indexes created
   ✓ Connection String: {DATABASE_URL}
   
   Ready for backend integration!
""")

print("\n4. Member A will then:")
print("   • Update config.py with your connection string")
print("   • Test the backend API")
print("   • Confirm connection works")

print("\n" + "="*70)
print("🎉 Great job! Database setup is complete!")
print("="*70 + "\n")
