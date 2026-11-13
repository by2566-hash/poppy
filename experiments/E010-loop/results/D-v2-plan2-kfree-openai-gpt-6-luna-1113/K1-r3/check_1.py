import duckdb
import pandas as pd


con = duckdb.connect()
data_path = "./data/crashes.parquet"

yearly = con.execute(
    """
    WITH by_year AS (
        SELECT
            EXTRACT(YEAR FROM crash_date)::INTEGER AS year,
            COUNT(*) AS crash_rows,
            COUNT(*) FILTER (WHERE crash_date IS NULL) AS missing_crash_date,
            COUNT(*) FILTER (WHERE number_of_pedestrians_killed IS NULL)
                AS missing_pedestrian_fatality_count,
            MIN(crash_date) AS first_crash_date,
            MAX(crash_date) AS last_crash_date
        FROM read_parquet(?)
        WHERE crash_date >= DATE '2013-01-01'
          AND crash_date < DATE '2026-01-01'
        GROUP BY year
    ), years AS (
        SELECT generate_series AS year
        FROM generate_series(2013, 2025)
    )
    SELECT
        years.year,
        COALESCE(by_year.crash_rows, 0) AS crash_rows,
        COALESCE(by_year.missing_crash_date, 0) AS missing_crash_date,
        COALESCE(by_year.missing_pedestrian_fatality_count, 0)
            AS missing_pedestrian_fatality_count,
        by_year.first_crash_date,
        by_year.last_crash_date
    FROM years
    LEFT JOIN by_year USING (year)
    ORDER BY years.year
    """,
    [data_path],
).df()

facts = []
facts.append(("population_rows_2013_2025", int(yearly["crash_rows"].sum())))
for row in yearly.itertuples(index=False):
    facts.append((f"crash_rows_{row.year}", int(row.crash_rows)))
    facts.append((f"missing_crash_date_{row.year}", int(row.missing_crash_date)))
    facts.append(
        (
            f"missing_number_of_pedestrians_killed_{row.year}",
            int(row.missing_pedestrian_fatality_count),
        )
    )
    facts.append((f"first_crash_date_{row.year}", str(row.first_crash_date or "none")))
    facts.append((f"last_crash_date_{row.year}", str(row.last_crash_date or "none")))

facts.extend(
    [
        ("crash_date_type", "DATE; NULL values cannot enter the planned date filter"),
        (
            "crash_date_impossible_or_default_within_population",
            "None identified: dates within the selected interval are valid DATE values; no default convention is specified in the data description",
        ),
        (
            "partial_year_assessment",
            "For each year, observed first and last crash dates are reported above; a year is temporally partial if its observed bounds do not span Jan 1–Dec 31. Bounds do not establish completeness between dates.",
        ),
    ]
)

pd.DataFrame(facts, columns=["fact", "value"]).to_csv("./out/check_1.csv", index=False)
