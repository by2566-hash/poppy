import csv
import json
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"

plans = [json.loads((OUT / f"plan_{i}.json").read_text()) for i in (1, 2, 3)]
con = duckdb.connect()

# Establish the plan's latest available calendar year using only the planned
# date grouping field. Null dates are checked separately in the Brooklyn rows.
coverage = con.execute(
    "SELECT min(crash_date), max(crash_date) FROM read_parquet(?) "
    "WHERE crash_date >= DATE '2013-01-01'",
    [str(DATA)],
).fetchone()
latest_year = coverage[1].year if coverage[1] else 2013
complete_year = latest_year if coverage[1] and coverage[1].month == 12 and coverage[1].day == 31 else latest_year - 1
start = "2013-01-01"
end = f"{complete_year}-12-31"

for plan in plans:
    pid = plan["id"]
    outcome_cols = (
        ["number_of_pedestrians_injured", "number_of_pedestrians_killed"]
        if pid == 1
        else ["number_of_pedestrians_killed"]
        if pid == 2
        else ["number_of_pedestrians_injured"]
    )
    cols = ["crash_date", "borough", *outcome_cols]
    select_cols = ", ".join(f'"{c}"' for c in cols)
    relation = f"read_parquet('{DATA.as_posix()}')"
    facts = []

    def add(fact, value):
        facts.append((fact, str(value)))

    # Rows in the plan's borough population and years, before outcome-cell
    # filtering; per-year counts disclose that analysis base.
    total = con.execute(
        f"SELECT count(*) FROM {relation} WHERE crash_date BETWEEN DATE '{start}' AND DATE '{end}' "
        "AND lower(trim(coalesce(borough, ''))) = 'brooklyn'"
    ).fetchone()[0]
    add("Brooklyn crash rows in plan years before outcome missing-value filter", total)
    annual = con.execute(
        f"SELECT year(crash_date), count(*) FROM {relation} "
        f"WHERE crash_date BETWEEN DATE '{start}' AND DATE '{end}' "
        "AND lower(trim(coalesce(borough, ''))) = 'brooklyn' "
        "GROUP BY 1 ORDER BY 1"
    ).fetchall()
    for year, count in annual:
        add(f"Brooklyn crash rows in {year} before outcome missing-value filter", count)

    # Filter-column quality is assessed before applying the borough filter,
    # within the plan's years. Valid NYC borough names are retained as expected.
    borough_quality = con.execute(
        f"SELECT count(*) FILTER (WHERE borough IS NULL), "
        f"count(*) FILTER (WHERE borough IS NOT NULL AND trim(borough) = ''), "
        f"count(*) FILTER (WHERE lower(trim(coalesce(borough, ''))) IN "
        "('unknown', 'unspecified', 'n/a', 'na', 'none', 'null', 'missing', 'other')), "
        f"count(*) FILTER (WHERE borough IS NOT NULL AND trim(borough) <> '' AND "
        "lower(trim(borough)) NOT IN ('brooklyn','queens','manhattan','bronx','staten island')) "
        f"FROM {relation} WHERE crash_date BETWEEN DATE '{start}' AND DATE '{end}'"
    ).fetchone()
    add("borough missing: NULL, in plan years before borough filter", borough_quality[0])
    add("borough missing: empty or whitespace, in plan years before borough filter", borough_quality[1])
    add("borough missing/unknown placeholder words, in plan years before borough filter", borough_quality[2])
    add("borough invalid/unrecognized values, in plan years before borough filter", borough_quality[3])
    borough_distribution = con.execute(
        f"SELECT coalesce(nullif(trim(borough), ''), '<NULL/blank>'), count(*) FROM {relation} "
        f"WHERE crash_date BETWEEN DATE '{start}' AND DATE '{end}' "
        "GROUP BY 1 ORDER BY 2 DESC, 1 LIMIT 8"
    ).fetchall()
    for label, count in borough_distribution:
        add(f"borough most common value {label!r} (default/pile-up check; pre-filter)", count)

    # Grouping-column missingness in the Brooklyn population; null dates cannot
    # be assigned to a calendar year and are therefore counted separately.
    add(
        "Brooklyn population rows with missing crash_date (cannot assign year)",
        con.execute(
            f"SELECT count(*) FROM {relation} WHERE lower(trim(coalesce(borough,'')))='brooklyn' "
            "AND crash_date IS NULL"
        ).fetchone()[0],
    )
    add("crash_date rows exactly at common default date 1900-01-01, among Brooklyn plan-year population", con.execute(
        f"SELECT count(*) FROM {relation} WHERE lower(trim(coalesce(borough,'')))='brooklyn' "
        f"AND crash_date BETWEEN DATE '{start}' AND DATE '{end}' AND crash_date = DATE '1900-01-01'"
    ).fetchone()[0])
    add("crash_date rows exactly at common default date 1970-01-01, among Brooklyn plan-year population", con.execute(
        f"SELECT count(*) FROM {relation} WHERE lower(trim(coalesce(borough,'')))='brooklyn' "
        f"AND crash_date BETWEEN DATE '{start}' AND DATE '{end}' AND crash_date = DATE '1970-01-01'"
    ).fetchone()[0])
    for year, bound in ((2013, "min"), (complete_year, "max")):
        date_val = con.execute(
            f"SELECT {bound}(crash_date) FROM {relation} WHERE year(crash_date) = {year} "
            "AND lower(trim(coalesce(borough,'')))='brooklyn'"
        ).fetchone()[0]
        add(f"Brooklyn crash_date {bound} observed date in {year}", date_val)
    add("overall crash_date minimum from 2013 onward", coverage[0])
    add("overall crash_date maximum from 2013 onward", coverage[1])
    add(f"latest file year {latest_year} is partial; excluded from final plans", coverage[1] if latest_year > complete_year else "no")

    # Per-outcome missingness is counted, never the outcome's values or sums.
    for col in outcome_cols:
        count = con.execute(
            f"SELECT count(*) FROM {relation} WHERE crash_date BETWEEN DATE '{start}' AND DATE '{end}' "
            "AND lower(trim(coalesce(borough, ''))) = 'brooklyn' "
            f'AND "{col}" IS NULL'
        ).fetchone()[0]
        add(f"{col} missing (NULL) in Brooklyn plan-year rows", count)

    with (OUT / f"check_{pid}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)

print(f"checked final-plan years 2013-{complete_year}; file dates {coverage[0]} to {coverage[1]}")
