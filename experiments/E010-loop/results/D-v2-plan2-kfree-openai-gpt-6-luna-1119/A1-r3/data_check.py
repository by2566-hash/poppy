import csv
import json
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "crashes.parquet"
OUT = Path(__file__).resolve().parent
OUTCOMES = {
    1: ["number_of_pedestrians_injured"],
    2: ["number_of_pedestrians_killed"],
    3: ["number_of_pedestrians_injured", "number_of_pedestrians_killed"],
}


def main():
    con = duckdb.connect()
    outcomes = sorted({col for cols in OUTCOMES.values() for col in cols})
    columns = ["crash_date", "borough", *outcomes]
    selected = ", ".join(f'"{col}"' for col in columns)
    rows = con.execute(
        f"SELECT {selected} FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01'",
        [str(DATA)],
    ).fetchdf()
    missing_dates = con.execute(
        "SELECT count(*) FROM read_parquet(?) WHERE crash_date IS NULL", [str(DATA)]
    ).fetchone()[0]
    rows["year"] = rows["crash_date"].dt.year
    borough_text = rows["borough"].astype("string").str.strip()
    borough_lower = borough_text.str.lower()
    missing_borough = borough_text.isna() | borough_text.eq("") | borough_lower.isin(
        ["unknown", "unspecified", "n/a", "na", "null", "none"]
    )
    valid_boroughs = {"bronx", "brooklyn", "manhattan", "queens", "staten island"}
    invalid_borough = ~missing_borough & ~borough_lower.isin(valid_boroughs)
    brooklyn = borough_lower.eq("brooklyn")
    facts_common = []

    # Counts outside the assigned-borough population are filter diagnostics: they
    # document records in the requested years whose borough cannot be assigned.
    facts_common.extend(
        [
            ("Rows with crash_date missing (cannot be assigned to a planned year)", int(missing_dates)),
            ("Crash rows with a dated crash in 2013+ before the borough filter", len(rows)),
            ("Rows in 2013+ with borough missing/unknown/empty (excluded by Brooklyn filter)", int(missing_borough.sum())),
            ("Rows in 2013+ with a nonstandard borough value (excluded by Brooklyn filter)", int(invalid_borough.sum())),
            ("Rows in 2013+ assigned to Brooklyn", int(brooklyn.sum())),
        ]
    )
    years = sorted(int(y) for y in rows["year"].dropna().unique())
    for year in years:
        year_rows = rows["year"].eq(year)
        target = year_rows & brooklyn
        facts_common.append((f"Brooklyn crash rows in {year}", int(target.sum())))
        date_min = rows.loc[year_rows, "crash_date"].min()
        date_max = rows.loc[year_rows, "crash_date"].max()
        facts_common.append((f"Observed crash_date range in {year} (all boroughs)", f"{date_min.date()} to {date_max.date()}"))
        brooklyn_min = rows.loc[target, "crash_date"].min()
        brooklyn_max = rows.loc[target, "crash_date"].max()
        facts_common.append(
            (
                f"Observed crash_date range in {year} (Brooklyn population)",
                "no rows" if pd_is_missing(brooklyn_min) else f"{brooklyn_min.date()} to {brooklyn_max.date()}",
            )
        )
        facts_common.append(
            (
                f"Brooklyn rows with missing/empty/unknown borough in {year}",
                0,
            )
        )

    for option_id, option_outcomes in OUTCOMES.items():
        facts = list(facts_common)
        facts.append(("Rows in final metric population before outcome-missing exclusions", int(brooklyn.sum())))
        for col in option_outcomes:
            total_missing = int(rows.loc[brooklyn, col].isna().sum())
            facts.append((f"Brooklyn rows with {col} missing", total_missing))
            for year in years:
                target = brooklyn & rows["year"].eq(year)
                missing = int(rows.loc[target, col].isna().sum())
                facts.append((f"Brooklyn rows with {col} missing in {year}", missing))
        with (OUT / f"check_{option_id}.csv").open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["fact", "value"])
            writer.writerows(facts)


def pd_is_missing(value):
    return value is None or str(value) == "NaT"


if __name__ == "__main__":
    main()
