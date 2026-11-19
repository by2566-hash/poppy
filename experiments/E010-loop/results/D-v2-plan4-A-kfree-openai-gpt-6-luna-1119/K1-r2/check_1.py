import csv

import duckdb


PARQUET = "data/crashes.parquet"
START_YEAR = 2013
END_YEAR = 2025

db = duckdb.connect()
facts = []
year_records = []

for year in range(START_YEAR, END_YEAR + 1):
    start = f"{year}-01-01"
    end = f"{year + 1}-01-01"
    row_count, first_date, last_date, missing_dates, missing_pedestrian_death_counts = db.execute(
        """
        SELECT count(*), min(crash_date), max(crash_date),
               count(*) FILTER (WHERE crash_date IS NULL),
               count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL)
        FROM read_parquet(?)
        WHERE crash_date >= ?::DATE AND crash_date < ?::DATE
        """,
        [PARQUET, start, end],
    ).fetchone()
    year_records.append((year, row_count))
    facts.extend(
        [
            (f"population_rows_year_{year}", row_count),
            (f"crash_date_missing_rows_year_{year}", missing_dates),
            (
                f"number_of_pedestrians_killed_missing_rows_year_{year}",
                missing_pedestrian_death_counts,
            ),
            (
                f"observed_crash_date_span_year_{year}",
                f"{first_date} to {last_date}" if row_count else "no rows",
            ),
        ]
    )

total = sum(count for _, count in year_records)
facts.insert(0, ("population_rows_2013_2025", total))

with open("out/check_1.csv", "w", newline="") as output:
    writer = csv.writer(output)
    writer.writerow(["fact", "value"])
    writer.writerows(facts)
