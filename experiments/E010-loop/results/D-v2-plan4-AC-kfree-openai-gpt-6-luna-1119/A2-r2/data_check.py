from pathlib import Path
from datetime import time

import duckdb
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)

con = duckdb.connect()
query = """
    SELECT crash_date, crash_time,
           number_of_persons_injured, number_of_persons_killed
    FROM read_parquet(?)
"""
rows = con.execute(query, [str(SOURCE)]).fetchdf()
rows["year"] = rows["crash_date"].dt.year
dated = rows[rows["year"].notna()].copy()

facts = []


def add(fact, value):
    facts.append({"fact": fact, "value": value})


add("rows_with_missing_crash_date_all_file", int(rows["crash_date"].isna().sum()))
add("rows_in_plan_years_total", int(len(dated)))
add("number_of_plan_years", int(dated["year"].nunique()))
add("crash_date_type_note", "DATE type: NULL checked; empty, unknown-word, and impossible dates cannot be represented as DATE values")
add("crash_time_type_note", "TIME type: NULL checked; empty, unknown-word, and impossible times cannot be represented as TIME values")
add("outcome_type_note", "INT type: NULL checked as missing for both person outcome fields")

for year, yearly in dated.groupby("year", sort=True):
    year = int(year)
    start = pd.Timestamp(year=year, month=1, day=1)
    end = pd.Timestamp(year=year, month=12, day=31)
    min_date = yearly["crash_date"].min()
    max_date = yearly["crash_date"].max()
    complete = min_date == start and max_date == end
    add(f"rows_in_year_{year}", int(len(yearly)))
    usable_yearly = yearly[
        yearly["crash_time"].notna()
        & yearly["number_of_persons_injured"].notna()
        & yearly["number_of_persons_killed"].notna()
    ]
    add(f"usable_rows_after_time_and_outcome_filters_in_year_{year}", int(len(usable_yearly)))
    add(f"first_crash_date_in_year_{year}", min_date.date().isoformat())
    add(f"last_crash_date_in_year_{year}", max_date.date().isoformat())
    add(f"calendar_coverage_complete_by_edge_dates_{year}", bool(complete))
    add(f"missing_crash_time_in_year_{year}", int(yearly["crash_time"].isna().sum()))
    add(f"midnight_crash_time_in_year_{year}", int((yearly["crash_time"] == time(0, 0)).sum()))
    add(f"missing_number_of_persons_injured_in_year_{year}", int(yearly["number_of_persons_injured"].isna().sum()))
    add(f"missing_number_of_persons_killed_in_year_{year}", int(yearly["number_of_persons_killed"].isna().sum()))
    add(
        f"rows_missing_either_person_outcome_in_year_{year}",
        int(yearly[["number_of_persons_injured", "number_of_persons_killed"]].isna().any(axis=1).sum()),
    )

add("missing_crash_time_all_plan_years", int(dated["crash_time"].isna().sum()))
add("midnight_crash_time_all_plan_years", int((dated["crash_time"] == time(0, 0)).sum()))
add("missing_number_of_persons_injured_all_plan_years", int(dated["number_of_persons_injured"].isna().sum()))
add("missing_number_of_persons_killed_all_plan_years", int(dated["number_of_persons_killed"].isna().sum()))
add(
    "rows_missing_either_person_outcome_all_plan_years",
    int(dated[["number_of_persons_injured", "number_of_persons_killed"]].isna().any(axis=1).sum()),
)

complete_years = []
for year, yearly in dated.groupby("year", sort=True):
    year = int(year)
    if yearly["crash_date"].min() == pd.Timestamp(year=year, month=1, day=1) and yearly["crash_date"].max() == pd.Timestamp(year=year, month=12, day=31):
        complete_years.append(year)
complete = dated[dated["year"].isin(complete_years)]
usable_complete = complete[
    complete["crash_time"].notna()
    & complete["number_of_persons_injured"].notna()
    & complete["number_of_persons_killed"].notna()
]
add("complete_calendar_years_by_edge_dates", ",".join(map(str, complete_years)))
add("rows_in_complete_calendar_years", int(len(complete)))
add("usable_rows_after_time_and_outcome_filters_in_complete_years", int(len(usable_complete)))
add("rows_in_excluded_partial_years", int(len(dated) - len(complete)))
add("missing_crash_time_in_complete_calendar_years", int(complete["crash_time"].isna().sum()))
add("midnight_crash_time_in_complete_calendar_years", int((complete["crash_time"] == time(0, 0)).sum()))
add("missing_number_of_persons_injured_in_complete_calendar_years", int(complete["number_of_persons_injured"].isna().sum()))
add("missing_number_of_persons_killed_in_complete_calendar_years", int(complete["number_of_persons_killed"].isna().sum()))
add(
    "rows_missing_either_person_outcome_in_complete_calendar_years",
    int(complete[["number_of_persons_injured", "number_of_persons_killed"]].isna().any(axis=1).sum()),
)

check = pd.DataFrame(facts)
for option_id in (1, 2):
    check.to_csv(OUT / f"check_{option_id}.csv", index=False)
print(check.to_string(index=False))
