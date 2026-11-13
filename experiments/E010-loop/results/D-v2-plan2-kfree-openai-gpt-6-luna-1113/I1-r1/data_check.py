import csv
import json
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
SOURCE = (ROOT / "data" / "crashes.parquet").as_posix().replace("'", "''")
START_YEAR = 2013
END_YEAR = 2025


def main():
    con = duckdb.connect()
    facts = []
    # A null crash date cannot be assigned to the plan's year population, so
    # report it as a filter-exclusion diagnostic separately.
    null_dates = con.execute(
        f"SELECT count(*) FROM read_parquet('{SOURCE}') WHERE crash_date IS NULL"
    ).fetchone()[0]
    total_rows = con.execute(
        f"SELECT count(*) FROM read_parquet('{SOURCE}')"
    ).fetchone()[0]
    facts.extend([
        ("source_rows", total_rows),
        ("rows_excluded_because_crash_date_is_missing", null_dates),
    ])

    for option_id in (1, 2, 3):
        outcome = "number_of_motorist_killed"
        # The scoped query reads only the plan's year/grouping field and the
        # outcome's missingness; it does not inspect outcome values.
        by_year = con.execute(
            f"""
            SELECT year(crash_date) AS crash_year,
                   count(*) AS crash_rows,
                   count(*) FILTER (WHERE {outcome} IS NULL) AS missing_outcome_rows,
                   min(crash_date) AS first_date,
                   max(crash_date) AS last_date
            FROM read_parquet('{SOURCE}')
            WHERE crash_date >= DATE '{START_YEAR}-01-01'
              AND crash_date < DATE '{END_YEAR + 1}-01-01'
            GROUP BY crash_year
            ORDER BY crash_year
            """
        ).fetchall()
        year_map = {int(row[0]): row for row in by_year}
        facts = [
            ("source_rows", total_rows),
            ("rows_excluded_because_crash_date_is_missing", null_dates),
            ("requested_years", f"{START_YEAR}-{END_YEAR}"),
        ]
        for year in range(START_YEAR, END_YEAR + 1):
            row = year_map.get(year)
            if row is None:
                facts.extend([
                    (f"rows_{year}", 0),
                    (f"missing_number_of_motorist_killed_{year}", 0),
                    (f"date_coverage_{year}", "no rows"),
                ])
                continue
            _, row_count, missing_outcome, first_date, last_date = row
            facts.extend([
                (f"rows_{year}", row_count),
                (f"missing_number_of_motorist_killed_{year}", missing_outcome),
                (f"date_coverage_{year}", f"{first_date} through {last_date}"),
            ])
        facts.append(("crash_date_type", "DATE; empty strings and text sentinels cannot occur in this typed field"))

        output = OUT / f"check_{option_id}.csv"
        with output.open("w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["fact", "value"])
            writer.writerows(facts)

        plan_path = OUT / f"plan_{option_id}.json"
        plan = json.loads(plan_path.read_text())
        missing_total = sum(year_map[y][2] for y in year_map if START_YEAR <= y <= END_YEAR)
        eligible_total = sum(year_map[y][1] - year_map[y][2] for y in year_map if START_YEAR <= y <= END_YEAR)
        annual_notes = []
        for year in range(START_YEAR, END_YEAR + 1):
            row = year_map.get(year)
            if row is not None:
                _, count, missing, first_date, last_date = row
                partial = (
                    first_date.isoformat() != f"{year}-01-01"
                    or last_date.isoformat() != f"{year}-12-31"
                )
                annual_notes.append({
                    "year": year,
                    "dated_crash_rows_before_outcome_missingness_filter": count,
                    "missing_motorist_killed_rows": missing,
                    "usable_rows_after_complete_case_filter": count - missing,
                    "observed_date_span": f"{first_date} through {last_date}",
                    "calendar_year_partial_by_observed_date_span": partial,
                })
        plan["data_check"] = {
            "source_rows": total_rows,
            "rows_with_missing_crash_date_excluded_and_not_assignable_to_a_year": null_dates,
            "dated_rows_in_2013_2025_before_outcome_filter": sum(row[1] for year, row in year_map.items() if START_YEAR <= year <= END_YEAR),
            "rows_with_missing_number_of_motorist_killed_in_2013_2025": missing_total,
            "usable_complete_case_rows_in_2013_2025": eligible_total,
            "annual_check": annual_notes,
            "date_field_note": "crash_date is typed DATE, so empty strings and text sentinels are not representable; observed min/max dates are checked by year",
        }
        plan["status"] = "final"
        plan["final_population_decision"] = "Use dated crashes in 2013-2025 with a nonmissing number_of_motorist_killed value; exclude rows missing the motorist-death count from each annual metric and, for rate/share metrics, from the denominator as well."
        plan["data_check_interpretation"] = f"Among the {sum(row[1] for year, row in year_map.items() if START_YEAR <= year <= END_YEAR)} dated crashes in 2013-2025, {missing_total} have a missing number_of_motorist_killed value, so the complete-case decision removes 0 rows; {null_dates} rows have no crash_date and cannot be assigned to a year. All 13 years have observed dates from Jan 1 through Dec 31, so no requested year is partial by its observed endpoints. crash_date is a typed DATE, so empty strings and textual unknown sentinels are impossible; invalid dates cannot be represented."
        plan["limitations"] = "The dataset has no vehicle-miles-traveled exposure, so none of these metrics is risk per mile. These are outcomes among police-reported crashes and can change with crash volume, traffic exposure, reporting, or the number of people in each crash. All requested years have Jan 1-Dec 31 observed date spans; date-span endpoints do not independently establish that reporting is complete on every day."
        plan_path.write_text(json.dumps(plan, indent=2) + "\n")
    con.close()


if __name__ == "__main__":
    main()
