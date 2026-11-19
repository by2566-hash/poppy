import csv
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"
START_YEAR = 2013
END_YEAR = 2025

con = duckdb.connect()
con.execute("SET threads=1")

# Restrict the check population to rows whose typed crash_date falls in the
# plan's requested years. No death values are aggregated or counted by value.
year_rows = con.execute(
    """
    SELECT year(crash_date) AS year, count(*) AS rows
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
    """,
    [str(DATA)],
).fetchall()

year_date_bounds = con.execute(
    """
    SELECT year(crash_date) AS year, min(crash_date), max(crash_date)
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
    """,
    [str(DATA)],
).fetchall()

date_quality = con.execute(
    """
    WITH scoped AS (
      SELECT crash_date
      FROM read_parquet(?)
      WHERE crash_date >= DATE '2013-01-01'
        AND crash_date < DATE '2026-01-01'
    ), date_counts AS (
      SELECT crash_date, count(*) AS n FROM scoped GROUP BY crash_date
    )
    SELECT min(crash_date), max(crash_date),
           count(*) FILTER (WHERE crash_date IS NULL),
           count(*) FILTER (WHERE crash_date IN (DATE '2013-01-01', DATE '1970-01-01', DATE '1900-01-01'))
    FROM scoped
    """,
    [str(DATA)],
).fetchone()

max_day = con.execute(
    """
    SELECT crash_date, n FROM (
      SELECT crash_date, count(*) AS n
      FROM read_parquet(?)
      WHERE crash_date >= DATE '2013-01-01'
        AND crash_date < DATE '2026-01-01'
      GROUP BY crash_date
      ORDER BY n DESC, crash_date
      LIMIT 1
    )
    """,
    [str(DATA)],
).fetchone()

missing = con.execute(
    """
    SELECT count(*) FILTER (WHERE number_of_motorist_killed IS NULL),
           count(*) FILTER (WHERE number_of_cyclist_killed IS NULL)
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    """,
    [str(DATA)],
).fetchone()

facts = [
    ("population_rows_2013_2025", sum(rows for _, rows in year_rows)),
    ("observed_first_crash_date_in_scope", date_quality[0]),
    ("observed_last_crash_date_in_scope", date_quality[1]),
    ("crash_date_missing_rows_in_scope", date_quality[2]),
    ("crash_date_known_sentinel_dates_in_scope", date_quality[3]),
    ("largest_single_date_pileup", f"{max_day[0]}: {max_day[1]} rows" if max_day else "none"),
    ("number_of_motorist_killed_missing_rows_in_scope", missing[0]),
    ("number_of_cyclist_killed_missing_rows_in_scope", missing[1]),
]
facts.extend((f"rows_in_{year}", rows) for year, rows in year_rows)
for year, first_date, last_date in year_date_bounds:
    facts.append((f"first_crash_date_in_{year}", first_date))
    facts.append((f"last_crash_date_in_{year}", last_date))

# Report every requested year, including years with no records.
year_map = dict(year_rows)
for year in range(START_YEAR, END_YEAR + 1):
    if year not in year_map:
        facts.append((f"rows_in_{year}", 0))

for option_id in (1, 2):
    with (OUT / f"check_{option_id}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)
