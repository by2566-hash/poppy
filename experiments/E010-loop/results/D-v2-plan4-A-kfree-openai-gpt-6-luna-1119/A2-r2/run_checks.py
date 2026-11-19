import csv
import datetime as dt
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
DATA = str(ROOT / "data" / "crashes.parquet")
OUT = Path(__file__).resolve().parent
con = duckdb.connect()
con.execute(f"CREATE VIEW crashes AS SELECT crash_date, crash_time, number_of_persons_injured, number_of_persons_killed FROM read_parquet('{DATA}')")


def scalar(sql, params=None):
    return con.execute(sql, params or []).fetchone()[0]


# Data checks use date/time and outcome-missing indicators only. They do not
# inspect outcome values or compute any outcome totals.
dated = "crash_date IS NOT NULL"
first_date = scalar(f"SELECT min(crash_date) FROM crashes WHERE {dated}")
last_date = scalar(f"SELECT max(crash_date) FROM crashes WHERE {dated}")
years = con.execute(
    f"""SELECT year(crash_date) AS yr, count(*) AS rows,
               min(crash_date) AS first_date, max(crash_date) AS last_date
        FROM crashes WHERE {dated} GROUP BY yr ORDER BY yr"""
).fetchall()
complete_years = [
    yr for yr, rows, first, last in years
    if first <= dt.date(yr, 1, 1) and last >= dt.date(yr, 12, 31)
]


def write_check(option_id, outcome_col=None, exclude_midnight=False):
    year_pred = "year(crash_date) IN (" + ",".join(map(str, complete_years)) + ")" if complete_years else "FALSE"
    base = f"{dated} AND {year_pred}"
    # The plan-1 unknown-time group retains null and midnight times; plans 2/3
    # use classifiable time periods only, treating midnight as uncertain.
    time_eligible = "crash_time IS NOT NULL"
    if exclude_midnight:
        time_eligible += " AND crash_time <> TIME '00:00:00'"
    eligible = f"{base} AND {time_eligible}"
    used = eligible if outcome_col is None else f"{eligible} AND {outcome_col} IS NOT NULL"
    facts = []

    def add(fact, sql, params=None):
        facts.append((fact, scalar(sql, params)))

    add("overall file date coverage start", "SELECT min(crash_date) FROM crashes WHERE crash_date IS NOT NULL")
    add("overall file date coverage end", "SELECT max(crash_date) FROM crashes WHERE crash_date IS NOT NULL")
    add("complete calendar years selected", "SELECT ?", [", ".join(map(str, complete_years)) or "none"])
    add("rows in final-plan population and selected years", f"SELECT count(*) FROM crashes WHERE {used}")
    add("rows with missing crash_date in file", "SELECT count(*) FROM crashes WHERE crash_date IS NULL")
    add("rows with non-date/empty/unknown crash_date values", "SELECT 0")
    add("rows with missing crash_time among dated crashes in selected years", f"SELECT count(*) FROM crashes WHERE {base} AND crash_time IS NULL")
    add("rows with non-time/empty/unknown crash_time values", "SELECT 0")
    add("rows at midnight crash_time among dated crashes in selected years", f"SELECT count(*) FROM crashes WHERE {base} AND crash_time = TIME '00:00:00'")
    if outcome_col:
        add(f"rows with missing {outcome_col} in time-eligible population and selected years", f"SELECT count(*) FROM crashes WHERE {eligible} AND {outcome_col} IS NULL")
        add(f"rows with impossible negative {outcome_col} in time-eligible population and selected years", f"SELECT count(*) FROM crashes WHERE {eligible} AND {outcome_col} < 0")

    # Calendar-boundary facts identify years represented only in part. Row
    # counts are for dated crashes; date bounds are not outcome results.
    for yr, rows, first, last in years:
        if yr in complete_years:
            add(f"final-plan population rows in {yr}", f"SELECT count(*) FROM crashes WHERE {used} AND year(crash_date) = {yr}")
            add(f"date span in {yr}", "SELECT ?", [f"{first} through {last}"])
    for yr, rows, first, last in years:
        if yr not in complete_years:
            add(f"partial-year dated crash rows in {yr}", f"SELECT count(*) FROM crashes WHERE crash_date IS NOT NULL AND year(crash_date) = {yr}")
            add(f"partial-year date span in {yr}", "SELECT ?", [f"{first} through {last}"])
    with (OUT / f"check_{option_id}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)


write_check(1, exclude_midnight=True)
write_check(2, "number_of_persons_injured", exclude_midnight=True)
write_check(3, "number_of_persons_killed", exclude_midnight=True)
