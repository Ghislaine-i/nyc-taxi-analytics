"""
NYC Taxi Trip Analyzer - Flask Backend API
A - Backend Service

This Flask application provides REST API endpoints for:
- Trip data retrieval with filtering
- Statistical insights and aggregations
- Hourly and daily patterns
- Location-based analytics
- Summary statistics
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from sqlalchemy import create_engine, text
import os
from config import Config

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for frontend

print("\n" + "="*70)
print("NYC TAXI TRIP ANALYZER - BACKEND API")
print("="*70)

# ============================================================================
# DATABASE CONNECTION
# ============================================================================

print("\n[DATABASE] Initializing connection...")
print(f"   Database URL: {Config.DATABASE_URL}")

try:
    engine = create_engine(Config.DATABASE_URL)
    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        result.fetchone()
    print("   [OK] Database connection successful!")
    db_connected = True
except Exception as e:
    print(f"   [WARNING] Database connection failed: {e}")
    print("   [INFO] API will run but database queries will fail")
    print("   [INFO] To fix this:")
    print("       1. Run python import_to_database.py")
    print("       2. Update config.py with the connection string")
    print("       3. Restart the server")
    engine = None
    db_connected = False

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def execute_query(query, params=None):
    """Execute SQL query and return results as JSON"""
    if not engine:
        return None, "Database not connected"
    
    try:
        df = pd.read_sql(query, engine, params=params)
        # Replace NaN with None for valid JSON
        df = df.where(pd.notnull(df), None)
        return df, None
    except Exception as e:
        return None, str(e)

def success_response(data, count=None):
    """Standard success response format"""
    # Handle NaN values in data (replace with None for valid JSON)
    import math
    
    def clean_nan(obj):
        if isinstance(obj, dict):
            return {k: clean_nan(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_nan(item) for item in obj]
        elif isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
            return None
        return obj
    
    cleaned_data = clean_nan(data)
    response = {"success": True, "data": cleaned_data}
    if count is not None:
        response["count"] = count
    return jsonify(response)

def error_response(message, code=500):
    """Standard error response format"""
    return jsonify({
        "success": False,
        "error": message
    }), code

# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Check if API is running and database is connected
    
    Returns:
        JSON with API status and database connection status
    """
    return jsonify({
        "success": True,
        "message": "NYC Taxi Trip Analyzer API is running",
        "database": "connected" if db_connected else "disconnected",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "trips": "/api/trips",
            "daily_trips": "/api/insights/daily_trips",
            "hourly_pattern": "/api/insights/hourly_pattern",
            "top_locations": "/api/insights/top_locations",
            "borough_stats": "/api/insights/borough_stats",
            "fare_distribution": "/api/insights/fare_distribution",
            "summary": "/api/stats/summary"
        }
    })

@app.route('/api/test', methods=['GET'])
def test_database():
    """Test database connection with a simple query"""
    if not engine:
        return error_response("Database not connected", 500)
    
    query = "SELECT COUNT(*) as total FROM trips"
    df, error = execute_query(query)
    
    if error:
        return error_response(f"Database query failed: {error}", 500)
    
    return success_response({
        "message": "Database connection working",
        "total_trips": int(df['total'].iloc[0])
    })

# ============================================================================
# DATA RETRIEVAL ENDPOINTS
# ============================================================================

@app.route('/api/trips', methods=['GET'])
def get_trips():
    """
    Get trip records with optional filtering
    
    Query Parameters:
        limit (int): Number of records to return (default: 100, max: 1000)
        borough (str): Filter by pickup borough
        min_fare (float): Minimum fare amount
        max_fare (float): Maximum fare amount
        min_distance (float): Minimum trip distance
        max_distance (float): Maximum trip distance
        date (str): Filter by pickup date (YYYY-MM-DD)
        
    Examples:
        /api/trips?limit=50
        /api/trips?borough=Manhattan&limit=100
        /api/trips?min_fare=10&max_fare=50
    """
    if not engine:
        return error_response("Database not connected", 500)
    
    # Get and validate query parameters
    limit = min(request.args.get('limit', 100, type=int), 1000)
    borough = request.args.get('borough')
    min_fare = request.args.get('min_fare', type=float)
    max_fare = request.args.get('max_fare', type=float)
    min_distance = request.args.get('min_distance', type=float)
    max_distance = request.args.get('max_distance', type=float)
    date = request.args.get('date')
    
    # Build query with filters
    conditions = ["1=1"]
    
    if borough:
        conditions.append(f"pickup_borough = '{borough}'")
    if min_fare:
        conditions.append(f"fare_amount >= {min_fare}")
    if max_fare:
        conditions.append(f"fare_amount <= {max_fare}")
    if min_distance:
        conditions.append(f"trip_distance >= {min_distance}")
    if max_distance:
        conditions.append(f"trip_distance <= {max_distance}")
    if date:
        conditions.append(f"DATE(tpep_pickup_datetime) = '{date}'")
    
    where_clause = " AND ".join(conditions)
    query = f"""
    SELECT 
        tpep_pickup_datetime,
        tpep_dropoff_datetime,
        passenger_count,
        trip_distance,
        fare_amount,
        tip_amount,
        total_amount,
        pickup_borough,
        pickup_zone,
        dropoff_borough,
        dropoff_zone,
        trip_duration_minutes,
        avg_speed_mph,
        fare_per_mile
    FROM trips
    WHERE {where_clause}
    ORDER BY tpep_pickup_datetime DESC
    LIMIT {limit}
    """
    
    df, error = execute_query(query)
    
    if error:
        return error_response(f"Query failed: {error}", 500)
    
    return success_response(df.to_dict('records'), count=len(df))

