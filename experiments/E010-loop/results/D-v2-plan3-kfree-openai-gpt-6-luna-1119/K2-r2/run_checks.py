import csv
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"
YEARS = range(2013, 2026)

con = duckdb.connect()
data_path = str(DATA).replace("'", "''")
con.execute(f"CREATE VIEW crashes AS SELECT crash_date FROM read_parquet('{data_path}')")

for option_id in (1, 2):
    facts = []

    def add(fact, value):
        facts.append((fact, str(value)))

    add("eligible_population_rows_2013_2025", con.execute("""
        SELECT COUNT(*) FROM crashes
        WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    """).fetchone()[0])
    add("rows_with_missing_crash_date_in_source_excluded_by_filter", con.execute("""
        SELECT COUNT(*) FROM crashes WHERE crash_date IS NULL
    """).fetchone()[0])
    add("rows_with_crash_date_outside_2013_2025_excluded_by_filter", con.execute("""
        SELECT COUNT(*) FROM crashes
        WHERE crash_date < DATE '2013-01-01' OR crash_date >= DATE '2026-01-01'
    """).fetchone()[0])
    add("crash_date_missing_or_unknown_within_population", 0)
    add("impossible_crash_date_values_within_population", 0)
    add("recognized_sentinel_dates_0001_1900_1970_within_population", con.execute("""
        SELECT COUNT(*) FROM crashes
        WHERE crash_date IN (DATE '0001-01-01', DATE '1900-01-01', DATE '1970-01-01')
          AND crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    """).fetchone()[0])

    by_year = con.execute("""
        SELECT YEAR(crash_date) AS year, COUNT(*) AS rows,
               MIN(crash_date) AS first_date, MAX(crash_date) AS last_date
        FROM crashes
        WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
        GROUP BY year ORDER BY year
    """).fetchall()
    found = {row[0]: row for row in by_year}
    for year in YEARS:
        row = found.get(year)
        if row:
            add(f"rows_{year}", row[1])
            add(f"first_crash_date_{year}", row[2])
            add(f"last_crash_date_{year}", row[3])
            first_full = f"{year}-01-01"
            last_full = f"{year}-12-31"
            add(f"year_{year}_coverage", "full calendar year" if str(row[2]) == first_full and str(row[3]) == last_full else "partial calendar year")
        else:
            add(f"rows_{year}", 0)
            add(f"first_crash_date_{year}", "none")
            add(f"last_crash_date_{year}", "none")
            add(f"year_{year}_coverage", "no crash dates in file")

    with (OUT / f"check_{option_id}.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)
