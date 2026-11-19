import csv
from pathlib import Path

import duckdb


DATA = "data/crashes.parquet"
OUT = Path("out")
con = duckdb.connect()

# This check is restricted to date/time grouping fields and the outcome fields
# used by the three initial plans. It deliberately never aggregates outcome
# values, only NULL counts.
year_rows = con.execute(
    f"""
    SELECT year(crash_date) AS yr, min(crash_date) AS first_date,
           max(crash_date) AS last_date, count(*) AS n
    FROM read_parquet('{DATA}')
    WHERE crash_date IS NOT NULL
    GROUP BY yr ORDER BY yr
    """
).fetchall()
missing_date_rows = con.execute(
    f"SELECT count(*) FROM read_parquet('{DATA}') WHERE crash_date IS NULL"
).fetchone()[0]
complete_years = [
    yr for yr, first, last, _ in year_rows
    if first.month == 1 and first.day == 1 and last.month == 12 and last.day == 31
]
complete_clause = "(" + ",".join(map(str, complete_years)) + ")" if complete_years else "(NULL)"

year_coverage = "; ".join(
    f"{yr}: {first.isoformat()} to {last.isoformat()} ({n} dated rows; "
    f"{'complete by date extent' if yr in complete_years else 'partial by date extent'})"
    for yr, first, last, n in year_rows
)

base = f"""
    FROM read_parquet('{DATA}')
    WHERE crash_date IS NOT NULL AND year(crash_date) IN {complete_clause}
"""
base_count = con.execute(f"SELECT count(*) {base}").fetchone()[0]
per_year = con.execute(
    f"SELECT year(crash_date), count(*) {base} GROUP BY 1 ORDER BY 1"
).fetchall()
time_facts = con.execute(
    f"""
    SELECT
      count(*) FILTER (WHERE crash_time IS NULL) AS null_time,
      count(*) FILTER (WHERE lower(trim(CAST(crash_time AS VARCHAR))) IN
        ('', 'unknown', 'unspecified', 'n/a', 'na', 'null', 'none')) AS placeholder_time,
      count(*) FILTER (WHERE try_cast(crash_time AS TIME) IS NULL AND crash_time IS NOT NULL) AS invalid_time,
      count(*) FILTER (WHERE crash_time = TIME '00:00:00') AS midnight_time
    {base}
    """
).fetchone()

for option, outcomes in {
    1: [],
    2: ["number_of_persons_injured", "number_of_persons_killed"],
    3: ["number_of_persons_injured"],
}.items():
    eligible_condition = " AND ".join(f"{column} IS NOT NULL" for column in outcomes) or "TRUE"
    eligible_total = con.execute(
        f"SELECT count(*) {base} AND {eligible_condition}"
    ).fetchone()[0]
    eligible_by_year = con.execute(
        f"SELECT year(crash_date), count(*) {base} AND {eligible_condition} "
        "GROUP BY 1 ORDER BY 1"
    ).fetchall()
    facts = [
        ("file_year_coverage_and_partial_years", year_coverage),
        ("crash_date_missing_null_rows_excluded_no_year", missing_date_rows),
        ("complete_calendar_years_used", ", ".join(map(str, complete_years))),
        ("population_rows_all_complete_years_with_nonnull_crash_date", base_count),
    ]
    facts.extend((f"population_rows_year_{yr}", count) for yr, count in per_year)
    facts.append(("final_eligible_population_rows_all_complete_years", eligible_total))
    facts.extend((f"final_eligible_population_rows_year_{yr}", count) for yr, count in eligible_by_year)
    facts.extend([
        ("crash_time_missing_null_rows", time_facts[0]),
        ("crash_time_placeholder_string_rows", time_facts[1]),
        ("crash_time_invalid_nonnull_rows", time_facts[2]),
        ("crash_time_midnight_rows_possible_default_review", time_facts[3]),
    ])
    for column in outcomes:
        missing = con.execute(f"SELECT count(*) FILTER (WHERE {column} IS NULL) {base}").fetchone()[0]
        facts.append((f"{column}_missing_null_rows_only", missing))
    with (OUT / f"check_{option}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)
