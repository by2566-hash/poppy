import csv
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
con = duckdb.connect()
con.from_parquet(str(ROOT / "data/crashes.parquet")).project(
    "crash_date, crash_time, number_of_persons_injured, number_of_persons_killed"
).create_view("crashes")

facts = []


def add(fact, value):
    facts.append((fact, str(value)))


add("population_definition", "Rows with nonmissing crash_date; counted before applying time and outcome completeness filters")
add("population_rows", con.execute("SELECT count(*) FROM crashes WHERE crash_date IS NOT NULL").fetchone()[0])
add("crash_date_missing_rows", con.execute("SELECT count(*) FROM crashes WHERE crash_date IS NULL").fetchone()[0])
add("crash_date_sentinel_1900_rows", con.execute("SELECT count(*) FROM crashes WHERE crash_date = DATE '1900-01-01' OR year(crash_date) = 1900").fetchone()[0])

year_rows = con.execute("""
    SELECT year(crash_date) AS yr, count(*) AS n, min(crash_date) AS first_date,
           max(crash_date) AS last_date,
           count(*) FILTER (WHERE crash_time IS NULL) AS missing_time,
           count(*) FILTER (WHERE crash_time = TIME '00:00:00') AS midnight_time,
           count(*) FILTER (WHERE number_of_persons_injured IS NULL) AS missing_injured,
           count(*) FILTER (WHERE number_of_persons_killed IS NULL) AS missing_killed,
           count(*) FILTER (WHERE number_of_persons_injured IS NULL OR number_of_persons_killed IS NULL) AS missing_either_outcome
    FROM crashes WHERE crash_date IS NOT NULL
    GROUP BY yr ORDER BY yr
""").fetchall()

for yr, n, first_date, last_date, missing_time, midnight_time, missing_injured, missing_killed, missing_either_outcome in year_rows:
    add(f"rows_year_{yr}", n)
    add(f"date_range_year_{yr}", f"{first_date} to {last_date}")
    add(f"missing_crash_time_year_{yr}", missing_time)
    add(f"midnight_crash_time_year_{yr}", midnight_time)
    add(f"missing_number_of_persons_injured_year_{yr}", missing_injured)
    add(f"missing_number_of_persons_killed_year_{yr}", missing_killed)
    add(f"missing_either_person_count_year_{yr}", missing_either_outcome)
    if first_date.year != yr or last_date.year != yr:
        partial = "yes: observed range does not span this calendar year"
    elif first_date.month != 1 or first_date.day != 1 or last_date.month != 12 or last_date.day != 31:
        partial = "possible/indicated partial coverage: observed dates do not reach both calendar-year boundaries"
    else:
        partial = "no partial coverage indicated by observed date range (date presence alone cannot prove full source coverage)"
    add(f"year_{yr}_coverage_assessment", partial)

add("missing_crash_time_all_years", sum(row[4] for row in year_rows))
add("midnight_crash_time_all_years", sum(row[5] for row in year_rows))
add("missing_number_of_persons_injured_all_years", sum(row[6] for row in year_rows))
add("missing_number_of_persons_killed_all_years", sum(row[7] for row in year_rows))
add("missing_either_person_count_all_years", sum(row[8] for row in year_rows))
complete_year_rows = [row for row in year_rows if 2013 <= row[0] <= 2025]
add("rows_in_candidate_complete_years_2013_2025", sum(row[1] for row in complete_year_rows))
add("midnight_time_candidate_complete_years_2013_2025", sum(row[5] for row in complete_year_rows))
add("missing_injured_candidate_complete_years_2013_2025", sum(row[6] for row in complete_year_rows))
add("missing_killed_candidate_complete_years_2013_2025", sum(row[7] for row in complete_year_rows))
add("missing_either_person_count_candidate_complete_years_2013_2025", sum(row[8] for row in complete_year_rows))
add("time_value_domain", "crash_time has DuckDB TIME type; non-NULL malformed/impossible clock values are not representable in this typed column")
add("time_group_definitions", "night 20:00–05:59; day 06:00–19:59")

with (OUT / "check_1.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["fact", "value"])
    writer.writerows(facts)

with (OUT / "check_2.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["fact", "value"])
    writer.writerows(facts)
