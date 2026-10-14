import duckdb

con = duckdb.connect()
P = "'./data/crashes.parquet'"

print("== null borough rate by year ==")
print(con.sql(f"""
SELECT EXTRACT(YEAR FROM crash_date)::INT y, COUNT(*) n,
 ROUND(100.0*SUM(CASE WHEN borough IS NULL THEN 1 ELSE 0 END)/COUNT(*),1) null_pct
FROM {P} GROUP BY 1 ORDER BY 1"""))

print("== monthly Brooklyn crash counts (reporting discontinuities?) ==")
print(con.sql(f"""
SELECT STRFTIME(crash_date, '%Y-%m') m, COUNT(*) n, SUM(number_of_persons_injured) inj
FROM {P} WHERE borough='BROOKLYN' GROUP BY 1 ORDER BY 1"""))

print("== Brooklyn annual detail 2013-2025 ==")
print(con.sql(f"""
SELECT EXTRACT(YEAR FROM crash_date)::INT y,
 COUNT(*) crashes,
 SUM(number_of_persons_injured) all_inj,
 SUM(number_of_pedestrians_injured) ped_inj,
 SUM(number_of_pedestrians_killed) ped_killed,
 ROUND(100.0*SUM(number_of_pedestrians_injured)/SUM(number_of_persons_injured),1) ped_share
FROM {P} WHERE borough='BROOKLYN' AND EXTRACT(YEAR FROM crash_date) BETWEEN 2013 AND 2025
GROUP BY 1 ORDER BY 1"""))

print("== Brooklyn pedestrian injuries by month of year, 2013-2015 vs 2023-2025 ==")
print(con.sql(f"""
SELECT CASE WHEN EXTRACT(YEAR FROM crash_date) BETWEEN 2013 AND 2015 THEN '2013-15'
            WHEN EXTRACT(YEAR FROM crash_date) BETWEEN 2023 AND 2025 THEN '2023-25' END grp,
 COUNT(*) crashes, SUM(number_of_pedestrians_injured) ped_inj, SUM(number_of_pedestrians_killed) ped_killed
FROM {P} WHERE borough='BROOKLYN' AND EXTRACT(YEAR FROM crash_date) IN (2013,2014,2015,2023,2024,2025)
GROUP BY 1"""))

print("== top contributing factors in Brooklyn ped-injury crashes 2013-2025 ==")
print(con.sql(f"""
SELECT contributing_factor_vehicle_1 f, COUNT(*) n
FROM {P}
WHERE borough='BROOKLYN' AND EXTRACT(YEAR FROM crash_date) BETWEEN 2013 AND 2025
  AND number_of_pedestrians_injured + number_of_pedestrians_killed > 0
GROUP BY 1 ORDER BY n DESC LIMIT 12"""))
