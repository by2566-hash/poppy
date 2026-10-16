import duckdb

con = duckdb.connect()
P = "'./data/crashes.parquet'"

# valid-coordinate, borough-present records
con.sql(f"""
CREATE OR REPLACE TEMP TABLE geocoded AS
SELECT collision_id, round(latitude::FLOAT,2) la, round(longitude::FLOAT,2) lo, borough
FROM {P}
WHERE borough IS NOT NULL AND latitude BETWEEN 40.4 AND 40.95 AND longitude BETWEEN -74.3 AND -73.6
""")

con.sql("""
CREATE OR REPLACE TEMP TABLE train AS
SELECT la, lo, borough, COUNT(*) n FROM geocoded
WHERE hash(collision_id) % 2 = 0 GROUP BY 1,2,3
""")
con.sql("""
CREATE OR REPLACE TEMP TABLE cellmode AS
SELECT la, lo, arg_max(borough, n) b, SUM(n) cell_n FROM train GROUP BY 1,2
""")

print("== holdout accuracy of cell-mode classifier ==")
print(con.sql("""
SELECT COUNT(*) n,
 SUM(CASE WHEN c.b IS NOT NULL THEN 1 ELSE 0 END) covered,
 SUM(CASE WHEN c.b = g.borough THEN 1 ELSE 0 END) correct,
 ROUND(100.0*SUM(CASE WHEN c.b = g.borough THEN 1 ELSE 0 END)/COUNT(*),2) acc_pct,
 ROUND(100.0*SUM(CASE WHEN c.b IS NOT NULL THEN 1 ELSE 0 END)/COUNT(*),2) covered_pct
FROM geocoded g LEFT JOIN cellmode c USING (la,lo)
WHERE hash(collision_id) % 2 = 1"""))

# neighbor fill for uncovered cells: nearest cell within small radius
con.sql("""
CREATE OR REPLACE TEMP TABLE nbr AS
SELECT c1.la, c1.lo, arg_max(c2.b, c2.cell_n) b
FROM cellmode c1 JOIN cellmode c2
  ON abs(c1.la-c2.la)<=0.03 AND abs(c1.lo-c2.lo)<=0.03
GROUP BY 1,2
""")
print("== holdout accuracy with neighbor fill ==")
print(con.sql("""
SELECT COUNT(*) n,
 SUM(CASE WHEN COALESCE(c.b, nb.b) IS NOT NULL THEN 1 ELSE 0 END) covered,
 ROUND(100.0*SUM(CASE WHEN COALESCE(c.b, nb.b)=g.borough THEN 1 ELSE 0 END)/COUNT(*),2) acc_pct
FROM geocoded g
LEFT JOIN cellmode c USING (la,lo)
LEFT JOIN nbr nb USING (la,lo)
WHERE hash(collision_id) % 2 = 1"""))

# Now classify all missing-borough rows with coords
con.sql(f"""
CREATE OR REPLACE TEMP TABLE missing AS
SELECT collision_id, round(latitude::FLOAT,2) la, round(longitude::FLOAT,2) lo
FROM {P}
WHERE borough IS NULL AND latitude BETWEEN 40.4 AND 40.95 AND longitude BETWEEN -74.3 AND -73.6
""")
print("== recovered borough mix among missing-borough rows (coords present) ==")
print(con.sql("""
SELECT COALESCE(c.b, nb.b, 'UNCLASSIFIED') b, COUNT(*) n
FROM missing m LEFT JOIN cellmode c USING (la,lo) LEFT JOIN nbr nb USING (la,lo)
GROUP BY 1 ORDER BY n DESC"""))
