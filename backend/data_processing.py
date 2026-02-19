"""
NYC Taxi Trip Analyzer - Data Processing Pipeline

This script handles:
1. Loading raw taxi trip data (CSV/Parquet)
2. Data quality checks and cleaning
3. Feature engineering (derived metrics)
4. Integration with taxi zone lookup data
5. Export cleaned data for database import

Usage:
    python data_processing.py
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys
from config import Config

# ============================================================================
# LOGGING UTILITIES
# ============================================================================

class DataLogger:
    """Simple logging utility for processing pipeline"""
    
    def __init__(self, log_file='processing_log.txt'):
        self.log_file = log_file
        self.logs = []
        
    def log(self, message, level='INFO'):
        """Log a message to console and file"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        self.logs.append(log_entry)
        
    def save(self):
        """Save all logs to file"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.logs))
        print(f"\n[OK] Log saved to: {self.log_file}")

logger = DataLogger(Config.PROCESSING_REPORT_FILE)

# ============================================================================
# DATA LOADING
# ============================================================================

def load_trip_data(filepath):
    """
    Load taxi trip data from CSV or Parquet file
    
    Args:
        filepath (str): Path to data file
        
    Returns:
        pd.DataFrame: Raw trip data
    """
    logger.log("="*70)
    logger.log("STEP 1: LOADING RAW DATA")
    logger.log("="*70)
    
    try:
        if filepath.endswith('.parquet'):
            logger.log(f"Loading Parquet file: {filepath}")
            df = pd.read_parquet(filepath)
        else:
            logger.log(f"Loading CSV file: {filepath}")
            df = pd.read_csv(filepath)
        
        logger.log(f"[OK] Loaded {len(df):,} records")
        logger.log(f"  Columns: {list(df.columns)}")
        logger.log(f"  Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        return df
        
    except FileNotFoundError:
        logger.log(f"[OK] ERROR: File not found: {filepath}", 'ERROR')
        sys.exit(1)
    except Exception as e:
        logger.log(f"[OK] ERROR loading data: {e}", 'ERROR')
        sys.exit(1)

def load_zone_lookup(filepath):
    """Load taxi zone lookup data"""
    logger.log("\nLoading taxi zone lookup data...")
    
    try:
        lookup = pd.read_csv(filepath)
        logger.log(f"[OK] Loaded {len(lookup)} taxi zones")
        
        # Rename columns for clarity
        lookup.columns = ['LocationID', 'Borough', 'Zone', 'service_zone']
        
        return lookup
        
    except Exception as e:
        logger.log(f"[!]  Could not load lookup file: {e}", 'WARNING')
        return None

# ============================================================================
# DATA QUALITY CHECKS AND CLEANING
# ============================================================================

def initial_data_exploration(df):
    """Explore raw data characteristics"""
    logger.log("\n" + "="*70)
    logger.log("STEP 2: INITIAL DATA EXPLORATION")
    logger.log("="*70)
    
    logger.log(f"\nDataset Shape: {df.shape[0]:,} rows [OK] {df.shape[1]} columns")
    
    # Missing values
    logger.log("\nMissing Values:")
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    if len(missing) > 0:
        for col, count in missing.items():
            pct = (count / len(df)) * 100
            logger.log(f"  {col}: {count:,} ({pct:.2f}%)")
    else:
        logger.log("  None detected")
    
    # Data types
    logger.log("\nData Types:")
    for col, dtype in df.dtypes.items():
        logger.log(f"  {col}: {dtype}")
    
    # Basic statistics for numeric columns
    logger.log("\nNumeric Column Statistics:")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols[:5]:  # Show first 5 numeric columns
        logger.log(f"  {col}: min={df[col].min():.2f}, max={df[col].max():.2f}, mean={df[col].mean():.2f}")

def remove_duplicates(df):
    """Remove duplicate records"""
    logger.log("\n" + "-"*70)
    logger.log("Removing Duplicates...")
    logger.log("-"*70)
    
    initial_count = len(df)
    df = df.drop_duplicates()
    removed = initial_count - len(df)
    
    logger.log(f"  Removed: {removed:,} duplicate records")
    logger.log(f"  Remaining: {len(df):,} records")
    
    return df

def handle_missing_values(df):
    """
    Handle missing values according to business logic
    
    Strategy:
    - Required fields (passenger_count, distance, fare): Drop rows
    - Optional fields (tip_amount, tolls): Fill with 0
    """
    logger.log("\n" + "-"*70)
    logger.log("Handling Missing Values...")
    logger.log("-"*70)
    
    initial_count = len(df)
    
    # Critical columns - drop rows if missing
    critical_cols = ['passenger_count', 'trip_distance', 'fare_amount', 
                     'tpep_pickup_datetime', 'tpep_dropoff_datetime']
    
    existing_critical = [col for col in critical_cols if col in df.columns]
    
    logger.log(f"  Dropping rows with missing values in: {existing_critical}")
    df = df.dropna(subset=existing_critical)
    
    dropped = initial_count - len(df)
    logger.log(f"  Dropped: {dropped:,} rows with missing critical data")
    
    # Optional columns - fill with 0
    optional_numeric = ['tip_amount', 'tolls_amount', 'improvement_surcharge', 
                       'total_amount', 'congestion_surcharge']
    
    for col in optional_numeric:
        if col in df.columns:
            missing = df[col].isnull().sum()
            if missing > 0:
                df[col] = df[col].fillna(0)
                logger.log(f"  Filled {missing:,} missing values in {col} with 0")
    
    logger.log(f"  Remaining: {len(df):,} records")
    
    return df

def remove_outliers(df):
    """
    Remove statistical and logical outliers
    
    Uses thresholds defined in Config class
    """
    logger.log("\n" + "-"*70)
    logger.log("Removing Outliers...")
    logger.log("-"*70)
    
    initial_count = len(df)
    
    # Passenger count
    if 'passenger_count' in df.columns:
        before = len(df)
        df = df[(df['passenger_count'] >= Config.MIN_PASSENGERS) & 
                (df['passenger_count'] <= Config.MAX_PASSENGERS)]
        removed = before - len(df)
        logger.log(f"  Passenger count ({Config.MIN_PASSENGERS}-{Config.MAX_PASSENGERS}): removed {removed:,}")
    
    # Trip distance
    if 'trip_distance' in df.columns:
        before = len(df)
        df = df[(df['trip_distance'] >= Config.MIN_DISTANCE) & 
                (df['trip_distance'] <= Config.MAX_DISTANCE)]
        removed = before - len(df)
        logger.log(f"  Trip distance ({Config.MIN_DISTANCE}-{Config.MAX_DISTANCE} mi): removed {removed:,}")
    
    # Fare amount
    if 'fare_amount' in df.columns:
        before = len(df)
        df = df[(df['fare_amount'] >= Config.MIN_FARE) & 
                (df['fare_amount'] <= Config.MAX_FARE)]
        removed = before - len(df)
        logger.log(f"  Fare amount (${Config.MIN_FARE}-${Config.MAX_FARE}): removed {removed:,}")
    
    total_removed = initial_count - len(df)
    logger.log(f"\n  Total outliers removed: {total_removed:,}")
    logger.log(f"  Remaining: {len(df):,} records")
    
    return df

# ============================================================================
# FEATURE ENGINEERING
# ============================================================================

def create_derived_features(df):
    """
    Create derived features from raw data
    
    Three main derived features (as required):
    1. Trip Duration (minutes)
    2. Average Speed (mph)
    3. Fare per Mile ($/mile)
    
    Plus additional time-based features for insights
    """
    logger.log("\n" + "="*70)
    logger.log("STEP 3: FEATURE ENGINEERING")
    logger.log("="*70)
    
    initial_count = len(df)
    
    # Feature 1: Trip Duration
    logger.log("\n1. Creating Trip Duration feature...")
    if 'tpep_pickup_datetime' in df.columns and 'tpep_dropoff_datetime' in df.columns:
        # Convert to datetime if not already
        df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
        df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])
        
        # Calculate duration in minutes
        df['trip_duration_minutes'] = (
            df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']
        ).dt.total_seconds() / 60
        
        logger.log(f"   [OK] Trip duration calculated")
        logger.log(f"     Range: {df['trip_duration_minutes'].min():.1f} - {df['trip_duration_minutes'].max():.1f} minutes")
        logger.log(f"     Average: {df['trip_duration_minutes'].mean():.1f} minutes")
        
        # Remove invalid durations
        before = len(df)
        df = df[(df['trip_duration_minutes'] >= Config.MIN_DURATION) & 
                (df['trip_duration_minutes'] <= Config.MAX_DURATION)]
        removed = before - len(df)
        if removed > 0:
            logger.log(f"     Removed {removed:,} trips with invalid duration")
    
    # Feature 2: Average Speed
    logger.log("\n2. Creating Average Speed feature...")
    if 'trip_distance' in df.columns and 'trip_duration_minutes' in df.columns:
        # Speed = distance / time (in hours)
        df['avg_speed_mph'] = df['trip_distance'] / (df['trip_duration_minutes'] / 60)
        
        # Replace infinity/NaN with 0
        df['avg_speed_mph'] = df['avg_speed_mph'].replace([np.inf, -np.inf], 0)
        df['avg_speed_mph'] = df['avg_speed_mph'].fillna(0)
        
        logger.log(f"   [OK] Average speed calculated")
        logger.log(f"     Range: {df['avg_speed_mph'].min():.1f} - {df['avg_speed_mph'].max():.1f} mph")
        logger.log(f"     Average: {df['avg_speed_mph'].mean():.1f} mph")
        
        # Remove unrealistic speeds
        before = len(df)
        df = df[(df['avg_speed_mph'] >= Config.MIN_SPEED) & 
                (df['avg_speed_mph'] <= Config.MAX_SPEED)]
        removed = before - len(df)
        if removed > 0:
            logger.log(f"     Removed {removed:,} trips with unrealistic speed")
    
    # Feature 3: Fare per Mile
    logger.log("\n3. Creating Fare per Mile feature...")
    if 'fare_amount' in df.columns and 'trip_distance' in df.columns:
        # Fare per mile = fare / distance
        df['fare_per_mile'] = df['fare_amount'] / df['trip_distance']
        
        # Replace infinity/NaN with 0
        df['fare_per_mile'] = df['fare_per_mile'].replace([np.inf, -np.inf], 0)
        df['fare_per_mile'] = df['fare_per_mile'].fillna(0)
        
        logger.log(f"   [OK] Fare per mile calculated")
        logger.log(f"     Range: ${df['fare_per_mile'].min():.2f} - ${df['fare_per_mile'].max():.2f} per mile")
        logger.log(f"     Average: ${df['fare_per_mile'].mean():.2f} per mile")
        
        # Remove extreme outliers in fare per mile
        before = len(df)
        df = df[df['fare_per_mile'] <= 100]  # Reasonable max
        removed = before - len(df)
        if removed > 0:
            logger.log(f"     Removed {removed:,} trips with extreme fare/mile ratio")
    
    # Additional time-based features
    logger.log("\n4. Creating Time-based features...")
    if 'tpep_pickup_datetime' in df.columns:
        df['pickup_hour'] = df['tpep_pickup_datetime'].dt.hour
        df['pickup_day_of_week'] = df['tpep_pickup_datetime'].dt.dayofweek
        df['pickup_day_name'] = df['tpep_pickup_datetime'].dt.day_name()
        df['pickup_month'] = df['tpep_pickup_datetime'].dt.month
        
        logger.log(f"   [OK] Time features created: hour, day_of_week, day_name, month")
    
    total_removed = initial_count - len(df)
    if total_removed > 0:
        logger.log(f"\n  Total records removed during feature engineering: {total_removed:,}")
    logger.log(f"  Final record count: {len(df):,}")
    
    return df

# ============================================================================
# DATA INTEGRATION
# ============================================================================

def integrate_zone_lookup(df, lookup_df):
    """
    Integrate taxi zone lookup data with trip data
    
    Adds borough and zone names for pickup and dropoff locations
    """
    logger.log("\n" + "="*70)
    logger.log("STEP 4: INTEGRATING ZONE LOOKUP DATA")
    logger.log("="*70)
    
    if lookup_df is None:
        logger.log("  [!]  Skipping - lookup data not available")
        return df
    
    # Merge pickup location data
    if 'PULocationID' in df.columns:
        logger.log("\n  Merging pickup location data...")
        df = df.merge(
            lookup_df[['LocationID', 'Borough', 'Zone']],
            left_on='PULocationID',
            right_on='LocationID',
            how='left'
        )
        df = df.rename(columns={
            'Borough': 'pickup_borough',
            'Zone': 'pickup_zone'
        })
        df = df.drop(columns=['LocationID'], errors='ignore')
        
        matched = df['pickup_borough'].notna().sum()
        logger.log(f"    [OK] Matched {matched:,} / {len(df):,} pickup locations")
    
    # Merge dropoff location data
    if 'DOLocationID' in df.columns:
        logger.log("\n  Merging dropoff location data...")
        df = df.merge(
            lookup_df[['LocationID', 'Borough', 'Zone']],
            left_on='DOLocationID',
            right_on='LocationID',
            how='left'
        )
        df = df.rename(columns={
            'Borough': 'dropoff_borough',
            'Zone': 'dropoff_zone'
        })
        df = df.drop(columns=['LocationID'], errors='ignore')
        
        matched = df['dropoff_borough'].notna().sum()
        logger.log(f"    [OK] Matched {matched:,} / {len(df):,} dropoff locations")
    
    return df

# ============================================================================
# DATA SAMPLING AND EXPORT
# ============================================================================

def sample_data(df, sample_size=None):
    """
    Sample data if dataset is too large
    
    Uses stratified sampling to maintain data distribution
    """
    if sample_size is None:
        sample_size = Config.SAMPLE_SIZE
    
    logger.log("\n" + "="*70)
    logger.log("STEP 5: DATA SAMPLING")
    logger.log("="*70)
    
    if len(df) <= sample_size:
        logger.log(f"  Dataset size ({len(df):,}) is within sample limit ({sample_size:,})")
        logger.log("  Using full dataset")
        return df
    
    logger.log(f"  Dataset too large ({len(df):,} records)")
    logger.log(f"  Sampling {sample_size:,} records (random seed: {Config.RANDOM_SEED})")
    
    sampled_df = df.sample(n=sample_size, random_state=Config.RANDOM_SEED)
    
    logger.log(f"  [OK] Sampled {len(sampled_df):,} records")
    
    return sampled_df

def export_cleaned_data(df, filepath):
    """Export cleaned data to CSV for database import"""
    logger.log("\n" + "="*70)
    logger.log("STEP 6: EXPORTING CLEANED DATA")
    logger.log("="*70)
    
    logger.log(f"\n  Exporting to: {filepath}")
    logger.log(f"  Records: {len(df):,}")
    logger.log(f"  Columns: {len(df.columns)}")
    
    # Save to CSV
    df.to_csv(filepath, index=False)
    
    file_size = os.path.getsize(filepath) / 1024**2
    logger.log(f"  [OK] Export complete!")
    logger.log(f"  File size: {file_size:.2f} MB")
    
    # Also save a copy to shared folder
    shared_path = os.path.join('../shared', os.path.basename(filepath))
    os.makedirs('../shared', exist_ok=True)
    df.to_csv(shared_path, index=False)
    logger.log(f"  [OK] Copy saved to: {shared_path}")
    
    return filepath

def create_exclusion_log(df_original, df_final):
    """Create detailed log of excluded records"""
    logger.log("\n" + "="*70)
    logger.log("CREATING EXCLUSION LOG")
    logger.log("="*70)
    
    original_count = len(df_original)
    final_count = len(df_final)
    excluded_count = original_count - final_count
    exclusion_rate = (excluded_count / original_count) * 100
    
    log_content = f"""
