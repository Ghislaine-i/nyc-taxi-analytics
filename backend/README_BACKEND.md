# NYC Taxi Trip Analyzer - Backend Documentation
## Member A - Backend & Data Processing

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [Setup Instructions](#setup-instructions)
3. [Data Processing](#data-processing)
4. [API Documentation](#api-documentation)
5. [For Member B - Database](#for-member-b---database)
6. [For Member C - Frontend](#for-member-c---frontend)
7. [Troubleshooting](#troubleshooting)

---

## Overview

This backend service provides:
- **Data Processing Pipeline**: Cleans and enriches raw NYC taxi trip data
- **REST API**: Serves processed data to the frontend
- **Insights Engine**: Provides aggregated analytics and patterns

### Technology Stack
- **Framework**: Flask (Python web framework)
- **Database**: PostgreSQL (or SQLite fallback)
- **Data Processing**: Pandas, NumPy
- **API**: RESTful JSON endpoints with CORS enabled

---

## Setup Instructions

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Required packages:**
- Flask & flask-cors (API framework)
- pandas & numpy (data processing)
- SQLAlchemy & psycopg2-binary (database)
- pyarrow (for parquet files)

### 2. Process Raw Data

```bash
python data_processing.py
```

This script will:
- ✓ Load raw taxi trip data from `../data/`
- ✓ Clean and remove outliers
- ✓ Create derived features (duration, speed, fare/mile)
- ✓ Export cleaned data to `cleaned_taxi_data.csv`
- ✓ Generate exclusion log and processing report

**Important Files Generated:**
- `cleaned_taxi_data.csv` - Clean data for Member B
- `exclusion_log.txt` - Details on excluded records
- `processing_report.txt` - Full processing log

### 3. Configure Database Connection

Update `config.py` with database URL from Member B:

```python
# After Member B creates the database, update this:
DATABASE_URL = "postgresql://username:password@localhost:5432/taxi_db"
```

### 4. Run Backend Server

```bash
python app.py
```

Server will start at: **http://localhost:5000**

You should see:
```
NYC TAXI TRIP ANALYZER - BACKEND API
====================================
[DATABASE] Initializing connection...
   ✓ Database connection successful!

AVAILABLE ENDPOINTS:
  GET  /api/health
  GET  /api/trips
  ...
Starting server on http://0.0.0.0:5000
```

---

## Data Processing

### Input Data
- **Raw File**: `../data/yellow_tripdata.csv` (or .parquet)
- **Lookup File**: `../data/taxi_zone_lookup.csv`

### Cleaning Steps

1. **Remove Duplicates**
   - Exact duplicate records removed

2. **Handle Missing Values**
   - Critical fields (passenger_count, distance, fare): Drop rows
   - Optional fields (tips, tolls): Fill with 0

3. **Remove Outliers**
   - Passenger count: 1-6
   - Trip distance: 0.1-100 miles
   - Fare amount: $2.50-$500
   - Speed: 0.1-80 mph
   - Duration: 1-180 minutes

### Feature Engineering

**Three main derived features (as required by assignment):**

1. **trip_duration_minutes**
   ```python
   duration = (dropoff_time - pickup_time).total_seconds() / 60
   ```
   - **Justification**: Essential for speed calculations and temporal analysis
   - **Range**: 1-180 minutes

2. **avg_speed_mph**
   ```python
   speed = trip_distance / (duration_minutes / 60)
   ```
   - **Justification**: Indicates traffic conditions, reveals rush hours
   - **Range**: 0.1-80 mph

3. **fare_per_mile**
   ```python
   fare_per_mile = fare_amount / trip_distance
   ```
   - **Justification**: Identifies pricing patterns, surge pricing, route efficiency
   - **Range**: Reasonable values only (< $100/mile)

**Additional features:**
- `pickup_hour` - Hour of day (0-23)
- `pickup_day_of_week` - Day number (0=Monday, 6=Sunday)
- `pickup_day_name` - Day name (Monday, Tuesday, etc.)
- `pickup_month` - Month number

### Data Integration

**Zone Lookup Integration:**
- Maps `PULocationID` → pickup borough and zone name
- Maps `DOLocationID` → dropoff borough and zone name
- Allows location-based filtering and analysis

### Output

**Final Dataset Columns:**
- `tpep_pickup_datetime` - Pickup timestamp
- `tpep_dropoff_datetime` - Dropoff timestamp
- `passenger_count` - Number of passengers
- `trip_distance` - Distance in miles
- `fare_amount` - Base fare
- `tip_amount` - Tip amount
- `total_amount` - Total charge
- `PULocationID` - Pickup location ID
- `DOLocationID` - Dropoff location ID
- `pickup_borough` - Pickup borough name
- `pickup_zone` - Pickup zone name
- `dropoff_borough` - Dropoff borough name
- `dropoff_zone` - Dropoff zone name
- `trip_duration_minutes` ⭐ (derived)
- `avg_speed_mph` ⭐ (derived)
- `fare_per_mile` ⭐ (derived)
- `pickup_hour` (derived)
- `pickup_day_of_week` (derived)

---

## API Documentation

### Base URL
```
http://localhost:5000/api
```

### Response Format

**Success Response:**
```json
{
  "success": true,
  "data": [...],
  "count": 100
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message"
}
```

### Endpoints

#### 1. Health Check
```
GET /api/health
```
Check if API is running and database is connected.

**Response:**
```json
{
  "success": true,
  "message": "NYC Taxi Trip Analyzer API is running",
  "database": "connected",
  "version": "1.0.0"
}
```

---

#### 2. Get Trips
```
GET /api/trips
```
Retrieve trip records with optional filtering.

**Query Parameters:**
- `limit` (int) - Number of records (default: 100, max: 1000)
- `borough` (string) - Filter by pickup borough
- `min_fare` (float) - Minimum fare amount
- `max_fare` (float) - Maximum fare amount
- `min_distance` (float) - Minimum trip distance
- `max_distance` (float) - Maximum trip distance
- `date` (string) - Filter by date (YYYY-MM-DD)

**Examples:**
```
/api/trips?limit=50
/api/trips?borough=Manhattan&limit=100
/api/trips?min_fare=10&max_fare=50
/api/trips?date=2024-01-15
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "tpep_pickup_datetime": "2024-01-15 08:30:00",
      "tpep_dropoff_datetime": "2024-01-15 08:45:00",
      "passenger_count": 1,
      "trip_distance": 2.5,
      "fare_amount": 12.50,
      "pickup_borough": "Manhattan",
      "trip_duration_minutes": 15.0,
      "avg_speed_mph": 10.0,
      "fare_per_mile": 5.00
    }
  ],
  "count": 1
}
```

---

#### 3. Daily Trip Aggregations
```
GET /api/insights/daily_trips
```
Get trip counts and averages by day.

**Query Parameters:**
- `limit` (int) - Number of days (default: 30)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "date": "2024-01-15",
      "trip_count": 1250,
      "avg_fare": 15.75,
      "avg_distance": 3.2,
      "avg_duration": 18.5,
      "avg_speed": 10.4
    }
  ]
}
```

---

#### 4. Hourly Patterns
```
GET /api/insights/hourly_pattern
```
Get trip patterns by hour of day (0-23).

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "hour": 8,
      "trip_count": 450,
      "avg_distance": 3.1,
      "avg_speed": 12.5,
      "avg_fare": 14.20,
      "avg_duration": 15.0
    }
  ]
}
```

---

#### 5. Day of Week Patterns
```
GET /api/insights/day_of_week
```
Get trip patterns by day of week.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "day_name": "Monday",
      "day_number": 0,
      "trip_count": 2500,
      "avg_fare": 16.50,
      "avg_distance": 3.5,
      "avg_speed": 11.2
    }
  ]
}
```

---

#### 6. Top Pickup/Dropoff Locations
```
GET /api/insights/top_locations
```
Get top locations by trip count.

**Query Parameters:**
- `limit` (int) - Number of locations (default: 10)
- `type` (string) - 'pickup' or 'dropoff' (default: 'pickup')

**Examples:**
```
/api/insights/top_locations?limit=10
/api/insights/top_locations?type=dropoff&limit=5
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "zone": "Upper East Side",
      "borough": "Manhattan",
      "trip_count": 5800,
      "avg_fare": 18.50,
      "avg_distance": 2.8,
      "avg_duration": 12.5
    }
  ]
}
```

---

#### 7. Borough Statistics
```
GET /api/insights/borough_stats
```
Get comprehensive statistics by borough.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "borough": "Manhattan",
      "trip_count": 35000,
      "avg_fare": 17.20,
      "avg_distance": 2.9,
      "avg_speed": 10.8,
      "avg_duration": 16.2,
      "avg_fare_per_mile": 5.93,
      "avg_passengers": 1.3,
      "total_revenue": 602000.00
    }
  ]
}
```

