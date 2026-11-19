import csv
from pathlib import Path

import duckdb


DATA = "data/crashes.parquet"
OUT = Path("out")
con = duckdb.connect()


def write_facts(option_id, facts):
    with (OUT / f"check_{option_id}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)


# Both plans use crashes assignable to a calendar year. These are candidate
# rows before any decision to drop incomplete calendar years.
base = con.execute(
    f"""
    SELECT count(*) AS all_rows,
           count(*) FILTER (WHERE crash_date IS NULL) AS missing_date,
           count(*) FILTER (WHERE crash_date IS NOT NULL) AS dated_rows,
           min(crash_date) FILTER (WHERE crash_date IS NOT NULL) AS first_date,
           max(crash_date) FILTER (WHERE crash_date IS NOT NULL) AS last_date,
           count(*) FILTER (WHERE crash_date = DATE '1900-01-01') AS date_1900_default,
           count(*) FILTER (WHERE crash_date = DATE '1970-01-01') AS date_1970_default
    FROM read_parquet('{DATA}')
    """
).fetchone()

year_rows = con.execute(
    f"""
    SELECT year(crash_date) AS year, count(*) AS rows,
           min(crash_date) AS first_date, max(crash_date) AS last_date
    FROM read_parquet('{DATA}')
    WHERE crash_date IS NOT NULL
    GROUP BY year ORDER BY year
    """
).fetchall()

counts = con.execute(
    f"""
    SELECT count(*) AS final_year_candidate_rows,
           count(*) FILTER (WHERE crash_time IS NULL) AS missing_time,
           count(*) FILTER (WHERE crash_time = TIME '00:00:00') AS midnight_time,
           count(*) FILTER (WHERE crash_date = DATE '1900-01-01') AS date_1900_default,
           count(*) FILTER (WHERE crash_date = DATE '1970-01-01') AS date_1970_default
    FROM read_parquet('{DATA}')
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    """
).fetchone()

outcome_counts = con.execute(
    f"""
    SELECT count(*) FILTER (WHERE number_of_persons_injured IS NULL) AS missing_injured,
           count(*) FILTER (WHERE number_of_persons_killed IS NULL) AS missing_killed,
           count(*) FILTER (WHERE number_of_persons_injured IS NULL
                             OR number_of_persons_killed IS NULL) AS missing_either_outcome,
           count(*) FILTER (WHERE number_of_persons_injured IS NOT NULL
                             AND number_of_persons_killed IS NOT NULL) AS classifiable_outcome_rows
    FROM read_parquet('{DATA}')
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    """
).fetchone()

# The schema declares DATE and TIME, so non-null values cannot be blank text,
# textual unknowns, or syntactically impossible dates/times.
schema = con.execute(f"DESCRIBE SELECT crash_date, crash_time FROM read_parquet('{DATA}')").fetchall()
schema_types = {row[0]: row[1] for row in schema}

common_facts = [
    ("all_file_rows", base[0]),
    ("rows_missing_crash_date_excluded_from_year_grouping", base[1]),
    ("dated_candidate_rows_across_all_years", base[2]),
    ("first_recorded_crash_date", str(base[3])),
    ("last_recorded_crash_date", str(base[4])),
    ("dated_rows_in_1900-01-01_date_default_across_file", base[5]),
    ("dated_rows_in_1970-01-01_date_default_across_file", base[6]),
    ("crash_date_schema_type", schema_types["crash_date"]),
    ("crash_time_schema_type", schema_types["crash_time"]),
    ("rows_in_final_years_2013_through_2025", counts[0]),
    ("crash_time_missing_rows_in_final_years_2013_through_2025", counts[1]),
    ("crash_time_midnight_rows_in_final_years_2013_through_2025", counts[2]),
    ("crash_date_1900-01-01_rows_in_final_years_2013_through_2025", counts[3]),
    ("crash_date_1970-01-01_rows_in_final_years_2013_through_2025", counts[4]),
    ("DATE_and_TIME_typed_fields_exclude_blank_unknown_text_and_impossible_encoded_values", "yes; NULL is the missing/unclassifiable representation"),
]
for year, rows, first_date, last_date in year_rows:
    common_facts.extend(
        [
            (f"rows_in_{year}", rows),
            (f"first_recorded_date_in_{year}", str(first_date)),
            (f"last_recorded_date_in_{year}", str(last_date)),
            (f"calendar_year_{year}_appears_partial_by_recorded_date_span", "yes" if first_date.year != year or last_date.month != 12 or last_date.day != 31 or first_date.month != 1 or first_date.day != 1 else "no"),
        ]
    )

write_facts(1, common_facts)
write_facts(
    2,
    common_facts
    + [
        ("number_of_persons_injured_missing_rows_in_final_years_2013_through_2025", outcome_counts[0]),
        ("number_of_persons_killed_missing_rows_in_final_years_2013_through_2025", outcome_counts[1]),
        ("rows_missing_either_total_outcome_field_in_final_years_2013_through_2025", outcome_counts[2]),
        ("rows_with_both_total_outcome_fields_present_in_final_years_2013_through_2025", outcome_counts[3]),
    ],
)
con.close()
