# NYC Taxi Trip Analyzer — Technical Report

## Team: [Your Team Name]
## Members: Member A (Backend & Data Processing), Member B (Database & Schema), Member C (Frontend & Documentation)

---

## 1. Problem Framing and Dataset Analysis

### Dataset Overview

The dataset used in this project is sourced from the New York City Taxi and Limousine Commission (TLC). It is composed of three components:

- **yellow_tripdata** (Fact Table): Raw trip-level records spanning timestamps, distances, fare breakdowns, passenger counts, and rate codes. The raw file contained 7,667,792 records across 18 columns.
- **taxi_zone_lookup** (Dimension Table): Maps PULocationID and DOLocationID integers to 265 named boroughs and service zones.
- **taxi_zones** (Spatial Metadata): GeoJSON boundaries corresponding to each taxi zone ID.

The dataset represents real-world urban mobility patterns from yellow cab trips within New York City, providing a rich basis for temporal, geographic, and economic analysis.

### Data Challenges Identified

Several data quality issues were identified during the initial exploration phase:

| Issue | Detail | Resolution |
|---|---|---|
| Missing values | `congestion_surcharge` was null in 63.33% of rows (4,855,978 records) | Filled with 0, as absence indicates the surcharge was not applied |
| Zero-distance trips | Trip distance of 0.0 miles found in dataset | Excluded — physically invalid for a completed trip |
| Negative fares | Some fare_amount values were negative or below the NYC minimum | Excluded (threshold: $2.50–$500) |
| Invalid passenger counts | Entries with 0 or more than 6 passengers | Excluded (threshold: 1–6 passengers) |
| Logically impossible speeds | Calculated avg_speed_mph reached up to 2,682 mph after initial feature engineering | Records above 80 mph excluded |
| Timestamp anomalies | Some dropoff times preceded pickup times, yielding negative durations | 38,713 records with duration outside 1–180 minutes excluded |

### Assumptions Made During Cleaning

1. Trips with `congestion_surcharge = NULL` are treated as trips where the surcharge was not applied (value set to 0), not missing data.
2. A maximum trip distance of 100 miles is a reasonable bound for NYC taxi operations.
3. A maximum fare of $500 covers airport flat rates and long-distance rides without including clear data entry errors.
4. The sample of 50,000 records drawn with a fixed random seed (42) is representative of the full 7.4 million cleaned records.

### Unexpected Observation

During feature engineering, the raw average speed across the dataset was 11.7 mph — substantially lower than highway speed. This reflects the reality of dense Manhattan traffic and short-haul trips within congested city blocks. This finding influenced the dashboard design: rather than treating speed as a secondary metric, we made it a primary KPI card and overlaid it on the hourly trip count chart to surface the clear inverse relationship between peak-hour demand and travel speed.

---

## 2. System Architecture and Design Decisions

### Architecture Diagram

```
Raw Data (CSV / Parquet)
        |
        v
[ Data Processing — Member A ]
  data_processing.py
  - Load 7,667,792 records
  - Clean, filter, normalise
  - Engineer 3 derived features
  - Sample 50,000 records
  - Export: cleaned_taxi_data.csv
        |
        v
[ Relational Database — Member B ]
  SQLite (taxi_db.sqlite)
  - locations table (265 zones)
  - trips table (50,000 records)
  - Indexes on datetime and location columns
        |
        v
[ REST API Backend — Member A ]
  Flask (app.py) — http://localhost:5000
  11 endpoints: /trips, /insights/*, /stats/summary
  CORS-enabled, JSON responses
        |
        v
[ Frontend Dashboard — Member C ]
  HTML + CSS + JavaScript (Chart.js)
  7 chart types, 6 KPI cards, data table
  Filter by borough, fare range, date
```

### Technology Stack Justification

| Layer | Technology | Reason |
|---|---|---|
| Backend | Python / Flask | Lightweight, readable, integrates well with Pandas and SQLAlchemy for data-heavy workloads |
| Database | SQLite (via SQLAlchemy) | Zero-configuration setup, suitable for a contained academic project; schema is compatible with a PostgreSQL migration |
| Frontend | HTML / CSS / JavaScript | No build tools required — runs directly in any browser from `index.html` |
| Charts | Chart.js | Browser-native, no server rendering needed, wide chart type support |
| Data processing | Pandas / NumPy / PyArrow | Industry standard for tabular data manipulation in Python |

