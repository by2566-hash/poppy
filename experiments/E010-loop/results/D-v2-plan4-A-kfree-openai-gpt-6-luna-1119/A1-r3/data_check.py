from pathlib import Path

import duckdb
import pandas as pd


DATA = Path(__file__).resolve().parents[1] / "data" / "crashes.parquet"
OUT = Path(__file__).resolve().parent

con = duckdb.connect()
con.from_parquet(str(DATA)).create_view("crashes")

# These checks are limited to the columns used by the two initial plans:
# crash_date, borough, number_of_pedestrians_injured, and
# number_of_pedestrians_killed. Outcome fields are checked only for NULLs.
date_summary = con.execute(
    """
    SELECT MIN(crash_date) AS min_date,
           MAX(crash_date) AS max_date,
           COUNT(*) FILTER (WHERE crash_date IS NULL) AS missing_dates
    FROM crashes
    """
).fetchone()
min_date, max_date, missing_dates = date_summary

year_rows = con.execute(
    """
    SELECT YEAR(crash_date) AS year,
           MIN(crash_date) AS first_recorded_date,
           MAX(crash_date) AS last_recorded_date,
           COUNT(*) FILTER (
               WHERE LOWER(TRIM(COALESCE(borough, ''))) = 'brooklyn'
           ) AS brooklyn_rows
    FROM crashes
    WHERE crash_date >= DATE '2013-01-01'
    GROUP BY YEAR(crash_date)
    ORDER BY year
    """
).fetchdf()

borough_check = con.execute(
    """
    SELECT COUNT(*) FILTER (
               WHERE borough IS NULL OR LOWER(TRIM(borough)) IN
                     ('', 'unknown', 'unk', 'n/a', 'na', 'null', 'none',
                      'unspecified', 'not known', 'not applicable', '0')
           ) AS missing_or_placeholder,
           COUNT(*) FILTER (
               WHERE LOWER(TRIM(COALESCE(borough, ''))) IN
                     ('unknown', 'unk', 'unspecified', 'not known',
                      'not applicable', '0')
           ) AS placeholder_or_default
    FROM crashes
    WHERE crash_date >= DATE '2013-01-01'
    """
).fetchone()

facts = [
    ("file_min_recorded_crash_date", str(min_date)),
    ("file_max_recorded_crash_date", str(max_date)),
    ("rows_with_missing_crash_date_in_file", int(missing_dates)),
    ("dated_rows_in_2013_or_later", int(con.execute(
        "SELECT COUNT(*) FROM crashes WHERE crash_date >= DATE '2013-01-01'"
    ).fetchone()[0])),
    ("borough_missing_or_placeholder_rows_among_dated_2013_plus", int(borough_check[0])),
    ("borough_placeholder_or_default_rows_among_dated_2013_plus", int(borough_check[1])),
]

for _, row in year_rows.iterrows():
    y = int(row["year"])
    first = pd.Timestamp(row["first_recorded_date"]).date()
    last = pd.Timestamp(row["last_recorded_date"]).date()
    expected_start = pd.Timestamp(year=y, month=1, day=1).date()
    expected_end = pd.Timestamp(year=y, month=12, day=31).date()
    partial = first > expected_start or last < expected_end
    facts.extend([
        (f"dated_rows_{y}", int(con.execute(
            "SELECT COUNT(*) FROM crashes WHERE YEAR(crash_date) = ?", [y]
        ).fetchone()[0])),
        (f"brooklyn_rows_{y}", int(row["brooklyn_rows"])),
        (f"first_recorded_date_{y}", str(first)),
        (f"last_recorded_date_{y}", str(last)),
        (f"year_{y}_appears_partial_by_recorded_date_span", str(partial).lower()),
    ])

    # Restrict outcome missingness checks to the Brooklyn population and year.
    miss = con.execute(
        """
        SELECT COUNT(*) FILTER (WHERE number_of_pedestrians_injured IS NULL),
               COUNT(*) FILTER (WHERE number_of_pedestrians_killed IS NULL)
        FROM crashes
        WHERE YEAR(crash_date) = ?
          AND LOWER(TRIM(COALESCE(borough, ''))) = 'brooklyn'
        """,
        [y],
    ).fetchone()
    facts.extend([
        (f"pedestrian_injuries_missing_rows_{y}_brooklyn", int(miss[0])),
        (f"pedestrian_deaths_missing_rows_{y}_brooklyn", int(miss[1])),
    ])

facts.extend([
    ("pedestrian_injuries_missing_rows_2013_plus_brooklyn", int(con.execute(
        """SELECT COUNT(*) FROM crashes
           WHERE crash_date >= DATE '2013-01-01'
             AND LOWER(TRIM(COALESCE(borough, ''))) = 'brooklyn'
             AND number_of_pedestrians_injured IS NULL"""
    ).fetchone()[0])),
    ("pedestrian_deaths_missing_rows_2013_plus_brooklyn", int(con.execute(
        """SELECT COUNT(*) FROM crashes
           WHERE crash_date >= DATE '2013-01-01'
             AND LOWER(TRIM(COALESCE(borough, ''))) = 'brooklyn'
             AND number_of_pedestrians_killed IS NULL"""
    ).fetchone()[0])),
    ("brooklyn_rows_2013_to_2025", int(con.execute(
        """SELECT COUNT(*) FROM crashes
           WHERE crash_date >= DATE '2013-01-01'
             AND crash_date < DATE '2026-01-01'
             AND LOWER(TRIM(COALESCE(borough, ''))) = 'brooklyn'"""
    ).fetchone()[0])),
    ("dated_rows_2013_to_2025", int(con.execute(
        """SELECT COUNT(*) FROM crashes
           WHERE crash_date >= DATE '2013-01-01'
             AND crash_date < DATE '2026-01-01'"""
    ).fetchone()[0])),
    ("borough_missing_or_placeholder_rows_2013_to_2025", int(con.execute(
        """SELECT COUNT(*) FROM crashes
           WHERE crash_date >= DATE '2013-01-01'
             AND crash_date < DATE '2026-01-01'
             AND (borough IS NULL OR LOWER(TRIM(borough)) IN
                  ('', 'unknown', 'unk', 'n/a', 'na', 'null', 'none',
                   'unspecified', 'not known', 'not applicable', '0'))"""
    ).fetchone()[0])),
    ("borough_impossible_nonmissing_rows_2013_to_2025", int(con.execute(
        """SELECT COUNT(*) FROM crashes
           WHERE crash_date >= DATE '2013-01-01'
             AND crash_date < DATE '2026-01-01'
             AND borough IS NOT NULL
             AND LOWER(TRIM(borough)) NOT IN
                 ('', 'unknown', 'unk', 'n/a', 'na', 'null', 'none',
                  'unspecified', 'not known', 'not applicable', '0',
                  'brooklyn', 'queens', 'manhattan', 'bronx',
                  'staten island')"""
    ).fetchone()[0])),
    ("borough_placeholder_or_default_rows_2013_to_2025", int(con.execute(
        """SELECT COUNT(*) FROM crashes
           WHERE crash_date >= DATE '2013-01-01'
             AND crash_date < DATE '2026-01-01'
             AND LOWER(TRIM(COALESCE(borough, ''))) IN
                 ('unknown', 'unk', 'unspecified', 'not known',
                  'not applicable', '0')"""
    ).fetchone()[0])),
])

for option_id in (1, 2):
    pd.DataFrame(facts, columns=["fact", "value"]).to_csv(
        OUT / f"check_{option_id}.csv", index=False
    )

print(f"Wrote checks for {len(year_rows)} years ({min_date} through {max_date}).")
