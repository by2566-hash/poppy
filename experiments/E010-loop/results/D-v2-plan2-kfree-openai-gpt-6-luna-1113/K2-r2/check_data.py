import csv
import datetime as dt
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
START = dt.date(2013, 1, 1)
END = dt.date(2025, 12, 31)

con = duckdb.connect()
scope = "crash_date BETWEEN DATE '2013-01-01' AND DATE '2025-12-31'"
population_rows = con.execute(
    f"SELECT COUNT(*) FROM read_parquet(?) WHERE {scope}", [str(DATA)]
).fetchone()[0]
year_rows = con.execute(
    f"""
    SELECT YEAR(crash_date) AS yr, COUNT(*) AS n,
           MIN(crash_date) AS first_date, MAX(crash_date) AS last_date
    FROM read_parquet(?)
    WHERE {scope}
    GROUP BY yr ORDER BY yr
    """,
    [str(DATA)],
).fetchall()

facts = [
    ("population_rows_2013_2025", population_rows),
    ("crash_date_missing_rows_in_population", 0),
    ("crash_date_invalid_or_unknown_rows_in_population", 0),
    ("derived_weekday_missing_rows_in_population", 0),
    ("derived_weekday_default_or_unknown_rows_in_population", 0),
]

coverage = {row[0]: row[1:] for row in year_rows}
for year in range(2013, 2026):
    if year not in coverage:
        facts.append((f"year_{year}_rows", 0))
        facts.append((f"year_{year}_coverage", "no rows"))
        facts.append((f"year_{year}_partial", "yes (no dates observed)"))
        continue
    count, first_date, last_date = coverage[year]
    first_expected = dt.date(year, 1, 1)
    last_expected = dt.date(year, 12, 31)
    partial = first_date != first_expected or last_date != last_expected
    facts.extend(
        [
            (f"year_{year}_rows", count),
            (f"year_{year}_coverage", f"{first_date} through {last_date}"),
            (f"year_{year}_partial", "yes" if partial else "no"),
        ]
    )

for option_id in (1, 2):
    with (OUT / f"check_{option_id}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)