# ============================================================================
# INSIGHT ENDPOINTS - TEMPORAL PATTERNS
# ============================================================================

@app.route('/api/insights/daily_trips', methods=['GET'])
def daily_trips():
    """
    Get aggregated trip data by day
    
    Returns daily counts, averages for fare, distance, duration
    """
    if not engine:
        return error_response("Database not connected", 500)
    
    limit = request.args.get('limit', 30, type=int)
    
    query = f"""
    SELECT 
        DATE(tpep_pickup_datetime) as date,
        COUNT(*) as trip_count,
        AVG(fare_amount) as avg_fare,
        AVG(trip_distance) as avg_distance,
        AVG(trip_duration_minutes) as avg_duration,
        AVG(avg_speed_mph) as avg_speed
    FROM trips
    GROUP BY DATE(tpep_pickup_datetime)
    ORDER BY date DESC
    LIMIT {limit}
    """
    
    df, error = execute_query(query)
    
    if error:
        return error_response(f"Query failed: {error}", 500)
    
    # Round numeric values
    for col in ['avg_fare', 'avg_distance', 'avg_duration', 'avg_speed']:
        if col in df.columns:
            df[col] = df[col].round(2)
    
    return success_response(df.to_dict('records'))

@app.route('/api/insights/hourly_pattern', methods=['GET'])
def hourly_pattern():
    """
    Get trip patterns by hour of day (0-23)
    
    Shows how trip count, distance, speed, and fare vary by hour
    """
    if not engine:
        return error_response("Database not connected", 500)
    
    query = """
    SELECT 
        pickup_hour as hour,
        COUNT(*) as trip_count,
        AVG(trip_distance) as avg_distance,
        AVG(avg_speed_mph) as avg_speed,
        AVG(fare_amount) as avg_fare,
        AVG(trip_duration_minutes) as avg_duration
    FROM trips
    GROUP BY pickup_hour
    ORDER BY hour
    """
    
    df, error = execute_query(query)
    
    if error:
        return error_response(f"Query failed: {error}", 500)
    
    # Convert hour to int and round averages
    df['hour'] = df['hour'].astype(int)
    for col in ['avg_distance', 'avg_speed', 'avg_fare', 'avg_duration']:
        if col in df.columns:
            df[col] = df[col].round(2)
    
    return success_response(df.to_dict('records'))

@app.route('/api/insights/day_of_week', methods=['GET'])
def day_of_week_pattern():
    """
    Get trip patterns by day of week
    
    Shows how trips vary from Monday to Sunday
    """
    if not engine:
        return error_response("Database not connected", 500)
    
    query = """
    SELECT 
        pickup_day_name as day_name,
        pickup_day_of_week as day_number,
        COUNT(*) as trip_count,
        AVG(fare_amount) as avg_fare,
        AVG(trip_distance) as avg_distance,
        AVG(avg_speed_mph) as avg_speed
    FROM trips
    GROUP BY pickup_day_name, pickup_day_of_week
    ORDER BY day_number
    """
    
    df, error = execute_query(query)
    
    if error:
        return error_response(f"Query failed: {error}", 500)
    
    # Round numeric values
    for col in ['avg_fare', 'avg_distance', 'avg_speed']:
        if col in df.columns:
            df[col] = df[col].round(2)
    
    return success_response(df.to_dict('records'))

# ============================================================================
# INSIGHT ENDPOINTS - LOCATION-BASED
# ============================================================================

