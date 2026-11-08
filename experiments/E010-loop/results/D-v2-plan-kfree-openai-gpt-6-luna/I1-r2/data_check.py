import csv
import duckdb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
SOURCE = (ROOT / "data" / "crashes.parquet").as_posix().replace("'", "''")
YEARS = range(2013, 2026)

con = duckdb.connect()
con.execute(
    f"""
    CREATE VIEW planned_rows AS
    SELECT crash_date, number_of_motorist_killed
    FROM read_parquet('{SOURCE}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    """
)

year_rows = con.execute(
    """
    SELECT year(crash_date) AS year, count(*) AS rows,
           min(crash_date) AS first_date, max(crash_date) AS last_date,
           count(*) FILTER (WHERE number_of_motorist_killed IS NULL) AS missing_motorist_killed,
           count(*) FILTER (WHERE number_of_motorist_killed < 0) AS negative_motorist_killed,
           count(*) FILTER (WHERE number_of_motorist_killed = 0) AS zero_motorist_killed
    FROM planned_rows
    GROUP BY year
    ORDER BY year
    """
).fetchdf().set_index("year")

total_rows = con.execute("SELECT count(*) FROM planned_rows").fetchone()[0]
missing_dates = con.execute(
    f"SELECT count(*) FROM read_parquet('{SOURCE}') WHERE crash_date IS NULL"
).fetchone()[0]

facts = [
    ("planned_population_rows_2013_2025", int(total_rows)),
    ("rows_with_missing_crash_date_in_file_unassignable_to_year", int(missing_dates)),
]
for year in YEARS:
    row = year_rows.loc[year] if year in year_rows.index else None
    n = int(row["rows"]) if row is not None else 0
    first = str(row["first_date"])[:10] if row is not None else "none"
    last = str(row["last_date"])[:10] if row is not None else "none"
    facts.extend([
        (f"rows_{year}", n),
        (f"motorist_killed_missing_rows_{year}", int(row["missing_motorist_killed"]) if row is not None else 0),
        (f"motorist_killed_negative_rows_{year}", int(row["negative_motorist_killed"]) if row is not None else 0),
        (f"motorist_killed_zero_rows_{year}", int(row["zero_motorist_killed"]) if row is not None else 0),
        (f"date_coverage_edges_{year}", f"first={first}; last={last}"),
    ])
    if n == 0:
        coverage = "no rows in planned year"
    else:
        first_expected = f"{year}-01-01"
        last_expected = f"{year}-12-31"
        coverage = "edge-partial" if first != first_expected or last != last_expected else "full year at observed edges; internal date coverage not evaluated"
    facts.append((f"coverage_status_{year}", coverage))

for plan_id in (1, 2):
    with (OUT / f"check_{plan_id}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)
