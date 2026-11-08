"""E010-1 data profile generator (docs/v2-design-2026-11-07.md §3, §6 step 1).

Writes experiments/E010-loop/profile.md: a descriptive, trap-agnostic profile of the
file the agent reads (./data/crashes.parquet in its sandbox = data/processed/nyc_crashes.parquet).

Rules the output must keep (gate G1, reviewed by Bo):
- numbers and column facts only; no judgement words, no advice, no trap names;
- every column is treated by the same rule (nothing is selected or highlighted);
- no outcome aggregates (no sums of injured / killed by year or group), so the profile
  cannot hand the agent an answer to any question.

Run: ~/.poppy/venv/bin/python experiments/E010-loop/make_profile.py
"""
import hashlib
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
PARQUET = ROOT / "data" / "processed" / "nyc_crashes.parquet"
OUT = Path(__file__).resolve().parent / "profile.md"
MAX_LISTED_VALUES = 10   # VARCHAR columns with at most this many distinct values list them


def fmt_share(x):
    """One decimal; a non-zero share that would round to 0.0 is shown as <0.1."""
    return "<0.1" if 0 < x < 0.05 else f"{x:.1f}"


def main():
    c = duckdb.connect()
    c.execute(f"create view t as select * from read_parquet('{PARQUET}')")
    cols = c.execute("describe t").fetchall()          # (name, type, ...)
    n, d0, d1 = c.execute("select count(*), min(crash_date), max(crash_date) from t").fetchone()
    years = [r[0] for r in c.execute(
        "select distinct year(crash_date) y from t where crash_date is not null order by y").fetchall()]

    L = ["Data profile of ./data/crashes.parquet (computed by code from the file; descriptive only).", ""]
    L.append(f"Rows: {n:,}. crash_date from {d0} to {d1}.")
    L.append("")

    # 1. rows per year; rows per month for calendar years the date range covers only in part
    L.append("Rows per year:")
    per_year = dict(c.execute("select year(crash_date), count(*) from t group by 1").fetchall())
    L.append(" | ".join(f"{y}: {per_year[y]:,}" for y in years))
    for y in years:
        first, last = c.execute(
            f"select min(crash_date), max(crash_date) from t where year(crash_date) = {y}").fetchone()
        if (first.month, first.day) != (1, 1) or (last.month, last.day) != (12, 31):
            pm = c.execute(f"select month(crash_date), count(*) from t where year(crash_date) = {y} "
                           "group by 1 order by 1").fetchall()
            L.append(f"Rows per month in {y} (dates {first} to {last}): "
                     + " | ".join(f"{m:02d}: {k:,}" for m, k in pm))
    L.append("")

    # 2. NULL share per column per year (same rule for every column)
    L.append("Share of NULL values per column and year (%):")
    L.append("| column | " + " | ".join(str(y) for y in years) + " |")
    L.append("|---|" + "---|" * len(years))
    no_null = []
    for name, *_ in cols:
        q = (f"select year(crash_date), 100.0 * count(*) filter (where \"{name}\" is null) / count(*) "
             "from t where crash_date is not null group by 1")
        share = dict(c.execute(q).fetchall())
        if all(share.get(y, 0) == 0 for y in years):
            no_null.append(name)
            continue
        L.append(f"| {name} | " + " | ".join(fmt_share(share.get(y, 0)) for y in years) + " |")
    if no_null:
        L.append(f"No NULL values in any year: {', '.join(no_null)}.")
    L.append("")

    # 3. per-column type and range (row level, whole file)
    L.append("Columns (whole file, row level):")
    for name, typ, *_ in cols:
        if typ in ("INTEGER", "BIGINT", "DOUBLE"):
            lo, hi = c.execute(f'select min("{name}"), max("{name}") from t').fetchone()
            L.append(f"- {name} ({typ}): min {lo}, max {hi}")
        elif typ in ("DATE", "TIME"):
            lo, hi = c.execute(f'select min("{name}"), max("{name}") from t').fetchone()
            L.append(f"- {name} ({typ}): from {lo} to {hi}")
        else:
            k = c.execute(f'select count(distinct "{name}") from t').fetchone()[0]
            if k <= MAX_LISTED_VALUES:
                vals = [r[0] for r in c.execute(
                    f'select distinct "{name}" from t where "{name}" is not null order by 1').fetchall()]
                L.append(f"- {name} ({typ}): {k} distinct non-NULL values: {', '.join(vals)}")
            else:
                L.append(f"- {name} ({typ}): {k:,} distinct non-NULL values")

    text = "\n".join(L) + "\n"
    OUT.write_text(text)
    print(f"wrote {OUT} ({len(text):,} chars, sha256 {hashlib.sha256(text.encode()).hexdigest()[:16]})")


if __name__ == "__main__":
    main()
