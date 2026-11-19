import csv
import json
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parent.parent
DATA = str(ROOT / "data" / "crashes.parquet")
OUT = Path(__file__).resolve().parent
YEARS = range(2013, 2031)
PEDESTRIAN_FIELDS = [
    "number_of_pedestrians_injured",
    "number_of_pedestrians_killed",
]

con = duckdb.connect()
data_sql = DATA.replace("'", "''")
con.execute(f"CREATE VIEW crashes AS SELECT crash_date, borough, number_of_pedestrians_injured, number_of_pedestrians_killed FROM read_parquet('{data_sql}')")

# Only the planned years and the columns used by the three initial plans are
# inspected. Outcomes are checked for missing/impossible values, never summed.
base = con.execute("""
    SELECT crash_date, borough, number_of_pedestrians_injured,
           number_of_pedestrians_killed
    FROM crashes
    WHERE crash_date >= DATE '2013-01-01'
""").fetchdf()
base["year"] = base["crash_date"].dt.year
base["date_only"] = base["crash_date"].dt.date
years = sorted(int(y) for y in base["year"].dropna().unique())

borough_text = base["borough"].astype("string").str.strip()
borough_lower = borough_text.str.lower()
borough_missing = base["borough"].isna() | borough_text.eq("").fillna(False) | borough_lower.isin(
    ["unknown", "unspecified", "unk", "n/a", "na", "none", "null", "0"]
).fillna(False)
borough_invalid = ~borough_missing & ~borough_lower.isin(
    ["brooklyn", "bronx", "manhattan", "queens", "staten island"]
).fillna(False)
brooklyn = borough_lower.eq("brooklyn").fillna(False)

facts_by_option = {1: [], 2: [], 3: []}

def fact(option, name, value):
    facts_by_option[option].append((name, value))


for option in (1, 2, 3):
    fact(option, "rows_with_null_crash_date_unassignable_to_year_in_file", int(con.execute(
        "SELECT count(*) FROM crashes WHERE crash_date IS NULL"
    ).fetchone()[0]))
    fact(option, "years_present_from_2013", json.dumps(years))
    fact(option, "borough_missing_empty_or_unknown_rows_in_years_before_borough_filter", int(borough_missing.sum()))
    fact(option, "borough_unrecognized_nonmissing_rows_in_years_before_borough_filter", int(borough_invalid.sum()))
    fact(option, "borough_default_unknown_placeholder_rows_in_years_before_borough_filter", int((borough_missing & (base["borough"].notna())).sum()))

    for year in years:
        yr = base[base["year"] == year]
        brook = yr[brooklyn.loc[yr.index]]
        # A case is usable only when the outcome fields named by each plan are
        # present and nonnegative. These are validity counts, not outcome totals.
        both_valid = brook[PEDESTRIAN_FIELDS].notna().all(axis=1) & brook[PEDESTRIAN_FIELDS].ge(0).all(axis=1)
        killed_valid = brook["number_of_pedestrians_killed"].notna() & brook["number_of_pedestrians_killed"].ge(0)
        complete_n = int(both_valid.sum())
        killed_n = int(killed_valid.sum())
        fact(option, f"{year}_Brooklyn_crash_rows_before_outcome_validity_filter", int(len(brook)))
        if option in (1, 3):
            fact(option, f"{year}_planned_population_rows_after_complete_case_filter", complete_n)
        else:
            fact(option, f"{year}_planned_population_rows_after_killed_count_validity_filter", killed_n)

        # Borough is a filter: report absent/default values before it is applied.
        fact(option, f"{year}_borough_missing_empty_or_unknown_before_filter", int(borough_missing.loc[yr.index].sum()))
        fact(option, f"{year}_borough_unrecognized_nonmissing_before_filter", int(borough_invalid.loc[yr.index].sum()))

        # Outcome missing/impossible values are inspected in Brooklyn rows before
        # outcome validity filters, as required for quantifying the exclusions.
        fields = PEDESTRIAN_FIELDS if option in (1, 3) else ["number_of_pedestrians_killed"]
        for col in fields:
            fact(option, f"{year}_{col}_missing_in_Brooklyn_rows", int(brook[col].isna().sum()))
            fact(option, f"{year}_{col}_impossible_negative_in_Brooklyn_rows", int(brook[col].lt(0).sum()))
        if option == 1:
            fact(option, f"{year}_rows_missing_or_invalid_either_summed_field", int((~both_valid).sum()))
        if option == 3:
            fact(option, f"{year}_rows_missing_or_invalid_either_casualty_field", int((~both_valid).sum()))

    # Temporal bounds show whether the file's first/last observed year is cut
    # off; the most recent year's end bound is the key partial-year test.
    if years:
        first, last = years[0], years[-1]
        for y in years:
            yr_dates = base.loc[base["year"] == y, "date_only"]
            fact(option, f"{y}_observed_crash_date_range", f"{min(yr_dates)} to {max(yr_dates)}")
        fact(option, "first_observed_year_starts_after_Jan_1", bool(min(base["date_only"]) > min(base["date_only"]).replace(month=1, day=1)) if first == 2013 else False)
        fact(option, "latest_observed_year", last)
        latest_max = max(base.loc[base["year"] == last, "date_only"])
        fact(option, "latest_year_end_is_before_Dec_31", bool(latest_max < latest_max.replace(month=12, day=31)))
        fact(option, "latest_year_last_observed_crash_date", str(latest_max))

for option, facts in facts_by_option.items():
    final_period = base[base["year"].between(2013, 2025)]
    final_period_missing_borough = borough_missing.loc[final_period.index]
    final_period_brooklyn = final_period[brooklyn.loc[final_period.index]]
    fact(option, "2013_2025_rows_in_all_crashes", int(len(final_period)))
    fact(option, "2013_2025_rows_missing_empty_or_unknown_borough_before_filter", int(final_period_missing_borough.sum()))
    fact(option, "2013_2025_rows_with_unrecognized_nonmissing_borough_before_filter", int(borough_invalid.loc[final_period.index].sum()))
    fact(option, "2013_2025_Brooklyn_rows_before_outcome_validity_filter", int(len(final_period_brooklyn)))
    outcome_fields = PEDESTRIAN_FIELDS if option in (1, 3) else ["number_of_pedestrians_killed"]
    for col in outcome_fields:
        fact(option, f"2013_2025_{col}_missing_in_Brooklyn_rows", int(final_period_brooklyn[col].isna().sum()))
        fact(option, f"2013_2025_{col}_impossible_negative_in_Brooklyn_rows", int(final_period_brooklyn[col].lt(0).sum()))
    with (OUT / f"check_{option}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)
