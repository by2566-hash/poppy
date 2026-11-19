import csv
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
YEARS = range(2013, 2026)
DEATH_COLUMNS = (
    "number_of_motorist_killed",
    "number_of_cyclist_killed",
)

con = duckdb.connect()
source = (ROOT / "data" / "crashes.parquet").as_posix().replace("'", "''")
year_rows = con.execute(
    f"""
    SELECT year(crash_date) AS year, count(*) AS rows,
           min(crash_date) AS first_date, max(crash_date) AS last_date
    FROM read_parquet('{source}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year(crash_date)
    ORDER BY year
    """
).fetchall()
total_rows = sum(row[1] for row in year_rows)
missing_date, default_dates = con.execute(
    f"""
    SELECT count(*) FILTER (WHERE crash_date IS NULL),
           count(*) FILTER (WHERE crash_date IN
               (DATE '1900-01-01', DATE '1970-01-01', DATE '0001-01-01'))
    FROM read_parquet('{source}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    """
).fetchone()
missing_outcomes = con.execute(
    f"""
    SELECT {', '.join(f'count(*) FILTER (WHERE {c} IS NULL)' for c in DEATH_COLUMNS)}
    FROM read_parquet('{source}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    """
).fetchone()

facts = [
    ("population_rows_2013_2025", total_rows),
    ("crash_date_missing_within_population", missing_date),
    ("crash_date_known_default_dates_1900_1970_0001_within_population", default_dates),
    ("crash_date_is_DATE_type_invalid_dates", "not representable; DATE values are valid calendar dates"),
]
for year in YEARS:
    match = next((r for r in year_rows if r[0] == year), None)
    if match is None:
        facts.append((f"rows_{year}", 0))
        facts.append((f"observed_date_span_{year}", "no rows"))
    else:
        facts.append((f"rows_{year}", match[1]))
        facts.append((f"observed_date_span_{year}", f"{match[2]} through {match[3]}"))
for column, missing in zip(DEATH_COLUMNS, missing_outcomes):
    facts.append((f"{column}_missing_within_population", missing))

for plan_id in (1, 2):
    with (OUT / f"check_{plan_id}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(("fact", "value"))
        writer.writerows(facts)
