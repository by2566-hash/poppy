import csv
from pathlib import Path

import duckdb


con = duckdb.connect()
source = 'read_parquet("data/crashes.parquet")'
specs = {
    1: ["number_of_pedestrians_injured"],
    2: ["number_of_pedestrians_killed"],
    3: ["number_of_pedestrians_injured", "number_of_pedestrians_killed"],
}
out = Path("out")

for option_id, outcome_columns in specs.items():
    facts = []

    def add(fact, value):
        facts.append((fact, str(value)))

    years = con.execute(
        f"""
        SELECT year(crash_date)::INT AS yr,
               count(*)::BIGINT AS n,
               min(crash_date)::VARCHAR AS first_date,
               max(crash_date)::VARCHAR AS last_date
        FROM {source}
        WHERE upper(trim(borough)) = ?
          AND crash_date >= CAST(? AS DATE)
        GROUP BY yr
        ORDER BY yr
        """,
        ["BROOKLYN", "2013-01-01"],
    ).fetchall()
    complete_years = [
        row for row in years
        if row[2] == f"{row[0]}-01-01" and row[3] == f"{row[0]}-12-31"
    ]
    add(
        "Brooklyn crash rows with crash_date in 2013 onward (before outcome-field exclusions)",
        sum(row[1] for row in years),
    )
    add(
        "Brooklyn crash rows in 2013 onward years whose observed dates reach both Jan 1 and Dec 31",
        sum(row[1] for row in complete_years),
    )
    add(
        "Year selection based on observed date range",
        "2013 onward screened; years with observed dates not reaching both Jan 1 and Dec 31 flagged as partial and to be excluded",
    )
    for year, count, first_date, last_date in years:
        add(f"Brooklyn crash rows in {year}", count)
        add(
            f"Observed crash_date range in Brooklyn for {year}",
            f"{first_date} through {last_date}",
        )
        add(
            f"Calendar-year coverage note for {year}",
            "observed dates do not span the full calendar year"
            if first_date != f"{year}-01-01" or last_date != f"{year}-12-31"
            else "observed dates reach both calendar-year boundaries; continuous coverage not established",
        )

    borough_missing = con.execute(
        f"""
        SELECT count(*) FILTER (WHERE borough IS NULL)::BIGINT,
               count(*) FILTER (WHERE borough IS NOT NULL AND trim(borough) = '')::BIGINT,
               count(*) FILTER (
                   WHERE upper(trim(borough)) IN ('UNKNOWN', 'UNSPECIFIED', 'N/A', 'NULL')
               )::BIGINT
        FROM {source}
        WHERE crash_date >= CAST(? AS DATE)
        """,
        ["2013-01-01"],
    ).fetchone()
    add("2013-onward crash rows with borough NULL (not assignable to Brooklyn)", borough_missing[0])
    add("2013-onward crash rows with borough blank", borough_missing[1])
    add("2013-onward crash rows with borough labeled unknown/unspecified", borough_missing[2])
    add("Rows with borough missing within normalized Brooklyn population", 0)

    undated_brooklyn = con.execute(
        f"""
        SELECT count(*)::BIGINT
        FROM {source}
        WHERE upper(trim(borough)) = 'BROOKLYN'
          AND crash_date IS NULL
        """
    ).fetchone()[0]
    add("Brooklyn-labeled rows with missing crash_date (cannot be assigned to a year)", undated_brooklyn)

    invalid_borough = con.execute(
        f"""
        SELECT count(*)::BIGINT
        FROM {source}
        WHERE crash_date >= CAST(? AS DATE)
          AND borough IS NOT NULL
          AND upper(trim(borough)) NOT IN (
              'BRONX', 'BROOKLYN', 'MANHATTAN', 'QUEENS', 'STATEN ISLAND'
          )
        """,
        ["2013-01-01"],
    ).fetchone()[0]
    add("2013-onward rows with nonmissing borough outside the five NYC borough labels", invalid_borough)

    for column in outcome_columns:
        missing_by_year = con.execute(
            f"""
            SELECT year(crash_date)::INT,
                   count(*) FILTER (WHERE {column} IS NULL)::BIGINT
            FROM {source}
            WHERE upper(trim(borough)) = ?
              AND crash_date >= CAST(? AS DATE)
            GROUP BY 1
            ORDER BY 1
            """,
            ["BROOKLYN", "2013-01-01"],
        ).fetchall()
        complete_year_set = {row[0] for row in complete_years}
        add(
            f"Rows with {column} missing among Brooklyn crashes in complete observed 2013-onward years",
            sum(count for year, count in missing_by_year if year in complete_year_set),
        )
        for year, count in missing_by_year:
            add(f"Rows with {column} missing in Brooklyn crashes in {year}", count)

    with (out / f"check_{option_id}.csv").open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)

    print(
        f"check_{option_id}: Brooklyn rows={sum(row[1] for row in years)}, "
        f"observed years={years[0][0]}-{years[-1][0]}, "
        f"rows in years whose observed dates reach both endpoints={sum(row[1] for row in complete_years)}; "
        f"last dates={years[-1][2]}..{years[-1][3]}"
    )
