import csv
import duckdb

DATA = "data/crashes.parquet"
OUTPUT = "out/check_1.csv"

con = duckdb.connect()
con.execute(f"CREATE VIEW crashes AS SELECT crash_date, number_of_pedestrians_killed FROM read_parquet('{DATA}')")

facts = []
def record(fact, value):
    facts.append((fact, value))

period = con.execute("""
    SELECT COUNT(*) AS n,
           COUNT(*) FILTER (WHERE crash_date IS NULL) AS missing_date,
           COUNT(*) FILTER (WHERE crash_date = DATE '0001-01-01') AS year_0001_default,
           COUNT(*) FILTER (WHERE crash_date = DATE '1900-01-01') AS year_1900_default,
           COUNT(*) FILTER (WHERE crash_date = DATE '1970-01-01') AS year_1970_default
    FROM crashes
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
""").fetchone()
record("population_rows_2013_2025", period[0])
record("population_crash_date_missing", period[1])
record("population_crash_date_at_0001-01-01_default", period[2])
record("population_crash_date_at_1900-01-01_default", period[3])
record("population_crash_date_at_1970-01-01_default", period[4])

outside_null = con.execute("SELECT COUNT(*) FROM crashes WHERE crash_date IS NULL").fetchone()[0]
record("rows_unassignable_to_year_due_to_missing_crash_date_outside_population", outside_null)

year_rows = con.execute("""
    SELECT YEAR(crash_date) AS year,
           COUNT(*) AS rows,
           COUNT(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS pedestrian_killed_missing,
           MIN(crash_date) AS first_date,
           MAX(crash_date) AS last_date
    FROM crashes
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY YEAR(crash_date)
    ORDER BY year
""").fetchall()

for year, rows, missing, first_date, last_date in year_rows:
    record(f"rows_{year}", rows)
    record(f"number_of_pedestrians_killed_missing_{year}", missing)
    record(f"date_coverage_{year}", f"{first_date} through {last_date}")
    complete = str(first_date) == f"{year}-01-01" and str(last_date) == f"{year}-12-31"
    record(f"calendar_year_{year}_complete_date_bounds", str(complete).lower())

missing_total = con.execute("""
    SELECT COUNT(*)
    FROM crashes
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
      AND number_of_pedestrians_killed IS NULL
""").fetchone()[0]
record("number_of_pedestrians_killed_missing_2013_2025", missing_total)

with open(OUTPUT, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["fact", "value"])
    writer.writerows(facts)
