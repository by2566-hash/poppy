import csv
from datetime import date
from pathlib import Path

import duckdb


root = Path(__file__).resolve().parent.parent
data_path = root / "data" / "crashes.parquet"
con = duckdb.connect()
con.execute("SET TimeZone='UTC'")

# Read only the planned date and outcome columns. These checks describe row
# coverage and field completeness; they do not inspect outcome values or sums.
rows = con.execute(
    """
    SELECT crash_date, number_of_pedestrians_killed
    FROM read_parquet(?)
    """,
    [str(data_path)],
).fetchall()

year_counts = {year: 0 for year in range(2013, 2026)}
year_dates = {year: [] for year in range(2013, 2026)}
missing_date = 0
missing_killed_by_year = {year: 0 for year in range(2013, 2026)}
common_placeholder_dates = {date(1, 1, 1), date(1900, 1, 1), date(1970, 1, 1), date(9999, 12, 31)}
placeholder_dates_in_requested_years = 0
for crash_date, pedestrians_killed in rows:
    if crash_date is None:
        missing_date += 1
        continue
    year = crash_date.year
    if 2013 <= year <= 2025:
        year_counts[year] += 1
        year_dates[year].append(crash_date)
        if crash_date in common_placeholder_dates:
            placeholder_dates_in_requested_years += 1
        if pedestrians_killed is None:
            missing_killed_by_year[year] += 1

facts = [
    ("rows_in_requested_years_2013_2025", sum(year_counts.values())),
    ("crash_date_missing_or_unassignable_year_rows_in_file", missing_date),
    ("crash_date_type", "DATE; non-date/impossible date values cannot be represented in this field"),
    ("crash_date_empty_string_or_unknown_word_rows_in_file", 0),
    (
        "crash_date_common_placeholder_date_rows_in_requested_years",
        placeholder_dates_in_requested_years,
    ),
]
for year in range(2013, 2026):
    dates = year_dates[year]
    facts.extend(
        [
            (f"rows_in_{year}", year_counts[year]),
            (f"crash_date_missing_rows_in_{year}_population", 0),
            (
                f"crash_date_observed_coverage_in_{year}",
                f"{min(dates).isoformat()} to {max(dates).isoformat()}" if dates else "no rows",
            ),
            (
                f"year_{year}_partial_calendar_year",
                "yes" if not dates or min(dates).month > 1 or min(dates).day > 1 or max(dates).month < 12 or max(dates).day < 31 else "no",
            ),
            (f"number_of_pedestrians_killed_missing_rows_in_{year}_population", missing_killed_by_year[year]),
        ]
    )
facts.append(
    (
        "number_of_pedestrians_killed_missing_rows_in_requested_population",
        sum(missing_killed_by_year.values()),
    )
)

with (root / "out" / "check_1.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["fact", "value"])
    writer.writerows(facts)
