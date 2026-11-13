import calendar
import csv
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
DATA = str(ROOT / "data" / "crashes.parquet")
OUT = Path(__file__).resolve().parent

con = duckdb.connect()
year_rows = con.execute(
    """
    SELECT EXTRACT(YEAR FROM crash_date)::INTEGER AS year,
           COUNT(*) AS rows,
           MIN(crash_date) AS first_date,
           MAX(crash_date) AS last_date,
           COUNT(*) FILTER (WHERE crash_time IS NULL) AS time_missing,
           COUNT(*) FILTER (WHERE crash_time = TIME '00:00:00') AS time_default_midnight,
           COUNT(*) FILTER (
               WHERE crash_time = TIME '00:00:00'
                 AND number_of_persons_injured IS NOT NULL
                 AND number_of_persons_killed IS NOT NULL
           ) AS eligible_midnight,
           COUNT(*) FILTER (WHERE number_of_persons_injured IS NULL) AS injured_missing,
           COUNT(*) FILTER (WHERE number_of_persons_killed IS NULL) AS killed_missing,
           COUNT(*) FILTER (
               WHERE crash_time IS NOT NULL
                 AND number_of_persons_injured IS NOT NULL
                 AND number_of_persons_killed IS NOT NULL
           ) AS eligible_rows,
           COUNT(*) FILTER (WHERE crash_date = DATE '1900-01-01') AS date_default_1900,
           COUNT(*) FILTER (WHERE crash_date = DATE '0001-01-01') AS date_default_year1
    FROM read_parquet(?)
    WHERE crash_date IS NOT NULL
    GROUP BY year
    ORDER BY year
    """,
    [DATA],
).fetchall()
date_missing = con.execute(
    "SELECT COUNT(*) FROM read_parquet(?) WHERE crash_date IS NULL", [DATA]
).fetchone()[0]

for plan_id in (1, 2):
    complete_years = [row for row in year_rows if 2013 <= row[0] <= 2025]
    facts = [
        ("rows_with_nonmissing_crash_date_all_years", sum(row[1] for row in year_rows)),
        ("rows_with_missing_crash_date_outside_year_population", date_missing),
        ("crash_date_type_and_nontext_missing_values", "DATE type: only NULL can represent missing; text/unknown/impossible dates cannot be encoded"),
        ("crash_time_type_and_nontext_missing_values", "TIME type: only NULL can represent missing; text/unknown/impossible times cannot be encoded"),
        ("injury_death_count_type_and_nontext_missing_values", "INT types: only NULL can represent missing; text/unknown/impossible counts cannot be encoded"),
        ("rows_2013_2025_with_nonmissing_crash_date", sum(row[1] for row in complete_years)),
        ("rows_2013_2025_passing_time_and_outcome_missingness_filters", sum(row[9] for row in complete_years)),
        ("rows_2013_2025_excluded_for_missing_outcome_count", sum(row[1] - row[9] for row in complete_years)),
        ("crash_time_missing_rows_2013_2025", sum(row[4] for row in complete_years)),
        ("crash_time_midnight_default_candidate_rows_2013_2025", sum(row[5] for row in complete_years)),
        ("crash_time_midnight_rows_passing_outcome_filters_2013_2025", sum(row[6] for row in complete_years)),
        ("number_of_persons_injured_missing_rows_2013_2025", sum(row[7] for row in complete_years)),
        ("number_of_persons_killed_missing_rows_2013_2025", sum(row[8] for row in complete_years)),
        ("rows_2012_and_2026_excluded_as_partial_years", sum(row[1] for row in year_rows if row[0] in (2012, 2026))),
    ]
    for row in year_rows:
        year, rows, first_date, last_date, time_missing, midnight, midnight_eligible, injured_missing, killed_missing, eligible, date_1900, date_y1 = row
        days_in_year = 366 if calendar.isleap(year) else 365
        is_partial = first_date.year != year or first_date.timetuple().tm_yday != 1 or last_date.month != 12 or last_date.day != 31
        facts.extend([
            (f"rows_{year}_with_nonmissing_crash_date", rows),
            (f"rows_{year}_passing_time_and_outcome_missingness_filters", eligible),
            (f"crash_time_missing_rows_{year}", time_missing),
            (f"crash_time_midnight_default_candidate_rows_{year}", midnight),
            (f"crash_time_midnight_rows_passing_outcome_filters_{year}", midnight_eligible),
            (f"number_of_persons_injured_missing_rows_{year}", injured_missing),
            (f"number_of_persons_killed_missing_rows_{year}", killed_missing),
            (f"crash_date_1900_default_candidate_rows_{year}", date_1900),
            (f"crash_date_year_1_default_candidate_rows_{year}", date_y1),
            (f"year_{year}_file_coverage", f"first={first_date}; last={last_date}; calendar_days={days_in_year}; partial_year={str(is_partial).lower()}"),
        ])
    with (OUT / f"check_{plan_id}.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)

con.close()
