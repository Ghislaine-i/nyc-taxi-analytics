# NYC Taxi Trip Analyzer
## Enterprise Fullstack Application - Team Project

---

## 🚕 Project Overview

This is a comprehensive fullstack application for analyzing NYC taxi trip data. The system processes over 50,000 taxi trip records, stores them in a relational database, and provides an interactive dashboard for exploring urban mobility patterns.

### Key Features
- **Data Processing Pipeline**: Automated ETL with quality checks and feature engineering
- **RESTful API Backend**: Flask-based API with 11+ endpoints
- **Relational Database**: Normalized schema with efficient indexing
- **Interactive Dashboard**: Web-based UI for data exploration
- **Real-world Insights**: Temporal patterns, location analytics, fare distributions

---

## 👥 Team Structure

### Member A - Backend & Data Processing ✅
**Responsibilities:**
- Data cleaning and preprocessing
- Feature engineering (3 derived metrics)
- Flask REST API development
- Backend documentation

**Status**: COMPLETE
**Files Ready**: See `backend/` folder

### Member B - Database Design & Implementation ⏳
**Responsibilities:**
- Database schema design
- Data import and indexing
- Query optimization
- Data integrity validation

**Status**: WAITING FOR MEMBER B
**Needs**: `cleaned_taxi_data.csv` from Member A

### Member C - Frontend Dashboard ⏳
**Responsibilities:**
- Web dashboard development
- Data visualizations
- User interface design
- Frontend documentation

**Status**: WAITING FOR API CONNECTION
**Needs**: Backend running + database connected

---

## 📊 Dataset

**Source**: NYC Taxi & Limousine Commission (TLC)

### Files Used:
1. **yellow_tripdata** (Fact Table)
   - Raw trip-level records
   - Timestamps, distances, fares, locations
   
2. **taxi_zone_lookup** (Dimension Table)
   - Borough and zone mappings
   - PULocationID → Borough, Zone names
   
3. **taxi_zones** (Spatial Metadata)
   - GeoJSON boundaries for taxi zones

### Data Volume:
- Original: ~687MB raw data
- Processed: 50,000 cleaned records
- Features: 20+ columns including 3 derived metrics

---

## 🏗️ Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Raw Data  │─────▶│   Backend   │─────▶│  Database   │
│  (CSV/PKT)  │      │  (Flask)    │      │(PostgreSQL) │
└─────────────┘      └──────┬──────┘      └─────────────┘
                            │
                            │ REST API
                            │
                     ┌──────▼──────┐
                     │  Frontend   │
                     │    (HTML    │
                     │  JS/Charts) │
                     └─────────────┘
```

### Technology Stack:
- **Backend**: Python 3.9+, Flask, Pandas, NumPy
- **Database**: PostgreSQL (or SQLite fallback)
- **Frontend**: HTML5, CSS3, JavaScript, Chart.js
- **Data**: Parquet/CSV processing with PyArrow

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- PostgreSQL (optional - can use SQLite)
- Modern web browser

### Installation

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd nyc-taxi-trip-analyzer
```

#### 2. Set Up Backend (Member A)
```bash
cd backend
pip install -r requirements.txt
python data_processing.py      # Process raw data
python app.py                 # Start API server
```

**Backend will run at**: `http://localhost:5000`

#### 3. Set Up Database (Member B)
```bash
# Create database
createdb taxi_db

# Import cleaned data
python import_data.py

# Update backend/config.py with connection string
```

#### 4. Set Up Frontend (Member C)
```bash
# Open index.html in browser
# Or use a simple HTTP server:
python -m http.server 8000
```

**Frontend will run at**: `http://localhost:8000`

---

## 📁 Project Structure

