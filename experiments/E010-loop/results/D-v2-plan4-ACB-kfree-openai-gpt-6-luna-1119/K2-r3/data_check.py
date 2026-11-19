import csv
import json
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
YEARS = range(2013, 2026)

con = duckdb.connect()
source = str(DATA).replace("'", "''")
population = con.execute(
    f"""
    SELECT COUNT(*) AS n,
           COUNT(*) FILTER (WHERE crash_date IS NULL) AS missing_date,
           COUNT(*) FILTER (WHERE crash_date BETWEEN DATE '2013-01-01' AND DATE '2025-12-31') AS population_n
    FROM read_parquet('{source}')
    """
).fetchone()
year_rows = con.execute(
    f"""
    SELECT YEAR(crash_date) AS year, COUNT(*) AS n,
           MIN(crash_date) AS first_date, MAX(crash_date) AS last_date
    FROM read_parquet('{source}')
    WHERE crash_date BETWEEN DATE '2013-01-01' AND DATE '2025-12-31'
    GROUP BY YEAR(crash_date)
    ORDER BY year
    """
).fetchall()
by_year = {row[0]: row[1:] for row in year_rows}

facts = [
    ("rows_in_requested_years", population[2]),
    ("crash_date_missing_in_source_unassignable_to_year", population[1]),
    ("crash_date_impossible_values", "0 (DATE-typed column; impossible dates cannot be stored)"),
    ("crash_date_default_value_pileup", "Not applicable; no default date is defined"),
    ("weekday_derivation_invalid_values", "0 (all nonmissing DATE values map to a weekday)"),
]

for year in YEARS:
    if year in by_year:
        n, first_date, last_date = by_year[year]
        first_text, last_text = str(first_date), str(last_date)
        full_start, full_end = f"{year}-01-01", f"{year}-12-31"
        partial = first_text != full_start or last_text != full_end
        facts.extend([
            (f"rows_{year}", n),
            (f"coverage_{year}", f"{first_text} through {last_text}; {'partial' if partial else 'full'} calendar year"),
        ])
    else:
        facts.extend([
            (f"rows_{year}", 0),
            (f"coverage_{year}", "no dated rows; no coverage"),
        ])

for plan_id in (1, 2):
    with (OUT / f"check_{plan_id}.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)

summary = {
    "source_rows": population[0],
    "missing_date": population[1],
    "population_rows": population[2],
    "by_year": {str(year): {"rows": by_year[year][0], "first_date": str(by_year[year][1]), "last_date": str(by_year[year][2])} if year in by_year else {"rows": 0, "first_date": None, "last_date": None} for year in YEARS},
}
print(json.dumps(summary, indent=2))
