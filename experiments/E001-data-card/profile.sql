WITH crashes AS (SELECT * FROM read_parquet('data/processed/nyc_crashes.parquet'))
SELECT 'crash_date' AS column_name, count(*) AS row_count, count(crash_date) AS non_null_count, count(*)-count(crash_date) AS null_count, round(100.0*(count(*)-count(crash_date))/count(*),4) AS null_pct, count(DISTINCT crash_date) AS distinct_count FROM crashes
UNION ALL
SELECT 'crash_time' AS column_name, count(*) AS row_count, count(crash_time) AS non_null_count, count(*)-count(crash_time) AS null_count, round(100.0*(count(*)-count(crash_time))/count(*),4) AS null_pct, count(DISTINCT crash_time) AS distinct_count FROM crashes
UNION ALL
SELECT 'borough' AS column_name, count(*) AS row_count, count(borough) AS non_null_count, count(*)-count(borough) AS null_count, round(100.0*(count(*)-count(borough))/count(*),4) AS null_pct, count(DISTINCT borough) AS distinct_count FROM crashes
UNION ALL
SELECT 'zip_code' AS column_name, count(*) AS row_count, count(zip_code) AS non_null_count, count(*)-count(zip_code) AS null_count, round(100.0*(count(*)-count(zip_code))/count(*),4) AS null_pct, count(DISTINCT zip_code) AS distinct_count FROM crashes
UNION ALL
SELECT 'latitude' AS column_name, count(*) AS row_count, count(latitude) AS non_null_count, count(*)-count(latitude) AS null_count, round(100.0*(count(*)-count(latitude))/count(*),4) AS null_pct, count(DISTINCT latitude) AS distinct_count FROM crashes
UNION ALL
SELECT 'longitude' AS column_name, count(*) AS row_count, count(longitude) AS non_null_count, count(*)-count(longitude) AS null_count, round(100.0*(count(*)-count(longitude))/count(*),4) AS null_pct, count(DISTINCT longitude) AS distinct_count FROM crashes
UNION ALL
SELECT 'location' AS column_name, count(*) AS row_count, count(location) AS non_null_count, count(*)-count(location) AS null_count, round(100.0*(count(*)-count(location))/count(*),4) AS null_pct, count(DISTINCT location) AS distinct_count FROM crashes
UNION ALL
SELECT 'on_street_name' AS column_name, count(*) AS row_count, count(on_street_name) AS non_null_count, count(*)-count(on_street_name) AS null_count, round(100.0*(count(*)-count(on_street_name))/count(*),4) AS null_pct, count(DISTINCT on_street_name) AS distinct_count FROM crashes
UNION ALL
SELECT 'cross_street_name' AS column_name, count(*) AS row_count, count(cross_street_name) AS non_null_count, count(*)-count(cross_street_name) AS null_count, round(100.0*(count(*)-count(cross_street_name))/count(*),4) AS null_pct, count(DISTINCT cross_street_name) AS distinct_count FROM crashes
UNION ALL
SELECT 'off_street_name' AS column_name, count(*) AS row_count, count(off_street_name) AS non_null_count, count(*)-count(off_street_name) AS null_count, round(100.0*(count(*)-count(off_street_name))/count(*),4) AS null_pct, count(DISTINCT off_street_name) AS distinct_count FROM crashes
UNION ALL
SELECT 'number_of_persons_injured' AS column_name, count(*) AS row_count, count(number_of_persons_injured) AS non_null_count, count(*)-count(number_of_persons_injured) AS null_count, round(100.0*(count(*)-count(number_of_persons_injured))/count(*),4) AS null_pct, count(DISTINCT number_of_persons_injured) AS distinct_count FROM crashes
UNION ALL
SELECT 'number_of_persons_killed' AS column_name, count(*) AS row_count, count(number_of_persons_killed) AS non_null_count, count(*)-count(number_of_persons_killed) AS null_count, round(100.0*(count(*)-count(number_of_persons_killed))/count(*),4) AS null_pct, count(DISTINCT number_of_persons_killed) AS distinct_count FROM crashes
UNION ALL
SELECT 'number_of_pedestrians_injured' AS column_name, count(*) AS row_count, count(number_of_pedestrians_injured) AS non_null_count, count(*)-count(number_of_pedestrians_injured) AS null_count, round(100.0*(count(*)-count(number_of_pedestrians_injured))/count(*),4) AS null_pct, count(DISTINCT number_of_pedestrians_injured) AS distinct_count FROM crashes
UNION ALL
SELECT 'number_of_pedestrians_killed' AS column_name, count(*) AS row_count, count(number_of_pedestrians_killed) AS non_null_count, count(*)-count(number_of_pedestrians_killed) AS null_count, round(100.0*(count(*)-count(number_of_pedestrians_killed))/count(*),4) AS null_pct, count(DISTINCT number_of_pedestrians_killed) AS distinct_count FROM crashes
UNION ALL
SELECT 'number_of_cyclist_injured' AS column_name, count(*) AS row_count, count(number_of_cyclist_injured) AS non_null_count, count(*)-count(number_of_cyclist_injured) AS null_count, round(100.0*(count(*)-count(number_of_cyclist_injured))/count(*),4) AS null_pct, count(DISTINCT number_of_cyclist_injured) AS distinct_count FROM crashes
UNION ALL
SELECT 'number_of_cyclist_killed' AS column_name, count(*) AS row_count, count(number_of_cyclist_killed) AS non_null_count, count(*)-count(number_of_cyclist_killed) AS null_count, round(100.0*(count(*)-count(number_of_cyclist_killed))/count(*),4) AS null_pct, count(DISTINCT number_of_cyclist_killed) AS distinct_count FROM crashes
UNION ALL
SELECT 'number_of_motorist_injured' AS column_name, count(*) AS row_count, count(number_of_motorist_injured) AS non_null_count, count(*)-count(number_of_motorist_injured) AS null_count, round(100.0*(count(*)-count(number_of_motorist_injured))/count(*),4) AS null_pct, count(DISTINCT number_of_motorist_injured) AS distinct_count FROM crashes
UNION ALL
SELECT 'number_of_motorist_killed' AS column_name, count(*) AS row_count, count(number_of_motorist_killed) AS non_null_count, count(*)-count(number_of_motorist_killed) AS null_count, round(100.0*(count(*)-count(number_of_motorist_killed))/count(*),4) AS null_pct, count(DISTINCT number_of_motorist_killed) AS distinct_count FROM crashes
UNION ALL
SELECT 'contributing_factor_vehicle_1' AS column_name, count(*) AS row_count, count(contributing_factor_vehicle_1) AS non_null_count, count(*)-count(contributing_factor_vehicle_1) AS null_count, round(100.0*(count(*)-count(contributing_factor_vehicle_1))/count(*),4) AS null_pct, count(DISTINCT contributing_factor_vehicle_1) AS distinct_count FROM crashes
UNION ALL
SELECT 'contributing_factor_vehicle_2' AS column_name, count(*) AS row_count, count(contributing_factor_vehicle_2) AS non_null_count, count(*)-count(contributing_factor_vehicle_2) AS null_count, round(100.0*(count(*)-count(contributing_factor_vehicle_2))/count(*),4) AS null_pct, count(DISTINCT contributing_factor_vehicle_2) AS distinct_count FROM crashes
UNION ALL
SELECT 'contributing_factor_vehicle_3' AS column_name, count(*) AS row_count, count(contributing_factor_vehicle_3) AS non_null_count, count(*)-count(contributing_factor_vehicle_3) AS null_count, round(100.0*(count(*)-count(contributing_factor_vehicle_3))/count(*),4) AS null_pct, count(DISTINCT contributing_factor_vehicle_3) AS distinct_count FROM crashes
UNION ALL
SELECT 'contributing_factor_vehicle_4' AS column_name, count(*) AS row_count, count(contributing_factor_vehicle_4) AS non_null_count, count(*)-count(contributing_factor_vehicle_4) AS null_count, round(100.0*(count(*)-count(contributing_factor_vehicle_4))/count(*),4) AS null_pct, count(DISTINCT contributing_factor_vehicle_4) AS distinct_count FROM crashes
UNION ALL
SELECT 'contributing_factor_vehicle_5' AS column_name, count(*) AS row_count, count(contributing_factor_vehicle_5) AS non_null_count, count(*)-count(contributing_factor_vehicle_5) AS null_count, round(100.0*(count(*)-count(contributing_factor_vehicle_5))/count(*),4) AS null_pct, count(DISTINCT contributing_factor_vehicle_5) AS distinct_count FROM crashes
UNION ALL
SELECT 'collision_id' AS column_name, count(*) AS row_count, count(collision_id) AS non_null_count, count(*)-count(collision_id) AS null_count, round(100.0*(count(*)-count(collision_id))/count(*),4) AS null_pct, count(DISTINCT collision_id) AS distinct_count FROM crashes
UNION ALL
SELECT 'vehicle_type_code1' AS column_name, count(*) AS row_count, count(vehicle_type_code1) AS non_null_count, count(*)-count(vehicle_type_code1) AS null_count, round(100.0*(count(*)-count(vehicle_type_code1))/count(*),4) AS null_pct, count(DISTINCT vehicle_type_code1) AS distinct_count FROM crashes
UNION ALL
SELECT 'vehicle_type_code2' AS column_name, count(*) AS row_count, count(vehicle_type_code2) AS non_null_count, count(*)-count(vehicle_type_code2) AS null_count, round(100.0*(count(*)-count(vehicle_type_code2))/count(*),4) AS null_pct, count(DISTINCT vehicle_type_code2) AS distinct_count FROM crashes
UNION ALL
SELECT 'vehicle_type_code3' AS column_name, count(*) AS row_count, count(vehicle_type_code3) AS non_null_count, count(*)-count(vehicle_type_code3) AS null_count, round(100.0*(count(*)-count(vehicle_type_code3))/count(*),4) AS null_pct, count(DISTINCT vehicle_type_code3) AS distinct_count FROM crashes
UNION ALL
SELECT 'vehicle_type_code4' AS column_name, count(*) AS row_count, count(vehicle_type_code4) AS non_null_count, count(*)-count(vehicle_type_code4) AS null_count, round(100.0*(count(*)-count(vehicle_type_code4))/count(*),4) AS null_pct, count(DISTINCT vehicle_type_code4) AS distinct_count FROM crashes
UNION ALL
SELECT 'vehicle_type_code5' AS column_name, count(*) AS row_count, count(vehicle_type_code5) AS non_null_count, count(*)-count(vehicle_type_code5) AS null_count, round(100.0*(count(*)-count(vehicle_type_code5))/count(*),4) AS null_pct, count(DISTINCT vehicle_type_code5) AS distinct_count FROM crashes
ORDER BY column_name;
