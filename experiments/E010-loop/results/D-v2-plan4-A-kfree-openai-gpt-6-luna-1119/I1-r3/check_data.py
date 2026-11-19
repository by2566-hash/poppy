import csv
import duckdb

PARQUET = "data/crashes.parquet"
YEARS = range(2013, 2026)

con = duckdb.connect()
year_rows = con.execute(
    """
    SELECT year(crash_date) AS crash_year,
           count(*) AS crash_rows,
           min(crash_date) AS first_date,
           max(crash_date) AS last_date,
           count(*) FILTER (WHERE number_of_motorist_killed IS NULL) AS killed_value_missing,
           count(*) FILTER (WHERE crash_date = make_date(year(crash_date), 1, 1)) AS jan_1_rows
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY crash_year
    ORDER BY crash_year
    """,
    [PARQUET],
).fetchall()

totals = con.execute(
    """
    SELECT count(*) AS crash_rows,
           count(*) FILTER (WHERE number_of_motorist_killed IS NULL) AS killed_value_missing,
           count(*) FILTER (WHERE crash_date IS NULL) AS crash_date_missing
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    """,
    [PARQUET],
).fetchone()

facts = [
    ("rows_2013_2025_total", totals[0]),
    ("rows_2013_2025_with_missing_number_of_motorist_killed", totals[1]),
    ("rows_2013_2025_with_missing_crash_date", totals[2]),
]
observed = {row[0]: row for row in year_rows}
for year in YEARS:
    row = observed.get(year)
    if row is None:
        facts.append((f"rows_{year}", 0))
        facts.append((f"year_{year}_coverage", "no rows"))
        facts.append((f"rows_{year}_missing_number_of_motorist_killed", 0))
        facts.append((f"rows_{year}_on_jan_1", 0))
        continue
    _, count, first_date, last_date, missing, jan_1 = row
    facts.extend(
        [
            (f"rows_{year}", count),
            (f"year_{year}_observed_date_range", f"{first_date} through {last_date}"),
            (f"year_{year}_coverage", "appears partial at calendar boundary" if first_date.month > 1 or first_date.day > 1 or last_date.month < 12 or last_date.day < 31 else "both calendar boundaries observed"),
            (f"rows_{year}_missing_number_of_motorist_killed", missing),
            (f"rows_{year}_on_jan_1", jan_1),
        ]
    )

with open("out/check_1.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["fact", "value"])
    writer.writerows(facts)
with open("out/check_2.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["fact", "value"])
    writer.writerows(facts)
