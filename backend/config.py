"""
NYC Taxi Trip Analyzer - Configuration File
Member A - Backend Configuration

This file contains all configuration settings for the backend service.
Update DATABASE_URL after Member B creates and shares the database.
"""

import os

class Config:
    """
    Configuration class for Flask application
    
    Environment Variables (optional):
        DATABASE_URL: PostgreSQL connection string
        API_PORT: Port for Flask server (default: 5000)
        DEBUG: Enable debug mode (default: True)
    """
    
    # ========================================================================
    # DATABASE CONFIGURATION
    # ========================================================================
    # 🔴 IMPORTANT FOR MEMBER B: Update this after database setup!
    # 
    # PostgreSQL format: postgresql://username:password@host:port/database
    # SQLite format: sqlite:///path/to/database.db
    # 
    # Examples:
    #   PostgreSQL: "postgresql://postgres:password@localhost:5432/taxi_db"
    #   SQLite:     "sqlite:///taxi_db.sqlite"
    # ========================================================================
    
    # DATABASE_URL = os.environ.get('DATABASE_URL') or "postgresql://postgres:password@localhost:5432/taxi_db"
    
    # ✅ Member B database setup complete — PostgreSQL
    DATABASE_URL = "postgresql://postgres:Chris12@localhost:5432/taxi_db"
    
    # ========================================================================
    # API CONFIGURATION
    # ========================================================================
    
    # Server settings
    API_HOST = '0.0.0.0'  # Listen on all interfaces (allows network access)
    API_PORT = int(os.environ.get('PORT', 5000))  # Default port 5000
    
    # Debug mode (set to False in production)
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # CORS settings (Cross-Origin Resource Sharing for frontend)
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:5500', '*']
    
    # ========================================================================
    # DATA PROCESSING CONFIGURATION
    # ========================================================================
    
    # File paths (relative to project root)
    DATA_DIR = '../data'
    RAW_DATA_FILE = 'yellow_tripdata.csv'  # or .parquet
    LOOKUP_FILE = 'taxi_zone_lookup.csv'
    
    # Output files
    CLEANED_DATA_FILE = 'cleaned_taxi_data.csv'
    EXCLUSION_LOG_FILE = 'exclusion_log.txt'
    PROCESSING_REPORT_FILE = 'processing_report.txt'
    
    # Sampling configuration
    SAMPLE_SIZE = 50000  # Number of rows to keep (full dataset may be too large)
    RANDOM_SEED = 42     # For reproducibility
    
    # ========================================================================
    # DATA QUALITY THRESHOLDS
    # ========================================================================
    # These values define what we consider "valid" data
    
    # Passenger count limits
    MIN_PASSENGERS = 1
    MAX_PASSENGERS = 6
    
    # Trip distance limits (miles)
    MIN_DISTANCE = 0.1      # At least 0.1 mile
    MAX_DISTANCE = 100      # Max 100 miles (outlier threshold)
    
    # Fare amount limits (dollars)
    MIN_FARE = 2.50         # NYC minimum fare
    MAX_FARE = 500          # Reasonable maximum
    
    # Speed limits (mph)
    MIN_SPEED = 0.1         # Must be moving
    MAX_SPEED = 80          # Maximum reasonable speed in NYC
    
    # Duration limits (minutes)
    MIN_DURATION = 1        # At least 1 minute
    MAX_DURATION = 180      # Max 3 hours
    
    # ========================================================================
    # FEATURE ENGINEERING SETTINGS
    # ========================================================================
    
    # Derived features to calculate
    CALCULATE_DURATION = True
    CALCULATE_SPEED = True
    CALCULATE_FARE_PER_MILE = True
    CALCULATE_TIME_FEATURES = True  # hour, day of week, etc.
    
    # ========================================================================
    # API RATE LIMITING
    # ========================================================================
    
    MAX_RECORDS_PER_REQUEST = 1000  # Maximum records to return in one API call
    DEFAULT_PAGE_SIZE = 100         # Default number of records
    
    # ========================================================================
    # LOGGING CONFIGURATION
    # ========================================================================
    
    LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_TO_FILE = True
    LOG_FILE = 'backend.log'

    @staticmethod
    def print_config():
        """Print current configuration (for debugging)"""
        print("\n" + "="*70)
        print("BACKEND CONFIGURATION")
        print("="*70)
        print(f"Database URL: {Config.DATABASE_URL}")
        print(f"API Host: {Config.API_HOST}")
        print(f"API Port: {Config.API_PORT}")
        print(f"Debug Mode: {Config.DEBUG}")
        print(f"Sample Size: {Config.SAMPLE_SIZE}")
        print("="*70 + "\n")


# Quick test when running this file directly
if __name__ == '__main__':
    Config.print_config()
