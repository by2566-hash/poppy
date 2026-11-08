import csv
import datetime
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"
YEARS = range(2013, 2026)
KILLED_COLUMNS = (
    "number_of_cyclist_killed",
    "number_of_motorist_killed",
)


def main():
    con = duckdb.connect()
    date_rows = con.execute(
        """
        SELECT EXTRACT(YEAR FROM crash_date)::INTEGER AS year,
               COUNT(*) AS row_count,
               MIN(crash_date) AS first_date,
               MAX(crash_date) AS last_date
        FROM read_parquet(?)
        WHERE crash_date >= DATE '2013-01-01'
          AND crash_date < DATE '2026-01-01'
        GROUP BY year
        """,
        [str(DATA)],
    ).fetchall()
    by_year = {year: (count, first, last) for year, count, first, last in date_rows}

    facts = []

    def add(fact, value):
        facts.append({"fact": fact, "value": value})

    total_rows = sum(row[0] for row in by_year.values())
    add("population rows, 2013-2025", total_rows)
    for year in YEARS:
        count, first_date, last_date = by_year.get(year, (0, None, None))
        add(f"population rows in {year}", count)
        if first_date is None:
            coverage = "no rows"
        else:
            expected_first = datetime.date(year, 1, 1)
            expected_last = datetime.date(year, 12, 31)
            coverage = (
                f"{first_date} through {last_date}; "
                f"{'full-year date span' if first_date == expected_first and last_date == expected_last else 'partial-year date span'}"
            )
        add(f"date coverage in {year}", coverage)

    # Check only the two planned death-count columns and rows within the planned years.
    for column in KILLED_COLUMNS:
        column_rows = con.execute(
            f"""
            SELECT EXTRACT(YEAR FROM crash_date)::INTEGER AS year,
                   COUNT(*) FILTER (WHERE {column} IS NULL),
                   COUNT(*) FILTER (WHERE {column} = 0),
                   COUNT(*) FILTER (WHERE {column} < 0)
            FROM read_parquet(?)
            WHERE crash_date >= DATE '2013-01-01'
              AND crash_date < DATE '2026-01-01'
            GROUP BY year
            """,
            [str(DATA)],
        ).fetchall()
        column_by_year = {row[0]: row[1:] for row in column_rows}
        totals = [0, 0, 0]
        for year in YEARS:
            counts = column_by_year.get(year, (0, 0, 0))
            totals = [total + count for total, count in zip(totals, counts)]
            add(f"{column}: missing/NULL rows in {year}", counts[0])
            add(f"{column}: zero/default-value rows in {year}", counts[1])
            add(f"{column}: impossible negative-value rows in {year}", counts[2])
        add(f"{column}: missing/NULL rows, all years", totals[0])
        add(f"{column}: zero/default-value rows, all years", totals[1])
        add(f"{column}: impossible negative-value rows, all years", totals[2])
        add(f"{column}: text empty/unknown values", "not applicable: column is numeric")

    with (OUT / "check_1.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["fact", "value"])
        writer.writeheader()
        writer.writerows(facts)
    with (OUT / "check_2.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["fact", "value"])
        writer.writeheader()
        writer.writerows(facts)
    con.close()


if __name__ == "__main__":
    main()
