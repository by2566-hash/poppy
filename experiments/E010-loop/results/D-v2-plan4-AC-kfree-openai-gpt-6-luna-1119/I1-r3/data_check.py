import csv
import duckdb


DATA = "./data/crashes.parquet"
YEARS = range(2013, 2026)
START = "2013-01-01"
END = "2026-01-01"

con = duckdb.connect()
con.execute(f"CREATE VIEW scoped AS SELECT crash_date, number_of_motorist_killed FROM read_parquet('{DATA}') WHERE crash_date >= DATE '{START}' AND crash_date < DATE '{END}'")

rows = []
total = con.execute("SELECT COUNT(*) FROM scoped").fetchone()[0]
rows.append(("population_rows_2013_2025", total))
rows.append(("crash_date_missing_before_year_filter_all_file", con.execute(f"SELECT COUNT(*) FROM read_parquet('{DATA}') WHERE crash_date IS NULL").fetchone()[0]))
rows.append(("crash_date_common_default_before_year_filter_all_file", con.execute(f"SELECT COUNT(*) FROM read_parquet('{DATA}') WHERE crash_date IN (DATE '1900-01-01', DATE '1970-01-01')").fetchone()[0]))

by_year = con.execute(
    """SELECT YEAR(crash_date) AS year, COUNT(*) AS rows,
              MIN(crash_date) AS first_observed_date,
              MAX(crash_date) AS last_observed_date,
              COUNT(*) FILTER (WHERE crash_date IS NULL) AS crash_date_missing,
              COUNT(*) FILTER (WHERE crash_date IN (DATE '1900-01-01', DATE '1970-01-01')) AS crash_date_common_default,
              COUNT(*) FILTER (WHERE number_of_motorist_killed IS NULL) AS motorist_killed_missing
       FROM scoped GROUP BY YEAR(crash_date) ORDER BY year"""
).fetchall()
year_map = {int(record[0]): record[1:] for record in by_year}

for year in YEARS:
    info = year_map.get(year)
    if info is None:
        rows.append((f"rows_{year}", 0))
        rows.append((f"crash_date_observed_span_{year}", "no dated rows"))
        rows.append((f"crash_date_missing_in_population_{year}", 0))
        rows.append((f"crash_date_common_default_in_population_{year}", 0))
        rows.append((f"number_of_motorist_killed_missing_{year}", 0))
        rows.append((f"year_coverage_{year}", "no dated rows"))
        continue
    n, first, last, date_missing, date_default, outcome_missing = info
    rows.append((f"rows_{year}", n))
    first_text, last_text = first.isoformat(), last.isoformat()
    rows.append((f"crash_date_observed_span_{year}", f"{first_text} to {last_text}"))
    rows.append((f"crash_date_missing_in_population_{year}", date_missing))
    rows.append((f"crash_date_common_default_in_population_{year}", date_default))
    rows.append((f"number_of_motorist_killed_missing_{year}", outcome_missing))
    partial = first_text > f"{year}-01-01" or last_text < f"{year}-12-31"
    rows.append((f"year_coverage_{year}", "observed dates do not span the full calendar year; partial coverage possible" if partial else "observed dates span the full calendar year; full coverage not independently verifiable"))

rows.append(("number_of_motorist_killed_missing_2013_2025", con.execute("SELECT COUNT(*) FROM scoped WHERE number_of_motorist_killed IS NULL").fetchone()[0]))
with open("./out/check_1.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["fact", "value"])
    writer.writerows(rows)
with open("./out/check_2.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["fact", "value"])
    writer.writerows(rows)