```
nyc-taxi-trip-analyzer/
│
├── backend/                    # 🔧 Member A - Backend
│   ├── app.py                 # Flask REST API (626 lines)
│   ├── config.py              # Configuration
│   ├── data_processing.py     # ETL Pipeline (500+ lines)
│   ├── requirements.txt       # Python dependencies
│   ├── quick_start.py        # Setup diagnostic tool
│   │
│   ├── README_BACKEND.md     # Complete API documentation
│   ├── HANDOVER_TO_TEAM.md   # Team coordination guide
│   ├── COMPLETE_PACKAGE_SUMMARY.md  # Deliverables summary
│   │
│   ├── cleaned_taxi_data.csv  # Processed data (50K records)
│   ├── exclusion_log.txt     # Data quality report
│   └── processing_report.txt  # Processing log
│
├── shared/                     # 📦 Shared files
│   └── cleaned_taxi_data.csv  # Copy for Member B
│
├── data/                       # 📥 Raw input data
│   ├── yellow_tripdata.csv    # Raw trip data
│   └── taxi_zone_lookup.csv   # Zone lookup table
│
├── frontend/                   # 🎨 Member C - Frontend (to be created)
│   ├── index.html
│   ├── dashboard.js
│   └── styles.css
│
├── database/                   # 💾 Member B - Database (to be created)
│   ├── schema.sql
│   ├── import_data.py
│   └── queries.sql
│
├── docs/                       # 📄 Documentation (to be created)
│   ├── technical_report.pdf
│   ├── team_participation.xlsx
│   └── architecture.png
│
└── README.md                   # This file
```

---

## 🔌 API Endpoints

**Base URL**: `http://localhost:5000/api`

### Health & Testing
- `GET /api/health` - API health check
- `GET /api/test` - Database connection test

### Data Retrieval
- `GET /api/trips` - Get trip records with filters

**Example**: `/api/trips?borough=Manhattan&limit=50`

### Temporal Insights
- `GET /api/insights/daily_trips` - Daily aggregations
- `GET /api/insights/hourly_pattern` - Hourly patterns
- `GET /api/insights/day_of_week` - Day of week patterns

### Location Insights
- `GET /api/insights/top_locations` - Top pickup/dropoff zones
- `GET /api/insights/borough_stats` - Borough statistics

### Distributions
- `GET /api/insights/fare_distribution` - Fare distribution
- `GET /api/insights/distance_distribution` - Distance distribution

### Statistics
- `GET /api/stats/summary` - Overall summary statistics

**Full API Documentation**: See `backend/README_BACKEND.md`

---

## 🔬 Derived Features

### Three Main Engineered Features:

#### 1. trip_duration_minutes
```python
duration = (dropoff_time - pickup_time).total_seconds() / 60
```
**Justification**: Essential for speed calculations and temporal analysis. Reveals trip efficiency and traffic patterns.

#### 2. avg_speed_mph
```python
speed = trip_distance / (duration_minutes / 60)
```
**Justification**: Indicates traffic conditions, identifies rush hours, provides insights into urban mobility patterns.

#### 3. fare_per_mile
```python
fare_per_mile = fare_amount / trip_distance
```
**Justification**: Identifies pricing patterns, reveals surge pricing, enables economic analysis across routes and boroughs.

---

## 📊 Data Cleaning Process

### Quality Checks:
- ✅ Removed duplicates
- ✅ Handled missing values
- ✅ Removed outliers:
  - Passengers: 1-6
  - Distance: 0.1-100 miles
  - Fare: $2.50-$500
  - Speed: 0.1-80 mph
  - Duration: 1-180 minutes

### Results:
- Original records: ~700K+
- Final clean records: 50,000
- Exclusion log maintained for transparency

**Details**: See `backend/exclusion_log.txt`

---

## 🔄 Workflow & Timeline

### Day 1 - Foundation ✅
- [x] Member A: Data processing complete
- [x] Member A: API development complete
- [ ] Member B: Database setup
- [ ] Member B: Data import

### Day 2 - Integration
- [ ] Member A: Connect to database
- [ ] Member C: Build frontend
- [ ] Member C: Create visualizations
- [ ] All: Integration testing

### Day 3 - Finalization
- [ ] All: Final testing
- [ ] Member C: Record video walkthrough
- [ ] All: Complete documentation
- [ ] All: Submit deliverables

---

## 📝 Deliverables

### Required Submissions:

1. **Codebase (.zip)** + **GitHub Link**
   - All source code
   - Clean project structure
   - README with setup instructions

2. **Team Participation Sheet**
   - Role assignments
   - Meeting notes
   - Individual contributions

3. **Database Files**
   - Schema SQL files
   - Database dump
   - Sample queries

4. **PDF Documentation Report**
   - System architecture
   - Technical descriptions
   - Insights and findings
   - Reflections

5. **Video Walkthrough (5 minutes)**
   - System demonstration
   - Architecture explanation
   - Feature showcase
   - Technical insights

---

## 🎥 Video Walkthrough Structure

### Timeline (5 minutes):

