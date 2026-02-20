# NYC Taxi Trip Analyzer
## Enterprise Fullstack Application - Team Project

---

## Project Overview

This is a comprehensive fullstack application for analyzing NYC taxi trip data. The system processes over 50,000 taxi trip records, stores them in a relational database, and provides an interactive dashboard for exploring urban mobility patterns.

### Key Features
- **Data Processing Pipeline**: Automated ETL with quality checks and feature engineering
- **RESTful API Backend**: Flask-based API with 11+ endpoints
- **Relational Database**: Normalized schema with efficient indexing
- **Interactive Dashboard**: Web-based UI for data exploration
- **Real-world Insights**: Temporal patterns, location analytics, fare distributions

---

## Dataset

**Source**: NYC Taxi and Limousine Commission (TLC)

| File | Type | Description |
|---|---|---|
| `yellow_tripdata.csv` | Fact Table | 7,667,792 raw trip records |
| `taxi_zone_lookup.csv` | Dimension Table | 265 borough and zone mappings |
| `taxi_zones.geojson` | Spatial Metadata | GeoJSON boundaries for taxi zones |

**Processed**: 50,000 cleaned records, 29 columns, including 3 derived features.

---

## Video Walkthrough

(https://drive.google.com/file/d/1xAPNtHRGQtPw0Vi1O39hNBGqjVUnpTa5/view?usp=sharing)

---

## Quick Start (TL;DR)

```bash
# 1. Clone and setup
git clone <repository-url>
cd nyc-taxi-analytics

# 2. Create virtual environment and install dependencies
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Mac/Linux
pip install -r backend/requirements.txt

# 3. Import data to database (SQLite, no setup needed)
cd backend
python import_to_database.py   # Select option 2 for SQLite

# 4. Start backend API
python app.py

# 5. Start frontend (new terminal)
cd ..
python -m http.server 8000 --directory frontend

# 6. Open browser
# Backend: http://localhost:5000/api/health
# Frontend: http://localhost:8000
```

---

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- A modern web browser (Chrome, Firefox, Edge)
- (Optional) PostgreSQL if switching from the SQLite default

---

### Step 1 — Clone the Repository

```bash
git clone <repository-url>
cd nyc-taxi-analytics
```

---

### Step 2 — Create Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt.

---

### Step 3 — Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

The `requirements.txt` includes: Flask, Flask-CORS, Pandas, NumPy, SQLAlchemy, PyArrow, psycopg2-binary.

---

### Step 4 — Process the Raw Data (Optional)

Place the raw dataset files in the `data/` folder:
- `data/yellow_tripdata.csv` (or `.parquet`)
- `data/taxi_zone_lookup.csv`

Then run the processing pipeline:

```bash
cd backend
python data_processing.py
```

This will:
- Load and clean 7.6M+ raw records
- Apply outlier thresholds and handle missing values
- Engineer 3 derived features: `trip_duration_minutes`, `avg_speed_mph`, `fare_per_mile`
- Export `cleaned_taxi_data.csv` (50,000 records) to `backend/` and `shared/`
- Generate `exclusion_log.txt` and `processing_report.txt`

---

### Step 5 — Set Up the Database

The backend is pre-configured to use SQLite (`backend/taxi_db.sqlite`) for zero-configuration setup.

To import data into the SQLite database:

```bash
cd backend
python import_to_database.py
```

**To use PostgreSQL instead**, update `backend/config.py`:

```python
# Replace this line:
DATABASE_URL = "sqlite:///taxi_db.sqlite"

# With your PostgreSQL connection string:
DATABASE_URL = "postgresql://username:password@localhost:5432/taxi_db"
```

Then create the database and import:

```bash
createdb taxi_db
python import_to_database.py
```

---

### Step 6 — Start the Backend API

```bash
cd backend
python app.py
```

The API will run at: `http://localhost:5000`

Verify it is working by visiting: `http://localhost:5000/api/health`

Expected response:
```json
{
  "success": true,
  "message": "NYC Taxi Trip Analyzer API is running",
  "database": "connected"
}
```

---

### Step 7 — Launch the Frontend Dashboard

Open a new terminal from the project root:

```bash
python -m http.server 8000 --directory frontend
```

Then open your browser at: `http://localhost:8000`

Alternatively, open `frontend/index.html` directly in your browser.

> The dashboard connects automatically to the backend at `http://localhost:5000/api`. If the backend is offline, sample data is displayed so the page remains functional.

---

## Project Structure

```
nyc-taxi-analytics/
|
+-- backend/
|   +-- app.py                   # Flask REST API (11 endpoints)
|   +-- config.py                # Database and API configuration
|   +-- data_processing.py       # ETL pipeline
|   +-- import_to_database.py    # Database import script
|   +-- requirements.txt         # Python dependencies
|   +-- cleaned_taxi_data.csv    # Processed data (50,000 records)
|   +-- exclusion_log.txt        # Records excluded and reasons
|   +-- processing_report.txt    # Full processing pipeline log
|   +-- taxi_db.sqlite           # SQLite database (auto-generated)
|
+-- frontend/
|   +-- index.html               # Dashboard HTML structure
|   +-- styles.css               # Dark professional CSS theme
|   +-- dashboard.js             # Chart.js charts, API calls, filters
|
+-- data/
|   +-- yellow_tripdata.csv      # Raw trip data (place here)
|   +-- taxi_zone_lookup.csv     # Zone lookup table (place here)
|
+-- shared/
|   +-- cleaned_taxi_data.csv    # Shared clean data copy
|
+-- README.md
```

---

## API Endpoints

**Base URL**: `http://localhost:5000/api`

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | API and database status check |
| `/test` | GET | Database connectivity test |
| `/trips` | GET | Trip records with optional filters |
| `/insights/daily_trips` | GET | Daily aggregations |
| `/insights/hourly_pattern` | GET | Trip volume and speed by hour (0-23) |
| `/insights/day_of_week` | GET | Trip patterns Monday-Sunday |
| `/insights/top_locations` | GET | Top pickup or dropoff zones |
| `/insights/borough_stats` | GET | Statistics aggregated by borough |
| `/insights/fare_distribution` | GET | Trip count by fare range bucket |
| `/insights/distance_distribution` | GET | Trip count by distance range bucket |
| `/stats/summary` | GET | Overall dataset summary statistics |

**Filter parameters for `/trips`**:
- `borough` — Manhattan, Brooklyn, Queens, Bronx, Staten Island
- `min_fare`, `max_fare` — fare range in dollars
- `min_distance`, `max_distance` — trip distance in miles
- `date` — YYYY-MM-DD format
- `limit` — number of records (max 1000)

---

## Derived Features

Three features were engineered from the raw data:

| Feature | Formula | Purpose |
|---|---|---|
| `trip_duration_minutes` | `(dropoff_time - pickup_time) / 60` | Enables speed calculation and temporal analysis |
| `avg_speed_mph` | `trip_distance / (duration_minutes / 60)` | Reveals traffic conditions and rush-hour patterns |
| `fare_per_mile` | `fare_amount / trip_distance` | Economic analysis across routes and boroughs |

---

## Data Cleaning Summary

| Stage | Records Removed | Remaining |
|---|---|---|
| Original dataset | — | 7,667,792 |
| Duplicates | 0 | 7,667,792 |
| Passenger count (1-6) | 117,438 | 7,550,354 |
| Trip distance (0.1-100 mi) | 68,815 | 7,476,069 |
| Fare amount ($2.50-$500) | 5,470 | 7,470,599 |
| Duration (1-180 minutes) | 38,713 | 7,435,495 |
| Speed (0.1-80 mph) | 421 | 7,435,074 |
| Fare per mile (> $100) | 1,440 | 7,433,634 |
| Final sample (seed 42) | — | 50,000 |

Full exclusion log: `backend/exclusion_log.txt`

---

## Troubleshooting

**Backend will not start**
```bash
python backend/quick_start.py
pip install -r backend/requirements.txt
```

**Database connection failed**
- Verify `DATABASE_URL` in `backend/config.py`
- For SQLite: ensure `backend/taxi_db.sqlite` exists (run `import_to_database.py`)
- For PostgreSQL: ensure the server is running and credentials are correct

**Frontend shows no data**
- Confirm backend is running at `http://localhost:5000/api/health`
- Confirm the URL uses `http://` not `https://`
- Check browser console for CORS errors

**Charts not rendering**
- Confirm internet access (Chart.js is loaded from CDN)
- Check browser developer console for JavaScript errors
- Ensure `dashboard.js` is in the same folder as `index.html`

---

## Documentation

- API Reference: `backend/README_BACKEND.md`
- Processing Log: `backend/processing_report.txt`
- Exclusion Log: `backend/exclusion_log.txt`

---

## Acknowledgments

NYC Taxi and Limousine Commission for providing open trip record data.

---

*Last updated: February 2026*