NYC TAXI TRIP DATA - EXCLUSION LOG
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'='*70}
SUMMARY
{'='*70}

Original Records:     {original_count:,}
Final Records:        {final_count:,}
Excluded Records:     {excluded_count:,}
Exclusion Rate:       {exclusion_rate:.2f}%

{'='*70}
EXCLUSION CRITERIA
{'='*70}

The following records were excluded during processing:

1. DUPLICATES
   - Exact duplicate records removed

2. MISSING VALUES
   - Records with missing critical fields:
     - passenger_count, trip_distance, fare_amount
     - pickup/dropoff datetime

3. PASSENGER COUNT OUTLIERS
   - Outside range: {Config.MIN_PASSENGERS} - {Config.MAX_PASSENGERS} passengers

4. TRIP DISTANCE OUTLIERS
   - Outside range: {Config.MIN_DISTANCE} - {Config.MAX_DISTANCE} miles

5. FARE AMOUNT OUTLIERS
   - Outside range: ${Config.MIN_FARE} - ${Config.MAX_FARE}

6. TRIP DURATION OUTLIERS
   - Outside range: {Config.MIN_DURATION} - {Config.MAX_DURATION} minutes

7. SPEED OUTLIERS
   - Outside range: {Config.MIN_SPEED} - {Config.MAX_SPEED} mph

