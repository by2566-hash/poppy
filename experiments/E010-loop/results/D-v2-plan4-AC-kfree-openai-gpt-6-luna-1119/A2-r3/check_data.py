from pathlib import Path
import csv
import re

import duckdb
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "crashes.parquet"
OUT = Path(__file__).resolve().parent


def missing_time(value):
    if value is None:
        return True
    text = str(value).strip()
    if not text or text.lower() in {"unknown", "unspecified", "not known", "n/a", "na", "null"}:
        return True
    try:
        h, m, *rest = [int(part) for part in text.split(":")]
        return not (0 <= h <= 23 and 0 <= m <= 59 and (not rest or 0 <= rest[0] <= 59))
    except (ValueError, TypeError):
        return True


def missing_count(series, is_time=False):
    count = 0
    for value in series:
        if is_time:
            count += int(missing_time(value))
        else:
            count += int(pd.isna(value) or value < 0)
    return count


con = duckdb.connect()
df = con.execute(
    """SELECT CAST(crash_date AS VARCHAR) AS crash_date,
              CAST(crash_time AS VARCHAR) AS crash_time,
              number_of_persons_injured,
              number_of_persons_killed
       FROM read_parquet(?)""",
    [str(DATA)],
).fetchdf()
df["crash_date_parsed"] = pd.to_datetime(df["crash_date"], errors="coerce")
df["year"] = df["crash_date_parsed"].dt.year
dated = df[df["year"].notna()].copy()
years = sorted(int(y) for y in dated["year"].unique())

for option_id, outcome_columns in {
    1: ["number_of_persons_injured", "number_of_persons_killed"],
    2: ["number_of_persons_injured", "number_of_persons_killed"],
    3: ["number_of_persons_killed"],
}.items():
    facts = []

    def add(fact, value):
        facts.append((fact, value))

    add("rows_in_file", len(df))
    add("rows_with_missing_or_invalid_crash_date_excluded_from_year_population", int(df["crash_date_parsed"].isna().sum()))
    add("rows_in_plan_population_with_valid_crash_date", len(dated))
    for year in years:
        year_df = dated[dated["year"] == year]
        add(f"rows_in_plan_population_year_{year}", len(year_df))
        first = year_df["crash_date_parsed"].min().date()
        last = year_df["crash_date_parsed"].max().date()
        partial = first.strftime("%m-%d") != "01-01" or last.strftime("%m-%d") != "12-31"
        add(f"year_{year}_observed_date_range", f"{first} through {last}; partial_calendar_year={str(partial).lower()}")

    add("crash_time_missing_empty_unknown_or_impossible_in_plan_years_before_time_filter", sum(missing_time(v) for v in dated["crash_time"]))
    midnight = sum(
        1 for v in dated["crash_time"]
        if not missing_time(v) and str(v).strip().startswith("00:00")
    )
    add("crash_time_midnight_rows_in_plan_years_possible_default_or_legitimate", midnight)

    for column in outcome_columns:
        add(f"{column}_missing_or_impossible_negative_in_plan_years", missing_count(dated[column]))

    with (OUT / f"check_{option_id}.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)

print(f"Wrote plan-scoped data checks for {len(years)} years ({years[0]}–{years[-1]}).")
