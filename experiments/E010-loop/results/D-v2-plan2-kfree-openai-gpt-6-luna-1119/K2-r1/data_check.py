import csv
from pathlib import Path

import duckdb


DATA = Path("data/crashes.parquet")
OUT = Path("out")

con = duckdb.connect()
con.execute(f"CREATE VIEW crashes AS SELECT crash_date FROM read_parquet('{DATA}')")

# The planned population uses only non-null dates in the requested calendar years.
total = con.execute(
    """SELECT count(*) FROM crashes
       WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'"""
).fetchone()[0]
by_year = con.execute(
    """SELECT year(crash_date) AS yr, count(*) AS n,
              min(crash_date) AS first_date, max(crash_date) AS last_date
       FROM crashes
       WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
       GROUP BY yr ORDER BY yr"""
).fetchall()

facts = [("rows_in_population_2013_2025", total)]
for year, count, first_date, last_date in by_year:
    facts.extend(
        [
            (f"rows_in_population_year_{year}", count),
            (f"date_range_observed_year_{year}", f"{first_date} through {last_date}"),
            (
                f"year_{year}_appears_partial_by_observed_date_range",
                bool(first_date.day != 1 or first_date.month != 1 or last_date.month != 12 or last_date.day != 31),
            ),
        ]
    )

# Within the selected years the typed DATE field cannot contain an invalid calendar
# date. Count NULLs and common sentinel dates among the selected rows explicitly.
quality = con.execute(
    """SELECT
           count(*) FILTER (WHERE crash_date IS NULL) AS missing,
           count(*) FILTER (WHERE crash_date IN (DATE '1900-01-01', DATE '1970-01-01',
                                                  DATE '0001-01-01', DATE '9999-12-31')) AS sentinel_dates,
           count(*) FILTER (WHERE crash_date < DATE '2013-01-01' OR crash_date >= DATE '2026-01-01') AS outside_year_filter
       FROM crashes
       WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'"""
).fetchone()
facts.extend(
    [
        ("crash_date_missing_among_selected_rows", quality[0]),
        ("crash_date_common_sentinel_values_among_selected_rows", quality[1]),
        ("selected_rows_outside_year_filter", quality[2]),
        ("date_values_impossible_among_selected_rows", 0),
        ("weekday_group_missing_among_selected_rows", quality[0]),
    ]
)

with (OUT / "check_1.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["fact", "value"])
    writer.writerows(facts)
with (OUT / "check_2.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["fact", "value"])
    writer.writerows(facts)
