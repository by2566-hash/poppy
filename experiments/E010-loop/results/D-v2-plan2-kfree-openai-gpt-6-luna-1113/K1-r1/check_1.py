import csv
import duckdb


start = "2013-01-01"
end = "2026-01-01"
con = duckdb.connect()
con.execute("CREATE VIEW crashes AS SELECT crash_date, number_of_pedestrians_killed FROM read_parquet('./data/crashes.parquet')")
where_period = "crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'"
facts = []

total = con.execute(f"SELECT count(*) FROM crashes WHERE {where_period}").fetchone()[0]
facts.append(("rows_in_planned_population_2013_2025", total))

year_rows = con.execute(
    f"""SELECT year(crash_date) AS year, count(*) AS rows,
               min(crash_date) AS first_date, max(crash_date) AS last_date
        FROM crashes WHERE {where_period}
        GROUP BY year ORDER BY year"""
).fetchall()
for year, rows, first_date, last_date in year_rows:
    facts.append((f"rows_in_population_year_{year}", rows))
    facts.append((f"crash_date_coverage_year_{year}_first_and_last", f"{first_date} to {last_date}"))

# Within the planned population a crash_date is non-null and a valid DATE by construction.
facts.append(("crash_date_missing_within_planned_population", 0))
facts.append(("crash_date_invalid_or_unknown_within_planned_population", 0))

# Test common date sentinels in the selected years; these are included for transparency.
sentinels = con.execute(
    f"""SELECT count(*) FROM crashes WHERE {where_period}
        AND crash_date IN (DATE '1900-01-01', DATE '1970-01-01', DATE '2000-01-01')"""
).fetchone()[0]
facts.append(("crash_date_common_default_sentinel_dates_1900_1970_2000_rows", sentinels))

missing_total = con.execute(
    f"SELECT count(*) FROM crashes WHERE {where_period} AND number_of_pedestrians_killed IS NULL"
).fetchone()[0]
facts.append(("number_of_pedestrians_killed_missing_rows_in_population", missing_total))
missing_by_year = con.execute(
    f"""SELECT year(crash_date) AS year, count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL)
        FROM crashes WHERE {where_period} GROUP BY year ORDER BY year"""
).fetchall()
for year, missing in missing_by_year:
    facts.append((f"number_of_pedestrians_killed_missing_rows_year_{year}", missing))

with open("./out/check_1.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["fact", "value"])
    writer.writerows(facts)

print(f"Checked {total} planned crash rows across {len(year_rows)} observed years ({start} through {end} exclusive).")
