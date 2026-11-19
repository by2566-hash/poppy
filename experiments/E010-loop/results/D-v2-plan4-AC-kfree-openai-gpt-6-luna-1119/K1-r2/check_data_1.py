import csv
import sys
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "crashes.parquet"
CHECK_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 1
OUT = Path(__file__).resolve().parent / f"check_{CHECK_ID}.csv"
con = duckdb.connect()
data_path = str(DATA).replace("'", "''")
con.execute(f"CREATE VIEW crashes AS SELECT * FROM read_parquet('{data_path}')")

facts = []


def add(fact, value):
    facts.append((fact, str(value)))


# The selected population is all records with a valid crash date in 2013–2025.
population = con.execute(
    """SELECT count(*) FROM crashes
       WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'"""
).fetchone()[0]
add("Crash rows in plan population (2013–2025)", population)

year_counts = con.execute(
    """SELECT year(crash_date) AS yr, count(*) AS n
       FROM crashes
       WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
       GROUP BY yr ORDER BY yr"""
).fetchall()
for year, count in year_counts:
    add(f"Crash rows in {year}", count)
for year in range(2013, 2026):
    if year not in {row[0] for row in year_counts}:
        add(f"Crash rows in {year}", 0)

# Date values that cannot be assigned to a year are checked across the file;
# common sentinel dates are also checked explicitly as potential defaults.
date_nulls = con.execute("SELECT count(*) FROM crashes WHERE crash_date IS NULL").fetchone()[0]
total_rows = con.execute("SELECT count(*) FROM crashes").fetchone()[0]
add("Rows in file with missing crash_date (cannot be assigned to a year)", f"{date_nulls} of {total_rows}")
for sentinel in ("0001-01-01", "1900-01-01", "1970-01-01", "2099-12-31"):
    count = con.execute(
        "SELECT count(*) FROM crashes WHERE crash_date = ?::DATE", [sentinel]
    ).fetchone()[0]
    add(f"Rows with possible default crash_date {sentinel}", count)

dates_by_year = con.execute(
    """SELECT year(crash_date) AS yr, min(crash_date), max(crash_date)
       FROM crashes
       WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
       GROUP BY yr ORDER BY yr"""
).fetchall()
for year, first, last in dates_by_year:
    add(f"Observed crash_date span in {year}", f"{first} through {last}")

# For the only summed outcome field, record missingness only, never its values.
missing_outcome = con.execute(
    """SELECT count(*) FROM crashes
       WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
         AND number_of_pedestrians_killed IS NULL"""
).fetchone()[0]
add("Plan-population rows with missing number_of_pedestrians_killed", f"{missing_outcome} of {population}")
missing_by_year = con.execute(
    """SELECT year(crash_date), count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL)
       FROM crashes
       WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
       GROUP BY 1 ORDER BY 1"""
).fetchall()
for year, count in missing_by_year:
    add(f"Rows with missing number_of_pedestrians_killed in {year}", count)
for year in range(2013, 2026):
    if year not in {row[0] for row in missing_by_year}:
        add(f"Rows with missing number_of_pedestrians_killed in {year}", 0)

with OUT.open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["fact", "value"])
    writer.writerows(facts)
