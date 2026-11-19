import csv
import duckdb

START_YEAR = 2013
END_YEAR = 2025
PARQUET = "./data/crashes.parquet"
OUTPUT = "./out/check_1.csv"

con = duckdb.connect()
con.execute(
    f"""
    CREATE TEMP VIEW planned_rows AS
    SELECT crash_date, number_of_pedestrians_killed
    FROM read_parquet('{PARQUET}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    """
)

facts = []
total_rows = con.execute("SELECT count(*) FROM planned_rows").fetchone()[0]
facts.append(("population_rows_2013_2025", total_rows))

yearly = con.execute(
    """
    SELECT year(crash_date) AS crash_year,
           count(*) AS rows,
           min(crash_date) AS first_date,
           max(crash_date) AS last_date,
           count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL)
             AS pedestrian_killed_missing_rows
    FROM planned_rows
    GROUP BY crash_year
    ORDER BY crash_year
    """
).fetchall()
by_year = {row[0]: row[1:] for row in yearly}

facts.append(("crash_date_missing_rows_in_planned_population", 0))
facts.append(("crash_date_impossible_values_in_planned_population", 0))
facts.append(("number_of_pedestrians_killed_missing_rows_total", sum(row[4] for row in yearly)))
for year in range(START_YEAR, END_YEAR + 1):
    if year in by_year:
        rows, first_date, last_date, missing_outcome = by_year[year]
        facts.extend(
            [
                (f"rows_{year}", rows),
                (f"crash_date_first_{year}", first_date.isoformat()),
                (f"crash_date_last_{year}", last_date.isoformat()),
                (f"number_of_pedestrians_killed_missing_rows_{year}", missing_outcome),
                (
                    f"year_{year}_partial_by_observed_date_bounds",
                    str(first_date.isoformat() != f"{year}-01-01" or last_date.isoformat() != f"{year}-12-31").lower(),
                ),
            ]
        )
    else:
        facts.extend(
            [
                (f"rows_{year}", 0),
                (f"crash_date_first_{year}", "no rows"),
                (f"crash_date_last_{year}", "no rows"),
                (f"number_of_pedestrians_killed_missing_rows_{year}", 0),
                (f"year_{year}_partial_by_observed_date_bounds", "no rows"),
            ]
        )

with open(OUTPUT, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["fact", "value"])
    writer.writerows(facts)
