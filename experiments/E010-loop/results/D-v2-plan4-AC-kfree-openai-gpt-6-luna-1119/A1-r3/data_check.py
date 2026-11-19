import csv
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
PARQUET = ROOT / "data" / "crashes.parquet"
con = duckdb.connect()
con.execute("SET threads TO 2")

# The plan defines its endpoint as the latest year present, so first establish
# the date coverage using only the grouping column.
coverage = con.execute(
    "SELECT MIN(crash_date), MAX(crash_date) FROM read_parquet(?)",
    [str(PARQUET)],
).fetchone()
min_date, max_date = coverage
last_year = max_date.year if max_date else 2013
first_year = 2013

date_coverage = con.execute(
    """
    SELECT YEAR(crash_date) AS year, MIN(crash_date), MAX(crash_date), COUNT(*)
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < ?
    GROUP BY 1 ORDER BY 1
    """,
    [str(PARQUET), f"{last_year + 1}-01-01"],
).fetchall()

for option_id in (1, 2):
    facts = []

    def add(fact, value):
        facts.append((fact, str(value)))

    date_end = f"{last_year + 1}-01-01"
    base_where = f"crash_date >= DATE '2013-01-01' AND crash_date < DATE '{date_end}'"
    brooklyn = "UPPER(TRIM(borough)) = 'BROOKLYN'"
    table = f"read_parquet('{PARQUET.as_posix()}')"

    # Coverage facts use only crash_date.
    add("file_min_crash_date", min_date)
    add("file_max_crash_date", max_date)
    add("analysis_years", f"{first_year}-{last_year}")
    for year, min_d, max_d, n in date_coverage:
        partial = (year == first_year and min_d.month != 1 or
                   year == last_year and max_d.month != 12)
        add(f"year_{year}_date_extent_and_rows", f"{min_d} to {max_d}; {n} rows")
        add(f"year_{year}_boundary_coverage_partial", "yes" if partial else "no")

    # Brooklyn is a filter, so inspect its values before applying it on all
    # dated rows in the planned years.
    borough_diag = con.execute(
        f"""
        SELECT
          COUNT(*) FILTER (WHERE borough IS NULL OR TRIM(borough) = '' OR
            LOWER(TRIM(borough)) IN ('unknown','unspecified','not known','n/a','na','null','none','0')),
          COUNT(*) FILTER (WHERE borough IS NOT NULL AND TRIM(borough) <> '' AND
            UPPER(TRIM(borough)) NOT IN ('BRONX','BROOKLYN','MANHATTAN','QUEENS','STATEN ISLAND') AND
            LOWER(TRIM(borough)) NOT IN ('unknown','unspecified','not known','n/a','na','null','none','0')),
          COUNT(*) FILTER (WHERE UPPER(TRIM(borough)) = 'BROOKLYN'),
          COUNT(*)
        FROM {table} WHERE {base_where}
        """
    ).fetchone()
    add("dated_rows_in_analysis_years_before_borough_filter", borough_diag[3])
    add("borough_missing_or_unknown_rows_before_filter", borough_diag[0])
    add("borough_impossible_or_unrecognized_rows_before_filter", borough_diag[1])
    add("borough_brooklyn_rows_before_filter", borough_diag[2])

    # Crash dates with no year cannot be assigned to the series; count the
    # otherwise relevant Brooklyn records separately for disclosure.
    null_dates = con.execute(
        f"SELECT COUNT(*) FROM {table} WHERE crash_date IS NULL AND {brooklyn}"
    ).fetchone()[0]
    add("brooklyn_rows_with_missing_crash_date_year_unassignable", null_dates)

    if option_id == 1:
        population_where = f"{base_where} AND {brooklyn}"
        person_cols = ("number_of_pedestrians_injured", "number_of_pedestrians_killed")
    else:
        # For outcome-filter diagnostics, inspect Brooklyn rows before applying
        # the pedestrian casualty filter.
        population_where = f"{base_where} AND {brooklyn} AND " \
            "number_of_pedestrians_injured IS NOT NULL AND " \
            "number_of_pedestrians_killed IS NOT NULL AND " \
            "number_of_pedestrians_injured + number_of_pedestrians_killed > 0"
        person_cols = ("number_of_pedestrians_injured", "number_of_pedestrians_killed")

    row_counts = con.execute(
        f"SELECT COUNT(*) FROM {table} WHERE {population_where}"
    ).fetchone()[0]
    add("population_rows_in_analysis_years", row_counts)
    yearly = con.execute(
        f"SELECT YEAR(crash_date), COUNT(*) FROM {table} WHERE {population_where} "
        "GROUP BY 1 ORDER BY 1"
    ).fetchall()
    for year in range(first_year, last_year + 1):
        n = next((count for y, count in yearly if y == year), 0)
        add(f"population_rows_year_{year}", n)

    # Missing outcome values are checked only as missingness counts, never
    # summarized by value or summed during the data-check stage.
    missing_scope = f"{base_where} AND {brooklyn}"
    for col in person_cols:
        n_missing = con.execute(
            f"SELECT COUNT(*) FROM {table} WHERE {missing_scope} AND {col} IS NULL"
        ).fetchone()[0]
        add(f"{col}_missing_rows_in_brooklyn_years_before_outcome_use", n_missing)
    any_missing = con.execute(
        f"SELECT COUNT(*) FROM {table} WHERE {missing_scope} AND "
        "(number_of_pedestrians_injured IS NULL OR number_of_pedestrians_killed IS NULL)"
    ).fetchone()[0]
    add("rows_with_either_pedestrian_outcome_missing_before_outcome_use", any_missing)

    with (OUT / f"check_{option_id}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)

con.close()
