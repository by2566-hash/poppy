import csv
import json
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
PARQUET = ROOT / "data" / "crashes.parquet"

con = duckdb.connect()
parquet_literal = str(PARQUET).replace("'", "''")
con.execute(f"CREATE VIEW crashes AS SELECT crash_date, borough, number_of_pedestrians_injured, number_of_pedestrians_killed FROM read_parquet('{parquet_literal}')")

facts_by_plan = {1: [], 2: []}


def add(fact, value, plan_ids=(1, 2)):
    for plan_id in plan_ids:
        facts_by_plan[plan_id].append({"fact": fact, "value": value})


scope = "crash_date >= DATE '2013-01-01'"
all_years = con.execute(
    f"""
    SELECT year(crash_date) AS yr,
           count(*) AS city_rows,
           count(*) FILTER (WHERE upper(trim(borough)) = 'BROOKLYN') AS brooklyn_rows,
           min(crash_date) AS first_date,
           max(crash_date) AS last_date
    FROM crashes WHERE {scope}
    GROUP BY yr ORDER BY yr
    """
).fetchall()
add("Candidate population definition", "All rows with a nonmissing crash_date in 2013 or later; borough and outcome quality summarized separately")
candidate_n = con.execute(f"SELECT count(*) FROM crashes WHERE {scope}").fetchone()[0]
add("Candidate dated NYC crash rows (2013 onward)", candidate_n)
add("Rows with missing crash_date (cannot assign to a planned year)", con.execute("SELECT count(*) FROM crashes WHERE crash_date IS NULL").fetchone()[0])
sentinel_dates = "(DATE '0001-01-01', DATE '1900-01-01', DATE '1970-01-01', DATE '2013-01-01', DATE '9999-12-31')"
add(
    "Dated candidate rows at checked sentinel/default crash dates (0001-01-01, 1900-01-01, 1970-01-01, 2013-01-01, 9999-12-31)",
    con.execute(f"SELECT count(*) FROM crashes WHERE {scope} AND crash_date IN {sentinel_dates}").fetchone()[0],
)

valid_boroughs = "('BRONX', 'BROOKLYN', 'MANHATTAN', 'QUEENS', 'STATEN ISLAND')"
borough_stats = con.execute(
    f"""
    SELECT
      count(*) FILTER (WHERE borough IS NULL OR trim(borough) = '' OR upper(trim(borough)) IN ('UNKNOWN','UNSPECIFIED','N/A','NA','NONE')) AS missing_or_unknown,
      count(*) FILTER (WHERE borough IS NOT NULL AND trim(borough) <> '' AND upper(trim(borough)) NOT IN {valid_boroughs} AND upper(trim(borough)) NOT IN ('UNKNOWN','UNSPECIFIED','N/A','NA','NONE')) AS unsupported_value,
      count(*) FILTER (WHERE upper(trim(borough)) = 'BROOKLYN') AS brooklyn_rows
    FROM crashes WHERE {scope}
    """
).fetchone()
add("Borough missing/blank/unknown/sentinel rows in dated candidate population", borough_stats[0])
add("Borough unsupported-value rows in dated candidate population", borough_stats[1])
add("Brooklyn rows in dated candidate population", borough_stats[2])
add("Share of dated candidate rows with missing/unknown borough", borough_stats[0] / candidate_n if candidate_n else None)
add("Share of dated candidate rows with unsupported borough", borough_stats[1] / candidate_n if candidate_n else None)

for year, city_rows, brooklyn_rows, first_date, last_date in all_years:
    start = f"{year}-01-01"
    end = f"{year}-12-31"
    partial = str(first_date) > start or str(last_date) < end
    add(f"{year}: NYC candidate rows", city_rows)
    add(f"{year}: Brooklyn rows before outcome completeness filter", brooklyn_rows)
    add(f"{year}: observed date coverage", f"{first_date} through {last_date}")
    add(f"{year}: partial calendar year in file", "yes" if partial else "no")

    outcome_stats = con.execute(
        """
        SELECT count(*) AS brooklyn_rows,
          count(*) FILTER (WHERE number_of_pedestrians_injured IS NULL) AS pedestrian_injured_missing,
          count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS pedestrian_killed_missing,
          count(*) FILTER (WHERE number_of_pedestrians_injured IS NULL OR number_of_pedestrians_killed IS NULL) AS either_outcome_missing,
          count(*) FILTER (WHERE crash_date IN (DATE '0001-01-01', DATE '1900-01-01', DATE '1970-01-01', DATE '2013-01-01', DATE '9999-12-31')) AS checked_date_sentinel_rows
        FROM crashes
        WHERE upper(trim(borough)) = 'BROOKLYN' AND year(crash_date) = ?
        """,
        [year],
    ).fetchone()
    add(f"{year}: Brooklyn rows with missing number_of_pedestrians_injured", outcome_stats[1], (1,))
    add(f"{year}: Brooklyn rows with missing number_of_pedestrians_killed", outcome_stats[2], (1, 2))
    add(f"{year}: Brooklyn rows missing either pedestrian outcome field", outcome_stats[3], (1,))
    add(f"{year}: Brooklyn rows with both pedestrian outcome fields present", outcome_stats[0] - outcome_stats[3], (1,))
    add(f"{year}: Brooklyn rows with pedestrian death field present", outcome_stats[0] - outcome_stats[2], (2,))
    add(f"{year}: Brooklyn rows at checked sentinel/default crash dates", outcome_stats[4])

