import duckdb

con = duckdb.connect()
P = "'./data/crashes.parquet'"

print("== citywide ped injuries/killed vs Brooklyn (borough-assigned rows) ==")
print(con.sql(f"""
SELECT EXTRACT(YEAR FROM crash_date)::INT y,
 SUM(number_of_pedestrians_injured) city_ped_inj,
 SUM(CASE WHEN borough='BROOKLYN' THEN number_of_pedestrians_injured ELSE 0 END) bk_ped_inj,
 SUM(number_of_pedestrians_killed) city_ped_ked,
 SUM(CASE WHEN borough='BROOKLYN' THEN number_of_pedestrians_killed ELSE 0 END) bk_ped_ked,
 SUM(CASE WHEN borough IS NOT NULL THEN number_of_pedestrians_injured ELSE 0 END) assigned_ped_inj
FROM {P} WHERE EXTRACT(YEAR FROM crash_date) BETWEEN 2013 AND 2025
GROUP BY 1 ORDER BY 1"""))

print("== rows w/ vs w/o borough: injury profile ==")
print(con.sql(f"""
SELECT EXTRACT(YEAR FROM crash_date)::INT y,
 SUM(CASE WHEN borough IS NULL THEN 1 ELSE 0 END) n_missing,
 ROUND(100.0*SUM(CASE WHEN borough IS NULL THEN 1 ELSE 0 END)/COUNT(*),1) miss_pct,
 ROUND(100.0*SUM(CASE WHEN borough IS NULL AND number_of_persons_injured>0 THEN 1 ELSE 0 END)
       /NULLIF(SUM(CASE WHEN borough IS NULL THEN 1 ELSE 0 END),0),1) miss_inj_pct,
 ROUND(100.0*SUM(CASE WHEN borough IS NOT NULL AND number_of_persons_injured>0 THEN 1 ELSE 0 END)
       /NULLIF(SUM(CASE WHEN borough IS NOT NULL THEN 1 ELSE 0 END),0),1) pres_inj_pct
FROM {P} WHERE EXTRACT(YEAR FROM crash_date) BETWEEN 2013 AND 2025
GROUP BY 1 ORDER BY 1"""))

print("== crude bbox check: missing-borough rows with coords, rough Brooklyn box ==")
print(con.sql(f"""
SELECT EXTRACT(YEAR FROM crash_date)::INT y, COUNT(*) n,
 SUM(CASE WHEN latitude BETWEEN 40.55 AND 40.74 AND longitude BETWEEN -74.05 AND -73.83 THEN 1 ELSE 0 END) in_bk_box
FROM {P}
WHERE borough IS NULL AND EXTRACT(YEAR FROM crash_date) BETWEEN 2013 AND 2025
GROUP BY 1 ORDER BY 1"""))
