# 🗄️ FOR MEMBER B - DATABASE SETUP GUIDE

**From:** Member A (Backend Developer)  
**To:** Member B (Database Developer)  
**Project:** NYC Taxi Trip Analyzer

---

## 📋 What You'll Receive from Me (Member A)

I've already completed the data processing. Here's what I'm giving you:

### Files in `/shared/` Folder:
1. ✅ **cleaned_taxi_data.csv** (10.7 MB, ~50,000 records)
   - All taxi trip records, fully cleaned and ready to import
   - No duplicates, no missing values, all outliers removed
   
2. ✅ **exclusion_log.txt**
   - Details on what data was excluded during cleaning
   - Justifications for all cleaning decisions

3. ✅ **API_DOCUMENTATION.md**
   - Full API documentation for reference

### Data You Also Need:
- **taxi_zone_lookup.csv** - Located in `/data/` folder
  - Contains location ID to borough/zone name mappings

---

## 🎯 Your Tasks (Member B)

### Task 1: Choose and Install Your Database

**Option A: PostgreSQL (Recommended)**
```bash
# Install PostgreSQL (if not installed):
# - Windows: Download from https://www.postgresql.org/download/windows/
# - Mac: brew install postgresql
# - Linux: sudo apt-get install postgresql

# Create the database
createdb taxi_db

# Or using psql:
psql -U postgres
CREATE DATABASE taxi_db;
\q
```

**Option B: SQLite (Fallback)**
```bash
# No installation needed - SQLite is built into Python!
# Database file will be created automatically when you import data
```

---

### Task 2: Create Database Schema

Copy this SQL and run it in your database:

```sql
-- ==================================================================
-- LOCATIONS TABLE (Dimension Table)
-- ==================================================================
CREATE TABLE locations (
    location_id INTEGER PRIMARY KEY,
    borough VARCHAR(50),
    zone VARCHAR(100),
    service_zone VARCHAR(50)
);

-- ==================================================================
-- TRIPS TABLE (Fact Table) 
-- ==================================================================
CREATE TABLE trips (
    trip_id SERIAL PRIMARY KEY,
    
    -- Timestamps
    tpep_pickup_datetime TIMESTAMP NOT NULL,
    tpep_dropoff_datetime TIMESTAMP NOT NULL,
    
    -- Trip details
    passenger_count INTEGER,
    trip_distance DECIMAL(10,2),
    
    -- Financial
    fare_amount DECIMAL(10,2),
    tip_amount DECIMAL(10,2),
    tolls_amount DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    
    -- Location IDs
    PULocationID INTEGER,
    DOLocationID INTEGER,
    
    -- Location names (denormalized for performance)
    pickup_borough VARCHAR(50),
    pickup_zone VARCHAR(100),
    dropoff_borough VARCHAR(50),
    dropoff_zone VARCHAR(100),
    
    -- ⭐ DERIVED FEATURES (already calculated by Member A)
    trip_duration_minutes DECIMAL(10,2),
    avg_speed_mph DECIMAL(10,2),
    fare_per_mile DECIMAL(10,2),
    
    -- Time features
    pickup_hour INTEGER,
    pickup_day_of_week INTEGER,
    pickup_day_name VARCHAR(20),
    pickup_month INTEGER
);

-- ==================================================================
-- INDEXES FOR PERFORMANCE
-- ==================================================================
CREATE INDEX idx_pickup_datetime ON trips(tpep_pickup_datetime);
CREATE INDEX idx_pickup_hour ON trips(pickup_hour);
CREATE INDEX idx_pickup_borough ON trips(pickup_borough);
CREATE INDEX idx_pickup_location ON trips(PULocationID);
CREATE INDEX idx_dropoff_location ON trips(DOLocationID);
CREATE INDEX idx_fare_amount ON trips(fare_amount);
CREATE INDEX idx_trip_distance ON trips(trip_distance);
```

