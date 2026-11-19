import csv
import duckdb

DATA = "data/crashes.parquet"
START_YEAR = 2013
END_YEAR = 2025
OUTCOMES = ["number_of_motorist_killed", "number_of_cyclist_killed"]

con = duckdb.connect()
by_year = con.execute(
    f"""
    SELECT year(crash_date) AS year,
           count(*) AS rows,
           min(crash_date) AS first_date,
           max(crash_date) AS last_date,
           count(*) FILTER (WHERE crash_date IS NULL) AS missing_date,
           count(*) FILTER (WHERE crash_date IN (DATE '1900-01-01', DATE '1970-01-01')) AS default_date,
           count(*) FILTER (WHERE {OUTCOMES[0]} IS NULL) AS motorist_missing,
           count(*) FILTER (WHERE {OUTCOMES[1]} IS NULL) AS cyclist_missing
    FROM read_parquet('{DATA}')
    WHERE crash_date >= DATE '{START_YEAR}-01-01'
      AND crash_date < DATE '{END_YEAR + 1}-01-01'
    GROUP BY year
    ORDER BY year
    """
).fetchall()

all_rows = con.execute(
    f"""
    SELECT count(*) AS rows,
           count(*) FILTER (WHERE crash_date IS NULL) AS missing_date,
           count(*) FILTER (WHERE crash_date IN (DATE '1900-01-01', DATE '1970-01-01')) AS default_date,
           count(*) FILTER (WHERE {OUTCOMES[0]} IS NULL) AS motorist_missing,
           count(*) FILTER (WHERE {OUTCOMES[1]} IS NULL) AS cyclist_missing,
           min(crash_date) AS first_date,
           max(crash_date) AS last_date
    FROM read_parquet('{DATA}')
    WHERE crash_date >= DATE '{START_YEAR}-01-01'
      AND crash_date < DATE '{END_YEAR + 1}-01-01'
    """
).fetchone()

by_year = {row[0]: row[1:] for row in by_year}
facts = [
    ("population_rows_2013_2025", all_rows[0]),
    ("population_rows_by_year", "; ".join(f"{year}={by_year.get(year, (0,))[0]}" for year in range(START_YEAR, END_YEAR + 1))),
    ("population_date_range", f"{all_rows[5]} to {all_rows[6]}"),
    ("crash_date_missing_in_population", all_rows[1]),
    ("crash_date_default_1900_or_1970_in_population", all_rows[2]),
    ("crash_date_invalid_or_outside_selected_years_in_population", 0),
    ("number_of_motorist_killed_missing_in_population", all_rows[3]),
    ("number_of_cyclist_killed_missing_in_population", all_rows[4]),
    ("motorist_death_column_missing_by_year", "; ".join(f"{year}={by_year.get(year, (0, None, None, 0, 0, 0, 0))[4]}" for year in range(START_YEAR, END_YEAR + 1))),
    ("cyclist_death_column_missing_by_year", "; ".join(f"{year}={by_year.get(year, (0, None, None, 0, 0, 0, 0))[5]}" for year in range(START_YEAR, END_YEAR + 1))),
    ("year_coverage_first_and_last_dates", "; ".join(
        f"{year}={by_year[year][1]}..{by_year[year][2]}" if year in by_year else f"{year}=no rows"
        for year in range(START_YEAR, END_YEAR + 1)
    )),
    ("partial_years_by_observed_date_extent", "; ".join(
        str(year) for year in range(START_YEAR, END_YEAR + 1)
        if year not in by_year
        or by_year[year][1].month != 1 or by_year[year][1].day != 1
        or by_year[year][2].month != 12 or by_year[year][2].day != 31
    )),
]

for plan_id in (1, 2):
    with open(f"out/check_{plan_id}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)
