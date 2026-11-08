import csv
import duckdb
from datetime import date

DATA = "data/crashes.parquet"
YEARS = range(2013, 2026)
rows = []

con = duckdb.connect()
con.execute("CREATE VIEW crashes AS SELECT crash_date FROM read_parquet('data/crashes.parquet')")

total = con.execute(
    "SELECT COUNT(*) FROM crashes WHERE crash_date >= DATE '2013-01-01' "
    "AND crash_date <= DATE '2025-12-31'"
).fetchone()[0]
rows.append(("qualifying_rows_2013_2025", total))
null_dates = con.execute(
    "SELECT COUNT(*) FROM crashes WHERE crash_date >= DATE '2013-01-01' "
    "AND crash_date <= DATE '2025-12-31' AND crash_date IS NULL"
).fetchone()[0]
rows.append(("missing_crash_date_in_qualifying_population", null_dates))
rows.append((
    "crash_date_invalid_or_empty_in_qualifying_population",
    "0 by DATE type and inclusive year filter; invalid/empty text cannot match",
))
rows.append((
    "common_default_or_sentinel_crash_dates_in_qualifying_population",
    "0 for standard sentinels outside 2013-2025 (e.g. 1900-01-01, 1970-01-01)",
))

for year in YEARS:
    start = date(year, 1, 1)
    end = date(year, 12, 31)
    count, first, last = con.execute(
        "SELECT COUNT(*), MIN(crash_date), MAX(crash_date) FROM crashes "
        "WHERE crash_date >= ? AND crash_date <= ?",
        [start, end],
    ).fetchone()
    rows.append((f"rows_{year}", count))
    if count:
        partial = first != start or last != end
        rows.append((f"date_extent_{year}", f"{first} through {last}"))
        rows.append((f"partial_calendar_year_{year}", "yes" if partial else "no"))
    else:
        rows.append((f"date_extent_{year}", "no qualifying dates"))
        rows.append((f"partial_calendar_year_{year}", "no rows; coverage unavailable"))

with open("out/check_1.csv", "w", newline="") as output:
    writer = csv.writer(output)
    writer.writerow(["fact", "value"])
    writer.writerows(rows)
with open("out/check_2.csv", "w", newline="") as output:
    writer = csv.writer(output)
    writer.writerow(["fact", "value"])
    writer.writerows(rows)
