
SELECT COUNT(*) AS total_trips
FROM trips;



SELECT
    pickup_borough,
    pickup_zone,
    COUNT(*)                          AS trip_count,
    ROUND(AVG(fare_amount), 2)        AS avg_fare,
    ROUND(AVG(trip_distance), 2)      AS avg_distance_miles,
    ROUND(AVG(tip_amount), 2)         AS avg_tip
FROM trips
GROUP BY pickup_borough, pickup_zone
ORDER BY trip_count DESC
LIMIT 10;




SELECT
    pickup_borough,
    COUNT(*)                              AS total_trips,
    ROUND(AVG(fare_amount), 2)            AS avg_fare,
    ROUND(AVG(trip_distance), 2)          AS avg_distance,
    ROUND(AVG(trip_duration_minutes), 2)  AS avg_duration_min,
    ROUND(AVG(avg_speed_mph), 2)          AS avg_speed,
    ROUND(AVG(tip_amount), 2)             AS avg_tip,
    ROUND(SUM(total_amount), 2)           AS total_revenue
FROM trips
WHERE pickup_borough IS NOT NULL
GROUP BY pickup_borough
ORDER BY total_trips DESC;




SELECT
    pickup_hour,
    COUNT(*)                          AS trip_count,
    ROUND(AVG(fare_amount), 2)        AS avg_fare,
    ROUND(AVG(trip_distance), 2)      AS avg_distance,
    ROUND(AVG(trip_duration_minutes), 2) AS avg_duration,
    ROUND(SUM(total_amount), 2)       AS hour_revenue
FROM trips
GROUP BY pickup_hour
ORDER BY pickup_hour;




SELECT
    pickup_day_of_week,
    pickup_day_name,
    COUNT(*)                              AS trip_count,
    ROUND(AVG(fare_amount), 2)            AS avg_fare,
    ROUND(AVG(trip_distance), 2)          AS avg_distance,
    ROUND(AVG(trip_duration_minutes), 2)  AS avg_duration,
    ROUND(AVG(tip_amount), 2)             AS avg_tip
FROM trips
GROUP BY pickup_day_of_week, pickup_day_name
ORDER BY pickup_day_of_week;




SELECT
    CASE
        WHEN fare_amount < 5   THEN '$0 - $4.99'
        WHEN fare_amount < 10  THEN '$5 - $9.99'
        WHEN fare_amount < 15  THEN '$10 - $14.99'
        WHEN fare_amount < 20  THEN '$15 - $19.99'
        WHEN fare_amount < 30  THEN '$20 - $29.99'
        WHEN fare_amount < 50  THEN '$30 - $49.99'
        ELSE '$50+'
    END AS fare_bucket,
    COUNT(*)                       AS trip_count,
    ROUND(AVG(trip_distance), 2)   AS avg_distance,
    ROUND(AVG(tip_amount), 2)      AS avg_tip,
    ROUND(SUM(total_amount), 2)    AS bucket_revenue
FROM trips
GROUP BY fare_bucket
ORDER BY MIN(fare_amount);




SELECT
    pickup_hour,
    COUNT(*)                          AS trip_count,
    ROUND(SUM(total_amount), 2)       AS total_revenue,
    ROUND(AVG(total_amount), 2)       AS avg_revenue_per_trip,
    ROUND(SUM(tip_amount), 2)         AS total_tips
FROM trips
GROUP BY pickup_hour
ORDER BY total_revenue DESC
LIMIT 5;

-- QUERY 7: Distance vs Fare Relationship
SELECT
    ROUND(AVG(trip_distance), 2) AS avg_distance,
    ROUND(AVG(fare_amount), 2) AS avg_fare,
    ROUND(AVG(fare_per_mile), 2) AS avg_fare_per_mile,
    CORR(trip_distance, fare_amount) AS distance_fare_correlation
FROM trips;


--if using SQlite
SELECT
    ROUND(AVG(trip_distance), 2) AS avg_distance,
    ROUND(AVG(fare_amount), 2) AS avg_fare,
    ROUND(AVG(fare_per_mile), 2) AS avg_fare_per_mile
FROM trips;
