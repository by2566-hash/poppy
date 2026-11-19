import csv
import json
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
PARQUET = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"

con = duckdb.connect()
source = "read_parquet(?)"
null_dates = con.execute(
    f"SELECT count(*) FROM {source} WHERE crash_date IS NULL", [str(PARQUET)]
).fetchone()[0]
sentinels = ["0001-01-01", "1900-01-01", "1970-01-01", "9999-12-31"]
sentinel_counts = con.execute(
    f"SELECT CAST(crash_date AS VARCHAR), count(*) FROM {source} "
    "WHERE crash_date IN (DATE '0001-01-01', DATE '1900-01-01', "
    "DATE '1970-01-01', DATE '9999-12-31') GROUP BY 1 ORDER BY 1",
    [str(PARQUET)],
).fetchall()
sentinel_map = {date: count for date, count in sentinel_counts}

for plan_id in (1, 2):
    plan = json.loads((OUT / f"plan_{plan_id}.json").read_text())
    facts = []

    def add(fact, value):
        facts.append((fact, value))

    add("source_rows_with_null_crash_date_before_year_filter", null_dates)
    add("crash_date_type_and_unrepresentable_values", "DATE; empty strings, unknown words, and impossible calendar dates cannot be stored as DATE values")
    add(
        "crash_date_default_sentinel_counts_before_year_filter",
        json.dumps({date: sentinel_map.get(date, 0) for date in sentinels}, sort_keys=True),
    )

    for year, count, min_date, max_date in con.execute(
        f"SELECT year(crash_date), count(*), min(crash_date), max(crash_date) "
        f"FROM {source} WHERE crash_date >= DATE '2013-01-01' "
        "AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1",
        [str(PARQUET)],
    ).fetchall():
        add(f"eligible_crash_rows_year_{year}", count)
        add(f"observed_date_span_year_{year}", f"{min_date} to {max_date}")
        add(
            f"year_{year}_calendar_coverage",
            "full calendar year by observed endpoints"
            if str(min_date) == f"{year}-01-01" and str(max_date) == f"{year}-12-31"
            else "partial calendar year by observed endpoints",
        )

    eligible = con.execute(
        f"SELECT count(*) FROM {source} WHERE crash_date >= DATE '2013-01-01' "
        "AND crash_date < DATE '2026-01-01'",
        [str(PARQUET)],
    ).fetchone()[0]
    add("eligible_crash_rows_total_2013_2025", eligible)
    missing_weekday = con.execute(
        f"SELECT count(*) FROM {source} WHERE crash_date >= DATE '2013-01-01' "
        "AND crash_date < DATE '2026-01-01' AND dayofweek(crash_date) IS NULL",
        [str(PARQUET)],
    ).fetchone()[0]
    add("derived_weekday_missing_rows_in_eligible_population", missing_weekday)
    with (OUT / f"check_{plan_id}.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)

con.close()
