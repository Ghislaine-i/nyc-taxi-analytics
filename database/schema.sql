

CREATE TABLE IF NOT EXISTS locations (
    location_id   INTEGER PRIMARY KEY,            
    borough       VARCHAR(50) NOT NULL,         
    zone          VARCHAR(100) NOT NULL,           
    service_zone  VARCHAR(50)                      
);




CREATE TABLE IF NOT EXISTS trips (
    trip_id                   SERIAL PRIMARY KEY,

    
    VendorID                  INTEGER,             

    
    tpep_pickup_datetime      TIMESTAMP NOT NULL,  
    tpep_dropoff_datetime     TIMESTAMP NOT NULL,  

    
    passenger_count           INTEGER,             
    trip_distance             DECIMAL(10,2),       
    RatecodeID                INTEGER,             
    store_and_fwd_flag        VARCHAR(1),          

    
    PULocationID              INTEGER,             
    DOLocationID              INTEGER,             

    
    payment_type              INTEGER,             

    
    fare_amount               DECIMAL(10,2),       
    extra                     DECIMAL(10,2),       
    mta_tax                   DECIMAL(10,2),       
    tip_amount                DECIMAL(10,2),       
    tolls_amount              DECIMAL(10,2),       
    improvement_surcharge     DECIMAL(10,2),       
    total_amount              DECIMAL(10,2),       
    congestion_surcharge      DECIMAL(10,2),       

    
    trip_duration_minutes     DECIMAL(10,2),       
    avg_speed_mph             DECIMAL(10,2),       
    fare_per_mile             DECIMAL(10,2), 

    
    pickup_hour               INTEGER,             
    pickup_day_of_week        INTEGER,             
    pickup_day_name           VARCHAR(10),         
    pickup_month              INTEGER,             

    
    pickup_borough            VARCHAR(50),         
    pickup_zone               VARCHAR(100),        
    dropoff_borough           VARCHAR(50),         
    dropoff_zone              VARCHAR(100),      

    
    FOREIGN KEY (PULocationID) REFERENCES locations(location_id),
    FOREIGN KEY (DOLocationID) REFERENCES locations(location_id)
);





CREATE INDEX IF NOT EXISTS idx_trips_pickup_datetime    ON trips(tpep_pickup_datetime);
CREATE INDEX IF NOT EXISTS idx_trips_pickup_hour        ON trips(pickup_hour);
CREATE INDEX IF NOT EXISTS idx_trips_pickup_day         ON trips(pickup_day_of_week);
CREATE INDEX IF NOT EXISTS idx_trips_pickup_month       ON trips(pickup_month);


CREATE INDEX IF NOT EXISTS idx_trips_pickup_borough     ON trips(pickup_borough);
CREATE INDEX IF NOT EXISTS idx_trips_dropoff_borough    ON trips(dropoff_borough);
CREATE INDEX IF NOT EXISTS idx_trips_pu_location        ON trips(PULocationID);
CREATE INDEX IF NOT EXISTS idx_trips_do_location        ON trips(DOLocationID);


CREATE INDEX IF NOT EXISTS idx_trips_fare_amount        ON trips(fare_amount);
CREATE INDEX IF NOT EXISTS idx_trips_total_amount       ON trips(total_amount);
CREATE INDEX IF NOT EXISTS idx_trips_trip_distance      ON trips(trip_distance);

CREATE INDEX IF NOT EXISTS idx_trips_borough_hour       ON trips(pickup_borough, pickup_hour);
