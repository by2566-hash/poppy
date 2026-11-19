import csv
import json
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"

con = duckdb.connect()
year_rows = con.execute(
    """
    SELECT year(crash_date) AS year,
           count(*) AS rows,
           min(crash_date) AS first_date,
           max(crash_date) AS last_date
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date <= DATE '2025-12-31'
    GROUP BY year(crash_date)
    ORDER BY year
    """,
    [str(DATA)],
).fetchall()
missing_dates = con.execute(
    "SELECT count(*) FROM read_parquet(?) WHERE crash_date IS NULL", [str(DATA)]
).fetchone()[0]
sentinels = con.execute(
    """
    SELECT count(*) FROM read_parquet(?)
    WHERE crash_date IN (DATE '0001-01-01', DATE '1900-01-01',
                         DATE '1970-01-01', DATE '9999-12-31')
    """,
    [str(DATA)],
).fetchone()[0]

facts = [
    ("missing_crash_date_rows_in_file (cannot be assigned to a plan year; excluded)", str(missing_dates)),
    ("crash_date_sentinel_rows_in_file (0001-01-01, 1900-01-01, 1970-01-01, 9999-12-31)", str(sentinels)),
    ("plan_population_rows_2013_2025", str(sum(row[1] for row in year_rows))),
]
covered = {int(row[0]): row for row in year_rows}
for year in range(2013, 2026):
    row = covered.get(year)
    if row:
        _, count, first, last = row
        facts.extend(
            [
                (f"{year}_population_rows", str(count)),
                (f"{year}_first_crash_date", first.isoformat()),
                (f"{year}_last_crash_date", last.isoformat()),
                (
                    f"{year}_coverage_status",
                    "full calendar-year endpoints present"
                    if first.isoformat() == f"{year}-01-01" and last.isoformat() == f"{year}-12-31"
                    else "partial at one or both calendar-year endpoints",
                ),
            ]
        )
    else:
        facts.extend(
            [
                (f"{year}_population_rows", "0"),
                (f"{year}_first_crash_date", "none"),
                (f"{year}_last_crash_date", "none"),
                (f"{year}_coverage_status", "no rows"),
            ]
        )

for plan_id in (1, 2):
    with (OUT / f"check_{plan_id}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)
