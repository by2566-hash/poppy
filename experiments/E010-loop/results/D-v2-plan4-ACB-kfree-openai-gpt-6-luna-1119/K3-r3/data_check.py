import csv
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "crashes.parquet"
YEARS = range(2013, 2026)


def check(option_id: int) -> None:
    con = duckdb.connect()
    data_path = str(DATA).replace("'", "''")
    con.execute(f"CREATE VIEW crashes AS SELECT crash_date, number_of_motorist_killed, number_of_cyclist_killed FROM read_parquet('{data_path}')")
    rows = []

    def add(fact, value):
        rows.append({"fact": fact, "value": value})

    total = con.execute(
        """SELECT count(*) FROM crashes
           WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'"""
    ).fetchone()[0]
    add("population_rows_2013_2025", total)
    missing_dates = con.execute("SELECT count(*) FROM crashes WHERE crash_date IS NULL").fetchone()[0]
    add("missing_crash_date_rows_before_year_filter", missing_dates)

    for year in YEARS:
        start = f"{year}-01-01"
        end = f"{year + 1}-01-01"
        row_count, missing_motorist, missing_cyclist, first_date, last_date, epoch_day = con.execute(
            """SELECT count(*),
                      count(*) FILTER (WHERE number_of_motorist_killed IS NULL),
                      count(*) FILTER (WHERE number_of_cyclist_killed IS NULL),
                      min(crash_date), max(crash_date),
                      count(*) FILTER (WHERE crash_date = DATE '1970-01-01')
               FROM crashes WHERE crash_date >= CAST(? AS DATE) AND crash_date < CAST(? AS DATE)""",
            [start, end],
        ).fetchone()
        add(f"rows_{year}", row_count)
        add(f"missing_number_of_motorist_killed_rows_{year}", missing_motorist)
        add(f"missing_number_of_cyclist_killed_rows_{year}", missing_cyclist)
        add(f"crash_date_missing_rows_{year}", 0)
        add(f"crash_date_default_1970_01_01_rows_{year}", epoch_day)
        if row_count:
            partial = first_date.isoformat() != start or last_date.isoformat() != f"{year}-12-31"
            add(f"date_coverage_{year}", f"{first_date} through {last_date}; {'partial at year boundary' if partial else 'both calendar-year boundaries represented'}")
        else:
            add(f"date_coverage_{year}", "no rows; coverage unavailable")

    for col in ("number_of_motorist_killed", "number_of_cyclist_killed"):
        missing = con.execute(
            f"""SELECT count(*) FROM crashes WHERE crash_date >= DATE '2013-01-01'
                 AND crash_date < DATE '2026-01-01' AND {col} IS NULL"""
        ).fetchone()[0]
        add(f"missing_{col}_rows_2013_2025", missing)

    with (OUT / f"check_{option_id}.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["fact", "value"])
        writer.writeheader()
        writer.writerows(rows)
    con.close()


if __name__ == "__main__":
    check(1)
    check(2)
