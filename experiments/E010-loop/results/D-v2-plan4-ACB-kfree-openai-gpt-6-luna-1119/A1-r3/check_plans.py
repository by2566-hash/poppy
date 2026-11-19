import csv
from pathlib import Path

import duckdb


DATA = "data/crashes.parquet"
OUT = Path("out")
con = duckdb.connect()

# Discover the planned endpoint using only the date column.
date_bounds = con.execute(
    f"""
    SELECT MIN(crash_date), MAX(crash_date)
    FROM read_parquet('{DATA}')
    WHERE crash_date >= DATE '2013-01-01'
    """
).fetchone()
if date_bounds[1] is None:
    raise RuntimeError("No crashes on or after 2013-01-01 were found")
last_year = date_bounds[1].year
years = list(range(2013, last_year + 1))

for plan_id in (1, 2, 3):
    # The selected columns and date window are exactly those specified by the plans.
    row = con.execute(
        f"""
        SELECT
            COUNT(*) AS window_rows,
            COUNT(*) FILTER (WHERE crash_date IS NULL) AS missing_date_rows,
            COUNT(*) FILTER (
                WHERE UPPER(TRIM(COALESCE(borough, ''))) = 'BROOKLYN'
            ) AS brooklyn_rows,
            COUNT(*) FILTER (
                WHERE UPPER(TRIM(COALESCE(borough, ''))) NOT IN
                    ('BRONX', 'BROOKLYN', 'MANHATTAN', 'QUEENS', 'STATEN ISLAND')
            ) AS borough_missing_or_invalid_rows,
            COUNT(*) FILTER (
                WHERE UPPER(TRIM(COALESCE(borough, ''))) = 'BROOKLYN'
                  AND (number_of_pedestrians_injured IS NULL
                       OR number_of_pedestrians_killed IS NULL)
            ) AS brooklyn_rows_missing_any_ped_outcome,
            COUNT(*) FILTER (
                WHERE UPPER(TRIM(COALESCE(borough, ''))) = 'BROOKLYN'
                  AND number_of_pedestrians_injured IS NULL
            ) AS brooklyn_rows_missing_ped_injured,
            COUNT(*) FILTER (
                WHERE UPPER(TRIM(COALESCE(borough, ''))) = 'BROOKLYN'
                  AND number_of_pedestrians_killed IS NULL
            ) AS brooklyn_rows_missing_ped_killed
        FROM read_parquet('{DATA}')
        WHERE crash_date >= DATE '2013-01-01'
          AND crash_date < DATE '{last_year + 1}-01-01'
        """
    ).fetchone()
    (window_rows, missing_dates, brooklyn_rows, borough_missing,
     any_ped_missing, injured_missing, killed_missing) = row

    facts = [
        ("planned_years", f"2013-{last_year}"),
        ("years_in_window_rows", window_rows),
        ("rows_with_missing_crash_date_in_date_window", missing_dates),
        ("rows_with_brooklyn_borough_in_date_window", brooklyn_rows),
        ("rows_with_missing_or_invalid_borough_before_borough_filter_in_date_window", borough_missing),
        ("Brooklyn_rows_missing_pedestrian_injured_in_date_window", injured_missing),
        ("Brooklyn_rows_missing_pedestrian_killed_in_date_window", killed_missing),
        ("Brooklyn_rows_missing_either_pedestrian_outcome_in_date_window", any_ped_missing),
        ("crash_date_coverage_minimum", date_bounds[0].isoformat()),
        ("crash_date_coverage_maximum", date_bounds[1].isoformat()),
        ("first_year_partial", date_bounds[0].isoformat() != f"2013-01-01"),
        ("last_year_partial", date_bounds[1].isoformat() != f"{last_year}-12-31"),
    ]

    final_last_year = last_year - 1 if date_bounds[1].isoformat() != f"{last_year}-12-31" else last_year
    final_totals = con.execute(
        f"""
        SELECT COUNT(*) AS all_rows,
               COUNT(*) FILTER (
                   WHERE UPPER(TRIM(COALESCE(borough, ''))) = 'BROOKLYN'
               ) AS brooklyn_rows,
               COUNT(*) FILTER (
                   WHERE UPPER(TRIM(COALESCE(borough, ''))) NOT IN
                       ('BRONX', 'BROOKLYN', 'MANHATTAN', 'QUEENS', 'STATEN ISLAND')
               ) AS borough_missing_or_invalid
        FROM read_parquet('{DATA}')
        WHERE crash_date >= DATE '2013-01-01'
          AND crash_date < DATE '{final_last_year + 1}-01-01'
        """
    ).fetchone()
    facts.extend([
        (f"final_full_years", f"2013-{final_last_year}"),
        ("final_full_years_all_crash_rows", final_totals[0]),
        ("final_full_years_Brooklyn_crash_rows", final_totals[1]),
        ("final_full_years_missing_or_invalid_borough_rows", final_totals[2]),
    ])

    for year in years:
        bounds = con.execute(
            f"""
            SELECT MIN(crash_date), MAX(crash_date),
                   COUNT(*) AS all_rows,
                   COUNT(*) FILTER (
                       WHERE UPPER(TRIM(COALESCE(borough, ''))) = 'BROOKLYN'
                   ) AS brooklyn_rows,
                   COUNT(*) FILTER (
                       WHERE UPPER(TRIM(COALESCE(borough, ''))) NOT IN
                           ('BRONX', 'BROOKLYN', 'MANHATTAN', 'QUEENS', 'STATEN ISLAND')
                   ) AS borough_missing_or_invalid,
                   COUNT(*) FILTER (
                       WHERE UPPER(TRIM(COALESCE(borough, ''))) = 'BROOKLYN'
                         AND number_of_pedestrians_injured IS NULL
                   ) AS injured_missing,
                   COUNT(*) FILTER (
                       WHERE UPPER(TRIM(COALESCE(borough, ''))) = 'BROOKLYN'
                         AND number_of_pedestrians_killed IS NULL
                   ) AS killed_missing,
                   COUNT(*) FILTER (
                       WHERE UPPER(TRIM(COALESCE(borough, ''))) = 'BROOKLYN'
                         AND (number_of_pedestrians_injured IS NULL
                              OR number_of_pedestrians_killed IS NULL)
                   ) AS any_ped_missing
            FROM read_parquet('{DATA}')
            WHERE crash_date >= DATE '{year}-01-01'
              AND crash_date < DATE '{year + 1}-01-01'
            """
        ).fetchone()
        min_date, max_date, all_rows, bk_rows, bad_borough, inj_miss, kill_miss, any_miss = bounds
        facts.extend([
            (f"{year}_all_crash_rows", all_rows),
            (f"{year}_Brooklyn_crash_rows", bk_rows),
            (f"{year}_missing_or_invalid_borough_before_filter_rows", bad_borough),
            (f"{year}_Brooklyn_rows_missing_pedestrian_injured", inj_miss),
            (f"{year}_Brooklyn_rows_missing_pedestrian_killed", kill_miss),
            (f"{year}_Brooklyn_rows_missing_either_pedestrian_outcome", any_miss),
            (f"{year}_observed_date_range", f"{min_date.isoformat()} to {max_date.isoformat()}"),
            (f"{year}_partial_year", min_date.isoformat() != f"{year}-01-01" or max_date.isoformat() != f"{year}-12-31"),
        ])

    # crash_date is also the time grouping field; check missing dates among Brooklyn rows.
    null_brooklyn_dates = con.execute(
        f"""
        SELECT COUNT(*)
        FROM read_parquet('{DATA}')
        WHERE UPPER(TRIM(COALESCE(borough, ''))) = 'BROOKLYN'
          AND crash_date IS NULL
        """
    ).fetchone()[0]
    facts.append(("Brooklyn_rows_missing_grouping_date", null_brooklyn_dates))

    with (OUT / f"check_{plan_id}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)

con.close()
