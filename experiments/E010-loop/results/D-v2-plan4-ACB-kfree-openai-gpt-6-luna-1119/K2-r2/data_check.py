import csv
import json
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"
YEARS = range(2013, 2026)

con = duckdb.connect()
source = f"read_parquet('{DATA.as_posix()}')"
missing_date = con.execute(
    f"SELECT count(*) FROM {source} WHERE crash_date IS NULL"
).fetchone()[0]
year_rows = dict(
    con.execute(
        f"""
        SELECT year(crash_date) AS yr, count(*) AS n
        FROM {source}
        WHERE crash_date >= DATE '2013-01-01'
          AND crash_date < DATE '2026-01-01'
        GROUP BY yr ORDER BY yr
        """
    ).fetchall()
)
coverage = {
    year: (start, end)
    for year, start, end in con.execute(
        f"""
        SELECT year(crash_date) AS yr, min(crash_date), max(crash_date)
        FROM {source}
        WHERE crash_date >= DATE '2013-01-01'
          AND crash_date < DATE '2026-01-01'
        GROUP BY yr ORDER BY yr
        """
    ).fetchall()
}

facts = [
    ("crash_date_missing_source_rows_no_year_assignable", missing_date),
    ("crash_date_column_type", "DATE; empty/unknown text and impossible calendar dates are not representable"),
    ("crash_date_default_value_check", "not applicable: no default date or unknown marker is documented for the DATE column"),
]
for year in YEARS:
    n = year_rows.get(year, 0)
    bounds = coverage.get(year)
    facts.append((f"rows_{year}", n))
    facts.append(
        (
            f"date_coverage_{year}",
            "no dated rows" if bounds is None else f"{bounds[0]} through {bounds[1]}",
        )
    )

for option_id in (1, 2, 3):
    path = OUT / f"check_{option_id}.csv"
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)

print(json.dumps({"missing_date": missing_date, "years": year_rows, "coverage": coverage}, default=str))
