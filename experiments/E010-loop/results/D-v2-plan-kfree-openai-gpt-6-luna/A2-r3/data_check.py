import csv
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"

con = duckdb.connect()
data_sql_path = str(DATA).replace("'", "''")
con.execute(f"CREATE VIEW crashes AS SELECT crash_date, crash_time, number_of_persons_injured, number_of_persons_killed FROM read_parquet('{data_sql_path}')")

total_rows = con.execute("SELECT count(*) FROM crashes").fetchone()[0]
date_stats = con.execute(
    """SELECT min(crash_date), max(crash_date), count(*) FILTER (WHERE crash_date IS NULL)
       FROM crashes"""
).fetchone()
date_min, date_max, missing_date = date_stats

facts = []


def add(fact, value):
    facts.append((fact, value))


def save_check(check_id):
    with (OUT / f"check_{check_id}.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)


for check_id in (1, 2):
    facts.clear()
    add("all crash rows in file", total_rows)
    add("rows with missing crash_date (cannot assign year)", missing_date)
    add("rows with missing crash_time", con.execute("SELECT count(*) FROM crashes WHERE crash_time IS NULL").fetchone()[0])
    add("earliest nonmissing crash_date", date_min)
    add("latest nonmissing crash_date", date_max)

    all_candidate = "crash_date IS NOT NULL AND crash_time IS NOT NULL"
    candidate = all_candidate + " AND year(crash_date) BETWEEN 2013 AND 2025"
    usable = candidate + " AND number_of_persons_injured IS NOT NULL AND number_of_persons_killed IS NOT NULL"
    add("rows with date and time available in all years", con.execute(f"SELECT count(*) FROM crashes WHERE {all_candidate}").fetchone()[0])
    add("rows with date and time in complete years 2013–2025 (pre-outcome checks)", con.execute(f"SELECT count(*) FROM crashes WHERE {candidate}").fetchone()[0])
    add("rows with valid date, time, and both outcome counts in 2013–2025 (final population)", con.execute(f"SELECT count(*) FROM crashes WHERE {usable}").fetchone()[0])
    add("date+time rows excluded for partial boundary years 2012 and 2026", con.execute(f"SELECT count(*) FROM crashes WHERE {all_candidate} AND (year(crash_date) = 2012 OR year(crash_date) = 2026)").fetchone()[0])

    for col in ("number_of_persons_injured", "number_of_persons_killed"):
        add(f"{col}: missing among date/time-valid rows in 2013–2025", con.execute(f"SELECT count(*) FROM crashes WHERE {candidate} AND {col} IS NULL").fetchone()[0])
        add(f"{col}: negative/impossible among date/time-valid rows in 2013–2025", con.execute(f"SELECT count(*) FROM crashes WHERE {candidate} AND {col} < 0").fetchone()[0])
        add(f"{col}: zero among date/time-valid rows in 2013–2025 (valid zero, not missing)", con.execute(f"SELECT count(*) FROM crashes WHERE {candidate} AND {col} = 0").fetchone()[0])

    add("crash_time: exact-midnight rows in 2013–2025 (valid hour; check for pileup)", con.execute(f"SELECT count(*) FROM crashes WHERE {candidate} AND crash_time = TIME '00:00:00'").fetchone()[0])
    all_usable = all_candidate + " AND number_of_persons_injured IS NOT NULL AND number_of_persons_killed IS NOT NULL"
    years = con.execute(
        f"""SELECT year(crash_date) AS yr,
                   min(crash_date), max(crash_date),
                   count(*) FILTER (WHERE {all_candidate}) AS rows_with_date_and_time,
                   count(*) FILTER (WHERE {all_usable}) AS usable_rows,
                   count(*) FILTER (WHERE crash_time IS NULL) AS missing_time_rows
            FROM crashes WHERE crash_date IS NOT NULL
            GROUP BY yr ORDER BY yr"""
    ).fetchall()
    add("per-year counts: year | first date | last date | date+time rows | usable rows | missing-time rows", "")
    for yr, first, last, candidate_n, usable_n, missing_time_n in years:
        add(f"year {yr}: first/last date; date+time rows; usable rows; missing-time rows", f"{first} | {last} | {candidate_n} | {usable_n} | {missing_time_n}")
    if date_min is not None and date_max is not None:
        add("boundary-year coverage", f"first year begins on {date_min}; last year ends on {date_max}; any boundary year not spanning Jan 1 through Dec 31 is partial")
    save_check(check_id)

con.close()
