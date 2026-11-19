import csv
import duckdb

con = duckdb.connect()
con.execute("CREATE VIEW crashes AS SELECT * FROM read_parquet('data/crashes.parquet')")

population = "crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'"
total = con.execute(f"SELECT COUNT(*) FROM crashes WHERE {population}").fetchone()[0]
year_rows = con.execute(
    f"""SELECT YEAR(crash_date) AS year, COUNT(*) AS rows,
               MIN(crash_date) AS first_date, MAX(crash_date) AS last_date
        FROM crashes WHERE {population}
        GROUP BY year ORDER BY year"""
).fetchall()
missing_outcome = con.execute(
    f"SELECT COUNT(*) FROM crashes WHERE {population} AND number_of_pedestrians_killed IS NULL"
).fetchone()[0]
missing_dates_in_population = con.execute(
    f"SELECT COUNT(*) FROM crashes WHERE {population} AND crash_date IS NULL"
).fetchone()[0]

facts = [
    ("population_rows_2013_2025", total),
    ("crash_date_missing_rows_in_population", missing_dates_in_population),
    ("crash_date_impossible_values_in_population", "0 (DATE type cannot store an impossible calendar date)"),
    ("crash_date_default_dates_in_population", "0 (common sentinel dates such as 1900-01-01 and 1970-01-01 are outside the selected years)"),
    ("number_of_pedestrians_killed_missing_rows_in_population", missing_outcome),
]
for year, rows, first_date, last_date in year_rows:
    facts.extend([
        (f"rows_{year}", rows),
        (f"date_coverage_{year}", f"{first_date} through {last_date}"),
    ])

with open("out/check_1.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["fact", "value"])
    writer.writerows(facts)

con.close()
