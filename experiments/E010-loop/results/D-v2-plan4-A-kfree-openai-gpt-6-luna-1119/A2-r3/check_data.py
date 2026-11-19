import csv
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
DATA = str(ROOT / "data" / "crashes.parquet")
OUT = Path(__file__).resolve().parent
OUTCOMES = {
    2: ["number_of_persons_injured", "number_of_persons_killed"],
    3: ["number_of_persons_injured", "number_of_persons_killed"],
}

con = duckdb.connect()
view = f"read_parquet('{DATA}')"

for framing_id in (1, 2, 3):
    facts = []

    def record(fact, value):
        facts.append({"fact": fact, "value": str(value)})

    # Initial-plan check: establish calendar coverage before deciding whether
    # to retain partial first/last years. No crash outcome values are queried.
    total = con.execute(f"SELECT COUNT(*) FROM {view}").fetchone()[0]
    record("Rows in initial population across all file years", total)
    year_rows = con.execute(
        f"""SELECT YEAR(crash_date) AS yr, COUNT(*) AS n,
                   MIN(crash_date) AS first_date, MAX(crash_date) AS last_date
            FROM {view}
            GROUP BY YEAR(crash_date)
            ORDER BY yr"""
    ).fetchall()
    for year, count, first_date, last_date in year_rows:
        if year is None:
            record("Rows with missing crash_date year", count)
            continue
        record(f"Rows in year {year}", count)
        record(f"Observed date bounds in year {year}", f"{first_date} through {last_date}")
        partial = first_date.strftime("%Y-%m-%d") != f"{year}-01-01" or last_date.strftime("%Y-%m-%d") != f"{year}-12-31"
        record(f"Year {year} is partial by observed date bounds", partial)

    # The boundary years (2012 and 2026) are partial, so the final candidate
    # population is restricted to complete calendar years 2013–2025.
    base = f"(SELECT * FROM {view} WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01') AS final_years"
    base_count = con.execute(f"SELECT COUNT(*) FROM {base}").fetchone()[0]
    record("Candidate rows in final complete years 2013-2025", base_count)
    record("Rows in partial years excluded (2012 and 2026)", 100545 + 36424)
    yearly = con.execute(
        f"SELECT YEAR(crash_date), COUNT(*) FROM {base} GROUP BY YEAR(crash_date) ORDER BY 1"
    ).fetchall()
    for year, count in yearly:
        record(f"Candidate rows in final year {year}", count)

    date_check = con.execute(
        f"""SELECT COUNT(*) FILTER (WHERE crash_date IS NULL),
                   COUNT(*) FILTER (WHERE crash_date IN (DATE '1900-01-01', DATE '1970-01-01'))
            FROM {base}"""
    ).fetchone()
    record("crash_date missing/unparseable (NULL) in final candidate years", date_check[0])
    record("crash_date at sentinel dates 1900-01-01 or 1970-01-01 in final candidate years", date_check[1])

    # crash_time is a typed TIME column: non-NULL values cannot be blank,
    # unknown words, or impossible clock values after parquet parsing.
    time_check = con.execute(
        f"""SELECT COUNT(*) FILTER (WHERE crash_time IS NULL),
                   COUNT(*) FILTER (WHERE crash_time = TIME '00:00:00')
            FROM {base}"""
    ).fetchone()
    record("crash_time missing/unparseable (NULL; typed TIME excludes blank/unknown/impossible values) in final candidate years", time_check[0])
    record("crash_time at midnight default candidate 00:00:00 in final candidate years", time_check[1])

    for column in OUTCOMES.get(framing_id, []):
        missing = con.execute(f"SELECT COUNT(*) FROM {base} WHERE {column} IS NULL").fetchone()[0]
        record(f"{column} missing (NULL) in final candidate years", missing)

    if framing_id in (2, 3):
        columns = OUTCOMES[framing_id]
        incomplete = " OR ".join(f"{column} IS NULL" for column in columns)
        excluded = con.execute(f"SELECT COUNT(*) FROM {base} WHERE ({incomplete})").fetchone()[0]
        eligible = base_count - excluded
        record("Final eligible metric-population rows after excluding any missing outcome total", eligible)
        record("Rows excluded for missing one or more required outcome totals", excluded)
        eligible_by_year = con.execute(
            f"""SELECT YEAR(crash_date), COUNT(*) FILTER (WHERE NOT ({incomplete}))
                FROM {base} GROUP BY YEAR(crash_date) ORDER BY 1"""
        ).fetchall()
        for year, count in eligible_by_year:
            record(f"Final eligible metric-population rows in year {year}", count)
    else:
        record("Final metric-population rows after time classification", base_count)

    with (OUT / f"check_{framing_id}.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["fact", "value"])
        writer.writeheader()
        writer.writerows(facts)

print("Wrote plan-scoped checks for framings 1–3.")
