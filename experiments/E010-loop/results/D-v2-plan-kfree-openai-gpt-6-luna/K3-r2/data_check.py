import csv
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "crashes.parquet"
OUT = Path(__file__).resolve().parent
YEARS = range(2013, 2026)
KILL_COLUMNS = ["number_of_cyclist_killed", "number_of_motorist_killed"]

con = duckdb.connect()
data_path = str(DATA).replace("'", "''")
con.execute(f"CREATE VIEW planned_rows AS SELECT crash_date, number_of_cyclist_killed, number_of_motorist_killed FROM read_parquet('{data_path}') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'")

year_rows = con.execute("""
    SELECT year(crash_date) AS year, count(*) AS rows,
           min(crash_date) AS first_date, max(crash_date) AS last_date
    FROM planned_rows
    GROUP BY year ORDER BY year
""").fetchall()
by_year = {row[0]: row for row in year_rows}
total_rows = con.execute("SELECT count(*) FROM planned_rows").fetchone()[0]

facts = []
facts.append(("population_rows_in_2013_2025", total_rows))
for year in YEARS:
    row = by_year.get(year)
    if row is None:
        facts.append((f"rows_{year}", 0))
        facts.append((f"date_coverage_{year}", "no qualifying rows"))
    else:
        facts.append((f"rows_{year}", row[1]))
        facts.append((f"date_coverage_{year}", f"{row[2]} to {row[3]}"))
        complete = row[2].isoformat() <= f"{year}-01-01" and row[3].isoformat() >= f"{year}-12-31"
        facts.append((f"calendar_year_complete_{year}", str(complete).lower()))

for column in KILL_COLUMNS:
    stats = con.execute(f"""
        SELECT count(*) FILTER (WHERE {column} IS NULL) AS missing,
               count(*) FILTER (WHERE {column} = 0) AS zero_default,
               count(*) FILTER (WHERE {column} < 0) AS impossible_negative
        FROM planned_rows
    """).fetchone()
    facts.extend([
        (f"{column}_missing_rows", stats[0]),
        (f"{column}_zero_rows", stats[1]),
        (f"{column}_negative_rows", stats[2]),
    ])
    by_year_stats = con.execute(f"""
        SELECT year(crash_date) AS year,
               count(*) FILTER (WHERE {column} IS NULL) AS missing,
               count(*) FILTER (WHERE {column} = 0) AS zero_default,
               count(*) FILTER (WHERE {column} < 0) AS impossible_negative
        FROM planned_rows GROUP BY year ORDER BY year
    """).fetchall()
    year_stats = {row[0]: row[1:] for row in by_year_stats}
    for year in YEARS:
        stats = year_stats.get(year, (0, 0, 0))
        facts.extend([
            (f"{column}_missing_rows_{year}", stats[0]),
            (f"{column}_zero_rows_{year}", stats[1]),
            (f"{column}_negative_rows_{year}", stats[2]),
        ])

for option_id in (1, 2):
    with (OUT / f"check_{option_id}.csv").open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)
