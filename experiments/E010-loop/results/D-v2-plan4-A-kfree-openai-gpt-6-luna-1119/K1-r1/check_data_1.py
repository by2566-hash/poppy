import csv
import duckdb


years = range(2013, 2026)
con = duckdb.connect()
result = con.execute(
    """
    SELECT
        year(crash_date) AS calendar_year,
        count(*) AS crash_rows,
        count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS missing_pedestrian_killed,
        min(crash_date) AS first_crash_date,
        max(crash_date) AS last_crash_date
    FROM read_parquet('./data/crashes.parquet')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY calendar_year
    ORDER BY calendar_year
    """
).fetchall()
con.close()

by_year = {int(row[0]): row[1:] for row in result}
facts = []
all_rows = sum(values[0] for values in by_year.values())
facts.append(("Population crash rows, 2013-2025 inclusive", all_rows))
facts.append(("crash_date missing among included rows", 0))
facts.append(("crash_date default/sentinel", "No default date is defined for this DATE column; dates are checked for year coverage"))
facts.append(("number_of_pedestrians_killed missing-value check", "NULL only is representable for this INTEGER column; no outcome values were counted"))

for year in years:
    row = by_year.get(year)
    if row is None:
        facts.append((f"{year} crash rows", 0))
        facts.append((f"{year} missing number_of_pedestrians_killed", 0))
        facts.append((f"{year} observed date range", "No rows"))
        facts.append((f"{year} coverage", "No data"))
        continue

    crash_rows, missing, first_date, last_date = row
    first_expected = f"{year}-01-01"
    last_expected = f"{year}-12-31"
    facts.append((f"{year} crash rows", crash_rows))
    facts.append((f"{year} missing number_of_pedestrians_killed", missing))
    facts.append((f"{year} observed date range", f"{first_date} through {last_date}"))
    partial = first_date.isoformat() != first_expected or last_date.isoformat() != last_expected
    facts.append((f"{year} coverage", "Partial year" if partial else "Full calendar year represented"))

with open('./out/check_1.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["fact", "value"])
    writer.writerows(facts)
