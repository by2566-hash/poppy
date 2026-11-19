import csv
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "crashes.parquet"
OUT_DIR = Path(__file__).resolve().parent


def main():
    con = duckdb.connect()
    parquet_path = str(DATA).replace("'", "''")
    con.execute(f"CREATE VIEW crashes AS SELECT crash_date, number_of_motorist_killed, number_of_cyclist_killed FROM read_parquet('{parquet_path}')")
    result = con.execute("""
        SELECT EXTRACT(YEAR FROM crash_date)::INTEGER AS year,
               COUNT(*) AS rows_in_year,
               COUNT(*) FILTER (WHERE number_of_motorist_killed IS NULL) AS motorist_missing,
               COUNT(*) FILTER (WHERE number_of_cyclist_killed IS NULL) AS cyclist_missing,
               COUNT(*) FILTER (WHERE number_of_motorist_killed IS NULL OR number_of_cyclist_killed IS NULL) AS either_missing,
               COUNT(*) FILTER (WHERE crash_date IS NULL) AS crash_date_missing,
               COUNT(*) FILTER (WHERE crash_date IN (DATE '1900-01-01', DATE '1970-01-01')) AS default_date_rows,
               MIN(crash_date) AS first_date,
               MAX(crash_date) AS last_date
        FROM crashes
        WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
        GROUP BY year
        ORDER BY year
    """).fetchall()

    facts = []
    rows_total = sum(row[1] for row in result)
    facts.append(("rows in population and years (2013-2025)", rows_total))
    for year, row_count, motorist_missing, cyclist_missing, either_missing, crash_date_missing, default_date_rows, first_date, last_date in result:
        facts.extend([
            (f"{year} rows in population", row_count),
            (f"{year} rows missing number_of_motorist_killed", motorist_missing),
            (f"{year} rows missing number_of_cyclist_killed", cyclist_missing),
            (f"{year} rows missing either death count (excluded by complete-pair rule)", either_missing),
            (f"{year} rows missing crash_date", crash_date_missing),
            (f"{year} observed crash_date coverage", f"{first_date} through {last_date}"),
            (f"{year} rows with default-like crash_date (1900-01-01 or 1970-01-01)", default_date_rows),
        ])
    facts.extend([
        ("rows with both death counts present (eligible for analysis)", rows_total - sum(row[4] for row in result)),
        ("years with no qualifying crash rows", ", ".join(str(y) for y in range(2013, 2026) if y not in {r[0] for r in result}) or "none"),
        ("year coverage note", "First and last observed crash dates are listed per year; a year is partial if coverage does not span January 1 through December 31."),
    ])

    for option_id in (1, 2):
        with (OUT_DIR / f"check_{option_id}.csv").open("w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["fact", "value"])
            writer.writerows(facts)
    con.close()


if __name__ == "__main__":
    main()
