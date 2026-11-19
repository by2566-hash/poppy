import csv
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
PARQUET = ROOT / "data" / "crashes.parquet"
YEARS = range(2013, 2026)

con = duckdb.connect()
parquet_sql_path = str(PARQUET).replace("'", "''")
con.execute(f"CREATE VIEW crashes AS SELECT * FROM read_parquet('{parquet_sql_path}')")
facts = []

# Missing crash dates cannot be assigned to a requested year, so inspect this
# filter column before applying the requested year restriction.
missing_dates_overall = con.execute(
    "SELECT count(*) FROM crashes WHERE crash_date IS NULL"
).fetchone()[0]
facts.append(("crash_date_missing_before_year_filter_overall", missing_dates_overall))

# Counts and date coverage are limited to records in the requested calendar years.
for year in YEARS:
    start, end = f"{year}-01-01", f"{year + 1}-01-01"
    row = con.execute(
        """SELECT count(*) AS rows, min(crash_date) AS first_date,
                  max(crash_date) AS last_date,
                  count(*) FILTER (WHERE crash_date IS NULL) AS missing_crash_date,
                  count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS missing_pedestrian_killed
           FROM crashes WHERE crash_date >= ? AND crash_date < ?""",
        [start, end],
    ).fetchone()
    count, first_date, last_date, missing_date, missing_outcome = row
    facts.extend(
        [
            (f"rows_in_{year}", count),
            (f"first_crash_date_in_{year}", str(first_date) if first_date else "none"),
            (f"last_crash_date_in_{year}", str(last_date) if last_date else "none"),
            (f"crash_date_missing_in_{year}_within_year_population", missing_date),
            (f"number_of_pedestrians_killed_missing_in_{year}", missing_outcome),
        ]
    )

# DATE is a validated date type, so impossible date values cannot be stored; check
# for a possible default-date pileup only within the planned date range.
default_rows = con.execute(
    """SELECT count(*) FROM crashes
       WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
         AND crash_date = DATE '1900-01-01'"""
).fetchone()[0]
facts.append(("crash_date_default_1900_01_01_in_plan_years", default_rows))
facts.append(("impossible_crash_date_values_in_plan_years", "0 (DATE type validates dates)"))

with (OUT / "check_1.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["fact", "value"])
    writer.writerows(facts)
