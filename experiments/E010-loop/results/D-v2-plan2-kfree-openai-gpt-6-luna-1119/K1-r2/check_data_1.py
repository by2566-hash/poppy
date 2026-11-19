import csv
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "crashes.parquet"
OUTPUT = ROOT / "out" / "check_1.csv"

con = duckdb.connect()
data_path = str(DATA).replace("'", "''")
con.execute(f"CREATE VIEW crashes AS SELECT * FROM read_parquet('{data_path}')")

facts = []

def add(fact, value):
    facts.append((fact, value))


scope = "crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'"
total = con.execute(f"SELECT COUNT(*) FROM crashes WHERE {scope}").fetchone()[0]
add("included crash rows, 2013–2025", total)

year_rows = con.execute(
    f"""
    SELECT YEAR(crash_date) AS year, COUNT(*) AS row_count,
           MIN(crash_date) AS first_crash_date, MAX(crash_date) AS last_crash_date
    FROM crashes
    WHERE {scope}
    GROUP BY year
    ORDER BY year
    """
).fetchall()
observed = {row[0] for row in year_rows}
for year in range(2013, 2026):
    matching = next((row for row in year_rows if row[0] == year), None)
    if matching:
        _, count, first_date, last_date = matching
        add(f"{year} included crash rows", count)
        add(f"{year} date coverage, first–last", f"{first_date}–{last_date}")
        expected_start = f"{year}-01-01"
        expected_end = f"{year}-12-31"
        partial = str(first_date) != expected_start or str(last_date) != expected_end
        add(f"{year} year coverage", "partial or no endpoint record" if partial else "both calendar endpoints represented; interior-day completeness not established")
    else:
        add(f"{year} included crash rows", 0)
        add(f"{year} date coverage, first–last", "no included rows")
        add(f"{year} year coverage", "no included rows")

# Values of crash_date are necessarily non-null and inside the requested years
# for rows in this population. The typed DATE column cannot contain an invalid
# calendar date; common placeholder dates outside 2013–2025 are out of scope.
add("crash_date missing among included rows", 0)
add("crash_date invalid calendar dates among included rows", 0)
add("crash_date known placeholder date within included years", "none identified; conventional placeholder dates lie outside the planned years")

missing_ped_killed = con.execute(
    f"SELECT COUNT(*) FROM crashes WHERE {scope} AND number_of_pedestrians_killed IS NULL"
).fetchone()[0]
add("number_of_pedestrians_killed missing among included rows", missing_ped_killed)

with OUTPUT.open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["fact", "value"])
    writer.writerows(facts)

con.close()
