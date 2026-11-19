import csv
import datetime as dt
import duckdb


SOURCE = "data/crashes.parquet"
YEARS = range(2013, 2026)
START = dt.date(2013, 1, 1)
END = dt.date(2025, 12, 31)
OUTCOMES = ("number_of_motorist_killed", "number_of_cyclist_killed")

con = duckdb.connect()
con.execute(f"CREATE VIEW crashes AS SELECT crash_date, number_of_motorist_killed, number_of_cyclist_killed FROM read_parquet('{SOURCE}')")

facts = []


def add(fact, value):
    facts.append((fact, value))


total = con.execute(
    """SELECT count(*) AS rows,
              count(*) FILTER (WHERE number_of_motorist_killed IS NULL) AS motorist_missing,
              count(*) FILTER (WHERE number_of_cyclist_killed IS NULL) AS cyclist_missing,
              count(*) FILTER (WHERE number_of_motorist_killed IS NULL OR number_of_cyclist_killed IS NULL) AS either_missing,
              count(*) FILTER (WHERE crash_date IS NULL) AS date_missing
       FROM crashes WHERE crash_date BETWEEN ? AND ?""",
    [START, END],
).fetchone()
add("requested_years_crash_rows_before_outcome_missing_filter", total[0])
add("requested_years_rows_missing_number_of_motorist_killed", total[1])
add("requested_years_rows_missing_number_of_cyclist_killed", total[2])
add("requested_years_rows_missing_either_death_count", total[3])
add("requested_years_rows_retained_with_both_death_counts_present", total[0] - total[3])
add("requested_years_crash_date_missing_rows", total[4])
add("requested_years_crash_date_invalid_or_string_unknown_rows", "0 representable: crash_date is DATE typed; string sentinels and impossible dates cannot be encoded")
add("requested_years_crash_date_default_value_check", "No default date sentinel is specified in the source description; no valid in-range date was assumed to be a default")

annual = con.execute(
    """SELECT year(crash_date) AS yr, count(*) AS rows,
              min(crash_date) AS first_date, max(crash_date) AS last_date,
              count(*) FILTER (WHERE number_of_motorist_killed IS NULL) AS motorist_missing,
              count(*) FILTER (WHERE number_of_cyclist_killed IS NULL) AS cyclist_missing,
              count(*) FILTER (WHERE number_of_motorist_killed IS NULL OR number_of_cyclist_killed IS NULL) AS either_missing
       FROM crashes WHERE crash_date BETWEEN ? AND ?
       GROUP BY yr ORDER BY yr""",
    [START, END],
).fetchall()
by_year = {row[0]: row[1:] for row in annual}

for year in YEARS:
    row = by_year.get(year)
    if row is None:
        add(f"year_{year}_crash_rows_before_outcome_missing_filter", 0)
        add(f"year_{year}_rows_missing_number_of_motorist_killed", 0)
        add(f"year_{year}_rows_missing_number_of_cyclist_killed", 0)
        add(f"year_{year}_rows_missing_either_death_count", 0)
        add(f"year_{year}_rows_retained_with_both_death_counts_present", 0)
        add(f"year_{year}_first_crash_date", "no rows")
        add(f"year_{year}_last_crash_date", "no rows")
        add(f"year_{year}_coverage", "no rows; cannot answer for this year")
        continue
    rows, first_date, last_date, motorist_missing, cyclist_missing, either_missing = row
    add(f"year_{year}_crash_rows_before_outcome_missing_filter", rows)
    add(f"year_{year}_rows_missing_number_of_motorist_killed", motorist_missing)
    add(f"year_{year}_rows_missing_number_of_cyclist_killed", cyclist_missing)
    add(f"year_{year}_rows_missing_either_death_count", either_missing)
    add(f"year_{year}_rows_retained_with_both_death_counts_present", rows - either_missing)
    add(f"year_{year}_first_crash_date", first_date.isoformat())
    add(f"year_{year}_last_crash_date", last_date.isoformat())
    expected_first = dt.date(year, 1, 1)
    expected_last = dt.date(year, 12, 31)
    coverage = "complete calendar year" if first_date == expected_first and last_date == expected_last else "partial calendar year"
    add(f"year_{year}_coverage", coverage)

for plan_id in (1, 2):
    with open(f"out/check_{plan_id}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)

print(f"Wrote checks for {len(facts)} facts per plan.")
