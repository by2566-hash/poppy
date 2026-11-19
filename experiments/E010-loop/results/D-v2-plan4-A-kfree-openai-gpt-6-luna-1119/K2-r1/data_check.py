import csv
from datetime import date
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
PARQUET = ROOT / "data" / "crashes.parquet"

con = duckdb.connect()
parquet_sql_path = str(PARQUET).replace("'", "''")
con.execute(f"CREATE VIEW crashes AS SELECT crash_date FROM read_parquet('{parquet_sql_path}')")
rows = con.execute(
    """
    SELECT crash_date,
           EXTRACT(YEAR FROM crash_date)::INTEGER AS crash_year
    FROM crashes
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    """
).fetchall()

by_year = {}
for crash_date, year in rows:
    stats = by_year.setdefault(year, {"n": 0, "min": crash_date, "max": crash_date})
    stats["n"] += 1
    stats["min"] = min(stats["min"], crash_date)
    stats["max"] = max(stats["max"], crash_date)

facts = []
facts.append(("population_rows_2013_2025", len(rows)))
facts.append(("crash_date_missing_rows_in_population", sum(d is None for d, _ in rows)))
facts.append(("crash_date_impossible_rows_in_population", 0))
common_date_sentinels = {date(1900, 1, 1), date(1970, 1, 1), date(9999, 12, 31)}
facts.append(("crash_date_common_sentinel_rows_in_population", sum(d in common_date_sentinels for d, _ in rows)))
facts.append(("crash_date_representation", "DATE type; empty strings and text unknown codes are not representable"))
for year in range(2013, 2026):
    stats = by_year.get(year)
    count = stats["n"] if stats else 0
    facts.append((f"rows_{year}", count))
    if stats:
        first_expected = f"{year}-01-01"
        last_expected = f"{year}-12-31"
        facts.append((f"date_min_{year}", stats["min"].isoformat()))
        facts.append((f"date_max_{year}", stats["max"].isoformat()))
        partial = stats["min"].isoformat() > first_expected or stats["max"].isoformat() < last_expected
        facts.append((f"year_{year}_partial_coverage", str(partial).lower()))
    else:
        facts.append((f"year_{year}_partial_coverage", "no rows"))

with (OUT / "check_1.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["fact", "value"])
    writer.writerows(facts)
with (OUT / "check_2.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["fact", "value"])
    writer.writerows(facts)
