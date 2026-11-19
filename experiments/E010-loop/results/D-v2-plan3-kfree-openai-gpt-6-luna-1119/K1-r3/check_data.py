import csv
import duckdb

SOURCE = "./data/crashes.parquet"
START_YEAR = 2013
END_YEAR = 2025

con = duckdb.connect()
rows = con.execute(
    """
    SELECT
        year(crash_date) AS crash_year,
        count(*) AS crash_rows,
        min(crash_date) AS first_date,
        max(crash_date) AS last_date,
        count(*) FILTER (WHERE crash_date = make_date(year(crash_date), 1, 1)) AS jan_1_rows,
        count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS missing_pedestrian_killed_rows
    FROM read_parquet(?)
    WHERE crash_date >= make_date(?, 1, 1)
      AND crash_date < make_date(? + 1, 1, 1)
    GROUP BY year(crash_date)
    ORDER BY crash_year
    """,
    [SOURCE, START_YEAR, END_YEAR],
).fetchall()

facts = []
total_rows = sum(row[1] for row in rows)
total_missing = sum(row[5] for row in rows)
facts.append(("population_rows_2013_2025", total_rows))
facts.append(("missing_crash_date_in_population", 0))
facts.append(("missing_crash_year_in_population", 0))
facts.append(("missing_number_of_pedestrians_killed_rows_2013_2025", total_missing))

present_years = {row[0] for row in rows}
for year in range(START_YEAR, END_YEAR + 1):
    match = next((row for row in rows if row[0] == year), None)
    facts.append((f"crash_rows_{year}", match[1] if match else 0))
    facts.append((f"missing_pedestrian_killed_rows_{year}", match[5] if match else 0))
    if match:
        facts.append((f"date_coverage_{year}", f"{match[2]} through {match[3]}"))
        facts.append((f"jan_1_rows_{year}", match[4]))
    else:
        facts.append((f"date_coverage_{year}", "no rows"))
        facts.append((f"jan_1_rows_{year}", 0))
    facts.append((f"full_calendar_year_coverage_{year}", bool(match and str(match[2]) == f"{year}-01-01" and str(match[3]) == f"{year}-12-31")))

with open("./out/check_1.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["fact", "value"])
    writer.writerows(facts)

print(f"Checked {total_rows} crash rows across {len(present_years)} observed years.")
