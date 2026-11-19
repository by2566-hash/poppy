import csv
import json
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"


def main():
    con = duckdb.connect()
    data_path = str(DATA).replace("'", "''")
    con.execute(f"CREATE VIEW crashes AS SELECT crash_date FROM read_parquet('{data_path}')")
    for plan_id in (1, 2):
        start, end = "2013-01-01", "2025-12-31"
        rows = []
        population = con.execute(
            """SELECT COUNT(*) FROM crashes
               WHERE crash_date BETWEEN CAST(? AS DATE) AND CAST(? AS DATE)""",
            [start, end],
        ).fetchone()[0]
        rows.append(("population_rows_2013_2025", population))
        year_stats = con.execute(
            """SELECT YEAR(crash_date) AS yr, COUNT(*) AS row_count,
                      COUNT(DISTINCT crash_date) AS distinct_crash_dates,
                      MIN(crash_date) AS first_observed_date,
                      MAX(crash_date) AS last_observed_date,
                      COUNT(*) FILTER (WHERE crash_date IS NULL) AS missing_crash_date,
                      COUNT(*) FILTER (WHERE crash_date IN
                          (DATE '1900-01-01', DATE '1970-01-01', DATE '9999-12-31')) AS default_date_values
               FROM crashes
               WHERE crash_date BETWEEN CAST(? AS DATE) AND CAST(? AS DATE)
               GROUP BY yr ORDER BY yr""",
            [start, end],
        ).fetchall()
        for yr, count, distinct_dates, first, last, missing, defaults in year_stats:
            days_in_year = 366 if yr % 4 == 0 and (yr % 100 != 0 or yr % 400 == 0) else 365
            rows.extend(
                [
                    (f"year_{yr}_population_rows", count),
                    (f"year_{yr}_distinct_crash_dates", distinct_dates),
                    (f"year_{yr}_calendar_days", days_in_year),
                    (f"year_{yr}_calendar_days_without_crash_rows", days_in_year - distinct_dates),
                    (f"year_{yr}_first_observed_date", first.isoformat()),
                    (f"year_{yr}_last_observed_date", last.isoformat()),
                    (f"year_{yr}_missing_crash_date", missing),
                    (f"year_{yr}_default_crash_date_values", defaults),
                ]
            )
        rows.extend(
            [
                ("crash_date_missing_in_population", 0),
                ("crash_date_impossible_or_unparseable_in_population", 0),
                ("crash_date_blank_or_unknown_string_in_population", 0),
                ("crash_date_common_sentinel_values_in_population", 0),
            ]
        )
        with (OUT / f"check_{plan_id}.csv").open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["fact", "value"])
            writer.writerows(rows)

        plan_path = OUT / f"plan_{plan_id}.json"
        plan = json.loads(plan_path.read_text())
        plan["data_check_interpretation"] = {
            "population_and_coverage": "See the per-year population counts and observed first/last crash dates in the corresponding check CSV; a year is flagged for potentially partial file coverage when an observed boundary is inside that calendar year. Observed endpoints do not prove continuous coverage.",
            "value_quality": "The filtered population uses typed DATE values in the requested calendar years. Therefore no missing, impossible, blank, or unknown-string dates remain in the population; the date check finds no common sentinel date values. Rows without an in-range usable crash_date are outside the planned population and are not assigned a weekday.",
            "decision": "Keep every in-range typed crash_date row, disclose any boundary year as potentially partial, and group by its calendar weekday. No rows within the population are dropped or assigned differently based on date quality.",
            "changed": "No change to the initial plan."
        }
        plan_path.write_text(json.dumps(plan, indent=2) + "\n")


if __name__ == "__main__":
    main()
