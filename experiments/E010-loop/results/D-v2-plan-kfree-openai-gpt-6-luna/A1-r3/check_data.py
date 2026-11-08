import csv
import json
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"


def inspect(option_id, outcome_columns):
    con = duckdb.connect()
    source = str(DATA).replace("'", "''")
    rows = con.execute(
        f"""
        WITH scoped AS (
          SELECT *, year(crash_date) AS yr
          FROM read_parquet('{source}')
          WHERE crash_date >= DATE '2013-01-01'
        ), brooklyn AS (
          SELECT * FROM scoped WHERE lower(trim(coalesce(borough, ''))) = 'brooklyn'
        )
        SELECT 'Brooklyn crashes in ' || yr::VARCHAR,
               count(*)::VARCHAR
        FROM brooklyn
        GROUP BY yr
        ORDER BY yr
        """
    ).fetchall()

    facts = []
    for fact, value in rows:
        facts.append((fact, value))

    # Borough blanks/unknown labels are counted in date-eligible candidate rows,
    # since those records cannot be assigned to or included in Brooklyn.
    borough_missing = con.execute(
        f"""
        SELECT count(*)
        FROM read_parquet('{source}')
        WHERE crash_date >= DATE '2013-01-01'
          AND (borough IS NULL OR trim(borough) = '' OR
               lower(trim(borough)) IN ('unknown', 'unspecified', 'n/a', 'na', 'null', 'none'))
        """
    ).fetchone()[0]
    borough_total = con.execute(
        f"SELECT count(*) FROM read_parquet('{source}') WHERE crash_date >= DATE '2013-01-01'"
    ).fetchone()[0]
    borough_share = borough_missing / borough_total if borough_total else 0
    facts.append(("Date-eligible crashes with missing/unknown borough (all boroughs)", str(borough_missing)))
    facts.append(("Date-eligible crash rows (all boroughs; borough-missing denominator)", str(borough_total)))
    facts.append(("Date-eligible crashes with missing/unknown borough (share)", f"{borough_share:.6%}"))
    null_dates = con.execute(
        f"SELECT count(*) FROM read_parquet('{source}') WHERE crash_date IS NULL"
    ).fetchone()[0]
    facts.append(("Crashes with missing crash_date (cannot assign year)", str(null_dates)))

    for col in outcome_columns:
        stats = con.execute(
            f"""
            SELECT
              count(*) AS n,
              count(*) FILTER (WHERE {col} IS NULL) AS nulls,
              count(*) FILTER (WHERE {col} < 0) AS negative,
              count(*) FILTER (WHERE {col} = 0) AS zeros
            FROM read_parquet('{source}')
            WHERE crash_date >= DATE '2013-01-01'
              AND lower(trim(coalesce(borough, ''))) = 'brooklyn'
            """
        ).fetchone()
        n, nulls, negative, zeros = stats
        zero_share = zeros / n if n else 0
        facts.extend([
            (f"{col}: Brooklyn date-eligible crash rows", str(n)),
            (f"{col}: NULL values in Brooklyn rows", str(nulls)),
            (f"{col}: empty/unknown text values (not applicable; integer column)", "0"),
            (f"{col}: impossible negative values in Brooklyn rows", str(negative)),
            (f"{col}: zero/default values in Brooklyn rows", str(zeros)),
            (f"{col}: zero/default values in Brooklyn rows (share)", f"{zero_share:.6%}"),
        ])

    # Coverage uses the earliest/latest Brooklyn crash date observed in each year.
    coverage = con.execute(
        f"""
        SELECT year(crash_date) AS yr, min(crash_date), max(crash_date), count(*)
        FROM read_parquet('{source}')
        WHERE crash_date >= DATE '2013-01-01'
          AND lower(trim(coalesce(borough, ''))) = 'brooklyn'
        GROUP BY yr ORDER BY yr
        """
    ).fetchall()
    for yr, start, end, count in coverage:
        facts.append((f"Year {yr} Brooklyn date coverage (earliest to latest observed)", f"{start} to {end}"))
        partial = "no" if start.month == 1 and start.day == 1 and end.month == 12 and end.day == 31 else "yes / boundary coverage not full"
        facts.append((f"Year {yr} observed coverage flag", partial))

    path = OUT / f"check_{option_id}.csv"
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fact", "value"])
        writer.writerows(facts)
    con.close()


inspect(1, ["number_of_pedestrians_injured", "number_of_pedestrians_killed"])
inspect(2, ["number_of_pedestrians_killed"])
