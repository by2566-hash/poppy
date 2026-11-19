import csv
import duckdb
import sys
from pathlib import Path


DATA = "data/crashes.parquet"
OUT = Path("out")
OPTION = int(sys.argv[1])
con = duckdb.connect()

# Only inspect the date/time fields used by both plans here. No injury field
# is read for plan 1, and no injury values or outcome totals are calculated.
year_rows = con.execute(f"""
    SELECT year(crash_date) AS yr,
           count(*) AS dated_rows,
           min(crash_date) AS first_date,
           max(crash_date) AS last_date,
           count(*) FILTER (WHERE crash_time IS NULL) AS missing_time,
           count(*) FILTER (WHERE crash_time = TIME '00:00:00') AS midnight_time,
           count(*) FILTER (WHERE crash_time IS NOT NULL) AS valid_time_rows
    FROM read_parquet('{DATA}')
    WHERE crash_date IS NOT NULL
    GROUP BY yr
    ORDER BY yr
""").fetchall()
global_rows = con.execute(f"""
    SELECT count(*) AS total_rows,
           count(*) FILTER (WHERE crash_date IS NULL) AS missing_date,
           count(*) FILTER (WHERE crash_time IS NULL) AS missing_time_any_date,
           count(*) FILTER (WHERE crash_date = DATE '1900-01-01') AS date_1900_default,
           count(*) FILTER (WHERE crash_date = DATE '1970-01-01') AS date_1970_default,
           count(*) FILTER (WHERE crash_time = TIME '00:00:00') AS midnight_any_date
    FROM read_parquet('{DATA}')
""").fetchone()

years = []
for yr, dated_rows, first_date, last_date, missing_time, midnight_time, valid_time in year_rows:
    first_of_year = first_date.replace(month=1, day=1)
    last_of_year = last_date.replace(month=12, day=31)
    # Dataset boundaries are assessed from observed crash-date coverage.
    partial = first_date != first_of_year or last_date != last_of_year
    years.append({
        "year": yr, "rows": dated_rows, "first": first_date.isoformat(),
        "last": last_date.isoformat(), "partial": partial,
        "missing_time": missing_time, "midnight": midnight_time, "valid_time": valid_time,
    })

all_rows, missing_date, missing_time_any, date_1900, date_1970, midnight_all = global_rows
missing_time_in_years = sum(y["missing_time"] for y in years)
midnight_in_years = sum(y["midnight"] for y in years)
valid_datetime = sum(y["valid_time"] for y in years)
complete_years = [y for y in years if not y["partial"]]
eligible_rows_complete = sum(y["valid_time"] for y in complete_years)
eligible_rows_all = valid_datetime
complete_date_rows = sum(y["rows"] for y in complete_years)
midnight_complete = sum(y["midnight"] for y in complete_years)

def emit(option_id, facts):
    path = OUT / f"check_{option_id}.csv"
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)

year_text = "; ".join(
    f"{y['year']}: {y['rows']} dated rows, {y['first']} to {y['last']}, "
    f"{'partial' if y['partial'] else 'full-boundary'}, {y['valid_time']} valid date/time, "
    f"{y['missing_time']} missing time, {y['midnight']} midnight time"
    for y in years
)
common = [
    ("rows_by_year_and_date_coverage", year_text),
    ("rows_with_missing_crash_date_any_year", missing_date),
    ("rows_with_missing_crash_time_in_dated_year_rows", missing_time_in_years),
    ("rows_with_midnight_crash_time_in_dated_year_rows", midnight_in_years),
    ("rows_with_midnight_crash_time_in_complete_boundary_years", midnight_complete),
    ("share_of_valid_time_rows_at_midnight_in_complete_boundary_years",
     f"{midnight_complete / eligible_rows_complete:.6%}" if eligible_rows_complete else "0"),
    ("rows_with_midnight_crash_time_any_date", midnight_all),
    ("rows_with_crash_date_1900_01_01", date_1900),
    ("rows_with_crash_date_1970_01_01", date_1970),
    ("date_and_time_storage_types", "DATE and TIME: blank strings, unknown-word values, and impossible calendar/time values cannot be represented; NULL is the missing-value form"),
    ("date_rows_in_complete_boundary_years", complete_date_rows),
    ("valid_date_time_rows_in_complete_boundary_years", eligible_rows_complete),
    ("valid_date_time_rows_in_all_represented_years", eligible_rows_all),
    ("dataset_total_rows", all_rows),
]
emit(OPTION, common)
if OPTION == 2:
    injury_missing_by_year = con.execute(f"""
        SELECT year(crash_date) AS yr,
               count(*) FILTER (WHERE number_of_persons_injured IS NULL) AS missing_injury
        FROM read_parquet('{DATA}')
        WHERE crash_date IS NOT NULL
        GROUP BY yr
        ORDER BY yr
    """).fetchall()
    missing_injury_complete = sum(missing for yr, missing in injury_missing_by_year
                                  if any(y["year"] == yr and not y["partial"] for y in years))
    injury_facts = [
        ("rows_missing_number_of_persons_injured_in_complete_boundary_years", missing_injury_complete),
        ("share_of_dated_rows_missing_number_of_persons_injured_in_complete_boundary_years",
         f"{missing_injury_complete / complete_date_rows:.6%}" if complete_date_rows else "0"),
        ("rows_missing_number_of_persons_injured_by_year", "; ".join(
            f"{yr}: {missing} missing of {next(y['rows'] for y in years if y['year'] == yr)} dated rows"
            for yr, missing in injury_missing_by_year
        )),
    ]
    emit(2, common + injury_facts)
