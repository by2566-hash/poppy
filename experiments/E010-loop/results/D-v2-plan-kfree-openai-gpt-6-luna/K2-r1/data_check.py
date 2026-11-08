import csv
from pathlib import Path

import duckdb


DATA = "data/crashes.parquet"
OUT = Path("out")
START = "2013-01-01"
END = "2025-12-31"

con = duckdb.connect()
con.execute(f"CREATE VIEW crashes AS SELECT crash_date FROM read_parquet('{DATA}')")
overall = con.execute(
    """
    SELECT count(*) AS n,
           count(*) FILTER (WHERE crash_date IS NULL) AS missing_dates,
           count(*) FILTER (WHERE crash_date BETWEEN DATE '2013-01-01' AND DATE '2025-12-31') AS eligible
    FROM crashes
    """
).fetchone()
annual = con.execute(
    """
    SELECT year(crash_date) AS yr, count(*) AS n,
           min(crash_date) AS first_date, max(crash_date) AS last_date,
           count(DISTINCT crash_date) AS distinct_dates
    FROM crashes
    WHERE crash_date BETWEEN DATE '2013-01-01' AND DATE '2025-12-31'
    GROUP BY yr ORDER BY yr
    """
).fetchall()
defaults = con.execute(
    """
    SELECT count(*) FILTER (WHERE crash_date = DATE '1900-01-01') AS d1900,
           count(*) FILTER (WHERE crash_date = DATE '1970-01-01') AS d1970,
           count(*) FILTER (WHERE crash_date = DATE '2000-01-01') AS d2000,
           count(*) FILTER (WHERE crash_date = DATE '2013-01-01') AS d2013
    FROM crashes
    WHERE crash_date BETWEEN DATE '2013-01-01' AND DATE '2025-12-31'
    """
).fetchone()

facts = [
    ("Rows in requested date range (2013-01-01 through 2025-12-31)", overall[2]),
    ("Rows with missing crash_date in entire file (excluded; year cannot be assigned)", overall[1]),
    ("Rows with usable crash_date outside requested date range (excluded)", overall[0] - overall[1] - overall[2]),
    ("crash_date missing among eligible population rows", 0),
    ("crash_date has no empty-string/unknown-word/impossible values: parquet column is typed DATE; NULL count reported separately", "not applicable to DATE type"),
    ("crash_date count at candidate default 1900-01-01 in range", defaults[0]),
    ("crash_date count at candidate default 1970-01-01 in range", defaults[1]),
    ("crash_date count at candidate default 2000-01-01 in range", defaults[2]),
    ("crash_date count at candidate default 2013-01-01 in range", defaults[3]),
]
for yr in range(2013, 2026):
    row = next((x for x in annual if x[0] == yr), None)
    if row:
        facts.extend([
            (f"Rows in {yr}", row[1]),
            (f"Observed crash_date span in {yr}", f"{row[2]} through {row[3]}"),
            (f"Distinct crash dates represented in {yr}", row[4]),
            (f"Coverage endpoint check for {yr}", "full calendar-year endpoints observed" if str(row[2]) == f"{yr}-01-01" and str(row[3]) == f"{yr}-12-31" else "partial at one or both calendar-year endpoints"),
        ])
    else:
        facts.extend([
            (f"Rows in {yr}", 0),
            (f"Observed crash_date span in {yr}", "no rows"),
            (f"Distinct crash dates represented in {yr}", 0),
            (f"Coverage endpoint check for {yr}", "no observations"),
        ])

for plan_id in (1, 2, 3):
    with (OUT / f"check_{plan_id}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)
