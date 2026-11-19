from pathlib import Path
import csv
import sys

import duckdb


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
option_id = int(sys.argv[1])
outcome_columns = {
    1: ["number_of_pedestrians_injured", "number_of_pedestrians_killed"],
    2: ["number_of_pedestrians_killed"],
}[option_id]

con = duckdb.connect()
data_path = str(DATA).replace("'", "''")
con.execute("CREATE VIEW crashes AS SELECT crash_date, borough, " + ", ".join(outcome_columns) + f" FROM read_parquet('{data_path}')")

# Candidate rows are date-valid rows in the planned 2013+ period; borough
# completeness is checked before applying the Brooklyn filter so excluded
# unknown-borough records remain visible in the audit.
candidate = con.execute(
    """
    SELECT
      count(*) AS rows,
      count(*) FILTER (WHERE borough IS NULL OR trim(borough) = '' OR upper(trim(borough)) IN
        ('UNKNOWN', 'UNSPECIFIED', 'NOT REPORTED', 'N/A', 'NA', 'NULL', 'NONE', '(UNKNOWN)')) AS missing_borough,
      count(*) FILTER (WHERE upper(trim(borough)) = 'BROOKLYN') AS brooklyn_rows,
      min(crash_date) AS first_brooklyn_date,
      max(crash_date) AS last_brooklyn_date
    FROM crashes
    WHERE crash_date >= DATE '2013-01-01'
    """
).fetchone()

final_population = con.execute(
    """
    SELECT count(*) AS rows,
           count(*) FILTER (WHERE crash_date IS NULL) AS missing_crash_date,
           count(*) FILTER (WHERE borough IS NULL OR trim(borough) = '' OR upper(trim(borough)) IN
             ('UNKNOWN', 'UNSPECIFIED', 'NOT REPORTED', 'N/A', 'NA', 'NULL', 'NONE', '(UNKNOWN)')) AS missing_borough
    FROM crashes
    WHERE upper(trim(borough)) = 'BROOKLYN'
      AND crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    """
).fetchone()

facts = [
    ("2013_or_later_rows_before_borough_filter", candidate[0]),
    ("2013_or_later_rows_with_missing_or_unknown_borough", candidate[1]),
    ("2013_or_later_rows_normalized_borough_brooklyn", candidate[2]),
    ("first_observed_date_in_selected_borough_and_period", candidate[3]),
    ("last_observed_date_in_selected_borough_and_period", candidate[4]),
    ("brooklyn_crash_rows_final_complete_years_2013_2025", final_population[0]),
    ("final_population_rows_missing_crash_date", final_population[1]),
    ("final_population_rows_missing_or_unknown_borough", final_population[2]),
]

per_year = con.execute(
    """
    SELECT year(crash_date) AS year, count(*) AS rows,
           min(crash_date) AS first_date, max(crash_date) AS last_date,
           """ + ", ".join(
        f"count(*) FILTER (WHERE {column} IS NULL) AS missing_{column}"
        for column in outcome_columns
    ) + """
    FROM crashes
    WHERE crash_date >= DATE '2013-01-01'
      AND upper(trim(borough)) = 'BROOKLYN'
    GROUP BY year(crash_date)
    ORDER BY year
    """
).fetchall()

for year, rows, first_date, last_date, *missing_counts in per_year:
    facts.extend([
        (f"brooklyn_crash_rows_{year}", rows),
        (f"brooklyn_first_observed_crash_date_{year}", first_date),
        (f"brooklyn_last_observed_crash_date_{year}", last_date),
    ])
    for column, missing_count in zip(outcome_columns, missing_counts):
        facts.append((f"brooklyn_rows_missing_{column}_{year}", missing_count))

with (OUT / f"check_{option_id}.csv").open("w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["fact", "value"])
    writer.writerows(facts)
