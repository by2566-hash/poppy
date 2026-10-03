"""Reproduce E001 data conversion, profile, trap tables, and timing receipt."""
from __future__ import annotations

import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments" / "E001-data-card"
RESULTS = EXPERIMENT / "results"
PARQUET = ROOT / "data" / "processed" / "nyc_crashes.parquet"


def run_query(con: duckdb.DuckDBPyConnection, sql_path: Path, output: Path) -> float:
    started = time.perf_counter()
    relation = con.execute(sql_path.read_text())
    relation.df().to_csv(output, index=False, quoting=csv.QUOTE_MINIMAL)
    return time.perf_counter() - started


def markdown_table(headers: list[str], rows: list[dict[str, str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "")) for header in headers) + " |")
    return "\n".join(lines)


def main() -> None:
    started_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")
    wall_start = time.perf_counter()
    RESULTS.mkdir(parents=True, exist_ok=True)
    (ROOT / "data" / "processed").mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute("SET preserve_insertion_order = false")
    timings: dict[str, float] = {}

    step = time.perf_counter()
    source_rows = con.execute(
        "SELECT count(*) FROM read_csv_auto(?, header=true, all_varchar=true, sample_size=-1, null_padding=true)",
        [str(ROOT / "data" / "raw" / "nyc_crashes_h9gi-nx95.csv")],
    ).fetchone()[0]
    # SQL paths are relative to the repository root by design.
    import os

    os.chdir(ROOT)
    con.execute((EXPERIMENT / "build_parquet.sql").read_text())
    parquet_rows = con.execute("SELECT count(*) FROM read_parquet(?)", [str(PARQUET)]).fetchone()[0]
    if source_rows != parquet_rows:
        raise RuntimeError(f"Row-count mismatch: source={source_rows}, parquet={parquet_rows}")
    timings["load_and_type"] = time.perf_counter() - step
    (RESULTS / "row_counts.json").write_text(
        json.dumps({"source_rows": source_rows, "parquet_rows": parquet_rows, "match": True}, indent=2) + "\n"
    )

    step = time.perf_counter()
    summary = con.execute((EXPERIMENT / "profile_summary.sql").read_text()).df()
    summary.to_csv(RESULTS / "profile_summary.csv", index=False)
    profile_path = EXPERIMENT / "profile.sql"
    columns = con.execute(profile_path.read_text()).df()
    columns.to_csv(RESULTS / "profile_columns.csv", index=False)
    top_values = con.execute((EXPERIMENT / "profile_top_values.sql").read_text()).df()
    top_values.to_csv(
        RESULTS / "profile_top_values.csv", index=False
    )
    summary_text = markdown_table(list(summary.columns), summary.astype(str).to_dict("records"))
    columns_text = markdown_table(
        ["column_name", "null_pct", "distinct_count"],
        columns[["column_name", "null_pct", "distinct_count"]].astype(str).to_dict("records"),
    )
    top_text = markdown_table(
        ["column_name", "value", "occurrences", "pct"],
        top_values.astype(str).to_dict("records"),
    )
    (RESULTS / "profile.md").write_text(
        "# NYC Crashes Profile\n\n"
        "## Dataset summary\n\n" + summary_text + "\n\n"
        "## Null rate and distinct count by column\n\n" + columns_text + "\n\n"
        "## Top values (up to 25 per requested column)\n\n" + top_text + "\n"
    )
    timings["profile"] = time.perf_counter() - step

    trap_files = {
        "T01_reporting_break": "T01_reporting_break.sql",
        "T02_partial_periods": "T02_partial_periods.sql",
        "T03_missing_borough": "T03_missing_borough.sql",
        "T04_invalid_location": "T04_invalid_location.sql",
        "T05_unspecified_factor": "T05_unspecified_factor.sql",
        "T05_top_factors": "T05_top_factors.sql",
        "T06_micromobility_types": "T06_micromobility_types.sql",
        "T07_vulnerable_road_users": "T07_vulnerable_road_users.sql",
        "T08_persons_killed": "T08_persons_killed.sql",
    }
    for label, filename in trap_files.items():
        timings[label] = run_query(
            con,
            EXPERIMENT / "queries" / filename,
            RESULTS / f"{label}.csv",
        )

    timings["total_computation"] = time.perf_counter() - wall_start
    con.close()
    (RESULTS / "timings.json").write_text(
        json.dumps(
            {
                "started_utc": started_utc,
                "finished_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "wall_minutes": round(timings["total_computation"] / 60, 3),
                "steps_seconds": {key: round(value, 3) for key, value in timings.items()},
            },
            indent=2,
        )
        + "\n"
    )
    print(json.dumps({"source_rows": source_rows, "parquet_rows": parquet_rows, "timings": timings}, indent=2))


if __name__ == "__main__":
    main()