---

#### 8. Fare Distribution
```
GET /api/insights/fare_distribution
```
Get distribution of fares in predefined buckets.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "fare_range": "$10-20",
      "trip_count": 15000,
      "avg_distance": 2.5,
      "avg_duration": 12.0
    }
  ]
}
```

---

#### 9. Distance Distribution
```
GET /api/insights/distance_distribution
```
Get distribution of trip distances.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "distance_range": "1-3 miles",
      "trip_count": 20000,
      "avg_fare": 12.50,
      "avg_duration": 15.0
    }
  ]
}
```

---

#### 10. Summary Statistics
```
GET /api/stats/summary
```
Get overall summary statistics for entire dataset.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_trips": 50000,
    "total_revenue": 875000.00,
    "avg_fare": 17.50,
    "avg_distance": 3.2,
    "avg_duration": 16.5,
    "avg_passengers": 1.4,
    "avg_speed": 11.6,
    "avg_fare_per_mile": 5.47,
    "max_fare": 450.00,
    "max_distance": 95.5,
    "earliest_trip": "2024-01-01 00:05:00",
    "latest_trip": "2024-01-31 23:58:00"
  }
}
```

---

## For Member B - Database

### What You Need from Member A

**Files to receive:**
1. ✅ `cleaned_taxi_data.csv` - Cleaned trip data
2. ✅ `exclusion_log.txt` - Record exclusion details
3. ✅ `processing_report.txt` - Processing summary

**These files are in:** `backend/` and `shared/` folders

### Your Tasks

1. **Create Database**
   ```bash
   createdb taxi_db
   ```

2. **Design Schema**
   - Create `locations` table (from taxi_zone_lookup.csv)
   - Create `trips` table (from cleaned_taxi_data.csv)
   - Add foreign keys, indexes, constraints

3. **Import Data**
   - Load `cleaned_taxi_data.csv` into `trips` table
   - Load `taxi_zone_lookup.csv` into `locations` table

4. **Share Connection String**
   ```
   postgresql://username:password@localhost:5432/taxi_db
   ```
   Give this to Member A to update `config.py`

5. **Create Indexes**
   ```sql
   CREATE INDEX idx_pickup_date ON trips(tpep_pickup_datetime);
   CREATE INDEX idx_pickup_location ON trips(PULocationID);
   CREATE INDEX idx_dropoff_location ON trips(DOLocationID);
   ```

### Recommended Schema

```sql
-- Locations dimension table
CREATE TABLE locations (
    location_id INTEGER PRIMARY KEY,
    borough VARCHAR(50),
    zone VARCHAR(100),
    service_zone VARCHAR(50)
);

