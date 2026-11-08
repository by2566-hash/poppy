from pathlib import Path

import duckdb
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
con = duckdb.connect()
parquet_path = str(ROOT / "data/crashes.parquet").replace("'", "''")
con.execute(f"CREATE VIEW crashes AS SELECT crash_date FROM read_parquet('{parquet_path}')")

source = con.execute(
    """
    SELECT count(*) AS source_rows,
           count(*) FILTER (WHERE crash_date IS NULL) AS null_crash_dates
    FROM crashes
    """
).fetchone()
population_rows = con.execute(
    """
    SELECT count(*) FROM crashes
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    """
).fetchone()[0]
year_rows = con.execute(
    """
    SELECT year(crash_date) AS year,
           count(*) AS rows,
           min(crash_date) AS first_observed_date,
           max(crash_date) AS last_observed_date
    FROM crashes
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY year(crash_date)
    ORDER BY year
    """
).fetchdf()
in_scope_dates = con.execute(
    """
    SELECT count(*) FILTER (WHERE crash_date IS NULL) AS null_dates,
           count(*) FILTER (WHERE crash_date IN (DATE '1900-01-01', DATE '1970-01-01')) AS common_sentinel_dates
    FROM crashes
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    """
).fetchone()

facts = [
    ("source_rows_all_dates", source[0]),
    ("rows_with_null_crash_date_unassignable_to_year", source[1]),
    ("population_rows_with_crash_date_in_2013_2025", population_rows),
    ("in_scope_null_crash_date_rows", in_scope_dates[0]),
    ("in_scope_common_sentinel_dates_1900_1970", in_scope_dates[1]),
]
for row in year_rows.itertuples(index=False):
    y = int(row.year)
    first_date = pd.Timestamp(row.first_observed_date).date().isoformat()
    last_date = pd.Timestamp(row.last_observed_date).date().isoformat()
    facts.extend(
        [
            (f"year_{y}_rows", int(row.rows)),
            (f"year_{y}_first_observed_crash_date", first_date),
            (f"year_{y}_last_observed_crash_date", last_date),
            (
                f"year_{y}_boundary_observation_check",
                f"first_is_jan_1={first_date == f'{y}-01-01'};last_is_dec_31={last_date == f'{y}-12-31'}",
            ),
        ]
    )

for option_id in (1, 2):
    pd.DataFrame(facts, columns=["fact", "value"]).to_csv(OUT / f"check_{option_id}.csv", index=False)

print(pd.DataFrame(facts, columns=["fact", "value"]).to_string(index=False))