for plan_id, rows in facts_by_plan.items():
    path = OUT / f"check_{plan_id}.csv"
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["fact", "value"])
        writer.writeheader()
        writer.writerows(rows)

    plan_path = OUT / f"plan_{plan_id}.json"
    plan = json.loads(plan_path.read_text())
    years = [row[0] for row in all_years]
    partial_years = [
        row[0]
        for row in all_years
        if str(row[3]) > f"{row[0]}-01-01" or str(row[4]) < f"{row[0]}-12-31"
    ]
    plan["data_check_decisions"] = {
        "facts_file": f"check_{plan_id}.csv",
        "observed_years": years,
        "partial_calendar_years": partial_years,
        "borough_decision": "Keep borough labels that match Brooklyn after trimming whitespace and ignoring case. The dated NYC candidate population has 668406 missing/blank/unknown borough labels (30.82%) and 0 unsupported borough labels; those rows are not assigned to Brooklyn. See check file.",
        "outcome_decision": ("Use only rows with both pedestrian injury and death counts present. The data check found no missing values in either field among Brooklyn rows in any checked year, so no Brooklyn rows are dropped for outcome missingness." if plan_id == 1 else "Use only rows with a pedestrian death count present. The data check found no missing death counts among Brooklyn rows in any checked year, so no Brooklyn rows are dropped for outcome missingness."),
        "year_decision": "Retain complete years 2013–2025; exclude the 9700 Brooklyn crash rows in partial 2026 because observed coverage is 2026-01-01 through 2026-06-11.",
        "date_value_decision": "Crash_date is a DATE, with 0 missing values. The checked sentinel date 2013-01-01 has 102 Brooklyn rows (102 of 47024 Brooklyn crashes in 2013, below the annual average daily Brooklyn count); retain these valid in-period dates and disclose them rather than treating them as a pile-up.",
        "population_after_checks": ("Brooklyn crashes in complete calendar years from 2013 onward with both pedestrian injury and pedestrian death fields present." if plan_id == 1 else "Brooklyn crashes in complete calendar years from 2013 onward with the pedestrian death field present."),
        "changes_from_initial_plan": "Normalized borough matching by trimming whitespace and ignoring case after an exact-case Brooklyn match yielded no rows; excluded 2026 because date coverage ends on 2026-06-11 and it is partial. No outcome-missing rows were found among Brooklyn crashes, so the planned outcome completeness restriction removes none.",
    }
    plan["limitations"] = "The file reports crash counts, not pedestrian exposure or population, so absolute annual counts do not measure risk per trip or establish overall road safety. Of 2168642 NYC crash rows with dates from 2013 onward, 668406 (30.82%) have missing/blank/unknown borough labels and cannot be assigned to Brooklyn; 0 have unsupported nonblank borough labels. There are 0 missing crash dates and no Brooklyn rows with missing outcome counts used by this framing. The checked date 2013-01-01 has 102 Brooklyn rows (102 of 47024 Brooklyn crashes in 2013), which are retained as valid in-period dates rather than treated as a pile-up. The 9700 Brooklyn crashes in partial 2026 are excluded because file coverage ends 2026-06-11."
    final = plan["initial_plan"].copy()
    final["years"] = f"Complete calendar years from 2013 through {max(year for year in years if year not in partial_years)}; exclude partial years {partial_years}."
    final["population"] = ("Brooklyn crashes in the final complete calendar years with nonmissing values for both pedestrian injury and pedestrian death counts; count recorded pedestrian casualties from those crashes." if plan_id == 1 else "Brooklyn crashes in the final complete calendar years with a nonmissing pedestrian death count; count recorded pedestrian deaths from those crashes.")
    outcome_filter = "both pedestrian injury and pedestrian death counts are nonmissing" if plan_id == 1 else "pedestrian death count is nonmissing"
    final["filters"] = ["borough label equals Brooklyn after trimming whitespace and ignoring case", "crash_date is in a retained complete calendar year from 2013 through 2025", outcome_filter]
    final["changes_from_initial_plan"] = plan["data_check_decisions"]["changes_from_initial_plan"]
    final["data_check_decisions"] = plan["data_check_decisions"]
    final["limitations"] = plan["limitations"]
    plan["final_plan"] = final
    plan_path.write_text(json.dumps(plan, indent=2) + "\n")

con.close()
