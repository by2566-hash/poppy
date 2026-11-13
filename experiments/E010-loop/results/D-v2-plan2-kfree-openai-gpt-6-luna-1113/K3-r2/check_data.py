from pathlib import Path
import csv

import duckdb


ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "crashes.parquet"
source = f"read_parquet('{DATA.as_posix()}')"
population = f"""
    SELECT crash_date, number_of_motorist_killed, number_of_cyclist_killed
    FROM {source}
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
"""
con = duckdb.connect()
year_rows = con.execute(f"""
    SELECT EXTRACT(YEAR FROM crash_date)::INTEGER AS year,
           COUNT(*) AS rows,
           MIN(crash_date) AS first_date,
           MAX(crash_date) AS last_date
    FROM ({population})
    GROUP BY year
    ORDER BY year
""").fetchall()
total_rows = con.execute(f"SELECT COUNT(*) FROM ({population})").fetchone()[0]
missing = {
    name: con.execute(f"SELECT COUNT(*) FROM ({population}) WHERE {name} IS NULL").fetchone()[0]
    for name in ("number_of_motorist_killed", "number_of_cyclist_killed")
}
either_missing = con.execute(f"""
    SELECT COUNT(*) FROM ({population})
    WHERE number_of_motorist_killed IS NULL OR number_of_cyclist_killed IS NULL
""").fetchone()[0]
date_nulls = con.execute(f"SELECT COUNT(*) FROM ({population}) WHERE crash_date IS NULL").fetchone()[0]
default_dates = con.execute(f"""
    SELECT COUNT(*) FROM ({population})
    WHERE crash_date IN (DATE '1900-01-01', DATE '1970-01-01', DATE '2000-01-01')
""").fetchone()[0]

facts = [
    ("selected rows, all years 2013–2025", total_rows),
    *((f"rows in {year}", rows) for year, rows, _, _ in year_rows),
    *((f"{name}: missing rows among selected years", count) for name, count in missing.items()),
    ("rows with either summed killed field missing", either_missing),
    ("crash_date null among selected rows", date_nulls),
    ("crash_date rows at checked default dates 1900-01-01, 1970-01-01, 2000-01-01", default_dates),
    *((f"{year} date coverage", f"{first_date} through {last_date}") for year, _, first_date, last_date in year_rows),
]
for plan_id in (1, 2):
    with (OUT / f"check_{plan_id}.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("fact", "value"))
        writer.writerows(facts)