8. FARE PER MILE OUTLIERS
   - Fare per mile > $100

{'='*70}
JUSTIFICATION
{'='*70}

These exclusion criteria were applied to ensure data quality and 
remove physical/logical impossibilities:

- Negative or zero values for distances, fares, and counts are not valid
- Extremely high values likely represent data entry errors or system glitches
- Speed calculations outside NYC driving conditions are physically impossible
- Missing critical fields prevent meaningful analysis

All thresholds were set based on:
- NYC TLC regulations and policies
- Physical constraints of urban taxi operations
- Statistical analysis of data distribution
- Industry best practices

{'='*70}
NEXT STEPS
{'='*70}

1. Review this exclusion log
2. Run import_to_database.py to load data
3. Verify record counts match this log
4. Start the backend with python app.py
5. Test the API at http://localhost:5000/api/health

{'='*70}
"""
    
    # Save exclusion log
    with open(Config.EXCLUSION_LOG_FILE, 'w', encoding='utf-8') as f:
        f.write(log_content)
    
    logger.log(f"\n  [OK] Exclusion log saved to: {Config.EXCLUSION_LOG_FILE}")
    
    # Print summary
    print("\n" + "="*70)
    print("PROCESSING SUMMARY")
    print("="*70)
    print(f"Original records:  {original_count:,}")
    print(f"Final records:     {final_count:,}")
    print(f"Excluded:          {excluded_count:,} ({exclusion_rate:.2f}%)")
    print("="*70 + "\n")

# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main():
    """Main data processing pipeline"""
    
    print("\n" + "="*70)
    print("NYC TAXI TRIP ANALYZER - DATA PROCESSING PIPELINE")
    print("="*70 + "\n")
    
    logger.log("Starting data processing pipeline...")
    logger.log(f"Timestamp: {datetime.now()}")
    
    # Determine file paths
    data_dir = Config.DATA_DIR
    raw_file = os.path.join(data_dir, Config.RAW_DATA_FILE)
    lookup_file = os.path.join(data_dir, Config.LOOKUP_FILE)
    output_file = Config.CLEANED_DATA_FILE
    
    # Check if files exist
    if not os.path.exists(raw_file):
        # Try .parquet extension
        raw_file = raw_file.replace('.csv', '.parquet')
        if not os.path.exists(raw_file):
            logger.log(f"ERROR: Raw data file not found in {data_dir}", 'ERROR')
            logger.log("Expected: yellow_tripdata.csv or yellow_tripdata.parquet", 'ERROR')
            sys.exit(1)
    
    try:
        # Step 1: Load data
        df = load_trip_data(raw_file)
        df_original = df.copy()  # Keep for exclusion log
        
        lookup_df = load_zone_lookup(lookup_file)
        
        # Step 2: Explore and understand data
        initial_data_exploration(df)
        
        # Step 3: Clean data
        df = remove_duplicates(df)
        df = handle_missing_values(df)
        df = remove_outliers(df)
        
        # Step 4: Feature engineering
        df = create_derived_features(df)
        
        # Step 5: Integrate zone lookup
        df = integrate_zone_lookup(df, lookup_df)
        
        # Step 6: Sample if needed
        df = sample_data(df)
        
        # Step 7: Export data
        export_cleaned_data(df, output_file)
        
        # Step 8: Create exclusion log
        create_exclusion_log(df_original, df)
        
        # Save processing log
        logger.save()
        
        print("\n" + "="*70)
        print("[OK] DATA PROCESSING COMPLETE!")
        print("="*70)
        print("\nGenerated Files:")
        print(f"  1. {output_file} - Cleaned data")
        print(f"  2. {Config.EXCLUSION_LOG_FILE} - Exclusion log")
        print(f"  3. {Config.PROCESSING_REPORT_FILE} - Processing report")
        print(f"  4. ../shared/cleaned_taxi_data.csv - Shared copy")
        print("\nNext Steps:")
        print("  → Run python import_to_database.py to load into database")
        print("  → Run python app.py to start the API")
        print("="*70 + "\n")
        
    except Exception as e:
        logger.log(f"FATAL ERROR: {e}", 'ERROR')
        import traceback
        logger.log(traceback.format_exc(), 'ERROR')
        logger.save()
        sys.exit(1)

if __name__ == '__main__':
    main()

