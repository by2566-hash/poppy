from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
PLANS = {
    1: [],
    2: ["number_of_persons_injured", "number_of_persons_killed"],
    3: ["number_of_persons_killed"],
}


def qident(name):
    return '"' + name.replace('"', '""') + '"'


def run(option_id, outcome_columns):
    columns = ["crash_date", "crash_time", *outcome_columns]
    con = duckdb.connect()
    selected = ", ".join(qident(column) for column in columns)
    data_path = str(DATA).replace("'", "''")
    con.execute(f"CREATE VIEW scoped AS SELECT {selected} FROM read_parquet('{data_path}')")
    facts = []

    def add(fact, value):
        facts.append({"fact": fact, "value": str(value)})

    add("columns_checked", ", ".join(columns))
    add("population_rows_with_known_year", con.execute(
        "SELECT count(*) FROM scoped WHERE crash_date IS NOT NULL"
    ).fetchone()[0])
    add("rows_without_crash_date_or_year", con.execute(
        "SELECT count(*) FROM scoped WHERE crash_date IS NULL"
    ).fetchone()[0])

    annual = con.execute("""
        SELECT year(crash_date) AS yr, count(*) AS n,
               min(crash_date) AS first_date, max(crash_date) AS last_date
        FROM scoped WHERE crash_date IS NOT NULL
        GROUP BY yr ORDER BY yr
    """).fetchall()
    add("years_present", ", ".join(str(row[0]) for row in annual) if annual else "none")
    for year, count, first_date, last_date in annual:
        add(f"rows_in_year_{year}", count)
        full_start = first_date.strftime("%Y-%m-%d") == f"{year}-01-01"
        full_end = last_date.strftime("%Y-%m-%d") == f"{year}-12-31"
        add(f"date_coverage_{year}",
            f"{first_date} through {last_date}; starts_at_year_boundary={str(full_start).lower()}; "
            f"ends_at_year_boundary={str(full_end).lower()}; calendar_year_partial={str(not (full_start and full_end)).lower()}")

    year_filter = "year(crash_date) BETWEEN 2013 AND 2025"
    add("final_years_selected", "2013-2025 (complete calendar years)")
    add("rows_excluded_as_partial_years", con.execute(
        f"SELECT count(*) FROM scoped WHERE crash_date IS NOT NULL AND NOT ({year_filter})"
    ).fetchone()[0])
    add("rows_in_final_years", con.execute(
        f"SELECT count(*) FROM scoped WHERE crash_date IS NOT NULL AND {year_filter}"
    ).fetchone()[0])

    add("crash_date_null_rows", con.execute(
        "SELECT count(*) FROM scoped WHERE crash_date IS NULL"
    ).fetchone()[0])
    add("crash_date_type_and_invalid_values",
        "DATE type; non-null values are valid calendar dates; empty strings/unknown words cannot be stored as DATE")

    known_year = "crash_date IS NOT NULL"
    add("crash_time_null_rows_with_known_year", con.execute(
        f"SELECT count(*) FROM scoped WHERE {known_year} AND crash_time IS NULL"
    ).fetchone()[0])
    add("crash_time_midnight_rows_with_known_year", con.execute(
        f"SELECT count(*) FROM scoped WHERE {known_year} AND crash_time = TIME '00:00:00'"
    ).fetchone()[0])
    add("crash_time_type_and_invalid_values",
        "TIME type; non-null values are valid times; empty strings/unknown words and impossible clock values cannot be stored as TIME")
    add("crash_time_null_rows_in_final_years", con.execute(
        f"SELECT count(*) FROM scoped WHERE {year_filter} AND crash_time IS NULL"
    ).fetchone()[0])
    add("crash_time_midnight_rows_in_final_years", con.execute(
        f"SELECT count(*) FROM scoped WHERE {year_filter} AND crash_time = TIME '00:00:00'"
    ).fetchone()[0])

    for column in outcome_columns:
        col = qident(column)
        add(f"{column}_null_rows_with_known_year", con.execute(
            f"SELECT count(*) FROM scoped WHERE {known_year} AND {col} IS NULL"
        ).fetchone()[0])
        add(f"{column}_negative_impossible_rows_with_known_year", con.execute(
            f"SELECT count(*) FROM scoped WHERE {known_year} AND {col} < 0"
        ).fetchone()[0])
        add(f"{column}_zero_rows_with_known_year", con.execute(
            f"SELECT count(*) FROM scoped WHERE {known_year} AND {col} = 0"
        ).fetchone()[0])
        add(f"{column}_type_and_invalid_values",
            "INT type; negative counts are impossible; empty strings/unknown words cannot be stored as INT; zero is a valid recorded count")
        missing = con.execute(
            f"SELECT count(*) FROM scoped WHERE {year_filter} AND {col} IS NULL"
        ).fetchone()[0]
        base = con.execute(
            f"SELECT count(*) FROM scoped WHERE {year_filter}"
        ).fetchone()[0]
        add(f"{column}_null_rows_in_final_years", missing)
        add(f"{column}_null_share_in_final_years", f"{missing / base:.6%}" if base else "not applicable")
        add(f"{column}_negative_rows_in_final_years", con.execute(
            f"SELECT count(*) FROM scoped WHERE {year_filter} AND {col} < 0"
        ).fetchone()[0])
        add(f"{column}_zero_rows_in_final_years", con.execute(
            f"SELECT count(*) FROM scoped WHERE {year_filter} AND {col} = 0"
        ).fetchone()[0])

    if len(outcome_columns) > 1:
        null_condition = " OR ".join(f"{qident(column)} IS NULL" for column in outcome_columns)
        missing_any = con.execute(
            f"SELECT count(*) FROM scoped WHERE {year_filter} AND ({null_condition})"
        ).fetchone()[0]
        base = con.execute(f"SELECT count(*) FROM scoped WHERE {year_filter}").fetchone()[0]
        add("any_outcome_column_null_rows_in_final_years", missing_any)
        add("any_outcome_column_null_share_in_final_years", f"{missing_any / base:.6%}" if base else "not applicable")

    complete_condition = " AND ".join(
        ["crash_time IS NOT NULL", *(f"{qident(column)} IS NOT NULL" for column in outcome_columns)]
    )
    add("final_plan_population_rows_2013_2025", con.execute(
        f"SELECT count(*) FROM scoped WHERE {year_filter} AND {complete_condition}"
    ).fetchone()[0])
    eligible_by_year = con.execute(f"""
        SELECT year(crash_date) AS yr, count(*)
        FROM scoped
        WHERE {year_filter} AND {complete_condition}
        GROUP BY yr ORDER BY yr
    """).fetchall()
    for year, count in eligible_by_year:
        add(f"final_plan_population_rows_{year}", count)

    con.close()
    import pandas as pd

    pd.DataFrame(facts).to_csv(OUT / f"check_{option_id}.csv", index=False)


for option, columns in PLANS.items():
    run(option, columns)
