import csv
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
con = duckdb.connect()
data_path = str(DATA).replace("'", "''")
con.execute(f"CREATE VIEW crashes AS SELECT crash_date FROM read_parquet('{data_path}')")

population = "crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'"
total = con.execute(f"SELECT count(*) FROM crashes WHERE {population}").fetchone()[0]
by_year = con.execute(
    f"""SELECT year(crash_date) AS yr, count(*) AS n,
               min(crash_date) AS first_date, max(crash_date) AS last_date
        FROM crashes WHERE {population} GROUP BY yr ORDER BY yr"""
).fetchall()
date_missing = con.execute(
    f"SELECT count(*) FROM crashes WHERE {population} AND crash_date IS NULL"
).fetchone()[0]
date_default = con.execute(
    f"""SELECT count(*) FROM crashes WHERE {population}
        AND crash_date IN (DATE '1900-01-01', DATE '1970-01-01')"""
).fetchone()[0]

facts = [
    ("population_rows_2013_2025", total),
    ("crash_date_missing_in_population_rows", date_missing),
    ("crash_date_default_1900_or_1970_in_population_rows", date_default),
]
for year, n, first_date, last_date in by_year:
    facts.extend([
        (f"rows_{year}", n),
        (f"first_date_{year}", first_date.isoformat()),
        (f"last_date_{year}", last_date.isoformat()),
        (f"year_{year}_partial_calendar_coverage", str(
            first_date.isoformat() != f"{year}-01-01"
            or last_date.isoformat() != f"{year}-12-31"
        ).lower()),
    ])

for option_id in (1, 2):
    with (OUT / f"check_{option_id}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)
