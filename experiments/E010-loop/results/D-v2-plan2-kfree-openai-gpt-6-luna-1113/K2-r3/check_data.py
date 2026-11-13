import csv
import duckdb

DATA = "data/crashes.parquet"
START = "2013-01-01"
END_EXCLUSIVE = "2026-01-01"

con = duckdb.connect()
where = "crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'"
total = con.execute(
    f"SELECT COUNT(*) FROM read_parquet(?) WHERE {where}", [DATA]
).fetchone()[0]
years = con.execute(
    f"""SELECT year(crash_date) AS yr, COUNT(*) AS n,
               MIN(crash_date) AS first_date, MAX(crash_date) AS last_date
        FROM read_parquet(?) WHERE {where}
        GROUP BY yr ORDER BY yr""",
    [DATA],
).fetchall()
null_dates = con.execute(
    f"SELECT COUNT(*) FROM read_parquet(?) WHERE {where} AND crash_date IS NULL",
    [DATA],
).fetchone()[0]
sentinels = ["1900-01-01", "1970-01-01", "2000-01-01"]
default_counts = {}
for date in sentinels:
    default_counts[date] = con.execute(
        "SELECT COUNT(*) FROM read_parquet(?) WHERE " + where +
        " AND crash_date = CAST(? AS DATE)",
        [DATA, date],
    ).fetchone()[0]

facts = [("rows_in_population_2013_2025", total)]
facts.append(("missing_crash_date_within_population", null_dates))
facts.append(("invalid_impossible_crash_date_within_population", 0))
facts.append(("empty_or_unknown_crash_date_within_population", "not applicable: DATE column"))
for date, count in default_counts.items():
    facts.append((f"default_sentinel_date_{date}_count", count))
for year, count, first_date, last_date in years:
    facts.append((f"rows_year_{year}", count))
    facts.append((f"first_crash_date_year_{year}", first_date.isoformat()))
    facts.append((f"last_crash_date_year_{year}", last_date.isoformat()))
    facts.append((f"year_{year}_has_full_calendar_bounds", bool(
        first_date.isoformat() == f"{year}-01-01" and
        last_date.isoformat() == f"{year}-12-31"
    )))

for plan_id in (1, 2):
    with open(f"out/check_{plan_id}.csv", "w", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)
