import csv
import json
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"
START = "2013-01-01"
END_EXCLUSIVE = "2026-01-01"

con = duckdb.connect()
for plan_id in (1, 2):
    plan = json.loads((OUT / f"plan_{plan_id}.json").read_text())[
        "initial_plan"
    ]
    # These are the only plan fields used in the check: crash_date defines the
    # years, and number_of_motorist_killed is the outcome-availability filter.
    rows = con.execute(
        f"""
        SELECT year(crash_date) AS yr,
               count(*) AS year_rows_before_outcome_filter,
               count(*) FILTER (WHERE number_of_motorist_killed IS NULL)
                   AS outcome_missing_rows,
               count(*) FILTER (WHERE number_of_motorist_killed IS NOT NULL)
                   AS population_rows,
               min(crash_date) AS first_observed_date,
               max(crash_date) AS last_observed_date
        FROM read_parquet(?)
        WHERE crash_date >= DATE '{START}'
          AND crash_date < DATE '{END_EXCLUSIVE}'
        GROUP BY yr
        ORDER BY yr
        """,
        [str(DATA)],
    ).fetchall()
    by_year = {int(r[0]): r for r in rows}
    facts = []
    facts.append(("planned_years", plan["years"]))
    facts.append(("planned_population", plan["population"]))
    facts.append(("rows_in_planned_years_before_outcome_filter", sum(r[1] for r in rows)))
    facts.append(("population_rows_after_nonmissing_outcome_filter", sum(r[3] for r in rows)))
    facts.append(("outcome_missing_rows_before_outcome_filter", sum(r[2] for r in rows)))
    facts.append(("outcome_missing_value_types", "number_of_motorist_killed is numeric; NULL is the only representable missing form; empty strings/unknown words/impossible numeric strings cannot occur in this typed column"))
    facts.append(("crash_date_missing_or_impossible_in_planned_date_range", 0))
    facts.append(("crash_date_check_note", "DATE-typed crash_date values satisfying the inclusive 2013-2025 year filter are valid dates; NULL dates cannot be assigned to a planned year"))
    for yr in range(2013, 2026):
        r = by_year.get(yr)
        if r is None:
            facts.append((f"{yr}_rows_before_outcome_filter", 0))
            facts.append((f"{yr}_population_rows", 0))
            facts.append((f"{yr}_outcome_missing_rows", 0))
            facts.append((f"{yr}_observed_date_range", "no rows"))
        else:
            facts.append((f"{yr}_rows_before_outcome_filter", int(r[1])))
            facts.append((f"{yr}_population_rows", int(r[3])))
            facts.append((f"{yr}_outcome_missing_rows", int(r[2])))
            facts.append((f"{yr}_observed_date_range", f"{r[4]} through {r[5]}"))
    observed_years = sorted(by_year)
    partial_years = []
    for yr in observed_years:
        first, last = by_year[yr][4], by_year[yr][5]
        if first.isoformat() != f"{yr}-01-01" or last.isoformat() != f"{yr}-12-31":
            partial_years.append(yr)
    facts.append(("years_with_observed_dates_not_spanning_jan1_through_dec31", ",".join(map(str, partial_years)) or "none"))
    facts.append(("partial_year_interpretation", "An observed date range that does not span Jan 1 through Dec 31 is treated as a partial year; endpoint dates do not establish that every day in between is represented."))
    with (OUT / f"check_{plan_id}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)

con.close()
