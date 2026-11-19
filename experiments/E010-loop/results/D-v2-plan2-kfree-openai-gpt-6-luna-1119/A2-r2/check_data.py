import calendar
import json
from pathlib import Path

import duckdb
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = str(ROOT / "data" / "crashes.parquet")
OUT = Path(__file__).resolve().parent


def frame(sql):
    return duckdb.connect().execute(sql).fetchdf()


def date_text(value):
    return "" if pd.isna(value) else pd.Timestamp(value).date().isoformat()


def year_breakdown(df, population_mask):
    dates = pd.to_datetime(df["crash_date"], errors="coerce")
    eligible = df.loc[population_mask & dates.notna()].copy()
    eligible["_year"] = dates.loc[eligible.index].dt.year
    rows = []
    for year, group in eligible.groupby("_year", sort=True):
        low = pd.to_datetime(group["crash_date"]).min()
        high = pd.to_datetime(group["crash_date"]).max()
        full_year = low.date().isoformat() == f"{year}-01-01" and high.date().isoformat() == f"{year}-12-{calendar.monthrange(int(year), 12)[1]:02d}"
        rows.append((int(year), len(group), low.date().isoformat(), high.date().isoformat(), full_year))
    return rows


def time_checks(df, base_mask, facts):
    time_values = df.loc[base_mask, "crash_time"].astype("string")
    lower = time_values.str.strip().str.lower()
    missing = time_values.isna() | lower.isin(["", "null", "none", "nan", "n/a", "na", "unknown", "unspecified"])
    parsed = pd.to_datetime(time_values.where(~missing), format="mixed", errors="coerce")
    invalid = ~missing & parsed.isna()
    facts.append(("plan-population rows with missing/unknown crash_time", int(missing.sum())))
    facts.append(("plan-population rows with unclassifiable/impossible crash_time", int(invalid.sum())))
    facts.append(("plan-population rows at default/sentinel time 00:00:00", int((lower == "00:00:00").sum())))


for option_id in (1, 2):
    columns = ["crash_date", "crash_time"]
    if option_id == 2:
        columns += ["number_of_persons_injured", "number_of_persons_killed"]
    selection = ", ".join(columns)
    df = frame(f"SELECT {selection} FROM read_parquet('{DATA}')")
    facts = []
    dates = pd.to_datetime(df["crash_date"], errors="coerce")
    date_valid = dates.notna()
    facts.append(("source rows read from planned columns", len(df)))
    facts.append(("candidate rows with missing/unassignable crash_date", int((~date_valid).sum())))
    facts.append(("candidate rows at default/sentinel crash_date 1900-01-01 or 1970-01-01", int(dates.isin([pd.Timestamp("1900-01-01"), pd.Timestamp("1970-01-01")]).sum())))
    facts.append(("candidate rows with valid crash_date", int(date_valid.sum())))
    year_numbers = dates.dt.year
    full_year_mask = date_valid & year_numbers.between(2013, 2025)
    facts.append(("valid-date rows outside final complete-year window 2013-2025", int((date_valid & ~full_year_mask).sum())))
    years = year_breakdown(df, date_valid)
    for year, count, low, high, full_year in years:
        facts.append((f"candidate rows in {year}", count))
        facts.append((f"{year} date coverage", f"{low} through {high}"))
        facts.append((f"{year} is a complete calendar year", str(full_year).lower()))
    partial = [str(year) for year, _, _, _, full_year in years if not full_year]
    facts.append(("partial years in candidate data", ", ".join(partial) if partial else "none"))

    if option_id == 1:
        complete_year_days = sum(366 if calendar.isleap(year) else 365 for year in range(2013, 2026))
        facts.append(("complete calendar days in final window 2013-2025", complete_year_days))
        facts.append(("nominal daytime clock-hours in final window (14 hours/day)", complete_year_days * 14))
        facts.append(("nominal nighttime clock-hours in final window (10 hours/day)", complete_year_days * 10))

    if option_id == 1:
        time_checks(df, full_year_mask, facts)
        facts.append(("final-plan population rows (valid crash_date in complete years 2013-2025)", int(full_year_mask.sum())))
        final_years = year_breakdown(df, full_year_mask)
    else:
        injury_missing = df["number_of_persons_injured"].isna()
        killed_missing = df["number_of_persons_killed"].isna()
        complete = full_year_mask & ~injury_missing & ~killed_missing
        facts.append(("complete-year candidate rows with missing number_of_persons_injured", int((full_year_mask & injury_missing).sum())))
        facts.append(("complete-year candidate rows with missing number_of_persons_killed", int((full_year_mask & killed_missing).sum())))
        facts.append(("complete-year candidate rows missing either summed outcome column", int((full_year_mask & (injury_missing | killed_missing)).sum())))
        facts.append(("final-plan complete-case population rows", int(complete.sum())))
        time_checks(df, complete, facts)
        final_years = year_breakdown(df, complete)
    for year, count, _, _, _ in final_years:
        facts.append((f"final-plan population rows in {year}", count))

    pd.DataFrame(facts, columns=["fact", "value"]).to_csv(OUT / f"check_{option_id}.csv", index=False)
