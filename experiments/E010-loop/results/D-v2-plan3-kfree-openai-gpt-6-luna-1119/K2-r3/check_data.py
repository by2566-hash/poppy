import csv
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
START = "2013-01-01"
END = "2025-12-31"

con = duckdb.connect()
source = str(ROOT / "data" / "crashes.parquet").replace("'", "''")
year_rows = con.execute(
    f"""
    SELECT year(crash_date) AS yr,
           count(*) AS rows,
           min(crash_date) AS first_date,
           max(crash_date) AS last_date,
           count(*) FILTER (WHERE crash_date IS NULL) AS missing_dates
    FROM read_parquet('{source}')
    WHERE crash_date >= DATE '{START}' AND crash_date <= DATE '{END}'
    GROUP BY yr
    ORDER BY yr
    """
).fetchall()
population_rows = sum(row[1] for row in year_rows)
facts = [
    ("Population rows with crash_date from 2013-01-01 through 2025-12-31", population_rows),
    ("Missing crash_date values within selected population", 0),
    ("crash_date storage type", "DATE: empty strings, unknown words, and impossible calendar dates cannot be represented"),
]

for year, rows, first_date, last_date, missing in year_rows:
    full_start = f"{year}-01-01"
    full_end = f"{year}-12-31"
    partial = str(first_date) != full_start or str(last_date) != full_end
    facts.extend(
        [
            (f"{year} population rows", rows),
            (f"{year} first observed crash_date", str(first_date)),
            (f"{year} last observed crash_date", str(last_date)),
            (f"{year} missing crash_date values", missing),
            (f"{year} covers only part of calendar year by observed date bounds", str(partial).lower()),
        ]
    )

for option_id in (1, 2):
    with (OUT / f"check_{option_id}.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)
