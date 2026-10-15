import duckdb

con = duckdb.connect()
P = "'./data/crashes.parquet'"

print("== coord sanity for missing-borough rows ==")
print(con.sql(f"""
SELECT COUNT(*) n,
 SUM(CASE WHEN latitude IS NULL THEN 1 ELSE 0 END) null_lat,
 SUM(CASE WHEN latitude=0 OR longitude=0 THEN 1 ELSE 0 END) zero,
 SUM(CASE WHEN latitude BETWEEN 40.4 AND 40.95 AND longitude BETWEEN -74.3 AND -73.6 THEN 1 ELSE 0 END) in_nyc_box
FROM {P} WHERE borough IS NULL"""))

print("== grid classifier: mode borough per 0.01-deg cell (using records WITH borough) ==")
con.sql(f"""
CREATE OR REPLACE TEMP TABLE cells AS
SELECT round(latitude::FLOAT, 2) la, round(longitude::FLOAT, 2) lo, borough, COUNT(*) n
FROM {P}
WHERE borough IS NOT NULL AND latitude BETWEEN 40.4 AND 40.95 AND longitude BETWEEN -74.3 AND -73.6
GROUP BY 1,2,3
""")
print(con.sql("""
SELECT COUNT(DISTINCT format('{}_{}', la, lo)) cells FROM (
  SELECT la, lo, borough, n,
         ROW_NUMBER() OVER (PARTITION BY la, lo ORDER BY n DESC) rn FROM cells) t WHERE rn=1"""))

print("== how well does nearest-cell mode classify held-out borough-present rows? (50% sample) ==")
con.sql(f"""
CREATE OR REPLACE TEMP TABLE train AS
SELECT * FROM cells WHERE hash(la || lo || borough) % 2 = 0
""")
# mode borough per cell in train
print(con.sql("""
WITH cellmode AS (
  SELECT la, lo, arg_max(borough, n) b FROM train GROUP BY 1,2),
held AS (
  SELECT DISTINCT round(latitude::FLOAT,2) la, round(longitude::FLOAT,2) lo, borough
  FROM (SELECT * FROM cells WHERE hash(la || lo || borough) % 2 = 1)
)
SELECT COUNT(*) n,
  SUM(CASE WHEN c.b IS NOT NULL THEN 1 ELSE 0 END) covered,
  SUM(CASE WHEN c.b = h.borough THEN 1 ELSE 0 END) correct
FROM held h LEFT JOIN cellmode c USING (la, lo)"""))
