import csv
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
con = duckdb.connect()


def scalar(sql):
    return con.execute(sql).fetchone()[0]


def write_check(option_id, facts):
    with (OUT / f"check_{option_id}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)


for option_id, outcome in [
    (1, "number_of_pedestrians_injured"),
    (2, "number_of_pedestrians_killed"),
]:
    base = f"read_parquet('{DATA.as_posix()}')"
    where = "upper(trim(borough)) = 'BROOKLYN' AND crash_date >= DATE '2013-01-01'"
    final_where = where + " AND crash_date < DATE '2026-01-01'"
    facts = []
    candidate_n = scalar(f"SELECT count(*) FROM {base} WHERE {where}")
    n = scalar(f"SELECT count(*) FROM {base} WHERE {final_where}")
    facts.append(("Brooklyn_candidate_crash_rows_with_date_2013_onward_including_partial_2026", candidate_n))
    facts.append(("rows_in_final_annual_population_2013_2025", n))
    facts.append(("borough_label_normalization", "upper(trim(borough)) = BROOKLYN; the file label is uppercase"))
    facts.append(("borough_labels_after_normalization_in_population", ",".join(
        row[0] for row in con.execute(
            f"SELECT DISTINCT borough FROM {base} WHERE {where} ORDER BY borough"
        ).fetchall()
    )))
    facts.append(("crash_date_type_and_impossible_dates", "DATE; impossible calendar dates cannot be represented"))
    for col in ["borough", "crash_date"]:
        missing = scalar(f"SELECT count(*) FROM {base} WHERE {final_where} AND {col} IS NULL")
        facts.append((f"missing_{col}_in_population", missing))
    missing_outcome = scalar(
        f"SELECT count(*) FROM {base} WHERE {final_where} AND {outcome} IS NULL"
    )
    facts.append((f"missing_{outcome}_in_population", missing_outcome))
    facts.append((f"share_missing_{outcome}_in_population", missing_outcome / n if n else None))
    yearly = con.execute(
        f"""SELECT year(crash_date) AS yr, count(*) AS rows,
                   min(crash_date) AS first_date, max(crash_date) AS last_date
            FROM {base} WHERE {where} GROUP BY yr ORDER BY yr"""
    ).fetchall()
    facts.append(("years_present_from_2013", ",".join(str(row[0]) for row in yearly)))
    for yr, rows, first_date, last_date in yearly:
        facts.extend([
            (f"year_{yr}_candidate_rows", rows),
            (f"year_{yr}_final_population_rows", rows if 2013 <= yr <= 2025 else 0),
            (f"year_{yr}_observed_first_date", first_date.isoformat()),
            (f"year_{yr}_observed_last_date", last_date.isoformat()),
            (f"year_{yr}_calendar_boundary_coverage_partial_by_observed_dates",
             first_date.isoformat() != f"{yr}-01-01" or last_date.isoformat() != f"{yr}-12-31"),
        ])
    write_check(option_id, facts)


# For option 3, count missing outcomes only in the candidate Brooklyn/year rows;
# the final denominator consists of candidate rows with an observed injury count.
base = f"read_parquet('{DATA.as_posix()}')"
where = "upper(trim(borough)) = 'BROOKLYN' AND crash_date >= DATE '2013-01-01'"
final_where = where + " AND crash_date < DATE '2026-01-01'"
outcome = "number_of_pedestrians_injured"
facts = []
candidate_n = scalar(f"SELECT count(*) FROM {base} WHERE {where}")
final_candidate_n = scalar(f"SELECT count(*) FROM {base} WHERE {final_where}")
missing_n = scalar(f"SELECT count(*) FROM {base} WHERE {final_where} AND {outcome} IS NULL")
eligible_n = final_candidate_n - missing_n
facts.extend([
    ("candidate_Brooklyn_crash_rows_with_date_2013_onward_including_partial_2026", candidate_n),
    ("candidate_Brooklyn_rows_in_final_years_2013_2025", final_candidate_n),
    ("borough_label_normalization", "upper(trim(borough)) = BROOKLYN; the file label is uppercase"),
    ("borough_labels_after_normalization_in_population", ",".join(
        row[0] for row in con.execute(
            f"SELECT DISTINCT borough FROM {base} WHERE {where} ORDER BY borough"
        ).fetchall()
    )),
    ("crash_date_type_and_impossible_dates", "DATE; impossible calendar dates cannot be represented"),
    ("rows_excluded_for_missing_injury_count", missing_n),
    ("share_final_year_candidate_rows_excluded_for_missing_injury_count", missing_n / final_candidate_n if final_candidate_n else None),
    ("rows_in_final_denominator_2013_2025", eligible_n),
    ("missing_borough_in_final_population", scalar(f"SELECT count(*) FROM {base} WHERE {final_where} AND borough IS NULL")),
    ("missing_crash_date_in_final_population", scalar(f"SELECT count(*) FROM {base} WHERE {final_where} AND crash_date IS NULL")),
])
yearly = con.execute(
    f"""SELECT year(crash_date) AS yr, count(*) AS candidate_rows,
               count(*) FILTER (WHERE crash_date < DATE '2026-01-01'
                                  AND {outcome} IS NOT NULL) AS eligible_rows,
               count(*) FILTER (WHERE crash_date < DATE '2026-01-01'
                                  AND {outcome} IS NULL) AS missing_final_outcome_rows,
               min(crash_date) AS first_date, max(crash_date) AS last_date
        FROM {base} WHERE {where} GROUP BY yr ORDER BY yr"""
).fetchall()
facts.append(("years_present_from_2013", ",".join(str(row[0]) for row in yearly)))
for yr, candidates, eligible, missing_final, first_date, last_date in yearly:
    facts.extend([
        (f"year_{yr}_candidate_rows", candidates),
        (f"year_{yr}_final_denominator_rows", eligible),
        (f"year_{yr}_rows_excluded_for_missing_injury_count", missing_final),
        (f"year_{yr}_observed_first_date", first_date.isoformat()),
        (f"year_{yr}_observed_last_date", last_date.isoformat()),
        (f"year_{yr}_calendar_boundary_coverage_partial_by_observed_dates",
         first_date.isoformat() != f"{yr}-01-01" or last_date.isoformat() != f"{yr}-12-31"),
    ])
write_check(3, facts)