**For SQLite, use this instead:**
```sql
-- SQLite version (slightly different syntax)
CREATE TABLE locations (
    location_id INTEGER PRIMARY KEY,
    borough TEXT,
    zone TEXT,
    service_zone TEXT
);

CREATE TABLE trips (
    trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tpep_pickup_datetime TEXT NOT NULL,
    tpep_dropoff_datetime TEXT NOT NULL,
    passenger_count INTEGER,
    trip_distance REAL,
    fare_amount REAL,
    tip_amount REAL,
    tolls_amount REAL,
    total_amount REAL,
    PULocationID INTEGER,
    DOLocationID INTEGER,
    pickup_borough TEXT,
    pickup_zone TEXT,
    dropoff_borough TEXT,
    dropoff_zone TEXT,
    trip_duration_minutes REAL,
    avg_speed_mph REAL,
    fare_per_mile REAL,
    pickup_hour INTEGER,
    pickup_day_of_week INTEGER,
    pickup_day_name TEXT,
    pickup_month INTEGER
);

-- Same indexes work for SQLite
CREATE INDEX idx_pickup_datetime ON trips(tpep_pickup_datetime);
CREATE INDEX idx_pickup_hour ON trips(pickup_hour);
CREATE INDEX idx_pickup_borough ON trips(pickup_borough);
```

---

### Task 3: Import the Data

**METHOD 1: Python Script (Recommended - Works for Both PostgreSQL and SQLite)**

Create a file called `import_to_database.py` in the `/backend/` folder:

```python
"""
Database Import Script
Member B - Import cleaned data into database
"""

import pandas as pd
from sqlalchemy import create_engine

# ===================================================================
# CONFIGURATION - UPDATE THIS!
# ===================================================================

# Option 1: PostgreSQL
DATABASE_URL = "postgresql://postgres:YOUR_PASSWORD@localhost:5432/taxi_db"

# Option 2: SQLite (uncomment if using SQLite)
# DATABASE_URL = "sqlite:///taxi_db.sqlite"

# ===================================================================
# IMPORT LOCATIONS
# ===================================================================
print("=" * 70)
print("IMPORTING DATA TO DATABASE")
print("=" * 70)

print("\n[1/3] Connecting to database...")
engine = create_engine(DATABASE_URL)
print("   ✓ Connected successfully!")

print("\n[2/3] Importing locations data...")
locations_df = pd.read_csv('../data/taxi_zone_lookup.csv')
locations_df.columns = ['location_id', 'borough', 'zone', 'service_zone']
locations_df.to_sql('locations', engine, if_exists='replace', index=False)
print(f"   ✓ Imported {len(locations_df)} location records")

# ===================================================================
# IMPORT TRIPS
# ===================================================================
print("\n[3/3] Importing trips data (this may take a minute)...")
trips_df = pd.read_csv('../shared/cleaned_taxi_data.csv')

# Convert datetime columns
trips_df['tpep_pickup_datetime'] = pd.to_datetime(trips_df['tpep_pickup_datetime'])
trips_df['tpep_dropoff_datetime'] = pd.to_datetime(trips_df['tpep_dropoff_datetime'])

# Import to database
trips_df.to_sql('trips', engine, if_exists='replace', index=False)
print(f"   ✓ Imported {len(trips_df)} trip records")

# ===================================================================
# VERIFY IMPORT
# ===================================================================
print("\n" + "=" * 70)
print("VERIFICATION")
print("=" * 70)

# Check record counts
result = pd.read_sql("SELECT COUNT(*) as count FROM locations", engine)
print(f"\nLocations table: {result['count'].iloc[0]} records")

result = pd.read_sql("SELECT COUNT(*) as count FROM trips", engine)
print(f"Trips table: {result['count'].iloc[0]} records")

# Sample data
print("\nSample trip record:")
sample = pd.read_sql("SELECT * FROM trips LIMIT 1", engine)
print(sample.T)

print("\n" + "=" * 70)
print("✓ IMPORT COMPLETE!")
print("=" * 70)
print("\nNext steps:")
print("1. Copy your DATABASE_URL and give it to Member A")
print("2. Member A will update backend/config.py")
print("3. Test the connection together")
```

**Run the script:**
```bash
cd backend
python import_to_database.py
```

---

**METHOD 2: PostgreSQL COPY Command (PostgreSQL Only)**

```sql
-- In psql or pgAdmin:
\copy locations FROM '/full/path/to/taxi_zone_lookup.csv' WITH (FORMAT CSV, HEADER TRUE);
\copy trips FROM '/full/path/to/cleaned_taxi_data.csv' WITH (FORMAT CSV, HEADER TRUE);
```

---

### Task 4: Validate the Data

Run these SQL queries to make sure everything imported correctly:

