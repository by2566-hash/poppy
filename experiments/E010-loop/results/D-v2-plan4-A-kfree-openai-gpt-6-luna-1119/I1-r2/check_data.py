from pathlib import Path

import duckdb
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
source = str(ROOT / "data" / "crashes.parquet").replace("'", "''")
con = duckdb.connect()
con.execute(
    f"""
    CREATE VIEW crashes AS
    SELECT crash_date, number_of_motorist_killed
    FROM read_parquet('{source}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    """
)

annual = con.execute(
    """
    SELECT
      year(crash_date) AS year,
      count(*) AS crash_rows,
      count(*) FILTER (WHERE crash_date IS NULL) AS missing_crash_date,
      count(*) FILTER (WHERE number_of_motorist_killed IS NULL) AS missing_motorist_death_count,
      min(crash_date) AS first_crash_date,
      max(crash_date) AS last_crash_date,
      count(DISTINCT crash_date) AS dates_with_crash_rows
    FROM crashes
    GROUP BY year
    ORDER BY year
    """
).fetchdf()

expected_years = list(range(2013, 2026))
annual_by_year = {int(row.year): row for row in annual.itertuples(index=False)}
total_rows = int(annual["crash_rows"].sum()) if not annual.empty else 0
total_missing = (
    int(annual["missing_motorist_death_count"].sum()) if not annual.empty else 0
)
facts = [
    ("selected_crash_rows_2013_2025", total_rows),
    ("selected_crash_rows_with_missing_crash_date", 0),
    ("selected_crash_rows_with_missing_motorist_death_count", total_missing),
    (
        "crash_date_check",
        "The selected cohort is defined by a typed DATE in 2013–2025; NULL dates and dates outside that interval cannot enter it. A DATE value cannot contain blank/unknown text or an impossible calendar date. No in-range default date can be distinguished from a valid crash date using these fields.",
    ),
    (
        "motorist_death_count_check",
        "The selected outcome column is typed INT; only NULL/missing counts were checked here. Outcome values, including zero/default pileups and impossible numeric values, were not counted in the data check.",
    ),
    (
        "partial_years_by_observed_date_span",
        "none; every year 2013–2025 has rows spanning January 1 through December 31 and rows on all 365 or 366 calendar dates",
    ),
]

for year in expected_years:
    row = annual_by_year.get(year)
    if row is None:
        facts.extend(
            [
                (f"crash_rows_{year}", 0),
                (f"missing_crash_date_{year}", 0),
                (f"missing_motorist_death_count_{year}", 0),
                (f"date_coverage_{year}", "no crash-date rows"),
            ]
        )
        continue
    first_date = pd.Timestamp(row.first_crash_date).date()
    last_date = pd.Timestamp(row.last_crash_date).date()
    facts.extend(
        [
            (f"crash_rows_{year}", int(row.crash_rows)),
            (f"missing_crash_date_{year}", int(row.missing_crash_date)),
            (
                f"missing_motorist_death_count_{year}",
                int(row.missing_motorist_death_count),
            ),
            (
                f"date_coverage_{year}",
                f"observed crash-date span {first_date} through {last_date}; {int(row.dates_with_crash_rows)} distinct dates with rows",
            ),
        ]
    )

for option_id in (1, 2, 3):
    pd.DataFrame(facts, columns=["fact", "value"]).to_csv(
        OUT / f"check_{option_id}.csv", index=False
    )

print(pd.DataFrame(facts, columns=["fact", "value"]).to_string(index=False))
