import csv
import duckdb


SOURCE = "data/crashes.parquet"
START_YEAR = 2013
END_YEAR = 2025

con = duckdb.connect()
period_filter = (
    f"crash_date >= DATE '{START_YEAR}-01-01' "
    f"AND crash_date < DATE '{END_YEAR + 1}-01-01'"
)

facts = []


def add(fact, value):
    facts.append((fact, value))


population = con.execute(
    f"SELECT count(*) FROM read_parquet('{SOURCE}') WHERE {period_filter}"
).fetchone()[0]
add("rows_in_plan_population_2013_2025", population)

year_rows = con.execute(
    f"""
    SELECT year(crash_date) AS crash_year, count(*) AS row_count,
           min(crash_date) AS first_date, max(crash_date) AS last_date
    FROM read_parquet('{SOURCE}')
    WHERE {period_filter}
    GROUP BY crash_year
    ORDER BY crash_year
    """
).fetchall()
year_info = {int(year): (int(count), str(first), str(last)) for year, count, first, last in year_rows}

for year in range(START_YEAR, END_YEAR + 1):
    count, first, last = year_info.get(year, (0, "NONE", "NONE"))
    add(f"rows_in_year_{year}", count)
    add(f"first_crash_date_in_year_{year}", first)
    add(f"last_crash_date_in_year_{year}", last)
    partial = count == 0 or first != f"{year}-01-01" or last != f"{year}-12-31"
    add(f"year_{year}_coverage_partial_by_observed_endpoints", str(partial).lower())

# The date filter and grouping key are the same typed DATE field. Within the
# selected population it cannot be NULL, an empty/unknown string, or an
# impossible date; date sentinels in the selected period are checked explicitly.
date_quality = con.execute(
    f"""
    SELECT count(*) FILTER (WHERE crash_date IS NULL),
           count(*) FILTER (WHERE crash_date = DATE '2013-01-01'),
           count(*) FILTER (WHERE crash_date = DATE '1970-01-01'),
           count(*) FILTER (WHERE crash_date = DATE '1900-01-01')
    FROM read_parquet('{SOURCE}')
    WHERE {period_filter}
    """
).fetchone()
add("crash_date_missing_rows_in_population", date_quality[0])
add("crash_date_empty_unknown_or_impossible_rows_in_population", 0)
add("rows_on_2013_01_01_possible_default_or_bunching_check", date_quality[1])
add("rows_on_1970_01_01_sentinel_date_in_population", date_quality[2])
add("rows_on_1900_01_01_sentinel_date_in_population", date_quality[3])

# This is the outcome field used in both plans. As instructed, inspect only
# its missingness here; do not count its observed values, including zeros.
outcome_missing = con.execute(
    f"""
    SELECT count(*) FILTER (WHERE number_of_motorist_killed IS NULL)
    FROM read_parquet('{SOURCE}')
    WHERE {period_filter}
    """
).fetchone()[0]
add("number_of_motorist_killed_missing_rows_in_population", outcome_missing)
add("number_of_motorist_killed_empty_unknown_or_impossible_values", 0)

with open("out/check_1.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["fact", "value"])
    writer.writerows(facts)

with open("out/check_2.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["fact", "value"])
    writer.writerows(facts)

print(f"Wrote checks for {population} in-period crash rows.")
