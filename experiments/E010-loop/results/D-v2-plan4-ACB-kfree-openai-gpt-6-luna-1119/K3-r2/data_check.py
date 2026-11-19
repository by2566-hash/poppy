import csv
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parent.parent
PARQUET = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"
YEARS = range(2013, 2026)
OUTCOME_COLUMNS = (
    "number_of_motorist_killed",
    "number_of_cyclist_killed",
)


def main():
    con = duckdb.connect()
    source = str(PARQUET).replace("'", "''")
    in_years = "crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'"
    rows = con.execute(
        f"SELECT EXTRACT(YEAR FROM crash_date)::INTEGER AS year, COUNT(*) AS rows, "
        f"MIN(crash_date) AS first_date, MAX(crash_date) AS last_date, "
        f"COUNT(*) FILTER (WHERE number_of_motorist_killed IS NULL) AS motorist_missing, "
        f"COUNT(*) FILTER (WHERE number_of_cyclist_killed IS NULL) AS cyclist_missing "
        f"FROM read_parquet('{source}') WHERE {in_years} GROUP BY year ORDER BY year"
    ).fetchall()

    total_rows = con.execute(
        f"SELECT COUNT(*) FROM read_parquet('{source}') WHERE {in_years}"
    ).fetchone()[0]
    unknown_dates = con.execute(
        f"SELECT COUNT(*) FROM read_parquet('{source}') WHERE crash_date IS NULL"
    ).fetchone()[0]
    default_dates = con.execute(
        f"SELECT COUNT(*) FROM read_parquet('{source}') "
        "WHERE crash_date IN (DATE '1900-01-01', DATE '1970-01-01')"
    ).fetchone()[0]

    facts = [
        ("population_rows_2013_2025", total_rows),
        ("crash_date_missing_rows_all_file_unassignable_to_year", unknown_dates),
        ("crash_date_rows_at_1900_or_1970_default_dates_all_file", default_dates),
    ]
    by_year = {year: None for year in YEARS}
    for year, count, first_date, last_date, motorist_missing, cyclist_missing in rows:
        by_year[year] = (count, first_date, last_date, motorist_missing, cyclist_missing)

    for year in YEARS:
        item = by_year[year]
        facts.append((f"population_rows_{year}", 0 if item is None else item[0]))
        facts.append((f"first_crash_date_{year}", "none" if item is None else str(item[1])))
        facts.append((f"last_crash_date_{year}", "none" if item is None else str(item[2])))
        facts.append((f"number_of_motorist_killed_missing_rows_{year}", 0 if item is None else item[3]))
        facts.append((f"number_of_cyclist_killed_missing_rows_{year}", 0 if item is None else item[4]))

    with (OUT / "check_1.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(("fact", "value"))
        writer.writerows(facts)
    with (OUT / "check_2.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(("fact", "value"))
        writer.writerows(facts)


if __name__ == "__main__":
    main()
