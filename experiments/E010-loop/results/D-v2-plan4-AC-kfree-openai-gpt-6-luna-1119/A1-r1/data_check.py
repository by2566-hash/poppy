import csv
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
DATA = (ROOT / "data" / "crashes.parquet").as_posix()
con = duckdb.connect()
con.execute(f"CREATE VIEW crashes AS SELECT * FROM read_parquet('{DATA}')")

# Determine the final calendar year represented; all other checks are restricted
# to years 2013 through this year, as specified in both initial plans.
max_year = con.execute(
    "SELECT MAX(EXTRACT(YEAR FROM crash_date))::INTEGER FROM crashes WHERE crash_date IS NOT NULL"
).fetchone()[0]
years = list(range(2013, max_year + 1))

for option_id, outcome_columns in {
    1: ["number_of_pedestrians_injured", "number_of_pedestrians_killed"],
    2: ["number_of_pedestrians_killed"],
}.items():
    facts = []

    def add(fact, value):
        facts.append((fact, str(value)))

    date_missing = con.execute(
        "SELECT COUNT(*) FROM crashes WHERE crash_date IS NULL"
    ).fetchone()[0]
    add("rows_with_missing_crash_date_in_file_unassignable_to_plan_years", date_missing)

    borough_quality = con.execute(
        """
        SELECT
          COUNT(*) FILTER (WHERE borough IS NULL OR trim(borough) = ''
            OR upper(trim(borough)) IN ('UNKNOWN', 'UNSPECIFIED', 'N/A', 'NA', 'NULL')),
          COUNT(*) FILTER (WHERE borough IS NOT NULL AND trim(borough) <> ''
            AND upper(trim(borough)) NOT IN
              ('BRONX', 'BROOKLYN', 'MANHATTAN', 'QUEENS', 'STATEN ISLAND',
               'UNKNOWN', 'UNSPECIFIED', 'N/A', 'NA', 'NULL')),
          COUNT(*) FILTER (WHERE upper(trim(borough)) = 'UNKNOWN')
        FROM crashes
        WHERE crash_date >= DATE '2013-01-01'
          AND crash_date < make_date(?, 1, 1)
        """,
        [max_year + 1],
    ).fetchone()
    add("year_population_rows_before_borough_filter_2013_through_latest", con.execute(
        "SELECT COUNT(*) FROM crashes WHERE crash_date >= DATE '2013-01-01' AND crash_date < make_date(?,1,1)",
        [max_year + 1],
    ).fetchone()[0])
    add("borough_missing_null_empty_or_unknown_rows_before_borough_filter", borough_quality[0])
    add("borough_impossible_or_unrecognized_rows_before_borough_filter", borough_quality[1])
    add("borough_unknown_default_value_rows_before_borough_filter", borough_quality[2])

    final_end_year = max_year - 1 if con.execute(
        f"SELECT MAX(crash_date) < make_date({max_year}, 12, 31) FROM crashes"
    ).fetchone()[0] else max_year
    final_end_exclusive = f"{final_end_year + 1}-01-01"
    final_pre_filter = con.execute(
        "SELECT COUNT(*) FROM crashes WHERE crash_date >= DATE '2013-01-01' AND crash_date < ?::DATE",
        [final_end_exclusive],
    ).fetchone()[0]
    final_borough_quality = con.execute(
        """
        SELECT
          COUNT(*) FILTER (WHERE borough IS NULL OR trim(borough) = ''
            OR upper(trim(borough)) IN ('UNKNOWN', 'UNSPECIFIED', 'N/A', 'NA', 'NULL')),
          COUNT(*) FILTER (WHERE borough IS NOT NULL AND trim(borough) <> ''
            AND upper(trim(borough)) NOT IN
              ('BRONX', 'BROOKLYN', 'MANHATTAN', 'QUEENS', 'STATEN ISLAND',
               'UNKNOWN', 'UNSPECIFIED', 'N/A', 'NA', 'NULL'))
        FROM crashes
        WHERE crash_date >= DATE '2013-01-01' AND crash_date < ?::DATE
        """,
        [final_end_exclusive],
    ).fetchone()
    final_brooklyn_count = con.execute(
        "SELECT COUNT(*) FROM crashes WHERE crash_date >= DATE '2013-01-01' AND crash_date < ?::DATE AND upper(trim(borough)) = 'BROOKLYN'",
        [final_end_exclusive],
    ).fetchone()[0]
    add(f"final_period_years_2013_through_{final_end_year}_rows_before_borough_filter", final_pre_filter)
    add(f"final_period_years_2013_through_{final_end_year}_borough_missing_before_filter", final_borough_quality[0])
    add(f"final_period_years_2013_through_{final_end_year}_borough_unrecognized_before_filter", final_borough_quality[1])
    add(f"final_period_years_2013_through_{final_end_year}_brooklyn_population_rows", final_brooklyn_count)

    pop_count = con.execute(
        """
        SELECT COUNT(*) FROM crashes
        WHERE crash_date >= DATE '2013-01-01'
          AND crash_date < make_date(?, 1, 1)
          AND upper(trim(borough)) = 'BROOKLYN'
        """,
        [max_year + 1],
    ).fetchone()[0]
    add("brooklyn_population_rows_2013_through_latest", pop_count)

    for year in years:
        start = f"{year}-01-01"
        next_year = f"{year + 1}-01-01"
        count = con.execute(
            """
            SELECT COUNT(*) FROM crashes
            WHERE crash_date >= ?::DATE AND crash_date < ?::DATE
              AND upper(trim(borough)) = 'BROOKLYN'
            """,
            [start, next_year],
        ).fetchone()[0]
        add(f"brooklyn_population_rows_{year}", count)
        date_span = con.execute(
            "SELECT MIN(crash_date), MAX(crash_date), COUNT(*) FROM crashes WHERE crash_date >= ?::DATE AND crash_date < ?::DATE",
            [start, next_year],
        ).fetchone()
        add(f"all_boroughs_date_span_{year}", f"{date_span[0]} to {date_span[1]} ({date_span[2]} rows)")
        partial = date_span[0] is None or str(date_span[0]) > start or str(date_span[1]) < f"{year}-12-31"
        add(f"calendar_boundary_coverage_{year}", "partial or absent" if partial else "spans Jan 1 through Dec 31")

    for column in outcome_columns:
        nulls = con.execute(
            f"""
            SELECT COUNT(*) FROM crashes
            WHERE crash_date >= DATE '2013-01-01'
              AND crash_date < make_date(?, 1, 1)
              AND upper(trim(borough)) = 'BROOKLYN'
              AND {column} IS NULL
            """,
            [max_year + 1],
        ).fetchone()[0]
        add(f"{column}_missing_rows_in_brooklyn_population", nulls)
        final_nulls = con.execute(
            f"""
            SELECT COUNT(*) FROM crashes
            WHERE crash_date >= DATE '2013-01-01' AND crash_date < ?::DATE
              AND upper(trim(borough)) = 'BROOKLYN' AND {column} IS NULL
            """,
            [final_end_exclusive],
        ).fetchone()[0]
        add(f"{column}_missing_rows_in_final_brooklyn_population_2013_through_{final_end_year}", final_nulls)

    with (OUT / f"check_{option_id}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)

print(f"Checked 2013 through {max_year} for both plans.")
