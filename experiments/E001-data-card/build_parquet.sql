COPY (
    SELECT
        try_strptime("CRASH DATE", '%m/%d/%Y')::DATE AS crash_date,
        try_strptime("CRASH TIME", '%H:%M')::TIME AS crash_time,
        "BOROUGH" AS borough,
        "ZIP CODE" AS zip_code,
        try_cast("LATITUDE" AS DOUBLE) AS latitude,
        try_cast("LONGITUDE" AS DOUBLE) AS longitude,
        "LOCATION" AS location,
        "ON STREET NAME" AS on_street_name,
        "CROSS STREET NAME" AS cross_street_name,
        "OFF STREET NAME" AS off_street_name,
        try_cast("NUMBER OF PERSONS INJURED" AS INTEGER) AS number_of_persons_injured,
        try_cast("NUMBER OF PERSONS KILLED" AS INTEGER) AS number_of_persons_killed,
        try_cast("NUMBER OF PEDESTRIANS INJURED" AS INTEGER) AS number_of_pedestrians_injured,
        try_cast("NUMBER OF PEDESTRIANS KILLED" AS INTEGER) AS number_of_pedestrians_killed,
        try_cast("NUMBER OF CYCLIST INJURED" AS INTEGER) AS number_of_cyclist_injured,
        try_cast("NUMBER OF CYCLIST KILLED" AS INTEGER) AS number_of_cyclist_killed,
        try_cast("NUMBER OF MOTORIST INJURED" AS INTEGER) AS number_of_motorist_injured,
        try_cast("NUMBER OF MOTORIST KILLED" AS INTEGER) AS number_of_motorist_killed,
        "CONTRIBUTING FACTOR VEHICLE 1" AS contributing_factor_vehicle_1,
        "CONTRIBUTING FACTOR VEHICLE 2" AS contributing_factor_vehicle_2,
        "CONTRIBUTING FACTOR VEHICLE 3" AS contributing_factor_vehicle_3,
        "CONTRIBUTING FACTOR VEHICLE 4" AS contributing_factor_vehicle_4,
        "CONTRIBUTING FACTOR VEHICLE 5" AS contributing_factor_vehicle_5,
        try_cast("COLLISION_ID" AS BIGINT) AS collision_id,
        "VEHICLE TYPE CODE 1" AS vehicle_type_code1,
        "VEHICLE TYPE CODE 2" AS vehicle_type_code2,
        "VEHICLE TYPE CODE 3" AS vehicle_type_code3,
        "VEHICLE TYPE CODE 4" AS vehicle_type_code4,
        "VEHICLE TYPE CODE 5" AS vehicle_type_code5
    FROM read_csv_auto(
        'data/raw/nyc_crashes_h9gi-nx95.csv',
        header = true,
        all_varchar = true,
        sample_size = -1,
        null_padding = true
    )
) TO 'data/processed/nyc_crashes.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);
