from pathlib import Path

import duckdb
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
PARQUET = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"
START_YEAR = 2013
END_YEAR = 2025
DEATH_COLUMNS = ["number_of_motorist_killed", "number_of_cyclist_killed"]

con = duckdb.connect()
parquet_sql_path = str(PARQUET).replace("'", "''")
con.execute(
    "CREATE VIEW crashes AS SELECT crash_date, number_of_motorist_killed, "
    f"number_of_cyclist_killed FROM read_parquet('{parquet_sql_path}')"
)

# The selected population is exactly rows with a valid DATE in the planned
# calendar-year interval. Do not inspect outcome values except for NULL counts.
population = con.execute(
    """
    SELECT crash_date, EXTRACT(YEAR FROM crash_date)::INTEGER AS year,
           number_of_motorist_killed, number_of_cyclist_killed
    FROM crashes
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    """
).df()

facts = [
    ("population rows in planned years", str(len(population))),
    (
        "crash_date missing/impossible/default within selected population",
        "0 (NULL and invalid dates cannot satisfy the typed DATE interval filter; "
        "all selected dates are valid dates in 2013-2025)",
    ),
]

for year in range(START_YEAR, END_YEAR + 1):
    rows = population.loc[population["year"] == year]
    facts.append((f"rows in {year}", str(len(rows))))
    if len(rows):
        min_date = rows["crash_date"].min().date().isoformat()
        max_date = rows["crash_date"].max().date().isoformat()
        start = f"{year}-01-01"
        finish = f"{year}-12-31"
        partial = min_date != start or max_date != finish
        facts.append((f"date coverage in {year}", f"{min_date} through {max_date}"))
        facts.append((f"{year} appears partial by observed date boundaries", str(partial).lower()))
    else:
        facts.append((f"date coverage in {year}", "no rows"))
        facts.append((f"{year} appears partial by observed date boundaries", "true (no rows)"))

for column in DEATH_COLUMNS:
    missing = int(population[column].isna().sum())
    facts.append((f"{column} missing rows", str(missing)))

check = pd.DataFrame(facts, columns=["fact", "value"])
for plan_id in (1, 2):
    check.to_csv(OUT / f"check_{plan_id}.csv", index=False)

print(check.to_string(index=False))
