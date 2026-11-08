import csv
from datetime import date

import duckdb


DATA = "data/crashes.parquet"
START_YEAR = 2013
END_YEAR = 2025

con = duckdb.connect()
con.execute(f"CREATE VIEW crashes AS SELECT crash_date, number_of_pedestrians_killed FROM read_parquet('{DATA}')")

facts = []
def add(fact, value):
    facts.append((fact, value))

missing_dates = con.execute("SELECT count(*) FROM crashes WHERE crash_date IS NULL").fetchone()[0]
add("rows_with_missing_crash_date_full_file_excluded_from_years", missing_dates)

for year in range(START_YEAR, END_YEAR + 1):
    row = con.execute(
        """SELECT count(*) AS rows,
                  count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS missing_killed,
                  count(*) FILTER (WHERE number_of_pedestrians_killed < 0) AS negative_killed,
                  count(*) FILTER (WHERE number_of_pedestrians_killed = 0) AS zero_killed,
                  min(crash_date) AS first_date, max(crash_date) AS last_date
           FROM crashes
           WHERE crash_date >= ? AND crash_date < ?""",
        [date(year, 1, 1), date(year + 1, 1, 1)],
    ).fetchone()
    rows, missing, negative, zeros, first_date, last_date = row
    add(f"population_rows_{year}", rows)
    add(f"pedestrians_killed_missing_rows_{year}", missing)
    add(f"pedestrians_killed_negative_rows_{year}", negative)
    add(f"pedestrians_killed_zero_rows_{year}", zeros)
    if rows:
        complete = first_date == date(year, 1, 1) and last_date == date(year, 12, 31)
        coverage = f"{first_date} through {last_date}; {'full calendar-year boundary coverage' if complete else 'partial calendar-year boundary coverage'}"
    else:
        coverage = "no dated rows"
    add(f"date_coverage_{year}", coverage)

total = con.execute(
    "SELECT count(*) FROM crashes WHERE crash_date >= ? AND crash_date < ?",
    [date(START_YEAR, 1, 1), date(END_YEAR + 1, 1, 1)],
).fetchone()[0]
add("population_rows_total_2013_2025", total)

with open("out/check_1.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["fact", "value"])
    writer.writerows(facts)