**0:00-0:30** - Introduction
- Project overview
- Team member roles

**0:30-1:30** - Dashboard Demonstration
- Live data exploration
- Filtering and sorting
- Key visualizations

**1:30-2:30** - Architecture Explanation
- System components
- Data flow
- Technology choices

**2:30-3:30** - Key Insights
- Derived features explanation
- Data patterns discovered
- Business value

**3:30-4:30** - Code Walkthrough
- Backend highlights
- Database design
- Frontend implementation

**4:30-5:00** - Conclusion
- Challenges overcome
- Lessons learned
- Future improvements

---

## 🤝 Team Coordination

### Current Status:

#### Member A (Backend) - ✅ COMPLETE
**Delivered:**
- Cleaned data: `cleaned_taxi_data.csv`
- Flask API: All 11 endpoints functional
- Documentation: Complete API reference
- Handover guide: For Members B and C

**Next**: Waiting for database connection string from Member B

#### Member B (Database) - ⏳ IN PROGRESS
**Needs from Member A:**
- `cleaned_taxi_data.csv` ✅ Ready
- `taxi_zone_lookup.csv` ✅ Ready
- Database schema recommendations ✅ Provided

**Deliverables to Member A:**
- Database connection string
- Confirmation of data import
- Total record count validation

#### Member C (Frontend) - ⏳ PENDING
**Needs from Member A:**
- API base URL ✅ Ready: `http://localhost:5000/api`
- API documentation ✅ Ready
- Sample endpoints for testing ✅ Ready

**Needs from Project:**
- Backend server running ⏳ Waiting for database
- Sample data from API ⏳ Waiting for database

---

## 📚 Documentation

### For Teammates:

**Member A's Documentation:**
- `backend/README_BACKEND.md` - Complete API reference
- `backend/HANDOVER_TO_TEAM.md` - Team coordination guide
- `backend/COMPLETE_PACKAGE_SUMMARY.md` - Deliverables summary

**Quick Start:**
- `backend/quick_start.py` - Automated setup checker

**Logs & Reports:**
- `backend/exclusion_log.txt` - Data quality documentation
- `backend/processing_report.txt` - Processing pipeline log

---

## 🐛 Troubleshooting

### Backend won't start?
```bash
# Check dependencies
python backend/quick_start.py

# Install missing packages
pip install -r backend/requirements.txt
```

### Database connection failed?
- Verify PostgreSQL is running
- Check connection string in `backend/config.py`
- Try SQLite fallback (see config.py)

### Frontend can't connect to API?
- Ensure backend is running: `http://localhost:5000/api/health`
- Check CORS is enabled (already configured)
- Verify API base URL in frontend code

### Data processing errors?
- Check raw data files in `data/` folder
- Verify file names match configuration
- See `backend/processing_report.txt` for details

---

## 📞 Support

### Architecture Questions?
- See: `backend/README_BACKEND.md`
- Contact: Member A

### Database Questions?
- See: `backend/HANDOVER_TO_TEAM.md` (Database section)
- Contact: Member B

### Frontend Questions?
- See: `backend/README_BACKEND.md` (For Member C section)
- Contact: Member C

---

## 🏆 Success Criteria

### ✅ Ready for submission when:

**Technical:**
- [ ] Backend API running and returning data
- [ ] Database populated with cleaned data
- [ ] Frontend displaying visualizations
- [ ] All components integrated successfully

**Documentation:**
- [ ] README complete with setup instructions
- [ ] Technical report written
- [ ] Team participation sheet filled
- [ ] Video walkthrough recorded

**Quality:**
- [ ] No errors in console
- [ ] All filters working
- [ ] Data visualizations meaningful
- [ ] Code well-commented

---

## 📄 License

Academic project for educational purposes.

---

## 🙏 Acknowledgments

- NYC Taxi & Limousine Commission for providing open data
- Course instructors and teaching assistants
- Team members for collaborative effort

---

## 📅 Project Timeline

**Start Date**: Day 1  
**Current Status**: Member A Complete, Waiting for Member B  
**Target Completion**: Day 3  
**Submission Deadline**: [Your deadline here]

---

**Member A - Backend Component: COMPLETE ✅**  
**Member B - Database Component: IN PROGRESS ⏳**  
**Member C - Frontend Component: PENDING ⏳**

Last Updated: Day 1, End of Development Sprint
