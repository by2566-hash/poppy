import csv
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"

con = duckdb.connect()
data_path = str(DATA).replace("'", "''")
con.execute(
    f"CREATE VIEW crashes AS SELECT crash_date, number_of_motorist_killed FROM read_parquet('{data_path}')"
)

# Check the date filter before applying it, then check year populations and
# outcome-field missingness inside the planned 2013-2025 years. No outcomes
# are summed or counted by value in this data-quality step.
source_rows, missing_dates = con.execute(
    "SELECT count(*), count(*) FILTER (WHERE crash_date IS NULL) FROM crashes"
).fetchone()
year_rows = con.execute(
    """
    SELECT year(crash_date) AS year, count(*) AS rows,
           min(crash_date) AS first_date, max(crash_date) AS last_date,
           count(*) FILTER (WHERE number_of_motorist_killed IS NULL) AS missing_motorist_deaths
    FROM crashes
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
    """
).fetchall()

facts = [
    ("source_rows_checked_for_crash_date_filter", source_rows),
    ("source_rows_with_missing_crash_date_excluded_from_year_grouping", missing_dates),
]
observed = {row[0]: row for row in year_rows}
for year in range(2013, 2026):
    if year not in observed:
        facts.extend([
            (f"rows_in_{year}_population_before_outcome_missingness", 0),
            (f"{year}_date_coverage", "no dated rows"),
        (f"missing_number_of_motorist_killed_in_{year}_population", 0),
        ])
        continue
    _, count, first_date, last_date, missing_outcome = observed[year]
    partial = first_date.year > year or (first_date.year == year and (first_date.month, first_date.day) > (1, 1))
    partial = partial or last_date.year < year or (last_date.year == year and (last_date.month, last_date.day) < (12, 31))
    facts.extend([
        (f"rows_in_{year}_population_before_outcome_missingness", count),
        (f"{year}_date_coverage", f"{first_date} through {last_date}; {'partial' if partial else 'full calendar-year endpoints observed'}"),
        (f"missing_number_of_motorist_killed_in_{year}_population", missing_outcome),
    ])

for plan_id in (1, 2):
    path = OUT / f"check_{plan_id}.csv"
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)
