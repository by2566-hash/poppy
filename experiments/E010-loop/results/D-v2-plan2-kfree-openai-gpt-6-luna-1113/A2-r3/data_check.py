import csv
from pathlib import Path

import duckdb
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"


def add(rows, fact, value):
    rows.append({"fact": fact, "value": str(value)})


for option_id in (1, 2, 3):
    outcome_columns = (
        ["number_of_persons_injured", "number_of_persons_killed"]
        if option_id in (1, 2)
        else ["number_of_pedestrians_injured", "number_of_pedestrians_killed"]
    )
    columns = ["crash_date", "crash_time", *outcome_columns]
    selected = ", ".join(f'"{column}"' for column in columns)
    df = duckdb.connect().execute(
        f"SELECT {selected} FROM read_parquet(?)", [str(ROOT / "data" / "crashes.parquet")]
    ).fetchdf()

    rows = []
    total_rows = len(df)
    date_missing = df["crash_date"].isna()
    valid_date = df.loc[~date_missing].copy()
    valid_date["year"] = pd.to_datetime(valid_date["crash_date"]).dt.year
    years = sorted(valid_date["year"].unique().tolist())

    add(rows, "rows_in_file (only selected columns read)", total_rows)
    add(rows, "rows_missing_crash_date; excluded from year-scoped population", int(date_missing.sum()))
    add(rows, "rows_with_valid_crash_date; year-scoped candidate population", len(valid_date))
    if len(valid_date):
        add(rows, "valid_crash_date_min", str(pd.to_datetime(valid_date["crash_date"]).min().date()))
        add(rows, "valid_crash_date_max", str(pd.to_datetime(valid_date["crash_date"]).max().date()))
    for sentinel in ("1900-01-01", "1970-01-01"):
        n = int((pd.to_datetime(valid_date["crash_date"]).dt.strftime("%Y-%m-%d") == sentinel).sum())
        add(rows, f"crash_date_rows_at_possible_default_{sentinel}", n)

    valid_date["time_missing"] = valid_date["crash_time"].isna()
    # TIME is a typed Parquet field: non-NULL values are representable clock times.
    valid_date["time_midnight"] = valid_date["crash_time"].astype(str).str.startswith("00:00:00")
    valid_date["outcome_missing"] = valid_date[outcome_columns].isna().any(axis=1)
    valid_date["included_by_initial_filters"] = ~(
        valid_date["time_missing"] | valid_date["outcome_missing"]
    )

    add(rows, "valid_date_rows_missing_crash_time", int(valid_date["time_missing"].sum()))
    add(rows, "valid_date_rows_with_impossible_nonmissing_crash_time", 0)
    add(rows, "valid_date_rows_at_possible_default_crash_time_00:00:00 (kept; valid time)", int(valid_date["time_midnight"].sum()))
    for column in outcome_columns:
        add(rows, f"valid_date_rows_missing_{column}", int(valid_date[column].isna().sum()))
    add(rows, "valid_date_rows_missing_any_required_outcome_column", int(valid_date["outcome_missing"].sum()))
    add(rows, "rows_in_final_initial-plan_population_after_time_and_outcome_filters", int(valid_date["included_by_initial_filters"].sum()))

    for year in years:
        yr = valid_date.loc[valid_date["year"] == year]
        dated = pd.to_datetime(yr["crash_date"])
        first_day = dated.min().date()
        last_day = dated.max().date()
        partial = first_day != pd.Timestamp(year=year, month=1, day=1).date() or last_day != pd.Timestamp(year=year, month=12, day=31).date()
        add(rows, f"year_{year}_candidate_rows_with_valid_date", len(yr))
        add(rows, f"year_{year}_rows_in_initial-plan_population_after_filters", int(yr["included_by_initial_filters"].sum()))
        add(rows, f"year_{year}_first_observed_date", first_day)
        add(rows, f"year_{year}_last_observed_date", last_day)
        add(rows, f"year_{year}_coverage_partial_by_calendar_endpoints", str(partial).lower())
        add(rows, f"year_{year}_valid_date_rows_missing_crash_time", int(yr["time_missing"].sum()))
        add(rows, f"year_{year}_valid_date_rows_at_possible_default_crash_time_00:00:00 (kept)", int(yr["time_midnight"].sum()))
        add(rows, f"year_{year}_valid_date_rows_missing_any_required_outcome_column", int(yr["outcome_missing"].sum()))
        for column in outcome_columns:
            add(rows, f"year_{year}_valid_date_rows_missing_{column}", int(yr[column].isna().sum()))

    final_scope = valid_date.loc[valid_date["year"].between(2013, 2025)]
    add(rows, "final_plan_years", "2013-2025 (complete calendar years only)")
    add(rows, "final_plan_candidate_rows_with_valid_date", len(final_scope))
    add(rows, "final_plan_rows_missing_crash_time", int(final_scope["time_missing"].sum()))
    add(rows, "final_plan_rows_missing_any_required_outcome_column", int(final_scope["outcome_missing"].sum()))
    add(rows, "final_plan_rows_included_after_quality_filters", int(final_scope["included_by_initial_filters"].sum()))
    for column in outcome_columns:
        add(rows, f"final_plan_rows_missing_{column}", int(final_scope[column].isna().sum()))
        if option_id == 2:
            add(rows, f"final_plan_rows_with_impossible_negative_{column}", int((final_scope[column].dropna() < 0).sum()))
    partial_scope = valid_date.loc[valid_date["year"].isin([2012, 2026])]
    add(rows, "rows_excluded_because_year_is_partial_2012_or_2026", len(partial_scope))
    add(rows, "share_of_valid-date_rows_excluded_as_partial_years", f"{len(partial_scope) / len(valid_date):.6%}")
    add(rows, "final_plan_rows_at_possible_default_crash_time_00:00:00 (kept)", int(final_scope["time_midnight"].sum()))

    with (OUT / f"check_{option_id}.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["fact", "value"])
        writer.writeheader()
        writer.writerows(rows)
