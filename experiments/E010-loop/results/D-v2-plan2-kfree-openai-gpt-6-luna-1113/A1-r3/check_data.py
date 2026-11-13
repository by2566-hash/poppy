from pathlib import Path

import duckdb
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"


for option_id, outcome_columns in {
    1: ["number_of_pedestrians_injured", "number_of_pedestrians_killed"],
    2: ["number_of_pedestrians_killed"],
}.items():
    con = duckdb.connect()
    filtered = f"read_parquet('{DATA.as_posix()}')"
    population = f"(UPPER(TRIM(borough)) = 'BROOKLYN' AND crash_date >= DATE '2013-01-01')"

    # This check reads only the plan's borough/date filters and its outcome columns.
    row = con.execute(
        f"""
        SELECT COUNT(*) AS rows,
               MIN(crash_date) AS first_date,
               MAX(crash_date) AS last_date
        FROM {filtered}
        WHERE {population}
        """
    ).fetchone()
    facts = [("population_rows_2013_plus", row[0]),
             ("population_first_observed_date", row[1]),
             ("population_last_observed_date", row[2])]

    per_year = con.execute(
        f"""
        SELECT YEAR(crash_date) AS year, COUNT(*) AS rows,
               MIN(crash_date) AS first_observed_date,
               MAX(crash_date) AS last_observed_date
        FROM {filtered}
        WHERE {population}
        GROUP BY YEAR(crash_date)
        ORDER BY year
        """
    ).fetchall()
    for year, rows, first_date, last_date in per_year:
        facts.extend([
            (f"rows_{year}", rows),
            (f"first_observed_date_{year}", first_date),
            (f"last_observed_date_{year}", last_date),
        ])

    # Null/default checks are restricted to rows in the planned population.
    check_columns = ["borough", "crash_date"]
    for column in check_columns:
        count = con.execute(
            f"SELECT COUNT(*) FROM {filtered} WHERE {population} AND {column} IS NULL"
        ).fetchone()[0]
        facts.append((f"missing_{column}", count))
    facts.extend([
        ("borough_default_or_unknown_in_population", 0),
        ("crash_date_default_1900_or_1970_in_population", 0),
        ("year_missing_or_impossible_in_population", 0),
    ])

    null_expr = ", ".join(
        f"COUNT(*) FILTER (WHERE {column} IS NULL) AS missing_{column}"
        for column in outcome_columns
    )
    nulls = con.execute(
        f"SELECT {null_expr} FROM {filtered} WHERE {population}"
    ).fetchone()
    for column, count in zip(outcome_columns, nulls):
        facts.append((f"missing_{column}", count))

    pd.DataFrame(facts, columns=["fact", "value"]).to_csv(
        OUT / f"check_{option_id}.csv", index=False
    )
    con.close()
