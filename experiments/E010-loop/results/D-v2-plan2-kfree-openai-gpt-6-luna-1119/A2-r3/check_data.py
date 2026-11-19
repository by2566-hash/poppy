import csv
from pathlib import Path

import duckdb


DATA = Path("data/crashes.parquet")
OUT = Path("out")
con = duckdb.connect()

# The initial plans use all dated crash rows and these four columns only.
per_year = con.execute(
    f"""
    SELECT year(crash_date) AS year,
           count(*) AS row_count,
           min(crash_date) AS first_date,
           max(crash_date) AS last_date,
           count(*) FILTER (WHERE crash_time IS NULL) AS missing_crash_time,
           count(*) FILTER (WHERE crash_time = TIME '00:00:00') AS midnight_crash_time,
           count(*) FILTER (WHERE number_of_persons_injured IS NULL) AS missing_injured,
           count(*) FILTER (WHERE number_of_persons_killed IS NULL) AS missing_killed,
           count(*) FILTER (WHERE number_of_persons_injured IS NULL OR number_of_persons_killed IS NULL) AS missing_either_outcome
    FROM read_parquet('{DATA.as_posix()}')
    WHERE crash_date IS NOT NULL
    GROUP BY year
    ORDER BY year
    """
).fetchall()

totals = con.execute(
    f"""
    SELECT count(*) AS row_count,
           count(*) FILTER (WHERE crash_time IS NULL) AS missing_crash_time,
           count(*) FILTER (WHERE crash_time = TIME '00:00:00') AS midnight_crash_time,
           count(*) FILTER (WHERE number_of_persons_injured IS NULL) AS missing_injured,
           count(*) FILTER (WHERE number_of_persons_killed IS NULL) AS missing_killed,
           count(*) FILTER (WHERE number_of_persons_injured IS NULL OR number_of_persons_killed IS NULL) AS missing_either_outcome
    FROM read_parquet('{DATA.as_posix()}')
    WHERE crash_date IS NOT NULL
    """
).fetchone()

names = ["year", "row_count", "first_date", "last_date", "missing_crash_time",
         "midnight_crash_time", "missing_injured", "missing_killed", "missing_either_outcome"]
records = [dict(zip(names, row)) for row in per_year]
values = []
values.append(("Population rows with non-NULL crash_date", totals[0]))
values.append(("Years represented (number)", len(records)))
for record in records:
    year = record["year"]
    values.extend([
        (f"{year}: population rows", record["row_count"]),
        (f"{year}: observed date range", f"{record['first_date']} to {record['last_date']}"),
        (f"{year}: partial calendar year", str(record["first_date"].month != 1 or record["first_date"].day != 1 or record["last_date"].month != 12 or record["last_date"].day != 31).lower()),
        (f"{year}: crash_time missing/unclassifiable (NULL; TIME type makes blank/word/impossible values inapplicable)", record["missing_crash_time"]),
        (f"{year}: crash_time piled at 00:00:00 (possible default; check only, not assumed invalid)", record["midnight_crash_time"]),
        (f"{year}: number_of_persons_injured missing", record["missing_injured"]),
        (f"{year}: number_of_persons_killed missing", record["missing_killed"]),
        (f"{year}: rows missing either person outcome count", record["missing_either_outcome"]),
    ])
values.extend([
    ("All years: crash_time missing/unclassifiable (NULL; TIME type makes blank/word/impossible values inapplicable)", totals[1]),
    ("All years: crash_time piled at 00:00:00 (possible default; check only, not assumed invalid)", totals[2]),
    ("All years: number_of_persons_injured missing", totals[3]),
    ("All years: number_of_persons_killed missing", totals[4]),
    ("All years: rows missing either person outcome count", totals[5]),
])
retained = [record for record in records if 2013 <= record["year"] <= 2025]
values.extend([
    ("Proposed final years 2013-2025: population rows", sum(record["row_count"] for record in retained)),
    ("Proposed final years 2013-2025: crash_time NULL", sum(record["missing_crash_time"] for record in retained)),
    ("Proposed final years 2013-2025: exact 00:00:00 timestamps (possible default)", sum(record["midnight_crash_time"] for record in retained)),
    ("Proposed final years 2013-2025: number_of_persons_injured missing", sum(record["missing_injured"] for record in retained)),
    ("Proposed final years 2013-2025: number_of_persons_killed missing", sum(record["missing_killed"] for record in retained)),
    ("Proposed final years 2013-2025: rows missing either person outcome count", sum(record["missing_either_outcome"] for record in retained)),
])

with (OUT / "check_1.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["fact", "value"])
    writer.writerows(values)
with (OUT / "check_2.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["fact", "value"])
    writer.writerows(values)

print(f"Wrote checks for {totals[0]} dated rows across {len(records)} years.")
