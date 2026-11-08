import csv
from pathlib import Path

import duckdb


DATA = Path("data/crashes.parquet")
YEARS = range(2013, 2026)
DEATH_COLUMNS = ["number_of_motorist_killed", "number_of_cyclist_killed"]
con = duckdb.connect()

year_rows = con.execute(
    """
    SELECT YEAR(crash_date) AS yr, COUNT(*) AS n,
           MIN(crash_date) AS first_date, MAX(crash_date) AS last_date
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY yr ORDER BY yr
    """,
    [str(DATA)],
).fetchall()
year_lookup = {row[0]: row for row in year_rows}

for option_id in (1, 2):
    facts = [("population_rows_total_2013_2025", sum(row[1] for row in year_rows))]
    for year in YEARS:
        row = year_lookup.get(year)
        facts.append((f"population_rows_{year}", row[1] if row else 0))
        if row:
            first_date, last_date = row[2], row[3]
            full_endpoints = (
                first_date.strftime("%m-%d") == "01-01"
                and last_date.strftime("%m-%d") == "12-31"
            )
            coverage = "full endpoint coverage" if full_endpoints else "partial year"
            facts.append(
                (f"crash_date_coverage_{year}", f"{first_date} through {last_date}; {coverage}")
            )
        else:
            facts.append((f"crash_date_coverage_{year}", "no rows"))

    for column in DEATH_COLUMNS:
        totals = con.execute(
            f"""SELECT COUNT(*) FILTER (WHERE {column} IS NULL),
                       COUNT(*) FILTER (WHERE {column} < 0),
                       COUNT(*) FILTER (WHERE {column} = 0)
                FROM read_parquet(?)
                WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'""",
            [str(DATA)],
        ).fetchone()
        facts.extend(
            [
                (f"{column}_missing_null_rows", totals[0]),
                (f"{column}_impossible_negative_rows", totals[1]),
                (f"{column}_zero_value_rows", totals[2]),
            ]
        )
        for year in YEARS:
            values = con.execute(
                f"""SELECT COUNT(*) FILTER (WHERE {column} IS NULL),
                           COUNT(*) FILTER (WHERE {column} < 0),
                           COUNT(*) FILTER (WHERE {column} = 0)
                    FROM read_parquet(?) WHERE YEAR(crash_date) = ?""",
                [str(DATA), year],
            ).fetchone()
            facts.extend(
                [
                    (f"{column}_missing_null_rows_{year}", values[0]),
                    (f"{column}_impossible_negative_rows_{year}", values[1]),
                    (f"{column}_zero_value_rows_{year}", values[2]),
                ]
            )

    with open(f"out/check_{option_id}.csv", "w", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)
