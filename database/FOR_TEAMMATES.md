# Member B — Database Deliverables Summary

## What I Built

| File | Purpose |
|------|---------| 
| `database/schema.sql` | PostgreSQL schema — `locations` + `trips` tables, foreign keys, 12 indexes |
| `database/setup_database.py` | One-command script that creates the PostgreSQL DB and imports all data |
| `database/insight_queries.sql` | 6 analytical queries for the dashboard and report |
| `database/run_insights.py` | Runs queries and exports results as `insight_results.json` |
| `database/export_dump.py` | Generates `taxi_db_dump.sql` using pg_dump |
| `database/SECTION_4_INSIGHTS.md` | Written insights for Section 4 of the report |

---

## For Member A (Backend)

**Connection string (already set in `backend/config.py`):**

```
postgresql://postgres:Chris12@localhost:5432/taxi_db
```

The database contains:
- **50,000** cleaned trip records
- **~265** unique taxi zone locations
- **12** performance indexes
- All 3 derived features: `trip_duration_minutes`, `avg_speed_mph`, `fare_per_mile`
- All time features: `pickup_hour`, `pickup_day_of_week`, `pickup_day_name`, `pickup_month`

**Prerequisites:** Make sure `psycopg2-binary` is installed:
```bash
pip install psycopg2-binary
```

---

## For Member C (Frontend)

No action needed from you regarding the database. The API endpoints remain the same — Member A will start the backend and all endpoints will return live data from PostgreSQL.

---

## How to Recreate

```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Create DB + import data (~30s)
cd database
python setup_database.py

# Run insight queries + save JSON
python run_insights.py

# Generate SQL dump for submission
python export_dump.py
```
