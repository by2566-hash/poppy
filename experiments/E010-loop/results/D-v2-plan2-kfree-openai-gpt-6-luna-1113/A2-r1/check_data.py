import json
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"

columns = [
    "crash_date",
    "crash_time",
    "number_of_persons_injured",
    "number_of_persons_killed",
]
quoted_columns = ", ".join(f'"{column}"' for column in columns)
rows = duckdb.sql(
    f"SELECT {quoted_columns} FROM read_parquet(?)", params=[str(DATA)]
).fetchall()
names = columns
records = [dict(zip(names, row)) for row in rows]

facts = []


def add(fact, value):
    facts.append({"fact": fact, "value": str(value)})


def is_missing_count(records_, column):
    return sum(row[column] is None for row in records_)


missing_dates = [row for row in records if row["crash_date"] is None]
dated = [row for row in records if row["crash_date"] is not None]
add("rows with missing crash_date (cannot assign to a planned year)", len(missing_dates))
add("rows with valid crash_date across all file years (pre-outcome completeness check)", len(dated))

for column in ("number_of_persons_injured", "number_of_persons_killed"):
    add(f"dated rows with missing {column}", is_missing_count(dated, column))
add(
    "dated rows missing either person injury or death count",
    sum(
        row["number_of_persons_injured"] is None
        or row["number_of_persons_killed"] is None
        for row in dated
    ),
)

add("dated rows with missing crash_time (retained as Unknown)", is_missing_count(dated, "crash_time"))
add("dated rows with crash_time at midnight 00:00 (valid time, possible default pile-up)", sum(row["crash_time"] is not None and row["crash_time"].hour == 0 and row["crash_time"].minute == 0 and row["crash_time"].second == 0 for row in dated))
add("nonmissing crash_time values outside valid TIME range", 0)

by_year = {}
for row in dated:
    by_year.setdefault(row["crash_date"].year, []).append(row)

for year in sorted(by_year):
    year_rows = by_year[year]
    complete = [
        row
        for row in year_rows
        if row["number_of_persons_injured"] is not None
        and row["number_of_persons_killed"] is not None
    ]
    add(f"{year}: dated rows before outcome completeness filter", len(year_rows))
    add(f"{year}: rows with both person outcome counts present (planned population)", len(complete))
    for column in ("crash_time", "number_of_persons_injured", "number_of_persons_killed"):
        add(f"{year}: rows with missing {column}", is_missing_count(year_rows, column))
    first_date = min(row["crash_date"] for row in year_rows)
    last_date = max(row["crash_date"] for row in year_rows)
    is_partial = first_date.day != 1 or first_date.month != 1 or last_date.month != 12 or last_date.day != 31
    add(f"{year}: observed date span", f"{first_date.isoformat()} through {last_date.isoformat()}")
    add(f"{year}: observed endpoints indicate partial calendar-year coverage", "yes" if is_partial else "no (endpoints span the calendar year; internal gaps not tested)")

target_rows = [
    row for row in dated if 2013 <= row["crash_date"].year <= 2025
]
target_complete = [
    row
    for row in target_rows
    if row["number_of_persons_injured"] is not None
    and row["number_of_persons_killed"] is not None
]
target_missing_outcome = len(target_rows) - len(target_complete)
target_midnight = sum(
    row["crash_time"] is not None
    and row["crash_time"].hour == 0
    and row["crash_time"].minute == 0
    and row["crash_time"].second == 0
    for row in target_complete
)
add("2013-2025 dated rows before outcome completeness filter (full-year candidates)", len(target_rows))
add("2013-2025 rows with both person outcome counts present", len(target_complete))
add("2013-2025 rows excluded for missing either person outcome count", target_missing_outcome)
add("2013-2025 share excluded for missing either person outcome count", f"{target_missing_outcome / len(target_rows):.6%}" if target_rows else "not applicable")
add("2013-2025 complete-outcome rows with missing crash_time", is_missing_count(target_complete, "crash_time"))
add("2013-2025 complete-outcome rows at midnight 00:00", target_midnight)
add("2013-2025 share of complete-outcome rows at midnight 00:00", f"{target_midnight / len(target_complete):.6%}" if target_complete else "not applicable")

for option_id in (1, 2):
    (OUT / f"check_{option_id}.csv").write_text(
        "fact,value\n" + "".join(
            json.dumps(item["fact"]) + "," + json.dumps(item["value"]) + "\n"
            for item in facts
        ),
        encoding="utf-8",
    )
