import csv
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parent.parent
PARQUET = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"

con = duckdb.connect()
con.execute(
    "CREATE VIEW crashes AS SELECT crash_date, crash_time, number_of_persons_injured, "
    f"number_of_persons_killed FROM read_parquet('{PARQUET}')"
)

# The population is all records with a non-null crash_date. This is the date
# field that defines the included calendar years; records without a date cannot
# be assigned to a year and are counted separately.
coverage = con.execute(
    """
    SELECT COUNT(*) AS n,
           COUNT(*) FILTER (WHERE crash_date IS NULL) AS no_date,
           MIN(crash_date) AS first_date,
           MAX(crash_date) AS last_date
    FROM crashes
    """
).fetchone()
date_default_counts = con.execute(
    """
    SELECT COUNT(*) FILTER (WHERE crash_date = DATE '1900-01-01') AS date_1900,
           COUNT(*) FILTER (WHERE crash_date = DATE '1970-01-01') AS date_1970,
           COUNT(*) FILTER (WHERE crash_date = DATE '2000-01-01') AS date_2000,
           COUNT(*) FILTER (WHERE crash_date IS NOT NULL AND LOWER(TRIM(CAST(crash_date AS VARCHAR))) IN
             ('', 'unknown', 'unspecified', 'na', 'n/a', 'null')) AS date_unknown_text,
           COUNT(*) FILTER (WHERE crash_date IS NOT NULL AND
             TRY_CAST(CAST(crash_date AS VARCHAR) AS DATE) IS NULL) AS date_impossible
    FROM crashes
    """
).fetchone()
years = con.execute(
    """
    SELECT YEAR(crash_date) AS yr, COUNT(*) AS n,
           MIN(crash_date) AS first_date, MAX(crash_date) AS last_date
    FROM crashes WHERE crash_date IS NOT NULL
    GROUP BY yr ORDER BY yr
    """
).fetchall()

time_facts = con.execute(
    """
    SELECT COUNT(*) FILTER (WHERE crash_time IS NULL) AS missing,
           COUNT(*) FILTER (WHERE LOWER(TRIM(CAST(crash_time AS VARCHAR))) IN
             ('', 'unknown', 'unspecified', 'na', 'n/a', 'null')) AS unknown_text,
           COUNT(*) FILTER (WHERE crash_time IS NOT NULL AND
             TRY_CAST(CAST(crash_time AS VARCHAR) AS TIME) IS NULL) AS impossible,
           COUNT(*) FILTER (WHERE crash_time = TIME '00:00:00') AS midnight_default
    FROM crashes WHERE crash_date IS NOT NULL
    """
).fetchone()

all_rows = coverage[0]
date_missing = coverage[1]
date_min = coverage[2]
date_max = coverage[3]
year_rows = {row[0]: row for row in years}
outcome_facts = con.execute(
    """
    SELECT COUNT(*) FILTER (WHERE number_of_persons_injured IS NULL) AS injured_missing,
           COUNT(*) FILTER (WHERE number_of_persons_killed IS NULL) AS killed_missing,
           COUNT(*) FILTER (WHERE number_of_persons_injured IS NULL OR
                                  number_of_persons_killed IS NULL) AS either_missing
    FROM crashes WHERE crash_date IS NOT NULL
    """
).fetchone()

for option_id in (1, 2, 3):
    facts = [
        ("population_rows_with_date", all_rows - date_missing),
        ("population_rows_missing_crash_date_unassignable_to_year", date_missing),
        ("first_crash_date", date_min.isoformat() if date_min else "none"),
        ("last_crash_date", date_max.isoformat() if date_max else "none"),
        ("crash_date_at_1900_01_01_possible_default", date_default_counts[0]),
        ("crash_date_at_1970_01_01_possible_default", date_default_counts[1]),
        ("crash_date_at_2000_01_01_possible_default", date_default_counts[2]),
        ("crash_date_unknown_text_forms", date_default_counts[3]),
        ("crash_date_impossible_or_unparseable", date_default_counts[4]),
        ("crash_time_missing", time_facts[0]),
        ("crash_time_unknown_text_forms", time_facts[1]),
        ("crash_time_impossible_or_unparseable", time_facts[2]),
        ("crash_time_at_midnight_00_00_00_possible_default", time_facts[3]),
    ]
    for yr, n, first_date, last_date in years:
        facts.append((f"rows_in_{yr}", n))
        facts.append((f"date_range_in_{yr}", f"{first_date.isoformat()} through {last_date.isoformat()}"))
        if yr == years[0][0] or yr == years[-1][0]:
            calendar_start = f"{yr}-01-01"
            calendar_end = f"{yr}-12-31"
            partial = first_date.isoformat() > calendar_start or last_date.isoformat() < calendar_end
            facts.append((f"endpoint_year_{yr}_partial_by_observed_date_range", str(partial).lower()))
    if option_id in (2, 3):
        facts.extend([
            ("number_of_persons_injured_missing", outcome_facts[0]),
            ("number_of_persons_killed_missing", outcome_facts[1]),
            ("rows_missing_either_summed_outcome_field", outcome_facts[2]),
        ])
    with (OUT / f"check_{option_id}.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)
