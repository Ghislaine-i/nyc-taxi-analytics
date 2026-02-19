"""
QUICK START GUIDE - Backend Setup
NYC Taxi Trip Analyzer

Follow these steps in order!
"""

print("""
======================================================================
                                                                      
          NYC TAXI TRIP ANALYZER - QUICK START GUIDE                  
                      Backend Setup                          
                                                                      
======================================================================

This guide will help you set up and run the backend in 5 minutes!

""")

import sys
import os

def check_step(step_num, description, check_func):
    """Check if a step is complete"""
    print(f"\n{'='*70}")
    print(f"STEP {step_num}: {description}")
    print('='*70)
    
    result, message = check_func()
    
    if result:
        print(f"[OK] {message}")
        return True
    else:
        print(f"[!!] {message}")
        return False

def step1_dependencies():
    """Check if dependencies are installed"""
    try:
        import flask
        import pandas
        import sqlalchemy
        return True, "All dependencies installed"
    except ImportError as e:
        return False, f"Missing dependency: {e.name}\n   Run: pip install -r requirements.txt"

def step2_data_files():
    """Check if raw data files exist"""
    data_dir = '../data'
    raw_files = ['yellow_tripdata.csv', 'yellow_tripdata.parquet']
    lookup_file = 'taxi_zone_lookup.csv'
    
    # Check for raw data
    raw_exists = False
    for f in raw_files:
        if os.path.exists(os.path.join(data_dir, f)):
            raw_exists = True
            break
    
    lookup_exists = os.path.exists(os.path.join(data_dir, lookup_file))
    
    if raw_exists and lookup_exists:
        return True, "Raw data files found"
    elif not raw_exists:
        return False, f"Raw data file not found in {data_dir}\n   Expected: yellow_tripdata.csv or .parquet"
    else:
        return False, f"Lookup file not found: {data_dir}/{lookup_file}"

def step3_processed_data():
    """Check if data has been processed"""
    if os.path.exists('cleaned_taxi_data.csv'):
        return True, "Cleaned data file exists"
    else:
        return False, "Cleaned data not found\n   Run: python data_processing.py"

def step4_database():
    """Check if database is configured"""
    try:
        from config import Config
        from sqlalchemy import create_engine
        
        if "password" in Config.DATABASE_URL.lower():
            return False, "Database URL still has placeholder\n   Update config.py with your database connection\n   OR use SQLite fallback (see config.py)"
        
        try:
            engine = create_engine(Config.DATABASE_URL)
            with engine.connect() as conn:
                result = conn.execute("SELECT 1")
                result.fetchone()
            return True, "Database connection successful"
        except:
            return False, "Cannot connect to database\n   Check config.py settings\n   Backend will run but API queries will fail"
            
    except Exception as e:
        return False, f"Configuration error: {e}"

def step5_backend():
    """Check if backend can start"""
    try:
        import app
        return True, "Backend imports successful - ready to run"
    except Exception as e:
        return False, f"Backend import error: {e}"

def main():
    """Run all checks"""
    
    steps = [
        (1, "Check Python Dependencies", step1_dependencies),
        (2, "Check Raw Data Files", step2_data_files),
        (3, "Check Processed Data", step3_processed_data),
        (4, "Check Database Connection", step4_database),
        (5, "Check Backend Ready", step5_backend),
    ]
    
    results = []
    
    for num, desc, func in steps:
        result = check_step(num, desc, func)
        results.append((desc, result))
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    for desc, result in results:
        status = "[OK]" if result else "[!!]"
        print(f"{status} {desc}")
    
    # Next steps
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    
    all_passed = all(result for _, result in results)
    
    if not results[0][1]:  # Dependencies
        print("""
1. Install dependencies:
   -> pip install -r requirements.txt
   
2. Run this script again:
   -> python quick_start.py
""")
    
    elif not results[2][1]:  # Processed data
        print("""
1. Process the raw data:
   -> python data_processing.py
   
   This will:
   - Clean the data
   - Create derived features
   - Export cleaned_taxi_data.csv
   - Generate exclusion log
   
2. Run this script again:
   -> python quick_start.py
""")
    
    elif not results[3][1]:  # Database
        print("""
DATABASE NOT CONNECTED (Expected at this stage)

OPTION 1: Use SQLite (recommended for quick setup)
   1. Edit config.py
   2. Change DATABASE_URL to:
      DATABASE_URL = "sqlite:///taxi_db.sqlite"
   3. Run: python import_to_database.py
   4. Run backend: python app.py

OPTION 2: Use PostgreSQL
   1. Create PostgreSQL database
   2. Run: python import_to_database.py
   3. Update config.py with connection string
   4. Run backend: python app.py

BACKEND WILL RUN WITHOUT DATABASE:
   - API will start successfully
   - Health endpoint will work
   - Data endpoints will fail until DB connected
   
To test anyway:
   -> python app.py
""")
    
    elif all_passed:
        print("""
[SUCCESS] EVERYTHING READY!

Start the backend:
   -> python app.py

Then test in browser:
   -> http://localhost:5000/api/health

Available endpoints:
   - GET /api/health
   - GET /api/test
   - GET /api/trips?limit=10
   - GET /api/insights/hourly_pattern
   - GET /api/insights/borough_stats
   - GET /api/stats/summary

Full documentation: README_BACKEND.md

Ready for frontend integration!
""")
    
    print("="*70)
    
    # Show file structure
    print("\nFILE STRUCTURE:")
    print("""
backend/
|-- app.py                     # Flask API server
|-- config.py                  # Configuration
|-- data_processing.py         # Data cleaning pipeline
|-- requirements.txt           # Dependencies
|-- quick_start.py            # This file
|-- README_BACKEND.md         # Full documentation
|-- HANDOVER_TO_TEAM.md       # Guide for teammates
|-- cleaned_taxi_data.csv     # Cleaned data (generated)
|-- exclusion_log.txt         # Exclusion report (generated)
+-- processing_report.txt     # Processing log (generated)
""")
    
    print("\n" + "="*70)
    print("BACKEND CHECKLIST:")
    print("="*70)
    print("""
Setup:
  [OK] Install dependencies
  [ ? ] Process data
  [ - ] Import to database
  [ - ] Test backend

Integration:
  [ - ] Connect to database
  [ - ] Test API endpoints
  [ - ] Connect frontend

Final:
  [ - ] Final testing
  [ - ] Documentation
  [ - ] Submit
""")
    print("="*70 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
