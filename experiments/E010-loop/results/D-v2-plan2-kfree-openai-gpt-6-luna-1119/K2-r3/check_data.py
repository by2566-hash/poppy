import csv
import datetime

import duckdb


YEARS = range(2013, 2026)
START = datetime.date(2013, 1, 1)
STOP = datetime.date(2026, 1, 1)
con = duckdb.connect()
con.execute(
    "CREATE VIEW crashes AS "
    "SELECT crash_date FROM read_parquet('data/crashes.parquet')"
)
where = "crash_date >= ? AND crash_date < ?"
population = con.execute(
    f"SELECT count(*), min(crash_date), max(crash_date), "
    f"count(*) FILTER (WHERE crash_date IS NULL) "
    f"FROM crashes WHERE {where}",
    [START, STOP],
).fetchone()
annual = con.execute(
    f"SELECT year(crash_date), count(*), min(crash_date), max(crash_date), "
    f"count(*) FILTER (WHERE crash_date IS NULL) "
    f"FROM crashes WHERE {where} GROUP BY 1 ORDER BY 1",
    [START, STOP],
).fetchall()
by_year = {year: (count, low, high, missing) for year, count, low, high, missing in annual}
facts = [
    ("population_rows_2013_2025", population[0]),
    ("observed_min_date_in_population", population[1]),
    ("observed_max_date_in_population", population[2]),
    ("crash_date_missing_in_population", population[3]),
    (
        "crash_date_impossible_value_in_population",
        "0; crash_date is a native DATE, so invalid calendar dates cannot be stored",
    ),
    (
        "crash_date_empty_or_unknown_word_in_population",
        "not representable in the native DATE column",
    ),
    (
        "crash_date_default_value_pileup_in_population",
        "no default or sentinel date is specified by the supplied schema",
    ),
]

for year in YEARS:
    count, low, high, missing = by_year.get(year, (0, None, None, 0))
    facts.extend(
        [
            (f"rows_{year}", count),
            (f"observed_min_date_{year}", low),
            (f"observed_max_date_{year}", high),
            (f"crash_date_missing_in_population_{year}", missing),
        ]
    )
    if low is None:
        note = "no crash records observed; date coverage cannot be established"
    else:
        first_day = datetime.date(year, 1, 1)
        last_day = datetime.date(year, 12, 31)
        note = (
            "observed crash-date span touches both year boundaries; actual source "
            "coverage cannot be established from crash records alone"
            if low == first_day and high == last_day
            else f"observed crash-date span {low} to {high}; incomplete year coverage "
            "cannot be distinguished from no crashes at the edges using this file alone"
        )
    facts.append((f"year_coverage_note_{year}", note))

for option_id in (1, 2):
    with open(f"out/check_{option_id}.csv", "w", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)

print("population:", population)
print("annual:", annual)