### Trade-offs

- **SQLite vs PostgreSQL**: SQLite was chosen for ease of setup during the sprint. PostgreSQL is configured as the primary option in `config.py` and can replace SQLite by updating `DATABASE_URL`.
- **Sampling**: The full cleaned dataset of 7.4 million records was sampled to 50,000 to keep server response times fast without sacrificing analytical representativeness.
- **No authentication on the API**: Acceptable for a local academic project. A production version would require token-based auth.

---

## 3. Algorithmic Logic and Data Structures

### Custom Algorithm: Trip Anomaly Detection

To address the requirement of implementing a custom algorithm without relying on library functions such as `heapq`, `Counter`, or built-in sort methods, we implemented a manual anomaly detection routine that identifies trips with statistically unusual fare amounts and distances.

#### Problem Being Solved

The cleaned dataset still contains edge cases where a trip may have a fare amount that is disproportionate to its distance — for example, a 0.5-mile trip costing $90. These anomalies skew aggregate statistics. The algorithm flags these for inspection without removing them from the database.

#### Implementation

```python
def detect_anomalies(trips_data):
    """
    Custom anomaly detection for NYC taxi trips.
    Identifies trips where fare or distance deviates significantly from the mean.

    No use of: heapq, Counter, sort_values, statistics.stdev, or similar.

    Time complexity:  O(n) — two passes through the data
    Space complexity: O(n) — anomaly list may grow to size n in worst case
    """
    n = len(trips_data)
    if n == 0:
        return []

    # Pass 1: compute means manually
    total_fare     = 0.0
    total_distance = 0.0
    for trip in trips_data:
        total_fare     += trip['fare_amount']
        total_distance += trip['trip_distance']

    mean_fare     = total_fare     / n
    mean_distance = total_distance / n

    # Pass 2: compute variance manually
    var_fare     = 0.0
    var_distance = 0.0
    for trip in trips_data:
        var_fare     += (trip['fare_amount']   - mean_fare)     ** 2
        var_distance += (trip['trip_distance'] - mean_distance) ** 2

    std_fare     = (var_fare     / n) ** 0.5
    std_distance = (var_distance / n) ** 0.5

    # Pass 3: flag trips more than 3 standard deviations from the mean
    anomalies = []
    for trip in trips_data:
        fare_z     = abs(trip['fare_amount']   - mean_fare)     / (std_fare     or 1)
        distance_z = abs(trip['trip_distance'] - mean_distance) / (std_distance or 1)
        if fare_z > 3.0 or distance_z > 3.0:
            anomalies.append(trip)

    return anomalies
```

#### Pseudo-code

```
FUNCTION detect_anomalies(trips):
    n = length of trips
    
    sum_fare = 0, sum_dist = 0
    FOR each trip IN trips:
        sum_fare += trip.fare_amount
        sum_dist += trip.trip_distance
    mean_fare = sum_fare / n
    mean_dist = sum_dist / n

    var_fare = 0, var_dist = 0
    FOR each trip IN trips:
        var_fare += (trip.fare_amount - mean_fare)^2
        var_dist += (trip.trip_distance - mean_dist)^2
    std_fare = sqrt(var_fare / n)
    std_dist = sqrt(var_dist / n)

    anomalies = []
    FOR each trip IN trips:
        z_fare = |trip.fare_amount - mean_fare| / std_fare
        z_dist = |trip.trip_distance - mean_dist| / std_dist
        IF z_fare > 3 OR z_dist > 3:
            anomalies.append(trip)

    RETURN anomalies
```

#### Complexity Analysis

| Measure | Value | Explanation |
|---|---|---|
| Time complexity | O(n) | Three linear passes: means, variance, z-score flagging |
| Space complexity | O(n) | In the worst case (all trips are anomalies), the output list is size n |

---

## 4. Insights and Interpretation

### Insight 1 — Peak Demand Occurs at 6 PM, Traffic is Slowest at 8 AM

**Derivation**: Via the `/api/insights/hourly_pattern` endpoint, which returns `trip_count` and `avg_speed` grouped by hour of day (0–23).

