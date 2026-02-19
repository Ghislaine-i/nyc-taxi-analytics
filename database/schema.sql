-- ============================================================================
-- NYC TAXI TRIP ANALYZER - DATABASE SCHEMA (PostgreSQL)
-- Member B: Database Design & Implementation
-- ============================================================================
-- Database Engine : PostgreSQL
-- Dataset         : 50,000 cleaned NYC yellow taxi trip records (Jan 2019)
-- Source          : Member A's cleaned_taxi_data.csv
-- ============================================================================

-- ==================================================================
-- TABLE 1: LOCATIONS (Dimension Table)
-- ==================================================================
-- Stores unique taxi zone information for pickup and dropoff locations.
-- Based on the NYC TLC Taxi Zone Lookup table.
-- ==================================================================

CREATE TABLE IF NOT EXISTS locations (
    location_id   INTEGER PRIMARY KEY,            -- TLC LocationID (1-263)
    borough       VARCHAR(50) NOT NULL,            -- NYC borough name
    zone          VARCHAR(100) NOT NULL,           -- Specific zone/neighborhood name
    service_zone  VARCHAR(50)                      -- Service zone classification
);


-- ==================================================================
-- TABLE 2: TRIPS (Fact Table)
-- ==================================================================
-- Stores individual taxi trip records with original fields, derived
-- features engineered by Member A, and denormalized location names.
-- ==================================================================

CREATE TABLE IF NOT EXISTS trips (
    trip_id                   SERIAL PRIMARY KEY,

    -- ── Vendor ──────────────────────────────────────────────────────
    VendorID                  INTEGER,             -- 1=Creative Mobile, 2=VeriFone

    -- ── Timestamps ──────────────────────────────────────────────────
    tpep_pickup_datetime      TIMESTAMP NOT NULL,  -- Pickup date/time
    tpep_dropoff_datetime     TIMESTAMP NOT NULL,  -- Dropoff date/time

    -- ── Trip Details ────────────────────────────────────────────────
    passenger_count           INTEGER,             -- Number of passengers
    trip_distance             DECIMAL(10,2),       -- Trip distance in miles
    RatecodeID                INTEGER,             -- Rate code (1-6)
    store_and_fwd_flag        VARCHAR(1),          -- Store-and-forward flag (Y/N)

    -- ── Location IDs ────────────────────────────────────────────────
    PULocationID              INTEGER,             -- Pickup TLC zone ID
    DOLocationID              INTEGER,             -- Dropoff TLC zone ID

    -- ── Payment ─────────────────────────────────────────────────────
    payment_type              INTEGER,             -- 1=Credit, 2=Cash, 3=No charge, etc.

    -- ── Financial ───────────────────────────────────────────────────
    fare_amount               DECIMAL(10,2),       -- Base fare ($)
    extra                     DECIMAL(10,2),       -- Misc extras and surcharges ($)
    mta_tax                   DECIMAL(10,2),       -- MTA tax ($)
    tip_amount                DECIMAL(10,2),       -- Tip amount ($)
    tolls_amount              DECIMAL(10,2),       -- Tolls amount ($)
    improvement_surcharge     DECIMAL(10,2),       -- Improvement surcharge ($)
    total_amount              DECIMAL(10,2),       -- Total charged ($)
    congestion_surcharge      DECIMAL(10,2),       -- Congestion surcharge ($)

    -- ── DERIVED FEATURES (engineered by Member A) ───────────────────
    trip_duration_minutes     DECIMAL(10,2),       -- Duration in minutes (dropoff - pickup)
    avg_speed_mph             DECIMAL(10,2),       -- Average speed (distance / duration)
    fare_per_mile             DECIMAL(10,2),       -- Fare efficiency (fare / distance)

    -- ── TIME FEATURES (extracted by Member A) ───────────────────────
    pickup_hour               INTEGER,             -- Hour of pickup (0-23)
    pickup_day_of_week        INTEGER,             -- Day of week (0=Mon, 6=Sun)
    pickup_day_name           VARCHAR(10),         -- Day name (Monday-Sunday)
    pickup_month              INTEGER,             -- Month of pickup (1-12)

    -- ── DENORMALIZED LOCATION NAMES ─────────────────────────────────
    pickup_borough            VARCHAR(50),         -- Pickup borough name
    pickup_zone               VARCHAR(100),        -- Pickup zone/neighborhood
    dropoff_borough           VARCHAR(50),         -- Dropoff borough name
    dropoff_zone              VARCHAR(100),        -- Dropoff zone/neighborhood

    -- ── Foreign Keys ────────────────────────────────────────────────
    FOREIGN KEY (PULocationID) REFERENCES locations(location_id),
    FOREIGN KEY (DOLocationID) REFERENCES locations(location_id)
);


-- ==================================================================
-- INDEXES FOR QUERY PERFORMANCE
-- ==================================================================

-- Temporal indexes (hourly/daily pattern queries)
CREATE INDEX IF NOT EXISTS idx_trips_pickup_datetime    ON trips(tpep_pickup_datetime);
CREATE INDEX IF NOT EXISTS idx_trips_pickup_hour        ON trips(pickup_hour);
CREATE INDEX IF NOT EXISTS idx_trips_pickup_day         ON trips(pickup_day_of_week);
CREATE INDEX IF NOT EXISTS idx_trips_pickup_month       ON trips(pickup_month);

-- Location indexes (borough/zone aggregation queries)
CREATE INDEX IF NOT EXISTS idx_trips_pickup_borough     ON trips(pickup_borough);
CREATE INDEX IF NOT EXISTS idx_trips_dropoff_borough    ON trips(dropoff_borough);
CREATE INDEX IF NOT EXISTS idx_trips_pu_location        ON trips(PULocationID);
CREATE INDEX IF NOT EXISTS idx_trips_do_location        ON trips(DOLocationID);

-- Financial indexes (fare analysis and sorting)
CREATE INDEX IF NOT EXISTS idx_trips_fare_amount        ON trips(fare_amount);
CREATE INDEX IF NOT EXISTS idx_trips_total_amount       ON trips(total_amount);
CREATE INDEX IF NOT EXISTS idx_trips_trip_distance      ON trips(trip_distance);

-- Compound index for common dashboard filter patterns
CREATE INDEX IF NOT EXISTS idx_trips_borough_hour       ON trips(pickup_borough, pickup_hour);
