import duckdb

con = duckdb.connect()
P = "'./data/crashes.parquet'"

# Can we recover borough from zip_code for records with NULL borough?
print("== NULL borough records: how many have a usable zip? ==")
print(con.sql(f"""
SELECT COUNT(*) null_boro,
 SUM(CASE WHEN zip_code IS NOT NULL AND regexp_matches(zip_code, '^[0-9]{{5}}') THEN 1 ELSE 0 END) has_zip,
 SUM(CASE WHEN zip_code LIKE '112%' THEN 1 ELSE 0 END) bk_zip,
 SUM(CASE WHEN latitude IS NOT NULL THEN 1 ELSE 0 END) has_lat
FROM {P} WHERE borough IS NULL"""))

print("== zip prefix distribution among NULL-borough rows ==")
print(con.sql(f"""
SELECT CASE WHEN zip_code IS NULL THEN 'NULL'
            WHEN regexp_matches(zip_code,'^[0-9]{{5}}') THEN SUBSTRING(zip_code,1,3) ELSE 'other' END pfx,
 COUNT(*) n FROM {P} WHERE borough IS NULL GROUP BY 1 ORDER BY n DESC LIMIT 15"""))

print("== does zip agree with stated borough? (non-null borough) ==")
print(con.sql(f"""
SELECT borough, SUBSTRING(regexp_extract(zip_code,'^[0-9]{{5}}'),1,3) pfx, COUNT(*) n
FROM {P} WHERE borough IS NOT NULL AND regexp_matches(zip_code,'^[0-9]{{5}}')
GROUP BY 1,2 ORDER BY borough, n DESC"""))

# Recompute Brooklyn series with borough OR Brooklyn zip
print("== Brooklyn annual, stated-only vs stated+zip-recovered ==")
print(con.sql(f"""
WITH s AS (
 SELECT EXTRACT(YEAR FROM crash_date)::INT y,
        SUM(number_of_pedestrians_injured) ped_inj,
        SUM(number_of_pedestrians_killed) ped_ked,
        COUNT(*) n
 FROM {P} WHERE borough='BROOKLYN' AND EXTRACT(YEAR FROM crash_date) BETWEEN 2013 AND 2025
 GROUP BY 1),
r AS (
 SELECT EXTRACT(YEAR FROM crash_date)::INT y,
        SUM(number_of_pedestrians_injured) ped_inj,
        SUM(number_of_pedestrians_killed) ped_ked,
        COUNT(*) n
 FROM {P} WHERE (borough='BROOKLYN' OR (borough IS NULL AND zip_code LIKE '112%'))
   AND EXTRACT(YEAR FROM crash_date) BETWEEN 2013 AND 2025
 GROUP BY 1)
SELECT s.y, s.n stated, r.n recov, s.ped_inj st_inj, r.ped_inj rc_inj,
       s.ped_ked st_ked, r.ped_ked rc_ked
FROM s JOIN r USING (y) ORDER BY s.y"""))
