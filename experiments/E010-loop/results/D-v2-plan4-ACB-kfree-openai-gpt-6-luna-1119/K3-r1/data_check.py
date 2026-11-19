import csv
import duckdb

DATA = "data/crashes.parquet"
YEARS = range(2013, 2026)
OUTCOMES = [
    "number_of_motorist_killed",
    "number_of_cyclist_killed",
]

con = duckdb.connect()
con.execute(f"CREATE VIEW crashes AS SELECT * FROM read_parquet('{DATA}')")
facts = []

for year, n, first_day, last_day in con.execute(
    """
    SELECT year(crash_date), count(*), min(crash_date), max(crash_date)
    FROM crashes
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY year(crash_date)
    ORDER BY year(crash_date)
    """
).fetchall():
    facts.append((f"crashes_in_{year}", n))
    facts.append((f"date_coverage_in_{year}", f"{first_day} through {last_day}"))

counts = dict(
    con.execute(
        """
        SELECT year(crash_date), count(*)
        FROM crashes
        WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
        GROUP BY year(crash_date)
        """
    ).fetchall()
)
for year in YEARS:
    if year not in counts:
        facts.append((f"crashes_in_{year}", 0))
        facts.append((f"date_coverage_in_{year}", "no rows"))
facts.append(("crashes_in_2013_2025_total", sum(counts.values())))

null_dates = con.execute(
    "SELECT count(*) FROM crashes WHERE crash_date IS NULL"
).fetchone()[0]
facts.append(("crash_date_missing_rows_in_file_pre_filter", null_dates))

for column in OUTCOMES:
    n = con.execute(
        f"""SELECT count(*) FROM crashes
            WHERE crash_date >= DATE '2013-01-01'
              AND crash_date < DATE '2026-01-01'
              AND {column} IS NULL"""
    ).fetchone()[0]
    facts.append((f"{column}_missing_rows_in_plan_years", n))

with open("out/check_1.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["fact", "value"])
    writer.writerows(facts)

with open("out/check_2.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["fact", "value"])
    writer.writerows(facts)