-- Trips fact table
CREATE TABLE trips (
    trip_id SERIAL PRIMARY KEY,
    tpep_pickup_datetime TIMESTAMP,
    tpep_dropoff_datetime TIMESTAMP,
    passenger_count INTEGER,
    trip_distance DECIMAL(10,2),
    fare_amount DECIMAL(10,2),
    tip_amount DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    PULocationID INTEGER,
    DOLocationID INTEGER,
    pickup_borough VARCHAR(50),
    pickup_zone VARCHAR(100),
    dropoff_borough VARCHAR(50),
    dropoff_zone VARCHAR(100),
    trip_duration_minutes DECIMAL(10,2),
    avg_speed_mph DECIMAL(10,2),
    fare_per_mile DECIMAL(10,2),
    pickup_hour INTEGER,
    pickup_day_of_week INTEGER
);
```

### What to Give Back to Member A

- ✅ Database connection string
- ✅ Confirmation that data import succeeded
- ✅ Total record count in database

---

## For Member C - Frontend

### What You Need from Member A

**Backend API URL:**
```
http://localhost:5000/api
```

**All endpoints are ready to use!** See [API Documentation](#api-documentation) above.

### How to Use the API

1. **Fetch Data with JavaScript:**

```javascript
// Get trips
async function fetchTrips(limit = 100) {
  const response = await fetch(`http://localhost:5000/api/trips?limit=${limit}`);
  const data = await response.json();
  
  if (data.success) {
    return data.data;
  } else {
    console.error(data.error);
  }
}

