import json
from pathlib import Path

import duckdb
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"
con = duckdb.connect()
con.execute(
    "CREATE VIEW crashes AS SELECT * FROM read_parquet('" + str(DATA).replace("'", "''") + "')"
)

# Establish calendar-boundary coverage using only the planned date column.
date_bounds = con.execute(
    "SELECT min(crash_date) AS first_date, max(crash_date) AS last_date FROM crashes"
).fetchone()
first_date, last_date = date_bounds
all_years = [int(y[0]) for y in con.execute(
    "SELECT DISTINCT year(crash_date) FROM crashes WHERE crash_date IS NOT NULL ORDER BY 1"
).fetchall()]
complete_years = []
partial_year_facts = []
for year in all_years:
    year_first, year_last = con.execute(
        "SELECT min(crash_date), max(crash_date) FROM crashes WHERE year(crash_date) = ?",
        [year],
    ).fetchone()
    is_complete_by_bounds = (
        year_first.month == 1 and year_first.day == 1
        and year_last.month == 12 and year_last.day == 31
    )
    if is_complete_by_bounds:
        complete_years.append(year)
    else:
        partial_year_facts.append(
            f"{year}: observed date bounds {year_first} through {year_last}; does not span Jan 1–Dec 31"
        )

year_list = ",".join(str(y) for y in complete_years)
year_predicate = f"year(crash_date) IN ({year_list})" if year_list else "FALSE"
period = "(hour(crash_time) >= 19 OR hour(crash_time) < 7)"


def append_fact(rows, fact, value):
    rows.append({"fact": fact, "value": str(value)})


for option in (1, 2):
    facts = []
    date_candidates = f"crash_date IS NOT NULL AND {year_predicate}"
    valid_period = f"{date_candidates} AND crash_time IS NOT NULL"
    if option == 2:
        valid_population = (
            f"{valid_period} AND number_of_persons_injured IS NOT NULL "
            "AND number_of_persons_injured >= 0 "
            "AND number_of_persons_killed IS NOT NULL "
            "AND number_of_persons_killed >= 0"
        )
    else:
        valid_population = valid_period

    population_n = con.execute(
        f"SELECT count(*) FROM crashes WHERE {valid_population}"
    ).fetchone()[0]
    append_fact(facts, "final_plan_population_rows_total", population_n)
    by_year = con.execute(
        f"SELECT year(crash_date) AS year, count(*) AS rows "
        f"FROM crashes WHERE {valid_population} GROUP BY 1 ORDER BY 1"
    ).fetchall()
    for year, count in by_year:
        append_fact(facts, f"final_plan_population_rows_year_{year}", count)

    candidates = con.execute(
        f"SELECT count(*) FROM crashes WHERE {date_candidates}"
    ).fetchone()[0]
    append_fact(facts, "rows_with_nonnull_date_in_selected_complete_years_before_time_check", candidates)
    missing_dates = con.execute(
        "SELECT count(*) FROM crashes WHERE crash_date IS NULL"
    ).fetchone()[0]
    append_fact(facts, "rows_with_missing_crash_date_overall_excluded_from_year_assignment", missing_dates)
    date_sentinels = con.execute(
        f"SELECT count(*) FROM crashes WHERE {date_candidates} "
        "AND crash_date IN (DATE '1900-01-01', DATE '1970-01-01')"
    ).fetchone()[0]
    append_fact(facts, "rows_at_1900_or_1970_date_sentinel_in_selected_year_candidates", date_sentinels)
    nonfinite_dates = con.execute(
        f"SELECT count(*) FROM crashes WHERE {date_candidates} AND NOT isfinite(crash_date)"
    ).fetchone()[0]
    append_fact(facts, "nonfinite_or_impossible_crash_dates_in_selected_year_candidates", nonfinite_dates)
    append_fact(facts, "empty_or_unknown_words_in_crash_date_column", "not representable in the DATE-typed source column")
    missing_times = con.execute(
        f"SELECT count(*) FROM crashes WHERE {date_candidates} AND crash_time IS NULL"
    ).fetchone()[0]
    append_fact(facts, "rows_with_missing_crash_time_in_selected_year_candidates", missing_times)
    midnight = con.execute(
        f"SELECT count(*) FROM crashes WHERE {date_candidates} AND crash_time = TIME '00:00:00'"
    ).fetchone()[0]
    append_fact(facts, "rows_at_midnight_default_or_plausible_crash_time_in_selected_year_candidates", midnight)
    append_fact(facts, "invalid_or_out_of_range_crash_time_values", "not representable in the TIME-typed source column")
    append_fact(facts, "calendar_year_coverage_by_observed_date_bounds", "; ".join(partial_year_facts) if partial_year_facts else "all observed years span Jan 1 through Dec 31 by observed bounds")
    append_fact(facts, "years_included_after_boundary_year_exclusion", ",".join(map(str, complete_years)))

    segment_rows = con.execute(
        f"SELECT CASE WHEN {period} THEN 'night' ELSE 'day' END AS period, "
        f"year(crash_date) AS year, count(*) AS rows "
        f"FROM crashes WHERE {valid_period} GROUP BY 1,2 ORDER BY 2,1"
    ).fetchall()
    for segment, year, count in segment_rows:
        append_fact(facts, f"candidate_rows_period_{segment}_year_{year}_before_outcome_quality", count)

    if option == 2:
        for col in ("number_of_persons_injured", "number_of_persons_killed"):
            for label, condition in (
                ("missing", f"{col} IS NULL"),
                ("negative_impossible", f"{col} < 0"),
                ("zero_default_or_plausible", f"{col} = 0"),
            ):
                count = con.execute(
                    f"SELECT count(*) FROM crashes WHERE {valid_period} AND {condition}"
                ).fetchone()[0]
                append_fact(facts, f"{col}_{label}_among_selected_year_rows_with_valid_time", count)
        bad_outcome_rows = con.execute(
            f"SELECT count(*) FROM crashes WHERE {valid_period} AND "
            "(number_of_persons_injured IS NULL OR number_of_persons_injured < 0 "
            "OR number_of_persons_killed IS NULL OR number_of_persons_killed < 0)"
        ).fetchone()[0]
        append_fact(facts, "rows_dropped_for_missing_or_negative_person_counts", bad_outcome_rows)
        append_fact(facts, "empty_or_unknown_words_in_person_count_columns", "not representable in the INT-typed source columns")

    pd.DataFrame(facts).to_csv(OUT / f"check_{option}.csv", index=False)

print(json.dumps({"first_date": str(first_date), "last_date": str(last_date), "complete_years": complete_years, "partial_years": partial_year_facts}, indent=2))
