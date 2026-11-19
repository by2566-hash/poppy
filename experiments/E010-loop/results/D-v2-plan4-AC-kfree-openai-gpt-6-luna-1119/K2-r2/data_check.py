from pathlib import Path

import duckdb
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
PARQUET = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"
START_YEAR = 2013
END_YEAR = 2025

con = duckdb.connect()
con.execute(f"CREATE VIEW crashes AS SELECT crash_date FROM read_parquet('{PARQUET.as_posix()}')")

# crash_date is the only filter/grouping column in either initial plan. The
# missing/sentinel checks are before the year filter, as required for a filter
# column; year counts and coverage summaries are restricted to planned years.
source = con.execute(
    """
    SELECT
      count(*) AS source_rows,
      count(*) FILTER (WHERE crash_date IS NULL) AS missing_crash_date,
      count(*) FILTER (WHERE crash_date IN
        (DATE '0001-01-01', DATE '1900-01-01', DATE '1970-01-01', DATE '9999-12-31'))
        AS sentinel_crash_date
    FROM crashes
    """
).fetchone()

year_rows = con.execute(
    """
    SELECT year(crash_date) AS year, count(*) AS rows,
           min(crash_date) AS first_observed_date,
           max(crash_date) AS last_observed_date
    FROM crashes
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year(crash_date)
    ORDER BY year
    """
).df()

year_lookup = {int(row.year): row for row in year_rows.itertuples(index=False)}
facts = [
    ("Source rows checked for crash_date filter quality", int(source[0])),
    ("Rows with missing crash_date before year filter", int(source[1])),
    ("Rows with common default/sentinel crash_date (0001-01-01, 1900-01-01, 1970-01-01, 9999-12-31)", int(source[2])),
    ("Impossible crash_date values", "0 representable as DuckDB DATE; source column is typed DATE"),
    ("Plan years", f"{START_YEAR}-{END_YEAR} inclusive"),
    ("Valid dated crash rows in plan years", int(year_rows["rows"].sum()) if not year_rows.empty else 0),
    ("Dated rows outside plan years", int(source[0] - source[1] - (year_rows["rows"].sum() if not year_rows.empty else 0))),
]

for year in range(START_YEAR, END_YEAR + 1):
    row = year_lookup.get(year)
    if row is None:
        facts.append((f"{year} crash rows", 0))
        facts.append((f"{year} observed date coverage", "no dated rows"))
        facts.append((f"{year} partial-year flag", "yes — no observed dates"))
        continue
    first = pd.Timestamp(row.first_observed_date).date()
    last = pd.Timestamp(row.last_observed_date).date()
    facts.append((f"{year} crash rows", int(row.rows)))
    facts.append((f"{year} observed date coverage", f"{first} through {last}"))
    partial = first != pd.Timestamp(year=year, month=1, day=1).date() or last != pd.Timestamp(year=year, month=12, day=31).date()
    facts.append((f"{year} partial-year flag", "yes" if partial else "no (observed date range reaches both year boundaries)"))

for option_id in (1, 2):
    plan_facts = list(facts)
    if option_id == 2 and not year_rows.empty:
        first = min(row.first_observed_date for row in year_rows.itertuples(index=False))
        last = max(row.last_observed_date for row in year_rows.itertuples(index=False))
        weekdays = pd.date_range(first, last, freq="D").day_name().value_counts()
        facts_by_day = {day: int(weekdays.get(day, 0)) for day in
                        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
        plan_facts.extend([
            ("Inclusive observed date span for calendar-date denominator", f"{first} through {last}"),
            ("Calendar dates in denominator by weekday", "; ".join(f"{day}: {count}" for day, count in facts_by_day.items())),
        ])
    pd.DataFrame(plan_facts, columns=["fact", "value"]).to_csv(OUT / f"check_{option_id}.csv", index=False)

con.close()
