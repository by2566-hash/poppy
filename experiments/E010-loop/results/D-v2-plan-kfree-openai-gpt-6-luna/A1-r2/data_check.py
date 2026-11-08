from pathlib import Path
import duckdb
import pandas as pd

DATA = "data/crashes.parquet"
OUT = Path("out")
OUT.mkdir(exist_ok=True)

con = duckdb.connect()
con.execute(f"CREATE VIEW crashes AS SELECT crash_date, borough, number_of_pedestrians_injured, number_of_pedestrians_killed FROM read_parquet('{DATA}')")

# Coverage boundary metadata uses only crash_date in the planned year window.
coverage = con.execute("""
    SELECT MIN(crash_date) AS first_date, MAX(crash_date) AS last_date
    FROM crashes
    WHERE crash_date >= DATE '2013-01-01'
""").fetchone()
last_date = pd.Timestamp(coverage[1]) if coverage[1] is not None else None
latest_year = last_date.year if last_date is not None else None
latest_year_complete = bool(last_date is not None and last_date.month == 12 and last_date.day == 31)

# The check population is all Brooklyn crash rows dated 2013 or later.
yearly = con.execute("""
    SELECT YEAR(crash_date) AS year,
           COUNT(*) AS population_rows,
           COUNT(*) FILTER (WHERE number_of_pedestrians_injured IS NULL) AS ped_injured_missing,
           COUNT(*) FILTER (WHERE number_of_pedestrians_injured < 0) AS ped_injured_impossible,
           COUNT(*) FILTER (WHERE number_of_pedestrians_injured = 0) AS ped_injured_zero,
           COUNT(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS ped_killed_missing,
           COUNT(*) FILTER (WHERE number_of_pedestrians_killed < 0) AS ped_killed_impossible,
           COUNT(*) FILTER (WHERE number_of_pedestrians_killed = 0) AS ped_killed_zero,
           COUNT(*) FILTER (WHERE borough IS NULL OR TRIM(borough) = '' OR LOWER(TRIM(borough)) IN ('unknown', 'unspecified', 'n/a', 'na')) AS borough_missing_or_unknown,
           COUNT(*) FILTER (WHERE crash_date IS NULL) AS crash_date_missing
    FROM crashes
    WHERE UPPER(TRIM(borough)) = 'BROOKLYN' AND crash_date >= DATE '2013-01-01'
    GROUP BY YEAR(crash_date)
    ORDER BY year
""").df()

# Audit missing borough assignment in the dated source rows because those rows
# cannot be reliably assigned to the planned Brooklyn population.
borough_audit = con.execute("""
    SELECT YEAR(crash_date) AS year, COUNT(*) AS dated_rows,
           COUNT(*) FILTER (WHERE borough IS NULL OR TRIM(borough) = '' OR LOWER(TRIM(borough)) IN ('unknown', 'unspecified', 'n/a', 'na')) AS borough_missing_or_unknown
    FROM crashes
    WHERE crash_date >= DATE '2013-01-01'
    GROUP BY YEAR(crash_date)
    ORDER BY year
""").df()

for option_id in (1, 2):
    facts = [("coverage_first_date_2013_plus", str(pd.Timestamp(coverage[0]).date()) if coverage[0] is not None else "none")]
    facts.append(("coverage_last_date_2013_plus", str(last_date.date()) if last_date is not None else "none"))
    facts.append(("latest_calendar_year", str(latest_year) if latest_year is not None else "none"))
    facts.append(("latest_calendar_year_complete_by_date_boundary", str(latest_year_complete).lower()))
    facts.append(("borough_filter_normalization", "case-insensitive exact Brooklyn match after trimming whitespace"))
    for row in borough_audit.itertuples(index=False):
        facts.append((f"all_boroughs_dated_source_rows_{row.year}", int(row.dated_rows)))
        facts.append((f"all_boroughs_borough_missing_or_unknown_{row.year}", int(row.borough_missing_or_unknown)))
        share = row.borough_missing_or_unknown / row.dated_rows if row.dated_rows else 0
        facts.append((f"all_boroughs_borough_missing_or_unknown_share_{row.year}", round(share, 6)))
    if not yearly.empty:
        facts.append(("Brooklyn_population_rows_2013_plus_total", int(yearly.population_rows.sum())))
    for row in yearly.itertuples(index=False):
        facts.append((f"Brooklyn_population_rows_{row.year}", int(row.population_rows)))
        for column, missing, impossible, zero in (
            ("number_of_pedestrians_injured", row.ped_injured_missing, row.ped_injured_impossible, row.ped_injured_zero),
            ("number_of_pedestrians_killed", row.ped_killed_missing, row.ped_killed_impossible, row.ped_killed_zero),
        ):
            facts.append((f"{column}_missing_{row.year}", int(missing)))
            facts.append((f"{column}_impossible_negative_{row.year}", int(impossible)))
            facts.append((f"{column}_zero_{row.year}_valid_zero", int(zero)))
        facts.append((f"borough_missing_or_unknown_{row.year}", int(row.borough_missing_or_unknown)))
        facts.append((f"crash_date_missing_{row.year}", int(row.crash_date_missing)))
    pd.DataFrame(facts, columns=["fact", "value"]).to_csv(OUT / f"check_{option_id}.csv", index=False)
