import csv
import json
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
PARQUET = ROOT / "data" / "crashes.parquet"
CONNECTION = duckdb.connect()
CONNECTION.execute("SET threads = 2")

# Scope the check to Brooklyn and the plan's 2013-onward period. This first
# query checks only row counts and date coverage, not injury/death outcomes.
year_coverage = CONNECTION.execute(
    """
    SELECT year(crash_date) AS year,
           count(*) AS rows,
           min(crash_date) AS first_date,
           max(crash_date) AS last_date
    FROM read_parquet(?)
    WHERE upper(trim(borough)) = 'BROOKLYN'
      AND crash_date >= DATE '2013-01-01'
    GROUP BY year(crash_date)
    ORDER BY year
    """,
    [str(PARQUET)],
).fetchall()

complete_years = []
partial_years = []
for year, rows, first_date, last_date in year_coverage:
    if first_date.year == year and first_date.month == 1 and first_date.day == 1 and last_date.year == year and last_date.month == 12 and last_date.day == 31:
        complete_years.append(year)
    else:
        partial_years.append((year, first_date, last_date))

year_start = min(complete_years) if complete_years else None
year_end = max(complete_years) if complete_years else None
year_clause = ""
params = [str(PARQUET)]
if year_start is not None:
    year_clause = "AND crash_date >= CAST(? AS DATE) AND crash_date < CAST(? AS DATE)"
    params.extend([f"{year_start}-01-01", f"{year_end + 1}-01-01"])
else:
    # A false condition preserves a valid, empty result if no complete years exist.
    year_clause = "AND FALSE"

# All following checks are restricted to rows in the final plan's complete
# Brooklyn calendar years. Outcome columns are used only for NULL checks.
scope_facts = CONNECTION.execute(
    f"""
    SELECT count(*) AS rows,
           count(*) FILTER (WHERE borough IS NULL OR trim(borough) = '') AS borough_missing,
           count(*) FILTER (WHERE crash_date IS NULL) AS crash_date_missing,
           count(*) FILTER (WHERE upper(trim(borough)) IN ('UNKNOWN', 'UNSPECIFIED', 'N/A', 'NA', 'NULL', 'NONE', '0')) AS borough_default
    FROM read_parquet(?)
    WHERE upper(trim(borough)) = 'BROOKLYN'
      {year_clause}
    """,
    params,
).fetchone()

common_facts = [
    ("population_rows_complete_years", scope_facts[0]),
    ("borough_missing_rows_in_population", scope_facts[1]),
    ("borough_default_or_unknown_rows_in_population", scope_facts[3]),
    ("crash_date_missing_rows_in_population", scope_facts[2]),
    ("complete_years", ",".join(map(str, complete_years))),
    ("partial_years_in_2013_onward_scope", json.dumps([
        {"year": year, "first_date": str(first), "last_date": str(last)}
        for year, first, last in partial_years
    ])),
    ("incomplete_or_unrepresented_calendar_years", json.dumps([
        year for year in range(2013, (max(y for y, *_ in year_coverage) + 1) if year_coverage else 2013)
        if year not in {entry[0] for entry in year_coverage}
    ])),
]
year_facts = []
for year, rows, first_date, last_date in year_coverage:
    year_facts.append((f"rows_year_{year}", rows))
    year_facts.append((f"date_coverage_year_{year}", f"{first_date} through {last_date}"))

for option_id, outcome_columns in (
    (1, ["number_of_pedestrians_injured", "number_of_pedestrians_killed"]),
    (2, ["number_of_pedestrians_killed"]),
):
    outcome_checks = ", ".join(
        f"count(*) FILTER (WHERE {column} IS NULL)" for column in outcome_columns
    )
    missing_counts = CONNECTION.execute(
        f"""
        SELECT {outcome_checks}
        FROM read_parquet(?)
        WHERE upper(trim(borough)) = 'BROOKLYN'
          {year_clause}
        """,
        params,
    ).fetchone()
    facts = list(common_facts) + year_facts
    facts.extend(
        (f"missing_{column}_rows", count)
        for column, count in zip(outcome_columns, missing_counts)
    )
    with (OUT / f"check_{option_id}.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)

CONNECTION.close()
