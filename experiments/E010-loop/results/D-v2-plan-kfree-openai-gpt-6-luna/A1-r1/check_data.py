import csv
import duckdb
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"


def check(option_id, include_injured):
    cols = ["crash_date", "borough", "number_of_pedestrians_killed"]
    if include_injured:
        cols.append("number_of_pedestrians_injured")
    select_cols = ", ".join(cols)
    con = duckdb.connect()
    parquet_path = str(DATA).replace("'", "''")
    con.execute(
        f"CREATE TEMP VIEW source AS SELECT {select_cols} FROM read_parquet('{parquet_path}')"
    )
    con.execute(
        """CREATE TEMP VIEW population AS
           SELECT *, year(crash_date) AS crash_year
           FROM source
           WHERE upper(trim(borough)) = 'BROOKLYN'
             AND crash_date >= DATE '2013-01-01'"""
    )

    facts = []

    def add(fact, value):
        facts.append((fact, str(value)))

    row_count = con.execute("SELECT count(*) FROM population").fetchone()[0]
    add("population_rows_2013_onward", row_count)
    annual = con.execute(
        "SELECT crash_year, count(*) FROM population GROUP BY crash_year ORDER BY crash_year"
    ).fetchall()
    for year, count in annual:
        add(f"population_rows_{year}", count)
    date_bounds = con.execute(
        "SELECT min(crash_date), max(crash_date) FROM population"
    ).fetchone()
    add("population_min_crash_date", date_bounds[0])
    add("population_max_crash_date", date_bounds[1])
    for year, _ in annual:
        start, end = con.execute(
            "SELECT min(crash_date), max(crash_date) FROM population WHERE crash_year = ?",
            [year],
        ).fetchone()
        add(f"year_{year}_first_crash_date", start)
        add(f"year_{year}_last_crash_date", end)
        if year == date_bounds[1].year:
            add(f"year_{year}_coverage", f"partial through {end}")
        else:
            add(f"year_{year}_coverage", f"observed dates {start} through {end}; completeness not inferable from rows alone")

    # Quality checks are restricted to the planned Brooklyn rows in planned years.
    quality_conditions = {
        "borough_missing_null_blank_or_unknown": "borough IS NULL OR trim(borough) = '' OR upper(trim(borough)) IN ('UNKNOWN', 'UNSPECIFIED', 'N/A', 'NA')",
        "crash_date_missing": "crash_date IS NULL",
    }
    value_cols = ["number_of_pedestrians_killed"]
    if include_injured:
        value_cols.append("number_of_pedestrians_injured")
    for col in value_cols:
        quality_conditions[f"{col}_missing_null"] = f"{col} IS NULL"
        quality_conditions[f"{col}_default_zero"] = f"{col} = 0"
        quality_conditions[f"{col}_impossible_negative"] = f"{col} < 0"

    for label, condition in quality_conditions.items():
        add(
            f"{label}_in_population",
            con.execute(f"SELECT count(*) FROM population WHERE {condition}").fetchone()[0],
        )
        for year, _ in annual:
            add(
                f"{label}_in_{year}",
                con.execute(
                    f"SELECT count(*) FROM population WHERE crash_year = ? AND ({condition})",
                    [year],
                ).fetchone()[0],
            )

    with (OUT / f"check_{option_id}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)
    con.close()


check(1, True)
check(2, False)
