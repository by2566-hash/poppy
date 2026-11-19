import csv
import json
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
con = duckdb.connect()

for plan_id in (1, 2, 3):
    plan = json.loads((OUT / f"plan_{plan_id}.json").read_text())
    outcome_cols = (
        ["number_of_pedestrians_injured", "number_of_pedestrians_killed"]
        if plan_id in (1, 3)
        else ["number_of_pedestrians_killed"]
    )
    facts = []

    def fact(name, value):
        facts.append((name, value))

    # Final plan rows are the complete calendar years 2013–2025. The separate
    # 2026 coverage fact below documents why the partial year was excluded.
    total = con.execute(
        "SELECT count(*) FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'",
        [str(DATA)],
    ).fetchone()[0]
    brooklyn_total = con.execute(
        "SELECT count(*) FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' AND lower(trim(coalesce(borough, ''))) = 'brooklyn'",
        [str(DATA)],
    ).fetchone()[0]
    fact("all_city_rows_in_final_plan_years_2013_2025", total)
    fact("brooklyn_rows_in_final_plan_years_before_outcome_validity_filter", brooklyn_total)

    # Filter-column quality is checked before borough filtering, on all rows in
    # the plan's calendar-year window. Missing/unknown and impossible boroughs
    # are distinguished from ordinary non-Brooklyn borough values.
    borough_quality = con.execute(
        """
        SELECT
          count(*) FILTER (WHERE borough IS NULL OR trim(borough) = '' OR lower(trim(borough)) IN ('unknown','unspecified','n/a','na','null')),
          count(*) FILTER (WHERE borough IS NOT NULL AND trim(borough) <> '' AND lower(trim(borough)) NOT IN ('bronx','brooklyn','manhattan','queens','staten island','unknown','unspecified','n/a','na','null'))
        FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
        """,
        [str(DATA)],
    ).fetchone()
    fact("borough_missing_or_unknown_rows_before_borough_filter_in_final_plan_years", borough_quality[0])
    fact("borough_missing_or_unknown_share_of_city_rows_in_final_plan_years_percent", round(100 * borough_quality[0] / total, 4) if total else 0)
    fact("borough_impossible_value_rows_before_borough_filter_in_final_plan_years", borough_quality[1])

    # Date quality and partial-year coverage are assessed only within the plan
    # window; crash_date is DATE-typed, so impossible non-null values cannot occur.
    null_dates = con.execute(
        "SELECT count(*) FROM read_parquet(?) WHERE crash_date IS NULL",
        [str(DATA)],
    ).fetchone()[0]
    fact("null_crash_date_rows_in_file_cannot_be_assigned_to_a_plan_year", null_dates)
    fact("impossible_nonnull_crash_date_rows_DATE_type", 0)

    year_rows = con.execute(
        """
        SELECT year(crash_date) AS yr, count(*) AS city_rows,
               count(*) FILTER (WHERE lower(trim(coalesce(borough,'')))='brooklyn') AS brooklyn_rows,
               min(crash_date) AS first_date, max(crash_date) AS last_date
        FROM read_parquet(?)
        WHERE crash_date >= DATE '2013-01-01'
        GROUP BY yr ORDER BY yr
        """,
        [str(DATA)],
    ).fetchall()
    for year, city_n, bk_n, first_date, last_date in year_rows:
        is_partial = first_date.month > 1 or first_date.day > 1 or last_date.month < 12 or last_date.day < 31
        if year <= 2025:
            fact(f"year_{year}_all_city_rows", city_n)
            fact(f"year_{year}_brooklyn_rows_before_outcome_validity_filter", bk_n)
        if is_partial or year <= 2025:
            fact(f"year_{year}_coverage", f"partial ({first_date} through {last_date})" if is_partial else f"full calendar year ({first_date} through {last_date})")

    for col in outcome_cols:
        result = con.execute(
            f"SELECT count(*) FILTER (WHERE {col} IS NULL) FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' AND lower(trim(coalesce(borough,'')))='brooklyn'",
            [str(DATA)],
        ).fetchone()[0]
        fact(f"{col}_missing_rows_in_brooklyn_population_and_plan_years", result)

    # For the crash-share framing, count denominator records after excluding
    # records with missing pedestrian outcome fields; do not inspect outcomes.
    if plan_id == 3:
        for year, *_ in year_rows:
            if year > 2025:
                continue
            usable = con.execute(
                """
                SELECT count(*) FROM read_parquet(?)
                WHERE crash_date >= DATE '2013-01-01' AND year(crash_date)=?
                  AND lower(trim(coalesce(borough,'')))='brooklyn'
                  AND number_of_pedestrians_injured IS NOT NULL
                  AND number_of_pedestrians_killed IS NOT NULL
                """,
                [str(DATA), year],
            ).fetchone()[0]
            fact(f"year_{year}_plan_3_valid_denominator_crash_rows", usable)

    with (OUT / f"check_{plan_id}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)
