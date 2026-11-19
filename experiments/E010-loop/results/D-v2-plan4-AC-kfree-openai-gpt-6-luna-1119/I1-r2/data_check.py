import csv
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
START_YEAR = 2013
END_YEAR = 2025

con = duckdb.connect()
data_path = str(DATA).replace("'", "''")
con.execute(
    "CREATE VIEW crashes AS SELECT crash_date, number_of_motorist_killed "
    f"FROM read_parquet('{data_path}')"
)

rows = con.execute(
    """
    SELECT year(crash_date) AS yr,
           count(*) AS n_rows,
           min(crash_date) AS first_date,
           max(crash_date) AS last_date,
           count(*) FILTER (WHERE crash_date IS NULL) AS missing_crash_date,
           count(*) FILTER (WHERE number_of_motorist_killed IS NULL) AS missing_motorist_killed
    FROM crashes
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY yr
    ORDER BY yr
    """
).fetchall()

total_rows = sum(row[1] for row in rows)
facts = [
    ("population_rows_2013_2025", total_rows),
]

rows_by_year = {row[0]: row for row in rows}
for year in range(START_YEAR, END_YEAR + 1):
    record = rows_by_year.get(year)
    if record is None:
        facts.append((f"rows_{year}", 0))
        facts.append((f"date_coverage_{year}", "no dated rows"))
        facts.append((f"missing_crash_date_{year}", 0))
        facts.append((f"missing_number_of_motorist_killed_{year}", 0))
        continue
    _, count, first_date, last_date, missing_date, missing_killed = record
    facts.extend(
        [
            (f"rows_{year}", count),
            (f"date_coverage_{year}", f"{first_date} through {last_date}"),
            (f"missing_crash_date_{year}", missing_date),
            (f"missing_number_of_motorist_killed_{year}", missing_killed),
        ]
    )

for option_id in (1, 2):
    with (OUT / f"check_{option_id}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)
