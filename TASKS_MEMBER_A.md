# Member A — Tasks After Database Setup

Member B has completed the database. Here's what Member A needs to do to connect the backend.

---

## ✅ Pre-Done (Member B already handled)
- `backend/config.py` — DATABASE_URL already updated to `sqlite:///database/taxi_trips.db`

## Tasks

### 1. Verify Backend Connects to New Database
```bash
cd backend
python -c "from config import Config; print(Config.DATABASE_URL)"
```
Expected: `sqlite:///database/taxi_trips.db`

### 2. Fix Relative Path (if needed)
If Flask can't find the DB when running from `backend/`, change `config.py` to use the absolute path:
```python
DATABASE_URL = "sqlite:///C:/Users/CHRIS/OneDrive/Desktop/summative web/nyc-taxi-analytics/database/taxi_trips.db"
```

### 3. Start the Backend Server
```bash
cd backend
python app.py
```
Expected: Server starts on `http://localhost:5000`

### 4. Test API Endpoints
Open browser or use curl:
- `http://localhost:5000/api/health` → Should show `"database": "connected"`
- `http://localhost:5000/api/stats/summary` → Should return real stats
- `http://localhost:5000/api/trips?limit=5` → Should return 5 trip records
- `http://localhost:5000/api/insights/hourly_pattern` → Should return 24 hourly data points
- `http://localhost:5000/api/insights/borough_stats` → Should return 6 borough records

### 5. Confirm to Team
Once all endpoints return real data, tell Member C: **"Backend is live, start building the frontend."**

---

## Database Info from Member B

| Item | Value |
|------|-------|
| Database type | SQLite 3 |
| Database file | `database/taxi_trips.db` |
| Connection string | `sqlite:///database/taxi_trips.db` |
| Trip records | 50,000 |
| Location zones | 265 |
| Indexes | 12 performance indexes |
| Derived features | trip_duration_minutes, avg_speed_mph, fare_per_mile |
