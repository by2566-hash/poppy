import csv
from datetime import date
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
PARQUET = ROOT / "data" / "crashes.parquet"

con = duckdb.connect()
parquet_path = str(PARQUET).replace("'", "''")
con.execute(f"CREATE VIEW crashes AS SELECT * FROM read_parquet('{parquet_path}')")

for plan_id in (1, 2, 3):
    outcome_columns = (
        ["number_of_pedestrians_killed"]
        if plan_id == 3
        else ["number_of_pedestrians_injured", "number_of_pedestrians_killed"]
    )
    selected = ["crash_date", "borough", *outcome_columns]
    select_sql = ", ".join(f'"{column}"' for column in selected)
    base = f"""(
        SELECT {select_sql}
        FROM crashes
        WHERE UPPER(TRIM(borough)) = 'BROOKLYN'
          AND crash_date >= DATE '2013-01-01'
    )"""
    facts = []

    count = con.execute(f"SELECT COUNT(*) FROM {base}").fetchone()[0]
    facts.append(("population_rows_brooklyn_2013_onward", count))

    annual = con.execute(
        f"""SELECT YEAR(crash_date) AS year, COUNT(*) AS rows,
                   MIN(crash_date) AS first_date, MAX(crash_date) AS last_date
            FROM {base}
            GROUP BY year ORDER BY year"""
    ).fetchall()
    last_population_year = annual[-1][0] if annual else None
    for year, rows, first_date, last_date in annual:
        facts.append((f"population_rows_{year}", rows))
        facts.append((f"coverage_{year}", f"{first_date} through {last_date}"))
        partial = (
            (year == 2013 and first_date > date(2013, 1, 1))
            or (year == last_population_year and last_date < date(year, 12, 31))
        )
        facts.append((f"year_{year}_partial_coverage", str(partial).lower()))

    if annual:
        facts.append(("latest_year_in_population", annual[-1][0]))
        facts.append(("population_date_coverage", f"{annual[0][2]} through {annual[-1][3]}"))
    else:
        facts.append(("latest_year_in_population", "none"))
        facts.append(("population_date_coverage", "none"))

    # Column quality checks are restricted to the planned Brooklyn, 2013+ rows.
    quality_expressions = [
        "COUNT(*) FILTER (WHERE borough IS NULL OR TRIM(CAST(borough AS VARCHAR)) = '') AS borough_missing",
        "COUNT(*) FILTER (WHERE LOWER(TRIM(CAST(borough AS VARCHAR))) IN ('unknown', 'unspecified', 'n/a', 'na', 'null', 'none')) AS borough_unknown",
        "COUNT(*) FILTER (WHERE crash_date IS NULL) AS crash_date_missing",
        "COUNT(*) FILTER (WHERE crash_date IN (DATE '0001-01-01', DATE '1900-01-01', DATE '1970-01-01')) AS crash_date_default",
    ]
    quality_names = [
        "borough_missing_or_empty_rows",
        "borough_unknown_word_rows",
        "crash_date_missing_rows",
        "crash_date_common_default_date_rows",
    ]
    for column in outcome_columns:
        quality_expressions.append(f'COUNT(*) FILTER (WHERE "{column}" IS NULL) AS "{column}_missing"')
        quality_names.append(f"{column}_missing_rows")
    quality = con.execute(f"SELECT {', '.join(quality_expressions)} FROM {base}").fetchone()
    facts.extend(zip(quality_names, quality))
    facts.append(("borough_rows_matched_after_trim_and_case_normalization", count))

    # A missing person-outcome value is checked only for missingness, never tabulated by value.
    for year, rows, _, _ in annual:
        missing_expressions = ", ".join(
            f'COUNT(*) FILTER (WHERE "{column}" IS NULL)' for column in outcome_columns
        )
        missing = con.execute(
            f"SELECT {missing_expressions} FROM {base} WHERE YEAR(crash_date) = ?",
            [year],
        ).fetchone()
        for column, value in zip(outcome_columns, missing):
            facts.append((f"{column}_missing_rows_{year}", value))

    with (OUT / f"check_{plan_id}.csv").open("w", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)

con.close()
