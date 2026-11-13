import csv
import json
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
SOURCE = (ROOT / "data" / "crashes.parquet").as_posix()
YEARS = range(2013, 2026)

con = duckdb.connect()
con.execute("SET preserve_insertion_order = false")
results = {}

for option_id in (1, 2, 3):
    plan = json.loads((OUT / f"plan_{option_id}.json").read_text())
    output_rows = []

    # Only crash_date and the motorist-deaths field named in the plan are read.
    con.execute(
        "CREATE OR REPLACE TEMP VIEW scoped AS "
        "SELECT crash_date, number_of_motorist_killed "
        f"FROM read_parquet('{SOURCE}') "
        "WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'"
    )
    overall_rows = con.execute("SELECT COUNT(*) FROM scoped").fetchone()[0]
    output_rows.append(("source crash rows in planned years (before outcome classification)", overall_rows))

    annual = con.execute(
        "SELECT YEAR(crash_date) AS yr, COUNT(*) AS rows, "
        "MIN(crash_date) AS first_date, MAX(crash_date) AS last_date, "
        "COUNT(*) FILTER (WHERE number_of_motorist_killed IS NULL) AS missing_motorist_deaths "
        "FROM scoped GROUP BY yr ORDER BY yr"
    ).fetchall()
    present_years = {row[0] for row in annual}
    for year in YEARS:
        item = next((row for row in annual if row[0] == year), None)
        base_n = item[1] if item else 0
        missing_n = item[4] if item else 0
        if option_id == 3:
            used_n = base_n - missing_n
            output_rows.append((f"year {year}: rows in final planned population (known motorist-deaths field)", used_n))
        else:
            output_rows.append((f"year {year}: rows in source population", base_n))
        output_rows.append((f"year {year}: motorist-deaths field missing rows in source population", missing_n))
        if item:
            output_rows.append((f"year {year}: first and last crash_date observed", f"{item[2]} to {item[3]}"))
        else:
            output_rows.append((f"year {year}: first and last crash_date observed", "no rows"))

    # A row in this year-filtered population necessarily has a non-null date;
    # null dates cannot be assigned to any requested year and are not read here.
    output_rows.append(("crash_date missing rows in planned-year population", 0))

    date_defaults = con.execute(
        "SELECT COUNT(*) FROM scoped WHERE crash_date IN "
        "(DATE '1900-01-01', DATE '1970-01-01', DATE '0001-01-01')"
    ).fetchone()[0]
    output_rows.append(("crash_date rows at checked sentinel dates in planned years", date_defaults))

    if option_id == 3:
        for year in YEARS:
            item = next((row for row in annual if row[0] == year), None)
            missing_n = item[4] if item else 0
            output_rows.append((f"year {year}: source rows excluded for missing motorist-deaths field", missing_n))

    with (OUT / f"check_{option_id}.csv").open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["fact", "value"])
        writer.writerows(output_rows)

    results[option_id] = {"annual": annual, "source_rows": overall_rows, "date_defaults": date_defaults}

print(json.dumps(results, default=str))