@app.route('/api/insights/top_locations', methods=['GET'])
def top_locations():
    """
    Get top pickup locations by trip count
    
    Query Parameters:
        limit (int): Number of locations to return (default: 10)
        type (str): 'pickup' or 'dropoff' (default: 'pickup')
    """
    if not engine:
        return error_response("Database not connected", 500)
    
    limit = request.args.get('limit', 10, type=int)
    location_type = request.args.get('type', 'pickup')
    
    if location_type == 'dropoff':
        zone_col = 'dropoff_zone'
        borough_col = 'dropoff_borough'
    else:
        zone_col = 'pickup_zone'
        borough_col = 'pickup_borough'
    
    query = f"""
    SELECT 
        {zone_col} as zone,
        {borough_col} as borough,
        COUNT(*) as trip_count,
        AVG(fare_amount) as avg_fare,
        AVG(trip_distance) as avg_distance,
        AVG(trip_duration_minutes) as avg_duration
    FROM trips
    WHERE {zone_col} IS NOT NULL
    GROUP BY {zone_col}, {borough_col}
    ORDER BY trip_count DESC
    LIMIT {limit}
    """
    
    df, error = execute_query(query)
    
    if error:
        return error_response(f"Query failed: {error}", 500)
    
    # Round numeric values
    for col in ['avg_fare', 'avg_distance', 'avg_duration']:
        if col in df.columns:
            df[col] = df[col].round(2)
    
    return success_response(df.to_dict('records'))

@app.route('/api/insights/borough_stats', methods=['GET'])
def borough_stats():
    """
    Get comprehensive statistics by borough
    
    Returns trip counts and averages for each NYC borough
    """
    if not engine:
        return error_response("Database not connected", 500)
    
    query = """
    SELECT 
        pickup_borough as borough,
        COUNT(*) as trip_count,
        AVG(fare_amount) as avg_fare,
        AVG(trip_distance) as avg_distance,
        AVG(avg_speed_mph) as avg_speed,
        AVG(trip_duration_minutes) as avg_duration,
        AVG(fare_per_mile) as avg_fare_per_mile,
        AVG(passenger_count) as avg_passengers,
        SUM(fare_amount) as total_revenue
    FROM trips
    WHERE pickup_borough IS NOT NULL
    GROUP BY pickup_borough
    ORDER BY trip_count DESC
    """
    
    df, error = execute_query(query)
    
    if error:
        return error_response(f"Query failed: {error}", 500)
    
    # Round numeric values
    numeric_cols = ['avg_fare', 'avg_distance', 'avg_speed', 'avg_duration', 
                   'avg_fare_per_mile', 'avg_passengers', 'total_revenue']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].round(2)
    
    return success_response(df.to_dict('records'))

# ============================================================================
# INSIGHT ENDPOINTS - DISTRIBUTIONS
# ============================================================================

@app.route('/api/insights/fare_distribution', methods=['GET'])
def fare_distribution():
    """
    Get distribution of fares in predefined buckets
    
    Returns trip counts for different fare ranges
    """
    if not engine:
        return error_response("Database not connected", 500)
    
    query = """
    SELECT 
        CASE 
            WHEN fare_amount < 10 THEN '$0-10'
            WHEN fare_amount < 20 THEN '$10-20'
            WHEN fare_amount < 30 THEN '$20-30'
            WHEN fare_amount < 50 THEN '$30-50'
            WHEN fare_amount < 100 THEN '$50-100'
            ELSE '$100+'
        END as fare_range,
        COUNT(*) as trip_count,
        AVG(trip_distance) as avg_distance,
        AVG(trip_duration_minutes) as avg_duration
    FROM trips
    GROUP BY fare_range
    ORDER BY 
        CASE fare_range
            WHEN '$0-10' THEN 1
            WHEN '$10-20' THEN 2
            WHEN '$20-30' THEN 3
            WHEN '$30-50' THEN 4
            WHEN '$50-100' THEN 5
            ELSE 6
        END
    """
    
    df, error = execute_query(query)
    
    if error:
        return error_response(f"Query failed: {error}", 500)
    
    # Round numeric values
    for col in ['avg_distance', 'avg_duration']:
        if col in df.columns:
            df[col] = df[col].round(2)
    
    return success_response(df.to_dict('records'))

