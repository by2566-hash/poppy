import csv
from pathlib import Path

import duckdb


DATA = "data/crashes.parquet"
OUT = Path("out")
con = duckdb.connect()
year_rows = con.execute(
    f"""
    SELECT year(crash_date) AS yr, min(crash_date) AS first_date,
           max(crash_date) AS last_date, count(*) AS rows
    FROM read_parquet('{DATA}')
    WHERE crash_date IS NOT NULL
    GROUP BY yr ORDER BY yr
    """
).fetchall()
if not year_rows:
    raise RuntimeError("No dated crash rows found")

first_year, last_year = year_rows[0][0], year_rows[-1][0]
partial_years = []
for yr, first_date, last_date, _ in year_rows:
    partial = (yr == first_year and (first_date.month, first_date.day) > (1, 1))
    partial = partial or (yr == last_year and (last_date.month, last_date.day) < (12, 31))
    if partial:
        partial_years.append(yr)
complete_years = [row[0] for row in year_rows if row[0] not in partial_years]
if not complete_years:
    raise RuntimeError("No complete calendar years identified")

years_sql = ",".join(str(y) for y in complete_years)
base_rows = con.execute(
    f"""
    SELECT year(crash_date) AS yr, count(*) AS population_rows,
           count(*) FILTER (WHERE crash_time IS NULL) AS missing_time,
           count(*) FILTER (WHERE crash_time = TIME '00:00:00') AS midnight_time,
           count(*) FILTER (WHERE number_of_persons_injured IS NULL) AS missing_injured,
           count(*) FILTER (WHERE number_of_persons_killed IS NULL) AS missing_killed,
           count(*) FILTER (WHERE crash_time IS NOT NULL
                            AND number_of_persons_injured IS NOT NULL
                            AND number_of_persons_killed IS NOT NULL) AS eligible_rows
    FROM read_parquet('{DATA}')
    WHERE crash_date IS NOT NULL AND year(crash_date) IN ({years_sql})
    GROUP BY yr ORDER BY yr
    """
).fetchall()
group_rows = con.execute(
    f"""
    SELECT year(crash_date) AS yr,
           CASE WHEN crash_time = TIME '00:00:00' THEN 'midnight_possible_default'
                WHEN crash_time < TIME '06:00:00' OR crash_time >= TIME '20:00:00' THEN 'night'
                ELSE 'day' END AS period,
           count(*) AS eligible_rows
    FROM read_parquet('{DATA}')
    WHERE crash_date IS NOT NULL AND year(crash_date) IN ({years_sql})
      AND crash_time IS NOT NULL
      AND number_of_persons_injured IS NOT NULL
      AND number_of_persons_killed IS NOT NULL
    GROUP BY yr, period ORDER BY yr, period
    """
).fetchall()
undated = con.execute(
    f"SELECT count(*) FROM read_parquet('{DATA}') WHERE crash_date IS NULL"
).fetchone()[0]
time_type = con.execute(
    f"DESCRIBE SELECT crash_time FROM read_parquet('{DATA}')"
).fetchone()[1]

facts = [
    ("file_year_coverage", "; ".join(
        f"{yr}: {first_date} through {last_date} ({rows:,} dated rows)"
        for yr, first_date, last_date, rows in year_rows
    )),
    ("partial_calendar_years_excluded", ", ".join(map(str, partial_years)) or "none"),
    ("complete_calendar_years_used", ", ".join(map(str, complete_years))),
    ("rows_with_missing_crash_date_unassignable_to_year", f"{undated:,}"),
    ("population_rows_in_complete_years", f"{sum(r[1] for r in base_rows):,}"),
    ("rows_excluded_for_missing_injured_or_killed_count", f"{sum(r[1] - r[-1] for r in base_rows):,}"),
    ("share_of_population_rows_excluded_for_missing_injured_or_killed_count", f"{sum(r[1] - r[-1] for r in base_rows) / sum(r[1] for r in base_rows):.6%}"),
    ("rows_missing_number_of_persons_injured", f"{sum(r[4] for r in base_rows):,}"),
    ("rows_missing_number_of_persons_killed", f"{sum(r[5] for r in base_rows):,}"),
    ("total_midnight_rows_kept_as_separate_possible_default_group", f"{sum(r[3] for r in base_rows):,}"),
    ("crash_time_storage_type", time_type),
    ("crash_time_impossible_or_blank_values", "0; TIME typed column cannot store blank, unknown-word, or out-of-range clock values"),
    ("number_of_persons_injured_impossible_value_check", "not checked by value; this field is assessed only for missingness in the data check"),
    ("number_of_persons_killed_impossible_value_check", "not checked by value; this field is assessed only for missingness in the data check"),
]
for yr, first_date, last_date, rows in year_rows:
    facts.append((f"coverage_{yr}", f"{first_date} through {last_date}; {'partial boundary year excluded' if yr in partial_years else 'included'}"))
for yr, pop, missing_time, midnight, missing_injured, missing_killed, eligible in base_rows:
    facts.extend([
        (f"year_{yr}_population_rows", f"{pop:,}"),
        (f"year_{yr}_missing_crash_time_rows", f"{missing_time:,}"),
        (f"year_{yr}_midnight_time_rows_shown_separately", f"{midnight:,}"),
        (f"year_{yr}_missing_number_of_persons_injured_rows", f"{missing_injured:,}"),
        (f"year_{yr}_missing_number_of_persons_killed_rows", f"{missing_killed:,}"),
        (f"year_{yr}_eligible_rows_after_missing_field_filters", f"{eligible:,}"),
    ])
for yr, period, eligible in group_rows:
    facts.append((f"year_{yr}_{period}_eligible_rows", f"{eligible:,}"))
period_counts = {(yr, period): eligible for yr, period, eligible in group_rows}
if len(complete_years) > 1:
    changes = []
    for period in ("night", "day", "midnight_possible_default"):
        for y1, y2 in zip(complete_years, complete_years[1:]):
            delta = period_counts.get((y2, period), 0) - period_counts.get((y1, period), 0)
            changes.append((abs(delta), y1, y2, period, delta))
    _, y1, y2, period, delta = max(changes)
    facts.append(("largest_neighboring_year_change_in_group_eligible_rows", f"{period}, {y1} to {y2}: {delta:+,} rows (absolute change {abs(delta):,})"))
else:
    facts.append(("largest_neighboring_year_change_in_group_eligible_rows", "not applicable; fewer than two complete years"))
facts.append(("eligible_midnight_possible_default_group_rows", f"{sum(n for _, period, n in group_rows if period == 'midnight_possible_default'):,}"))

for option_id in (1, 2):
    with (OUT / f"check_{option_id}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)