// Get hourly pattern
async function fetchHourlyPattern() {
  const response = await fetch('http://localhost:5000/api/insights/hourly_pattern');
  const data = await response.json();
  return data.data;
}

// Get borough stats
async function fetchBoroughStats() {
  const response = await fetch('http://localhost:5000/api/insights/borough_stats');
  const data = await response.json();
  return data.data;
}
```

2. **Test API First:**

Before building your dashboard, test endpoints in browser:
```
http://localhost:5000/api/health
http://localhost:5000/api/trips?limit=10
http://localhost:5000/api/insights/borough_stats
```

3. **Handle CORS:**

CORS is already enabled in the backend. You can make requests from:
- `http://localhost:3000`
- `http://127.0.0.1:5500`
- Any origin (during development)

### Suggested Visualizations

Based on available endpoints:

1. **Line Chart** - Daily trips over time (`/api/insights/daily_trips`)
2. **Bar Chart** - Trips by hour of day (`/api/insights/hourly_pattern`)
3. **Pie Chart** - Trips by borough (`/api/insights/borough_stats`)
4. **Bar Chart** - Top pickup locations (`/api/insights/top_locations`)
5. **Histogram** - Fare distribution (`/api/insights/fare_distribution`)
6. **Table** - Recent trips (`/api/trips`)

---

## Troubleshooting

### Problem: Database Not Connected

**Symptoms:**
```
⚠️ Database connection failed
```

**Solutions:**
1. Check if Member B has created the database
2. Verify DATABASE_URL in `config.py` is correct
3. Test PostgreSQL connection:
   ```bash
   psql -U username -d taxi_db
   ```
4. Try SQLite fallback:
   ```python
   DATABASE_URL = "sqlite:///taxi_db.sqlite"
   ```

---

### Problem: Module Not Found

**Symptoms:**
```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
```bash
pip install -r requirements.txt
```

---

### Problem: Port Already in Use

**Symptoms:**
```
Address already in use
```

**Solutions:**
1. Change port in `config.py`:
   ```python
   API_PORT = 5001  # or any free port
   ```
2. Kill existing process:
   ```bash
   # Windows
   netstat -ano | findstr :5000
   taskkill /PID <process_id> /F
   
   # Linux/Mac
   lsof -ti:5000 | xargs kill -9
   ```

---

### Problem: CORS Errors in Frontend

**Symptoms:**
```
Access to fetch at 'http://localhost:5000/api/trips' from origin 
'http://localhost:3000' has been blocked by CORS policy
```

**Solution:**
CORS is already enabled in `app.py`. If still having issues:
1. Check `flask-cors` is installed
2. Add your frontend URL to `Config.CORS_ORIGINS` in `config.py`
3. Restart backend server

---

### Problem: No Data Returned

**Symptoms:**
API returns empty arrays

**Solutions:**
1. Check if Member B imported data into database
2. Test database directly:
   ```sql
   SELECT COUNT(*) FROM trips;
   ```
3. Check query parameters are valid
4. Review backend logs for errors

---

## File Structure

```
backend/
├── app.py                     # Flask API server
├── config.py                  # Configuration settings
├── data_processing.py         # Data cleaning pipeline
├── requirements.txt           # Python dependencies
├── README_BACKEND.md          # This file
├── cleaned_taxi_data.csv      # Cleaned data (generated)
├── exclusion_log.txt          # Exclusion report (generated)
└── processing_report.txt      # Processing log (generated)
```

---

## Testing Checklist

### Member A (You)
- [ ] Data processing runs without errors
- [ ] Cleaned data exported successfully
- [ ] Exclusion log created
- [ ] Backend server starts successfully
- [ ] All API endpoints respond correctly
- [ ] Database connection works (after Member B setup)

### Integration with Member B
- [ ] Shared cleaned_taxi_data.csv
- [ ] Received database connection string
- [ ] Updated config.py with database URL
- [ ] API can query database successfully

### Integration with Member C
- [ ] Confirmed API URL with Member C
- [ ] Member C can access /api/health
- [ ] Member C can fetch data from endpoints
- [ ] No CORS errors

---

## Contact & Support

**Member A Responsibilities:**
- ✅ Data processing and cleaning
- ✅ Feature engineering
- ✅ API development and maintenance
- ✅ Backend bug fixes

**Questions?**
- Data issues? → Check `processing_report.txt`
- API issues? → Check `backend.log`
- Need help? → Contact Member A!

---

**Last Updated:** 2024
**Version:** 1.0.0
