import csv
import duckdb
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"
YEARS = range(2013, 2026)

con = duckdb.connect()
year_facts = con.execute(
    """
    SELECT year(crash_date) AS year,
           count(*) AS crash_rows,
           min(crash_date) AS first_date,
           max(crash_date) AS last_date,
           count(*) FILTER (WHERE number_of_motorist_killed IS NULL) AS missing_motorist_killed
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year(crash_date)
    ORDER BY year
    """,
    [str(DATA)],
).fetchall()
null_dates = con.execute(
    "SELECT count(*) FROM read_parquet(?) WHERE crash_date IS NULL",
    [str(DATA)],
).fetchone()[0]
coverage = con.execute(
    """
    SELECT min(crash_date), max(crash_date)
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    """,
    [str(DATA)],
).fetchone()

by_year = {int(row[0]): row for row in year_facts}
facts = [
    ("population_years", "2013–2025 inclusive; one row per police-reported crash"),
    ("crash_date_null_rows_before_year_filter", null_dates),
    ("crash_date_type_and_other_missing_forms", "DATE type: empty strings/unknown words cannot occur; invalid dates cannot be represented as DATE"),
    ("plan_years_observed_min_date", coverage[0]),
    ("plan_years_observed_max_date", coverage[1]),
]
for year in YEARS:
    row = by_year.get(year)
    if row is None:
        facts.extend([
            (f"{year}_crash_rows", 0),
            (f"{year}_first_date", "no rows"),
            (f"{year}_last_date", "no rows"),
            (f"{year}_number_of_motorist_killed_missing_rows", 0),
        ])
    else:
        _, crash_rows, first_date, last_date, missing_deaths = row
        facts.extend([
            (f"{year}_crash_rows", crash_rows),
            (f"{year}_first_date", first_date),
            (f"{year}_last_date", last_date),
            (f"{year}_number_of_motorist_killed_missing_rows", missing_deaths),
        ])
facts.extend([
    ("number_of_motorist_killed_check", "Only NULL/missingness was counted; no death values or sums were computed in this check."),
    ("motorist_killed_missing_forms_or_default", "INT type: empty strings/unknown words cannot occur; no semantic default value is defined by the data description."),
])

for plan_id in (1, 2):
    with (OUT / f"check_{plan_id}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)
