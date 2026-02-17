"""
Quick Test Script - Import sample data to SQLite for testing
"""
import pandas as pd
from sqlalchemy import create_engine

print("Importing data to SQLite for testing...")

# Read cleaned data
df = pd.read_csv('cleaned_taxi_data.csv')
print(f"Loaded {len(df)} records")

# Convert datetime columns
df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])

# Create SQLite database
engine = create_engine('sqlite:///taxi_db.sqlite')

# Import to database
df.to_sql('trips', engine, if_exists='replace', index=False)

print(f"SUCCESS: Imported {len(df)} records into taxi_db.sqlite")
print("You can now test your API!")
