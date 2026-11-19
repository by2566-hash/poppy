from pathlib import Path

import duckdb
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "crashes.parquet"

con = duckdb.connect()
con.execute(
    "CREATE VIEW crashes AS SELECT crash_date, crash_time, number_of_persons_injured, number_of_persons_killed "
    f"FROM read_parquet('{DATA.as_posix()}')"
)

global_check = con.execute(
    """
    SELECT
      count(*) AS total_rows,
      count(*) FILTER (WHERE crash_date IS NULL) AS missing_crash_date,
      count(*) FILTER (WHERE crash_date IS NOT NULL) AS dated_rows,
      min(crash_date) AS first_date,
      max(crash_date) AS last_date
    FROM crashes
    """
).fetchone()

year_checks = con.execute(
    """
    SELECT
      year(crash_date) AS year,
      count(*) AS dated_rows,
      count(*) FILTER (WHERE crash_time IS NULL) AS missing_crash_time,
      count(*) FILTER (WHERE crash_time = TIME '00:00:00') AS midnight_time_rows,
      count(*) FILTER (WHERE number_of_persons_injured IS NULL) AS missing_persons_injured,
      count(*) FILTER (WHERE number_of_persons_killed IS NULL) AS missing_persons_killed,
      count(*) FILTER (
        WHERE crash_time IS NOT NULL
          AND number_of_persons_injured IS NOT NULL
          AND number_of_persons_killed IS NOT NULL
      ) AS eligible_rows,
      min(crash_date) AS first_observed_date,
      max(crash_date) AS last_observed_date
    FROM crashes
    WHERE crash_date IS NOT NULL
    GROUP BY year(crash_date)
    ORDER BY year
    """
).fetchdf()

for plan_id in (1, 2):
    facts = [
        ("source_total_rows", global_check[0]),
        ("rows_missing_crash_date_no_year", global_check[1]),
        ("rows_with_usable_calendar_year", global_check[2]),
        ("first_observed_date", str(global_check[3])),
        ("last_observed_date", str(global_check[4])),
        (
            "2013_2025_dated_candidate_rows",
            int(year_checks.loc[year_checks["year"].between(2013, 2025), "dated_rows"].sum()),
        ),
        (
            "2013_2025_eligible_rows_after_planned_filters",
            int(year_checks.loc[year_checks["year"].between(2013, 2025), "eligible_rows"].sum()),
        ),
        (
            "2013_2025_rows_excluded_for_missing_outcome_fields",
            int(
                (
                    year_checks.loc[year_checks["year"].between(2013, 2025), "dated_rows"]
                    - year_checks.loc[year_checks["year"].between(2013, 2025), "eligible_rows"]
                ).sum()
            ),
        ),
        ("2012_is_partial_calendar_year_and_will_be_excluded", "2012-07-01 through 2012-12-31"),
        ("2026_is_partial_calendar_year_and_will_be_excluded", "2026-01-01 through 2026-06-11"),
    ]
    for row in year_checks.itertuples(index=False):
        year = int(row.year)
        facts.extend([
            (f"{year}_dated_candidate_rows", int(row.dated_rows)),
            (f"{year}_missing_crash_time", int(row.missing_crash_time)),
            (f"{year}_midnight_time_rows_valid_but_check_for_pileup", int(row.midnight_time_rows)),
            (f"{year}_missing_number_of_persons_injured", int(row.missing_persons_injured)),
            (f"{year}_missing_number_of_persons_killed", int(row.missing_persons_killed)),
            (f"{year}_eligible_rows_after_planned_filters", int(row.eligible_rows)),
            (f"{year}_first_observed_date", str(row.first_observed_date)),
            (f"{year}_last_observed_date", str(row.last_observed_date)),
        ])
    pd.DataFrame(facts, columns=["fact", "value"]).to_csv(OUT / f"check_{plan_id}.csv", index=False)

con.close()