@app.route('/api/insights/distance_distribution', methods=['GET'])
def distance_distribution():
    """
    Get distribution of trip distances
    """
    if not engine:
        return error_response("Database not connected", 500)
    
    query = """
    SELECT 
        CASE 
            WHEN trip_distance < 1 THEN '< 1 mile'
            WHEN trip_distance < 3 THEN '1-3 miles'
            WHEN trip_distance < 5 THEN '3-5 miles'
            WHEN trip_distance < 10 THEN '5-10 miles'
            ELSE '10+ miles'
        END as distance_range,
        COUNT(*) as trip_count,
        AVG(fare_amount) as avg_fare,
        AVG(trip_duration_minutes) as avg_duration
    FROM trips
    GROUP BY distance_range
    ORDER BY 
        CASE distance_range
            WHEN '< 1 mile' THEN 1
            WHEN '1-3 miles' THEN 2
            WHEN '3-5 miles' THEN 3
            WHEN '5-10 miles' THEN 4
            ELSE 5
        END
    """
    
    df, error = execute_query(query)
    
    if error:
        return error_response(f"Query failed: {error}", 500)
    
    # Round numeric values
    for col in ['avg_fare', 'avg_duration']:
        if col in df.columns:
            df[col] = df[col].round(2)
    
    return success_response(df.to_dict('records'))

# ============================================================================
# SUMMARY STATISTICS ENDPOINT
# ============================================================================

@app.route('/api/stats/summary', methods=['GET'])
def summary_stats():
    """
    Get overall summary statistics for the entire dataset
    
    Returns total trips, revenue, and various averages
    """
    if not engine:
        return error_response("Database not connected", 500)
    
    query = """
    SELECT 
        COUNT(*) as total_trips,
        SUM(fare_amount) as total_revenue,
        AVG(fare_amount) as avg_fare,
        AVG(trip_distance) as avg_distance,
        AVG(trip_duration_minutes) as avg_duration,
        AVG(passenger_count) as avg_passengers,
        AVG(avg_speed_mph) as avg_speed,
        AVG(fare_per_mile) as avg_fare_per_mile,
        MAX(fare_amount) as max_fare,
        MAX(trip_distance) as max_distance,
        MIN(tpep_pickup_datetime) as earliest_trip,
        MAX(tpep_pickup_datetime) as latest_trip
    FROM trips
    """
    
    df, error = execute_query(query)
    
    if error:
        return error_response(f"Query failed: {error}", 500)
    
    # Convert to dictionary and round numeric values
    stats = df.to_dict('records')[0]
    
    # Round numeric fields
    numeric_fields = ['total_revenue', 'avg_fare', 'avg_distance', 'avg_duration',
                     'avg_passengers', 'avg_speed', 'avg_fare_per_mile', 
                     'max_fare', 'max_distance']
    
    for field in numeric_fields:
        if field in stats and stats[field] is not None:
            stats[field] = round(float(stats[field]), 2)
    
    # Convert timestamps to strings
    if stats.get('earliest_trip'):
        stats['earliest_trip'] = str(stats['earliest_trip'])
    if stats.get('latest_trip'):
        stats['latest_trip'] = str(stats['latest_trip'])
    
    return success_response(stats)

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return error_response("Endpoint not found", 404)

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return error_response("Internal server error", 500)

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return error_response("Method not allowed", 405)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

if __name__ == '__main__':
    print("\n" + "-"*70)
    print("AVAILABLE ENDPOINTS:")
    print("-"*70)
    print("\nHealth & Testing:")
    print("  GET  /api/health                       - API health check")
    print("  GET  /api/test                         - Database connection test")
    
    print("\nData Retrieval:")
    print("  GET  /api/trips                        - Get trip records (with filters)")
    
    print("\nTemporal Insights:")
    print("  GET  /api/insights/daily_trips         - Daily aggregations")
    print("  GET  /api/insights/hourly_pattern      - Hourly patterns")
    print("  GET  /api/insights/day_of_week         - Day of week patterns")
    
    print("\nLocation Insights:")
    print("  GET  /api/insights/top_locations       - Top pickup/dropoff zones")
    print("  GET  /api/insights/borough_stats       - Statistics by borough")
    
    print("\nDistributions:")
    print("  GET  /api/insights/fare_distribution   - Fare amount distribution")
    print("  GET  /api/insights/distance_distribution - Distance distribution")
    
    print("\nStatistics:")
    print("  GET  /api/stats/summary                - Overall summary stats")
    
    print("\n" + "-"*70)
    print(f"Starting server on http://{Config.API_HOST}:{Config.API_PORT}")
    print("Press CTRL+C to stop")
    print("="*70 + "\n")
    
    app.run(
        debug=Config.DEBUG,
        host=Config.API_HOST,
        port=Config.API_PORT
    )