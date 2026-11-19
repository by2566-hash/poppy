from pathlib import Path

import duckdb
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PARQUET = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"
YEARS = list(range(2013, 2026))
DATE_COLUMN = "crash_date"
DEATH_COLUMNS = ["number_of_motorist_killed", "number_of_cyclist_killed"]

con = duckdb.connect()
yearly = con.execute(
    f"""
    SELECT EXTRACT(YEAR FROM {DATE_COLUMN})::INTEGER AS year,
           COUNT(*) AS crash_rows,
           MIN({DATE_COLUMN}) AS first_date,
           MAX({DATE_COLUMN}) AS last_date,
           COUNT(*) FILTER (WHERE {DEATH_COLUMNS[0]} IS NULL) AS motorist_killed_missing,
           COUNT(*) FILTER (WHERE {DEATH_COLUMNS[1]} IS NULL) AS cyclist_killed_missing
    FROM read_parquet(?)
    WHERE {DATE_COLUMN} >= DATE '2013-01-01'
      AND {DATE_COLUMN} < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
    """,
    [str(PARQUET)],
).df()

facts = []
total_rows = int(yearly["crash_rows"].sum())
facts.append(("plan population rows dated 2013-2025", total_rows))

by_year = {int(row.year): row for row in yearly.itertuples(index=False)}
for year in YEARS:
    row = by_year.get(year)
    if row is None:
        facts.append((f"crash rows in {year}", 0))
        facts.append((f"date span observed in {year}", "no rows"))
        facts.append((f"year coverage status {year}", "no rows; coverage unavailable"))
        for col, label in zip(DEATH_COLUMNS, ("motorist deaths", "cyclist deaths")):
            facts.append((f"{label}: rows with missing value in {year}", 0))
        continue

    facts.append((f"crash rows in {year}", int(row.crash_rows)))
    first_date, last_date = pd.Timestamp(row.first_date).date(), pd.Timestamp(row.last_date).date()
    facts.append((f"date span observed in {year}", f"{first_date} through {last_date}"))
    partial = first_date > pd.Timestamp(year=year, month=1, day=1).date() or last_date < pd.Timestamp(year=year, month=12, day=31).date()
    status = "partial date span observed" if partial else "Jan 1-Dec 31 observed; completeness beyond date span cannot be verified"
    facts.append((f"year coverage status {year}", status))
    facts.append((f"crash_date missing/invalid encodings in selected population, {year}", 0))
    for column, label in zip(DEATH_COLUMNS, ("motorist deaths", "cyclist deaths")):
        facts.append((f"{label}: rows with missing value in {year}", int(getattr(row, column.replace("number_of_", "").replace("_killed", "_killed_missing")))))

facts.append(("crash_date type/validity", "DATE typed; non-NULL values cannot be empty strings, unknown words, or impossible dates; no date sentinel is specified by the schema"))
facts.append(("crash_date missing rows inside selected population", 0))

for option_id in (1, 2):
    pd.DataFrame(facts, columns=["fact", "value"]).to_csv(OUT / f"check_{option_id}.csv", index=False)

con.close()
