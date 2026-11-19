import csv
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
YEARS = range(2013, 2026)
source = str(ROOT / "data" / "crashes.parquet").replace("'", "''")
con = duckdb.connect()
con.execute(f"CREATE VIEW crashes AS SELECT crash_date, number_of_motorist_killed FROM read_parquet('{source}')")

facts = []
for plan_id in (1, 2):
    rows = con.execute(
        """
        SELECT count(*) AS n, min(crash_date), max(crash_date)
        FROM crashes
        WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
        """
    ).fetchone()
    facts.append(("plan_population_rows_2013_2025", rows[0]))
    for year in YEARS:
        n, first_date, last_date = con.execute(
            """
            SELECT count(*), min(crash_date), max(crash_date)
            FROM crashes
            WHERE crash_date >= ? AND crash_date < ?
            """,
            [f"{year}-01-01", f"{year + 1}-01-01"],
        ).fetchone()
        facts.extend(
            [
                (f"rows_{year}", n),
                (f"first_crash_date_{year}", str(first_date) if first_date else ""),
                (f"last_crash_date_{year}", str(last_date) if last_date else ""),
            ]
        )

    # These are exactly the planned date-year cohort rows. A typed DATE and
    # typed integer cannot contain empty/unknown text values.
    date_checks = con.execute(
        """
        SELECT
          count(*) FILTER (WHERE crash_date IS NULL),
          count(*) FILTER (WHERE crash_date = DATE '1970-01-01')
        FROM crashes
        WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
        """
    ).fetchone()
    motorist_missing = con.execute(
        """
        SELECT count(*) FILTER (WHERE number_of_motorist_killed IS NULL)
        FROM crashes
        WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
        """
    ).fetchone()[0]
    facts.extend(
        [
            ("crash_date_missing_within_plan_population", date_checks[0]),
            ("crash_date_default_1970_01_01_within_plan_population", date_checks[1]),
            ("number_of_motorist_killed_missing_within_plan_population", motorist_missing),
            ("typed_fields_textual_empty_or_unknown_values", "not representable in DATE/INTEGER schema"),
            ("outcome_value_frequency_counts", "not computed; outcome values are not tabulated in this check"),
        ]
    )

    with (OUT / f"check_{plan_id}.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)
    facts = []
