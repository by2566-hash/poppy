import duckdb
import pandas as pd

source = "data/crashes.parquet"
con = duckdb.connect()
population = "crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'"

counts = con.execute(
    f"""
    SELECT YEAR(crash_date) AS year, COUNT(*) AS crash_rows,
           MIN(crash_date) AS first_date, MAX(crash_date) AS last_date
    FROM read_parquet('{source}')
    WHERE {population}
    GROUP BY YEAR(crash_date)
    ORDER BY year
    """
).fetchdf()
total_rows = con.execute(
    f"SELECT COUNT(*) FROM read_parquet('{source}') WHERE {population}"
).fetchone()[0]
unknown_dates = con.execute(
    f"SELECT COUNT(*) FROM read_parquet('{source}') WHERE crash_date IS NULL"
).fetchone()[0]
outcome_check = con.execute(
    f"""
    SELECT COUNT(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS outcome_null,
           COUNT(*) FILTER (WHERE number_of_pedestrians_killed < 0) AS outcome_negative,
           COUNT(*) FILTER (WHERE number_of_pedestrians_killed = 0) AS outcome_zero
    FROM read_parquet('{source}')
    WHERE {population}
    """
).fetchdf().iloc[0]

facts = [
    ("crashes with crash_date in 2013-2025", int(total_rows)),
    ("rows with missing crash_date (cannot assign to a year)", int(unknown_dates)),
]
for row in counts.itertuples(index=False):
    facts.append((f"{row.year} crash rows", int(row.crash_rows)))
    facts.append((f"{row.year} observed date range", f"{row.first_date} to {row.last_date}"))
facts.extend([
    ("2013-2025 rows with missing number_of_pedestrians_killed", int(outcome_check.outcome_null)),
    ("2013-2025 rows with impossible negative number_of_pedestrians_killed", int(outcome_check.outcome_negative)),
    ("2013-2025 rows with number_of_pedestrians_killed equal to zero", int(outcome_check.outcome_zero)),
])
pd.DataFrame(facts, columns=["fact", "value"]).to_csv("out/check_2.csv", index=False)
