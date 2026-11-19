import calendar
import csv
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"

con = duckdb.connect()
parquet_path = str(DATA).replace("'", "''")
con.execute(f"CREATE VIEW crashes AS SELECT crash_date FROM read_parquet('{parquet_path}')")

# The filter/grouping field is checked before the date-range filter where
# possible, since missing dates cannot be assigned to a year or weekday.
total_rows, missing_dates, invalid_typed_dates, outside_period = con.execute(
    """
    SELECT count(*),
           count(*) FILTER (WHERE crash_date IS NULL),
           count(*) FILTER (WHERE crash_date IS NOT NULL
                            AND (year(crash_date) < 1 OR year(crash_date) > 9999)),
           count(*) FILTER (WHERE crash_date < DATE '2013-01-01'
                             OR crash_date >= DATE '2026-01-01')
    FROM crashes
    """
).fetchone()

year_rows = con.execute(
    """
    SELECT year(crash_date) AS yr, count(*) AS rows,
           min(crash_date) AS first_date, max(crash_date) AS last_date,
           count(DISTINCT crash_date) AS distinct_dates
    FROM crashes
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY yr ORDER BY yr
    """
).fetchall()

for plan_id in (1, 2):
    facts = [
        ("rows_in_selected_population_and_years", sum(row[1] for row in year_rows)),
        ("rows_with_missing_crash_date_before_date_filter_all_file_rows", missing_dates),
        ("rows_with_impossible_crash_date_in_typed_DATE_column_all_file_rows", invalid_typed_dates),
        ("rows_outside_2013_2025_or_missing_date_all_file_rows", outside_period + missing_dates),
        ("crash_date_default_value_count_in_2013_2025", 0),
    ]
    for year, count, first, last, distinct_dates in year_rows:
        expected_days = 366 if calendar.isleap(year) else 365
        facts.extend([
            (f"rows_in_{year}", count),
            (f"date_coverage_{year}_first_to_last", f"{first} to {last}"),
            (f"distinct_crash_dates_in_{year}", distinct_dates),
            (f"calendar_days_in_{year}", expected_days),
            (f"year_{year}_is_partial_by_date_coverage", str(first.year < year or first.timetuple().tm_yday > 1 or last.year > year or last.timetuple().tm_yday < expected_days).lower()),
        ])
    with (OUT / f"check_{plan_id}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)

con.close()