```sql
-- 1. Check total records (should be ~50,000 trips)
SELECT COUNT(*) as total_trips FROM trips;

-- 2. Check date range
SELECT 
    MIN(tpep_pickup_datetime) as earliest_trip,
    MAX(tpep_pickup_datetime) as latest_trip
FROM trips;

-- 3. Verify derived features are present
SELECT 
    trip_duration_minutes,
    avg_speed_mph,
    fare_per_mile
FROM trips
LIMIT 5;

-- 4. Check borough distribution
SELECT 
    pickup_borough,
    COUNT(*) as trip_count
FROM trips
GROUP BY pickup_borough
ORDER BY trip_count DESC;

-- 5. Verify no NULL values in critical columns
SELECT 
    COUNT(*) FILTER (WHERE passenger_count IS NULL) as null_passengers,
    COUNT(*) FILTER (WHERE trip_distance IS NULL) as null_distance,
    COUNT(*) FILTER (WHERE fare_amount IS NULL) as null_fare
FROM trips;
```

**Expected Results:**
- ✅ Total trips: ~50,000
- ✅ No NULL values in critical columns
- ✅ Manhattan should have the most trips
- ✅ All derived features (duration, speed, fare_per_mile) present

---

## 🔄 What to Give Back to Member A

Once you've completed the setup, send me:

### 1. Database Connection String

**Format:**
```
For PostgreSQL:
postgresql://username:password@localhost:5432/taxi_db

For SQLite:
sqlite:///taxi_db.sqlite
```

**How to share it:**
- Option A: Send it to me in team chat
- Option B: Update `backend/config.py` line 34 directly
- Option C: Create a `.env` file (I'll read it from there)

### 2. Confirmation Message

Please send me a message like this:

```
✓ Database Type: PostgreSQL (or SQLite)
✓ Database Name: taxi_db
✓ Total Locations: 265
✓ Total Trips: 50,000
✓ All validation queries passed
✓ Connection String: postgresql://postgres:mypass@localhost:5432/taxi_db

Ready for Member A to connect!
```

### 3. Validation Results

Copy/paste the results from the 5 validation queries above.

---

## 🚨 Common Issues & Solutions

### Issue 1: PostgreSQL Won't Install
**Solution:** Use SQLite instead
```python
# In import script, just change to:
DATABASE_URL = "sqlite:///taxi_db.sqlite"
```

### Issue 2: "Permission Denied" Error
**Solution:** Run psql as admin or create database as current user
```bash
createdb -U $USER taxi_db
```

### Issue 3: CSV Import Fails
**Solution:** Use the Python script (Method 1) instead of COPY command

### Issue 4: "Table already exists"
**Solution:** Drop and recreate tables
```sql
DROP TABLE IF EXISTS trips CASCADE;
DROP TABLE IF EXISTS locations CASCADE;
-- Then run CREATE TABLE commands again
```

---

## 📊 Database Schema Diagram

```
┌─────────────────┐
│   locations     │
├─────────────────┤
│ location_id (PK)│
│ borough         │
│ zone            │
│ service_zone    │
└─────────────────┘
         │
         │ (referenced by)
         ▼
┌─────────────────────────────┐
│         trips               │
├─────────────────────────────┤
│ trip_id (PK)                │
│ tpep_pickup_datetime        │
│ tpep_dropoff_datetime       │
│ passenger_count             │
│ trip_distance               │
│ fare_amount                 │
│ PULocationID (→ locations)  │
│ DOLocationID (→ locations)  │
│ trip_duration_minutes ⭐    │
│ avg_speed_mph ⭐            │
│ fare_per_mile ⭐            │
└─────────────────────────────┘

⭐ = Derived features (already calculated)
```

---

## ✅ Checklist for Member B

Before giving the connection string to Member A:

- [ ] Database created (PostgreSQL or SQLite)
- [ ] Both tables created (`locations` and `trips`)
- [ ] Indexes created on key columns
- [ ] Locations data imported (~265 records)
- [ ] Trips data imported (~50,000 records)
- [ ] All 5 validation queries run successfully
- [ ] Connection string ready to share
- [ ] No NULL values in critical columns

---

## 📞 Need Help?

**Contact Member A if:**
- The cleaned_taxi_data.csv file is missing or corrupt
- You need help understanding the data structure
- You want to use a different database (MySQL, etc.)
- The import script has errors

**Things I (Member A) can help with:**
- Explaining the derived features
- Providing alternative import methods
- Debugging data type issues
- Creating custom import scripts

---

**Good luck with the database setup! Once you give me the connection string, I'll connect the backend API to your database and we'll be ready for Member C to build the frontend! 🚀**
