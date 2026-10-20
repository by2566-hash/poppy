You are a data analyst. Answer the user's question about the data described below.

Data file: ./data/crashes.parquet (one row per police-reported motor vehicle crash in New York City; read it with DuckDB or pandas).
Columns: crash_date (DATE), crash_time (TIME), borough (VARCHAR, may be NULL), zip_code, latitude, longitude,
on_street_name, cross_street_name, number_of_persons_injured (INT), number_of_persons_killed (INT),
number_of_pedestrians_injured, number_of_pedestrians_killed, number_of_cyclist_injured, number_of_cyclist_killed,
number_of_motorist_injured, number_of_motorist_killed, contributing_factor_vehicle_1 ... contributing_factor_vehicle_5 (VARCHAR),
collision_id (BIGINT), vehicle_type_code1 ... vehicle_type_code5 (VARCHAR).
Python 3 with duckdb, pandas and matplotlib is available.

Write and run code yourself. Save the chart to ./out/initial.png and the plotted data to ./out/values.csv
(create ./out if needed). When finished, reply with a line `ANSWER:` followed by a short written answer
for a reader of the chart, based on the numbers you computed.

Question: How are NYC crashes distributed across the days of the week, 2013 to 2025?
