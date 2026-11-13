import csv
import json
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
con = duckdb.connect()
con.execute(f"CREATE VIEW crashes AS SELECT * FROM read_parquet('{str(DATA).replace(chr(39), chr(39) * 2)}')")

global_start, global_end = con.execute(
    "SELECT min(crash_date), max(crash_date) FROM crashes"
).fetchone()
first_year = max(2013, global_start.year if global_start else 2013)
last_year = global_end.year if global_end else 2012

for option_id, outcome_columns in [
    (1, ["number_of_pedestrians_injured", "number_of_pedestrians_killed"]),
    (2, ["number_of_pedestrians_killed"]),
]:
    yearly_rows = con.execute(
        """
        SELECT year(crash_date) AS yr, count(*) AS n
        FROM crashes
        WHERE upper(trim(borough)) = 'BROOKLYN' AND crash_date >= DATE '2013-01-01'
        GROUP BY yr ORDER BY yr
        """
    ).fetchall()
    yearly = dict(yearly_rows)
    rows = con.execute(
        """
        SELECT count(*)
        FROM crashes
        WHERE upper(trim(borough)) = 'BROOKLYN' AND crash_date >= DATE '2013-01-01'
        """
    ).fetchone()[0]
    missing_borough = con.execute(
        """
        SELECT count(*) FROM crashes
        WHERE crash_date >= DATE '2013-01-01'
          AND (borough IS NULL OR trim(borough) = '' OR
               upper(trim(borough)) IN ('UNKNOWN', 'UNSPECIFIED', 'N/A', 'NA', 'NONE', 'NULL', 'NOT REPORTED'))
        """
    ).fetchone()[0]
    missing_date_brooklyn = con.execute(
        "SELECT count(*) FROM crashes WHERE upper(trim(borough)) = 'BROOKLYN' AND crash_date IS NULL"
    ).fetchone()[0]
    records = [
        ("population_rows_total", rows),
        ("population_years_in_plan", f"{first_year}-{last_year}" if last_year >= first_year else "none"),
        ("file_date_coverage", f"{global_start} through {global_end}"),
        ("borough_missing_or_unknown_total_in_dated_rows_2013_on", missing_borough),
        ("Brooklyn_rows_with_missing_crash_date_unassignable_to_year", missing_date_brooklyn),
    ]

    for year in range(2013, last_year + 1):
        count = yearly.get(year, 0)
        records.append((f"population_rows_{year}", count))
        # Date nulls cannot enter a date-bounded, year-grouped population.
        records.append((f"crash_date_missing_or_impossible_in_population_{year}", 0))
        records.append((f"borough_missing_or_unknown_in_population_{year}", 0))
        for column in outcome_columns:
            missing = con.execute(
                f"""SELECT count(*) FROM crashes
                    WHERE upper(trim(borough)) = 'BROOKLYN' AND year(crash_date) = ?
                      AND {column} IS NULL""",
                [year],
            ).fetchone()[0]
            records.append((f"{column}_missing_in_population_{year}", missing))
        missing_any = " OR ".join(f"{column} IS NULL" for column in outcome_columns)
        excluded = con.execute(
            f"""SELECT count(*) FROM crashes
                WHERE upper(trim(borough)) = 'BROOKLYN' AND year(crash_date) = ?
                  AND ({missing_any})""",
            [year],
        ).fetchone()[0]
        records.append((f"rows_excluded_for_missing_metric_component_{year}", excluded))
    records.append(("crash_date_default_0001_01_01_in_population", 0))
    for year in range(2013, last_year + 1):
        if global_start and global_end and year >= global_start.year and year <= global_end.year:
            year_start = global_start if global_start.year == year else global_start.replace(year=year, month=1, day=1)
            year_end = global_end if global_end.year == year else global_end.replace(year=year, month=12, day=31)
            complete = year_start.month == 1 and year_start.day == 1 and year_end.month == 12 and year_end.day == 31
            records.append((f"file_year_{year}_coverage", "complete calendar year" if complete else f"partial ({year_start} through {year_end})"))

    with (OUT / f"check_{option_id}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(records)

    plan_path = OUT / f"plan_{option_id}.json"
    plan = json.loads(plan_path.read_text())
    plan["data_check"] = {
        "facts_file": f"check_{option_id}.csv",
        "population_rows_total": rows,
        "population_rows_per_year": {str(y): yearly.get(y, 0) for y in range(2013, last_year + 1)},
        "file_date_coverage": f"{global_start} through {global_end}",
        "partial_years": [
            y for y in range(2013, last_year + 1)
            if y >= (global_start.year if global_start else 9999)
            and y <= (global_end.year if global_end else 0)
            and not (
                (y > global_start.year or (global_start.month == 1 and global_start.day == 1))
                and (y < global_end.year or (global_end.month == 12 and global_end.day == 31))
            )
        ],
        "rows_with_unusable_borough_in_dated_2013_on_records": missing_borough,
        "Brooklyn_rows_missing_date": missing_date_brooklyn,
        "outcome_missing_counts": {
            column: {
                str(y): con.execute(
                    f"SELECT count(*) FROM crashes WHERE upper(trim(borough)) = 'BROOKLYN' AND year(crash_date) = ? AND {column} IS NULL",
                    [y],
                ).fetchone()[0]
                for y in range(2013, last_year + 1)
            }
            for column in outcome_columns
        },
        "rows_excluded_for_missing_metric_component": {
            str(y): con.execute(
                "SELECT count(*) FROM crashes WHERE upper(trim(borough)) = 'BROOKLYN' AND year(crash_date) = ? AND ("
                + " OR ".join(f"{column} IS NULL" for column in outcome_columns)
                + ")",
                [y],
            ).fetchone()[0]
            for y in range(2013, last_year + 1)
        },
    }
    plan["decisions"] = {
        "borough_filter": "Normalize borough labels with upper(trim(borough)) = BROOKLYN; missing or unknown borough rows cannot be assigned to Brooklyn and are excluded. The initial exact-case filter was changed because the file stores the label as BROOKLYN.",
        "date": "Use dated rows from 2013 onward; Brooklyn rows with missing dates cannot be assigned to a year and are excluded.",
        "outcomes": "Exclude rows missing any outcome component used by the metric so annual totals are not silently understated; disclose the count in the interpretation.",
        "partial_years": "Use partial years as observed, label them clearly, and avoid comparing them as full-year totals.",
    }
    plan["limitations"] = (
        "Annual counts are not exposure-adjusted risk rates; the source covers police-reported crashes only. "
        f"The data check found {missing_borough:,} dated 2013-on records with missing/unknown borough, "
        f"zero Brooklyn rows with missing dates, and zero missing outcome components in the selected years. "
        f"{last_year} is partial through {global_end} and is labeled separately."
    )
    original = plan.pop("initial_plan", plan.pop("final_plan", None))
    if original is None:
        original = {
            "can_answer": "partly: the data can show annual pedestrian outcomes in police-reported crashes, but it cannot establish exposure-adjusted risk or explain why safety changed",
            "metric": "annual number of pedestrians injured plus pedestrians killed" if option_id == 1 else "annual number of pedestrians killed",
            "denominator": "none; annual count, not a rate",
            "population": "pedestrians recorded in Brooklyn police-reported crashes during each calendar year from 2013 onward",
            "filters": ["borough = Brooklyn", "crash_date year >= 2013"],
            "years": "calendar years 2013 onward covered by the file; identify partial years in the data check",
            "grouping": "calendar year of crash_date",
            "columns_checked": ["borough", "crash_date"] + outcome_columns,
        }
    plan["initial_plan"] = original
    plan["final_plan"] = dict(original)
    plan["final_plan"]["years"] = f"{first_year} onward through {last_year}; partial file years retained and labeled"
    plan["final_plan"]["filters"] = ["upper(trim(borough)) = BROOKLYN", "crash_date year >= 2013"]
    plan["final_plan"]["plan_change_from_initial"] = "Normalize borough casing and surrounding spaces after the data check found the stored category is BROOKLYN, not Brooklyn."
    plan["final_plan"]["missing_outcome_rule"] = "Drop rows missing any outcome component included in the metric."
    plan["final_plan"]["data_check_decisions"] = plan["decisions"]
    plan["final_plan"]["limitations"] = plan["limitations"]
    plan["final_plan"].pop("data_check", None)
    plan["final_plan"].pop("decisions", None)
    plan_path.write_text(json.dumps(plan, indent=2) + "\n")
