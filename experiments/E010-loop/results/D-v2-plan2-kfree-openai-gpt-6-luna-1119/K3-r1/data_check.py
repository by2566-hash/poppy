import csv
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
YEARS = range(2013, 2026)
DEATH_COLUMNS = [
    "number_of_motorist_killed",
    "number_of_cyclist_killed",
]


def write_checks(option_id: int) -> None:
    rows = []
    con = duckdb.connect()
    file_path = (ROOT / "data" / "crashes.parquet").as_posix().replace("'", "''")

    # Only date and the two planned death columns are inspected. No death values
    # are counted or aggregated here; only NULLs are checked.
    coverage = con.execute(
        f"""
        SELECT
          COUNT(*) FILTER (WHERE crash_date IS NULL) AS missing_date_all,
          MIN(crash_date) FILTER (
            WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
          ) AS first_target_date,
          MAX(crash_date) FILTER (
            WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
          ) AS last_target_date
        FROM read_parquet('{file_path}')
        """
    ).fetchone()
    rows.extend([
        ("rows_missing_crash_date_entire_file", coverage[0]),
        ("first_crash_date_in_target_years", coverage[1]),
        ("last_crash_date_in_target_years", coverage[2]),
    ])

    yearly_rows = con.execute(
        f"""
        SELECT EXTRACT(YEAR FROM crash_date)::INTEGER AS year, COUNT(*) AS rows
        FROM read_parquet('{file_path}')
        WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
        GROUP BY year
        """
    ).fetchall()
    row_counts = dict(yearly_rows)
    for year in YEARS:
        rows.append((f"rows_in_population_year_{year}", row_counts.get(year, 0)))

    # Missing death entries only, overall and by year. Do not inspect their
    # values (including zero) or compute any outcome sums in this check.
    for column in DEATH_COLUMNS:
        overall = con.execute(
            f"""
            SELECT COUNT(*) FILTER (WHERE {column} IS NULL)
            FROM read_parquet('{file_path}')
            WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
            """
        ).fetchone()[0]
        rows.append((f"missing_{column}_in_target_population", overall))
        per_year = con.execute(
            f"""
            SELECT EXTRACT(YEAR FROM crash_date)::INTEGER AS year,
                   COUNT(*) FILTER (WHERE {column} IS NULL) AS missing
            FROM read_parquet('{file_path}')
            WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
            GROUP BY year
            """
        ).fetchall()
        missing_by_year = dict(per_year)
        for year in YEARS:
            rows.append((f"missing_{column}_in_year_{year}", missing_by_year.get(year, 0)))

    # Exact endpoint dates indicate whether the target year's file coverage is
    # partial at the beginning or end of the requested period.
    for year in YEARS:
        endpoints = con.execute(
            f"""
            SELECT MIN(crash_date), MAX(crash_date)
            FROM read_parquet('{file_path}')
            WHERE crash_date >= DATE '{year}-01-01'
              AND crash_date < DATE '{year + 1}-01-01'
            """
        ).fetchone()
        rows.append((f"first_date_in_year_{year}", endpoints[0]))
        rows.append((f"last_date_in_year_{year}", endpoints[1]))

    with (OUT / f"check_{option_id}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(rows)
    con.close()


for option in (1, 2):
    write_checks(option)
