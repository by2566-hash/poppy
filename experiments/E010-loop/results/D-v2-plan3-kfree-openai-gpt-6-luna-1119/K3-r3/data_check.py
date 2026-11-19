import csv
from pathlib import Path

import duckdb


DATA = Path("data/crashes.parquet")
OUT = Path("out")
YEARS = range(2013, 2026)
START = "2013-01-01"
END = "2026-01-01"
OUTCOMES = ("number_of_motorist_killed", "number_of_cyclist_killed")

con = duckdb.connect()
relation = "read_parquet('data/crashes.parquet')"
period = f"crash_date >= DATE '{START}' AND crash_date < DATE '{END}'"

for option_id in (1, 2):
    facts = []

    def add(fact, value):
        facts.append((fact, value))

    total = con.execute(
        f"SELECT COUNT(*) FROM {relation} WHERE {period}"
    ).fetchone()[0]
    add("population_rows_2013_2025", total)

    yearly = con.execute(
        f"""SELECT YEAR(crash_date) AS year, COUNT(*) AS rows,
                   MIN(crash_date) AS first_crash_date,
                   MAX(crash_date) AS last_crash_date
            FROM {relation}
            WHERE {period}
            GROUP BY YEAR(crash_date)
            ORDER BY year"""
    ).fetchall()
    by_year = {row[0]: row[1:] for row in yearly}
    for year in YEARS:
        count, first, last = by_year.get(year, (0, None, None))
        add(f"rows_{year}", count)
        add(f"first_crash_date_{year}", first)
        add(f"last_crash_date_{year}", last)
        add(f"crash_date_missing_{year}", 0)
        for sentinel in ("1900-01-01", "1970-01-01"):
            count = con.execute(
                f"SELECT COUNT(*) FROM {relation} WHERE {period} "
                f"AND crash_date = DATE '{sentinel}' AND YEAR(crash_date) = {year}"
            ).fetchone()[0]
            add(f"crash_date_default_sentinel_{sentinel}_{year}", count)

    for column in OUTCOMES:
        missing = con.execute(
            f"SELECT COUNT(*) FROM {relation} WHERE {period} AND {column} IS NULL"
        ).fetchone()[0]
        add(f"{column}_missing_2013_2025", missing)
        for year in YEARS:
            missing_year = con.execute(
                f"SELECT COUNT(*) FROM {relation} WHERE {period} "
                f"AND YEAR(crash_date) = {year} AND {column} IS NULL"
            ).fetchone()[0]
            add(f"{column}_missing_{year}", missing_year)

    with (OUT / f"check_{option_id}.csv").open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(("fact", "value"))
        writer.writerows(facts)

con.close()