**Observation**: Trip volume peaks between 17:00 and 19:00. Morning rush (08:00) shows the lowest average travel speed (approximately 11–12 mph) despite moderate trip counts, indicating heavy congestion. Late-night hours (01:00–04:00) have the highest average speeds (25+ mph) due to light traffic.

**Urban mobility interpretation**: Taxi supply peaks around evening commute hours when demand is highest. The morning commute, while less reliant on taxis, creates the worst travel conditions — useful information for dynamic pricing or route optimisation systems.

**Chart**: Trip Volume by Hour of Day (bar + speed overlay) — see dashboard.

---

### Insight 2 — Manhattan Accounts for over 65% of All Pickups

**Derivation**: Via the `/api/insights/borough_stats` endpoint, which returns trip counts and revenue aggregated by pickup borough.

**Observation**: Manhattan dominates trip volume (~65–70% of pickups), followed by Queens (~19%), Brooklyn (~10%), Bronx (~4%), and Staten Island (~1%). Despite fewer trips, outer-borough rides tend to have higher fares per trip, particularly Queens (which includes JFK Airport).

**Urban mobility interpretation**: Yellow cab demand is concentrated in the Manhattan core. Outer boroughs are underserved relative to demand — a pattern consistent with TLC's own published findings. This justifies the city's expansion of Boro Taxis and rideshare services in these areas.

**Chart**: Trips by Borough (doughnut), Borough Comparison — Avg Fare, Distance, Speed (grouped bar) — see dashboard.

---

### Insight 3 — Short Trips (1–3 miles) Are the Most Common but Have the Worst Fare-per-Mile Efficiency

**Derivation**: Cross-referencing the `/api/insights/distance_distribution` and `/api/insights/fare_distribution` endpoints, combined with the derived `fare_per_mile` feature engineered by Member A.

**Observation**: The 1–3 mile distance bucket contains the largest share of trips (~42%). These trips also show the highest `avg_fare_per_mile` (typically $6–$8/mile), compared to longer trips where the per-mile rate drops closer to $3–$4/mile. This is partly because the NYC base fare ($3.00) and MTA tax ($0.50) are applied regardless of distance.

**Urban mobility interpretation**: Very short urban trips are economically inefficient from a passenger perspective. Riders on 1–3 mile routes pay a disproportionate fare compared to the distance travelled. This reflects the fixed-cost structure of NYC metered fares and suggests that short-trip riders subsidise the economics of longer journeys.

**Chart**: Distance Distribution (polar area) and Fare Distribution (bar) — see dashboard.

---

## 5. Reflection and Future Work

### Technical Challenges

- **Dataset scale**: The original CSV file (7,667,792 records, ~1.3 GB in memory) required careful memory management during processing. Reading the full file into memory before sampling was the primary bottleneck; future work could use chunked reading or Dask.
- **SQLite limitations**: SQLite performs well for read-only queries but does not support concurrent writes or advanced geospatial indexing. Migrating to PostgreSQL + PostGIS would unlock spatial joins on the GeoJSON zone boundaries.
- **No real-time data**: The current system queries a static snapshot. Connecting to the TLC's live SODA API feed would allow near-real-time monitoring.

### Team Challenges

- Coordination across three independent workstreams required careful handoff documentation. Member A produced detailed API documentation (`shared/FOR_MEMBER_C_FRONTEND.md`) which remained the primary integration reference.
- The database-to-backend connection string required synchronisation between Member B and Member A's `config.py`. The SQLite fallback ensured the backend and frontend could be developed independently.

### Future Improvements

1. **Map visualisation**: Overlay trip density on an interactive NYC map using Leaflet.js and the GeoJSON zone boundaries, enabling spatial pattern discovery.
2. **Predictive modelling**: A fare prediction model (e.g., linear regression on distance, hour, and borough) could be exposed as a `/api/predict/fare` endpoint.
3. **Time-series anomaly alerts**: Integrate the custom anomaly detection algorithm into a live endpoint that flags unusual trips in near-real-time.
4. **User authentication and saved filters**: Allow users to save filter presets and return to personalised views.
5. **Full PostgreSQL + PostGIS deployment**: Enable true geospatial queries such as "show all trips that started within 500m of Times Square."
