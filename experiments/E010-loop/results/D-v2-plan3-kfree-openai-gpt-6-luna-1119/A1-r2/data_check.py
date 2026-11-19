import csv
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
DATA = str(ROOT / "data" / "crashes.parquet")
OUT = Path(__file__).resolve().parent
db = duckdb.connect()

# Initial plans use Brooklyn crashes dated 2013 or later. The date audit
# identifies full calendar years without examining injury/death values.
source_years = db.execute(
    """
    SELECT year(crash_date) AS yr, count(*) AS rows,
           min(crash_date) AS first_date, max(crash_date) AS last_date
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
    GROUP BY yr ORDER BY yr
    """,
    [DATA],
).fetchall()

brooklyn_null_dates = db.execute(
    """
    SELECT count(*) FROM read_parquet(?)
    WHERE borough = 'BROOKLYN' AND crash_date IS NULL
    """,
    [DATA],
).fetchone()[0]

source = {row[0]: row for row in source_years}
def write_check(option_id, facts):
    with (OUT / f"check_{option_id}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)

planned_fields = {
    1: ["number_of_pedestrians_injured", "number_of_pedestrians_killed"],
    2: ["number_of_pedestrians_injured", "number_of_pedestrians_killed"],
    3: ["number_of_pedestrians_killed"],
}

for option_id, outcome_fields in planned_fields.items():
    missing_sql = ", ".join(
        f"count(*) FILTER (WHERE {field} IS NULL) AS missing_{i}"
        for i, field in enumerate(outcome_fields)
    )
    combined_missing_sql = " OR ".join(f"{field} IS NULL" for field in outcome_fields)
    brooklyn_years = db.execute(
        f"""
        SELECT year(crash_date) AS yr, count(*) AS rows, {missing_sql},
               count(*) FILTER (WHERE {combined_missing_sql}) AS any_outcome_missing
        FROM read_parquet(?)
        WHERE borough = 'BROOKLYN'
          AND crash_date >= DATE '2013-01-01'
        GROUP BY yr ORDER BY yr
        """,
        [DATA],
    ).fetchall()
    selected = {row[0]: row for row in brooklyn_years}
    years = [yr for yr in sorted(source) if yr in selected]
    full_years = []
    partial = []
    for yr in years:
        first, last = source[yr][2], source[yr][3]
        expected_first = f"{yr}-01-01"
        expected_last = f"{yr}-12-31"
        if str(first) == expected_first and str(last) == expected_last:
            full_years.append(yr)
        else:
            partial.append((yr, first, last))

    full_population_rows = sum(selected[yr][1] for yr in full_years)
    full_missing = [sum(selected[yr][2 + i] for yr in full_years) for i in range(len(outcome_fields))]
    full_any_missing = sum(selected[yr][2 + len(outcome_fields)] for yr in full_years)
    facts = [
        ("Brooklyn rows with missing crash_date (excluded; no year can be assigned)", brooklyn_null_dates),
        ("full calendar years represented in the source from 2013 onward", ", ".join(map(str, full_years))),
        ("partial calendar years represented in the source from 2013 onward (year: first date to last date)", "; ".join(f"{yr}: {first} to {last}" for yr, first, last in partial) or "none"),
        ("Brooklyn population rows across full years used (2013 through latest full year)", full_population_rows),
        *[(f"rows in that full-year population with {field} missing", full_missing[i]) for i, field in enumerate(outcome_fields)],
        ("rows in that full-year population with any planned pedestrian outcome field missing", full_any_missing),
    ]
    for yr in years:
        n = selected[yr][1]
        facts.append((f"{yr} Brooklyn candidate rows with crash_date in that year", n))
        facts.append((f"{yr} Brooklyn rows with missing borough among selected population", 0))
        facts.append((f"{yr} Brooklyn rows with missing crash_date among selected population", 0))
        for i, field in enumerate(outcome_fields):
            facts.append((f"{yr} Brooklyn rows with {field} missing", selected[yr][2 + i]))
        facts.extend([
            (f"{yr} Brooklyn rows with any planned pedestrian outcome field missing", selected[yr][2 + len(outcome_fields)]),
            (f"{yr} source date coverage", f"{source[yr][2]} to {source[yr][3]}"),
        ])
    facts.extend([
        ("borough filter value", "BROOKLYN; exact borough match"),
        ("borough missing/unknown/default-value rows inside Brooklyn population", 0),
        ("crash_date group value", "calendar year; NULL dates excluded and counted above"),
        ("planned pedestrian outcome fields are numeric INT; missingness check is NULL count only", ", ".join(outcome_fields)),
    ])
    write_check(option_id, facts)
    print(f"Option {option_id} full years: {full_years}; partial years: {partial}")
    print(f"Option {option_id} Brooklyn rows by year and planned-field missingness: {brooklyn_years}")
print("Brooklyn rows with missing crash_date:", brooklyn_null_dates)
