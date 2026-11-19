import csv
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parent.parent
DATA = str(ROOT / "data" / "crashes.parquet")
YEARS = range(2013, 2026)


def check(plan_id: int) -> None:
    con = duckdb.connect()
    data_sql_path = DATA.replace("'", "''")
    con.execute(f"CREATE VIEW crashes AS SELECT crash_date FROM read_parquet('{data_sql_path}')")
    facts: list[tuple[str, str]] = []

    total, null_dates, sentinel_1970, sentinel_1900, sentinel_2000, sentinel_min = con.execute(
        """
        SELECT count(*), count(*) FILTER (WHERE crash_date IS NULL),
               count(*) FILTER (WHERE crash_date = DATE '1970-01-01'),
               count(*) FILTER (WHERE crash_date = DATE '1900-01-01'),
               count(*) FILTER (WHERE crash_date = DATE '2000-01-01'),
               count(*) FILTER (WHERE crash_date = DATE '0001-01-01')
        FROM crashes
        """
    ).fetchone()
    facts.extend(
        [
            ("rows_in_file", str(total)),
            ("missing_crash_date_rows_in_file", str(null_dates)),
            ("crash_date_1970-01-01_rows_in_file", str(sentinel_1970)),
            ("crash_date_1900-01-01_rows_in_file", str(sentinel_1900)),
            ("crash_date_2000-01-01_rows_in_file", str(sentinel_2000)),
            ("crash_date_0001-01-01_rows_in_file", str(sentinel_min)),
            ("impossible_crash_date_rows", "0 (DATE type; impossible calendar dates cannot be stored)"),
            ("empty_or_unknown_crash_date_values", "0 (DATE type; only NULL can represent missing)"),
        ]
    )

    start, end = 2013, 2025
    population, outside_period = con.execute(
        """
        SELECT count(*) FILTER (WHERE crash_date >= make_date(?, 1, 1)
                                  AND crash_date < make_date(?, 1, 1)),
               count(*) FILTER (WHERE crash_date < make_date(?, 1, 1)
                                  OR crash_date >= make_date(?, 1, 1))
        FROM crashes WHERE crash_date IS NOT NULL
        """,
        [start, end + 1, start, end + 1],
    ).fetchone()
    facts.append(("population_rows_2013-2025", str(population)))
    facts.append(("dated_rows_outside_2013-2025_excluded", str(outside_period)))

    yearly = con.execute(
        """
        SELECT year(crash_date) AS yr, count(*) AS rows,
               min(crash_date) AS first_date, max(crash_date) AS last_date
        FROM crashes
        WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
        GROUP BY yr ORDER BY yr
        """
    ).fetchall()
    year_data = {int(row[0]): row for row in yearly}
    for year in YEARS:
        row = year_data.get(year)
        if row is None:
            facts.append((f"rows_{year}", "0"))
            facts.append((f"date_bounds_{year}", "no dated crash rows"))
            facts.append((f"year_coverage_{year}", "no dated crash rows; coverage not established"))
            continue
        _, count, first_date, last_date = row
        facts.append((f"rows_{year}", str(count)))
        facts.append((f"date_bounds_{year}", f"{first_date} through {last_date}"))
        partial = first_date.isoformat() != f"{year}-01-01" or last_date.isoformat() != f"{year}-12-31"
        facts.append(
            (
                f"year_coverage_{year}",
                "appears partial from observed crash-date bounds" if partial else "observed bounds span Jan 1–Dec 31; completeness cannot be verified from crash rows alone",
            )
        )

    in_period_1970, in_period_1900, in_period_2000, in_period_min, in_period_missing = con.execute(
        """
        SELECT count(*) FILTER (WHERE crash_date = DATE '1970-01-01'),
               count(*) FILTER (WHERE crash_date = DATE '1900-01-01'),
               count(*) FILTER (WHERE crash_date = DATE '2000-01-01'),
               count(*) FILTER (WHERE crash_date = DATE '0001-01-01'),
               count(*) FILTER (WHERE crash_date IS NULL)
        FROM crashes
        WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
        """
    ).fetchone()
    facts.extend(
        [
            ("crash_date_1970-01-01_rows_in_plan_years", str(in_period_1970)),
            ("crash_date_1900-01-01_rows_in_plan_years", str(in_period_1900)),
            ("crash_date_2000-01-01_rows_in_plan_years", str(in_period_2000)),
            ("crash_date_0001-01-01_rows_in_plan_years", str(in_period_min)),
            ("missing_crash_date_rows_in_plan_years_before_filter", str(in_period_missing)),
            ("weekday_group_missing_rows_in_population", "0; every population row has a valid DATE for weekday derivation"),
        ]
    )
    con.close()

    with (ROOT / "out" / f"check_{plan_id}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)


if __name__ == "__main__":
    check(1)
    check(2)
