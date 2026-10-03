"""Build the E001 report and append its experiment-log entry from saved results."""
from __future__ import annotations

import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments" / "E001-data-card"
RESULTS = EXP / "results"


def rows(name: str) -> list[dict[str, str]]:
    with (RESULTS / name).open(newline="") as f:
        return list(csv.DictReader(f))


def table(headers: list[str], body: list[list[str]]) -> str:
    return "\n".join(
        ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
        + ["| " + " | ".join(row) + " |" for row in body]
    )


def pct(value: str, digits: int = 2) -> str:
    return f"{float(value):.{digits}f}%"


def main() -> None:
    started = time.perf_counter()
    counts = json.loads((RESULTS / "row_counts.json").read_text())
    times = json.loads((RESULTS / "timings.json").read_text())
    profile = {r["column_name"]: r for r in rows("profile_columns.csv")}
    overall = rows("profile_summary.csv")[0]
    t1 = {int(r["year"]): r for r in rows("T01_reporting_break.csv")}
    t2 = rows("T02_partial_periods.csv")
    t3 = rows("T03_missing_borough.csv")
    t4 = rows("T04_invalid_location.csv")
    t5 = {int(r["year"]): r for r in rows("T05_unspecified_factor.csv")}
    factors = rows("T05_top_factors.csv")
    unspecified = next(
        r for r in rows("profile_top_values.csv")
        if r["column_name"] == "contributing_factor_vehicle_1" and r["value"] == "Unspecified"
    )
    micromobility = rows("T06_micromobility_types.csv")
    t7 = {int(r["year"]): r for r in rows("T07_vulnerable_road_users.csv")}
    t8 = rows("T08_persons_killed.csv")

    t2_by_year: dict[int, list[dict[str, str]]] = {}
    for r in t2:
        t2_by_year.setdefault(int(r["year"]), []).append(r)
    t3_peak = max(t3, key=lambda r: float(r["missing_pct"]))
    t3_total_crashes = sum(int(r["crashes"]) for r in t3)
    t3_total_missing = sum(int(r["missing_borough"]) for r in t3)
    t3_overall_pct = 100.0 * t3_total_missing / t3_total_crashes
    t4_zero_peak = max(t4, key=lambda r: float(r["zero_coordinate_pct"]))
    t4_bounds_peak = max(t4, key=lambda r: int(r["outside_rough_bounds"]))
    top_all = next(r for r in factors if r["scope"] == "all_crashes")
    top_fatal = next(r for r in factors if r["scope"] == "fatal_crashes")
    bike = next(r for r in micromobility if r["type_code"] == "E-Bike")
    top_vehicles = next(r for r in rows("profile_top_values.csv") if r["column_name"] == "vehicle_type_code1")

    t1_rows = [
        [str(y), f"{int(t1[y]['crashes']):,}", f"{int(t1[y]['pdo_crashes']):,}", f"{int(t1[y]['injury_crashes']):,}", f"{int(t1[y]['outcome_unknown']):,}"]
        for y in range(2013, 2026)
    ]
    t8_rows = [[r["year"], f"{int(float(r['persons_killed'])):,}"] for r in t8]

    report = f"""# E001 — NYC Crashes Data Card and Trap Verification

## Result

The typed Parquet contains **{int(counts['parquet_rows']):,} rows**, matching the raw CSV row count ({int(counts['source_rows']):,}). It spans **{overall['first_date']} through {overall['last_date']}**. The conversion is reproducible in [`build_parquet.sql`](build_parquet.sql); query outputs and source SQL are saved under `queries/` and `results/`.

## Data card

- **Schema:** {len(profile)} columns. `crash_date` is DATE, `crash_time` TIME, latitude/longitude DOUBLE, eight injury/fatality count fields INTEGER, collision ID BIGINT, and remaining fields VARCHAR. Collision IDs are distinct for all rows.
- **Quality:** borough is null for {pct(profile['borough']['null_pct'])}; either coordinate is null for {pct(profile['latitude']['null_pct'])}; first contributing factor is null for {pct(profile['contributing_factor_vehicle_1']['null_pct'])}. Factor fields 3–5 are sparse: {pct(profile['contributing_factor_vehicle_3']['null_pct'])}, {pct(profile['contributing_factor_vehicle_4']['null_pct'])}, and {pct(profile['contributing_factor_vehicle_5']['null_pct'])} null respectively. Full per-column rates, distinct counts, and top values are in [`results/profile.md`](results/profile.md).

## Trap catalog

| ID | Verdict and evidence | Vague question it can break | Query |
|---|---|---|---|
| T1 | **Partly confirmed.** From 2019 to 2020 total crashes fell from {int(t1[2019]['crashes']):,} to {int(t1[2020]['crashes']):,}; strict PDO fell {int(t1[2019]['pdo_crashes']):,} to {int(t1[2020]['pdo_crashes']):,}, while injury crashes also fell {int(t1[2019]['injury_crashes']):,} to {int(t1[2020]['injury_crashes']):,}. The decline is larger in PDO, but not limited to it; counts alone do not establish a reporting cause. Rows with unresolved outcomes are shown separately. | “Did crashes become safer after 2019?” | [`T01`](queries/T01_reporting_break.sql) |
| T2 | **Confirmed.** First/last crash dates are {overall['first_date']} and {overall['last_date']}. {len(t2_by_year[2012])} months appear for 2012 (July–December); {len(t2_by_year[2026])} appear for 2026, and June ends on day {int(t2_by_year[2026][-1]['last_date'].split('-')[-1])}. | Full-year or year-over-year comparisons at either edge | [`T02`](queries/T02_partial_periods.sql) |
| T3 | **Confirmed.** Borough is missing on {t3_total_missing:,} rows ({t3_overall_pct:.2f}%) overall; annual peak is {pct(t3_peak['missing_pct'])} in {t3_peak['year']}. A borough `GROUP BY` omits null/empty-borough crashes. | “Which borough has the most crashes?” | [`T03`](queries/T03_missing_borough.sql) |
| T4 | **Confirmed.** Either coordinate is null on {int(profile['latitude']['null_count']):,} rows ({pct(profile['latitude']['null_pct'])}). Zero-coordinate share peaks at {pct(t4_zero_peak['zero_coordinate_pct'])} in {t4_zero_peak['year']}; nonzero rough-bound violations peak at {int(t4_bounds_peak['outside_rough_bounds']):,} rows in {t4_bounds_peak['year']}. | Neighborhood maps, hotspot comparisons, or mapped crash rates | [`T04`](queries/T04_invalid_location.sql) |
| T5 | **Confirmed.** Vehicle 1 cause is `Unspecified` in {pct(unspecified['pct'])} of crashes ({int(unspecified['occurrences']):,}); empty/null factor 1 is {pct(profile['contributing_factor_vehicle_1']['null_pct'])}. Among non-unspecified labels, the leading factor is {top_all['factor']} ({int(top_all['crashes']):,} rows); for crashes with a death, it is {top_fatal['factor']} ({int(top_fatal['crashes']):,}). | “What causes the most crashes/deaths?” | [`T05 yearly`](queries/T05_unspecified_factor.sql), [`T05 top factors`](queries/T05_top_factors.sql) |
| T6 | **Confirmed.** Pattern matching returns {len(micromobility)} distinct candidate labels across vehicle fields 1–5 and {int(float(bike['matched_occurrences'])):,} occurrences. Literal `E-Bike` alone finds {int(bike['occurrences']):,}; an exact one-spelling match misses {pct(bike['exact_top_spelling_undercount_pct'])} of pattern matches. | “How many crashes involved e-bikes/scooters?” | [`T06`](queries/T06_micromobility_types.sql) |
| T7 | **Partly confirmed.** Counts do not provide exposure rates. Cyclist injuries/deaths were {int(float(t7[2013]['cyclist_injured'])):,}/{int(float(t7[2013]['cyclist_killed']))} in 2013 and {int(float(t7[2025]['cyclist_injured'])):,}/{int(float(t7[2025]['cyclist_killed']))} in 2025; pedestrian injuries/deaths were {int(float(t7[2013]['pedestrian_injured'])):,}/{int(float(t7[2013]['pedestrian_killed']))} and {int(float(t7[2025]['pedestrian_injured'])):,}/{int(float(t7[2025]['pedestrian_killed'])):,}. These are burden counts, not per-trip safety. | “Are cyclists/pedestrians safer than before?” | [`T07`](queries/T07_vulnerable_road_users.sql) |
| T8 | **Control verified.** Persons killed per year (not fatal crashes): see exact series below. | Clear control question: “How many people were killed each year?” | [`T08`](queries/T08_persons_killed.sql) |

### T1 series: crash counts

{table(['Year','All crashes','PDO crashes','Injury crashes','Outcome unresolved'], t1_rows)}

### T8 control answer: persons killed

{table(['Year','Persons killed'], t8_rows)}

## Data engineering effort

Measured with `time.perf_counter()` in [`run_experiment.py`](run_experiment.py); report/log generation time is recorded by [`finalize_report.py`](finalize_report.py).

| Step | Wall time (minutes) |
|---|---:|
| Load/type and row-count parity | {times['steps_seconds']['load_and_type']/60:.5f} |
| Profile | {times['steps_seconds']['profile']/60:.5f} |
| Trap queries (T1–T8) | {sum(v for k,v in times['steps_seconds'].items() if k.startswith('T'))/60:.5f} |
| Report and log generation | pending |
| Pipeline total (excluding this report write) | {times['steps_seconds']['total_computation']/60:.5f} |

## Open issues

- No cycling, walking, or traffic-volume exposure denominator is present, so outcome counts cannot answer per-trip risk.
- The 2019–2020 step change is descriptive; this table cannot identify a reporting-policy or behavior cause.
- Coordinate bounds are a rough NYC screen, not a geocoding validation. The 2026 data is partial through {overall['last_date']}.
"""
    report_path = EXP / "REPORT.md"
    report_path.write_text(report)

    log_path = ROOT / "experiments" / "LOG.md"
    log_marker = "## 2026-10-03 — E001: NYC crashes data card and trap verification"
    if log_marker not in log_path.read_text():
        with log_path.open("a") as f:
            f.write(
                f"\n{log_marker}\n\n"
                f"- **Setup:** typed the NYC crashes CSV to Parquet with DuckDB; profiled all columns and ran saved T1–T8 queries.\n"
                f"- **Result:** {int(counts['source_rows']):,} source rows = {int(counts['parquet_rows']):,} Parquet rows; 2019–2020 declines include PDO and injury crashes; missing borough/location and unspecified causes are material; one literal e-bike spelling misses most regex-matched labels. An initial regex escape returned no T6 matches; corrected and reran.\n"
                f"- **Next:** use this catalog to define E002 expected trap flags and interpretation coverage; keep outcome counts distinct from exposure-adjusted safety.\n"
            )

    report_seconds = time.perf_counter() - started
    times["steps_seconds"]["report_and_log_generation"] = round(report_seconds, 3)
    pipeline_seconds = float(times["steps_seconds"]["total_computation"])
    times["steps_seconds"]["total_including_report_generation"] = round(pipeline_seconds + report_seconds, 3)
    times["report_generation_seconds"] = round(report_seconds, 3)
    (RESULTS / "timings.json").write_text(json.dumps(times, indent=2) + "\n")
    # Replace the pending report time with the measured value and total.
    report = report_path.read_text().replace(
        "| Report and log generation | pending |",
        f"| Report and log generation | {report_seconds/60:.5f} |",
    ).replace(
        f"| Pipeline total (excluding this report write) | {pipeline_seconds/60:.5f} |",
        f"| Pipeline total (excluding this report write) | {pipeline_seconds/60:.5f} |\n| Total measured processing | {(pipeline_seconds+report_seconds)/60:.5f} |",
    )
    report_path.write_text(report)


if __name__ == "__main__":
    main()
