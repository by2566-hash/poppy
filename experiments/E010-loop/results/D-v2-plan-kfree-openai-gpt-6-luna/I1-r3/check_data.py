from pathlib import Path

import duckdb
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
PARQUET = ROOT / "data" / "crashes.parquet"
YEARS = range(2013, 2026)

# All three initial plans use exactly this crash-date population and the
# motorist-death field. This check intentionally computes no outcome totals.
con = duckdb.connect()
parquet_path = str(PARQUET).replace("'", "''")
con.execute(f"CREATE VIEW crashes AS SELECT crash_date, number_of_motorist_killed FROM read_parquet('{parquet_path}')")
rows = con.execute(
    """
    SELECT year(crash_date) AS year,
           count(*) AS crash_rows,
           min(crash_date) AS first_observed_date,
           max(crash_date) AS last_observed_date,
           count(*) FILTER (WHERE number_of_motorist_killed IS NULL) AS death_value_null,
           count(*) FILTER (WHERE number_of_motorist_killed < 0) AS death_value_impossible_negative,
           count(*) FILTER (WHERE number_of_motorist_killed = 0) AS death_value_zero
    FROM crashes
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
    """
).fetchdf()
global_dates = con.execute(
    "SELECT min(crash_date), max(crash_date) FROM crashes WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'"
).fetchone()
con.close()

by_year = {int(row.year): row for row in rows.itertuples(index=False)}
facts = []

def add(fact, value):
    facts.append({"fact": fact, "value": str(value)})


population_rows = int(rows["crash_rows"].sum()) if not rows.empty else 0
add("Population: crash rows with crash_date in 2013–2025 inclusive", population_rows)
add("Population rows with usable crash_date missing", 0)
add("Observed crash_date minimum in target years", global_dates[0])
add("Observed crash_date maximum in target years", global_dates[1])

for year in YEARS:
    row = by_year.get(year)
    n = int(row.crash_rows) if row is not None else 0
    add(f"{year}: crash rows in population", n)
    add(f"{year}: observed first and last crash_date", f"{row.first_observed_date} .. {row.last_observed_date}" if row is not None else "no rows")
    add(f"{year}: number_of_motorist_killed NULL rows", int(row.death_value_null) if row is not None else 0)
    add(f"{year}: number_of_motorist_killed impossible negative rows", int(row.death_value_impossible_negative) if row is not None else 0)
    add(f"{year}: number_of_motorist_killed zero rows (valid no-motorist-death value; checked for pile-up)", int(row.death_value_zero) if row is not None else 0)

first_date, last_date = global_dates
for year in YEARS:
    year_start = pd.Timestamp(year=year, month=1, day=1).date()
    year_end = pd.Timestamp(year=year, month=12, day=31).date()
    partial = first_date is None or first_date > year_start or last_date < year_end
    add(f"{year}: coverage boundary check (inferred from target-period min/max crash_date)", "partial or no rows" if partial else "within observed date bounds")

pd.DataFrame(facts).to_csv(OUT / "check_1.csv", index=False)
pd.DataFrame(facts).to_csv(OUT / "check_2.csv", index=False)
pd.DataFrame(facts).to_csv(OUT / "check_3.csv", index=False)
