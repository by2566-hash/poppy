import csv
import json
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
con = duckdb.connect()
parquet = (ROOT / "data" / "crashes.parquet").as_posix()
con.execute(f"CREATE VIEW crashes AS SELECT * FROM read_parquet('{parquet}')")

coverage = con.execute(
    "SELECT min(crash_date), max(crash_date), count(*) FROM crashes"
).fetchone()
min_date, max_date, total_rows = coverage
full_years = con.execute(
    """
    SELECT y FROM (
      SELECT year(crash_date) AS y, min(crash_date) AS first_date,
             max(crash_date) AS last_date
      FROM crashes GROUP BY y
    )
    WHERE first_date = make_date(y, 1, 1)
      AND last_date = make_date(y, 12, 31)
    ORDER BY y
    """
).fetchnumpy()["y"].tolist()
full_years = [int(y) for y in full_years]
year_predicate = "year(crash_date) IN (" + ",".join(map(str, full_years)) + ")" if full_years else "FALSE"

def write_check(option_id, rows):
    with (OUT / f"check_{option_id}.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["fact", "value"])
        writer.writerows(rows)


def base_facts():
    facts = [
        ("file_min_crash_date", min_date.isoformat()),
        ("file_max_crash_date", max_date.isoformat()),
        ("file_total_rows", total_rows),
        ("fully_covered_calendar_years", ",".join(map(str, full_years))),
    ]
    annual = con.execute(
        """
        SELECT year(crash_date) AS y, min(crash_date), max(crash_date), count(*)
        FROM crashes GROUP BY y ORDER BY y
        """
    ).fetchall()
    for year, first, last, count in annual:
        partial = first.day != 1 or first.month != 1 or last.month != 12 or last.day != 31
        facts.append((f"year_{year}_file_rows", count))
        facts.append((f"year_{year}_date_coverage", f"{first.isoformat()} through {last.isoformat()}"))
        facts.append((f"year_{year}_partial_calendar_year", str(partial).lower()))
    return facts


for option_id in (1, 2, 3):
    facts = base_facts()
    facts.append(("planned_years", ",".join(map(str, full_years))))
    annual = con.execute(
        f"SELECT year(crash_date) AS y, count(*) FROM crashes WHERE {year_predicate} GROUP BY y ORDER BY y"
    ).fetchall()
    for year, count in annual:
        facts.append((f"year_{year}_population_rows", count))

    if option_id == 1:
        # crash_time is a TIME column: NULL is the only missing representation;
        # midnight is reported separately as a possible default-value pile-up.
        rows = con.execute(
            f"""
            SELECT year(crash_date),
                   count(*) FILTER (WHERE crash_time IS NULL),
                   count(*) FILTER (WHERE crash_time = TIME '00:00:00')
            FROM crashes WHERE {year_predicate} GROUP BY 1 ORDER BY 1
            """
        ).fetchall()
        for year, missing, midnight in rows:
            facts.extend([
                (f"year_{year}_crash_time_missing_rows", missing),
                (f"year_{year}_crash_time_midnight_rows_possible_default", midnight),
            ])
    else:
        outcomes = ["number_of_persons_injured", "number_of_persons_killed"] if option_id == 2 else ["number_of_persons_killed"]
        select_missing = ", ".join(f"count(*) FILTER (WHERE {column} IS NULL)" for column in outcomes)
        rows = con.execute(
            f"""
            SELECT year(crash_date),
                   count(*) FILTER (WHERE crash_time IS NULL),
                   count(*) FILTER (WHERE crash_time = TIME '00:00:00'),
                   {select_missing}
            FROM crashes WHERE {year_predicate} GROUP BY 1 ORDER BY 1
            """
        ).fetchall()
        for row in rows:
            year, time_missing, midnight, *outcome_missing = row
            facts.extend([
                (f"year_{year}_crash_time_missing_rows_before_filter", time_missing),
                (f"year_{year}_crash_time_midnight_rows_possible_default", midnight),
            ])
            for column, missing in zip(outcomes, outcome_missing):
                facts.append((f"year_{year}_{column}_missing_rows", missing))
        if option_id == 2:
            eligible_expr = "crash_time IS NOT NULL AND crash_time <> TIME '00:00:00' AND number_of_persons_injured IS NOT NULL AND number_of_persons_killed IS NOT NULL"
        else:
            eligible_expr = "crash_time IS NOT NULL AND crash_time <> TIME '00:00:00' AND number_of_persons_killed IS NOT NULL"
        eligible = con.execute(
            f"SELECT year(crash_date), count(*) FROM crashes WHERE {year_predicate} AND {eligible_expr} GROUP BY 1 ORDER BY 1"
        ).fetchall()
        for year, count in eligible:
            facts.append((f"year_{year}_eligible_rows_after_filters", count))

    write_check(option_id, facts)
