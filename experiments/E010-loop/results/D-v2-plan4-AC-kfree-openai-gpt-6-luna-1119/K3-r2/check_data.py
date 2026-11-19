import csv
import duckdb


YEARS = range(2013, 2026)
OUTCOMES = ("number_of_motorist_killed", "number_of_cyclist_killed")
con = duckdb.connect()
source = "read_parquet('./data/crashes.parquet')"
year_filter = "crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'"

# These checks inspect row coverage and field quality only; no outcome values
# or outcome aggregates are selected or computed here.
overall = con.execute(
    f"""SELECT COUNT(*) AS n,
               COUNT(*) FILTER (WHERE crash_date IS NULL) AS date_null,
               COUNT(*) FILTER (WHERE crash_date = DATE '2013-01-01') AS jan1_2013
        FROM {source}
        WHERE {year_filter}"""
).fetchone()
before_year_filter = con.execute(
    f"""SELECT COUNT(*) AS n,
               COUNT(*) FILTER (WHERE crash_date IS NULL) AS date_null,
               COUNT(*) FILTER (WHERE crash_date IN
                   (DATE '0001-01-01', DATE '1900-01-01', DATE '1970-01-01')) AS known_sentinel_dates
        FROM {source}"""
).fetchone()
by_year = con.execute(
    f"""SELECT EXTRACT(YEAR FROM crash_date)::INTEGER AS yr,
               COUNT(*) AS n,
               MIN(crash_date) AS first_day,
               MAX(crash_date) AS last_day,
               COUNT(*) FILTER (WHERE crash_date = make_date(EXTRACT(YEAR FROM crash_date)::INTEGER, 1, 1)) AS jan1_rows
        FROM {source}
        WHERE {year_filter}
        GROUP BY yr
        ORDER BY yr"""
).fetchall()
missing_outcomes = {
    col: con.execute(
        f"SELECT COUNT(*) FROM {source} WHERE {year_filter} AND {col} IS NULL"
    ).fetchone()[0]
    for col in OUTCOMES
}

rows_by_year = {row[0]: row for row in by_year}
facts = [
    ("rows_before_year_filter_all_dates", before_year_filter[0]),
    ("crash_date_missing_before_year_filter_all_dates", before_year_filter[1]),
    ("crash_date_known_sentinel_dates_before_year_filter_all_dates", before_year_filter[2]),
    ("population_rows_2013_2025", overall[0]),
    ("crash_date_missing_within_selected_years", overall[1]),
    ("crash_date_exact_2013_01_01_within_selected_years", overall[2]),
]
for year in YEARS:
    row = rows_by_year.get(year)
    if row:
        _, n, first_day, last_day, jan1_rows = row
        facts.extend([
            (f"rows_{year}", n),
            (f"first_date_{year}", first_day.isoformat()),
            (f"last_date_{year}", last_day.isoformat()),
            (f"january_1_rows_{year}", jan1_rows),
        ])
    else:
        facts.extend([
            (f"rows_{year}", 0),
            (f"first_date_{year}", "none"),
            (f"last_date_{year}", "none"),
            (f"january_1_rows_{year}", 0),
        ])
for col, n in missing_outcomes.items():
    facts.append((f"missing_{col}_within_selected_years", n))

for option_id in (1, 2):
    with open(f"./out/check_{option_id}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)
