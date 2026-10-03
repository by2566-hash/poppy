# E001 — NYC Crashes Data Card and Trap Verification

## Result

The typed Parquet contains **2,269,187 rows**, matching the raw CSV row count (2,269,187). It spans **2012-07-01 through 2026-06-11**. The conversion is reproducible in [`build_parquet.sql`](build_parquet.sql); query outputs and source SQL are saved under `queries/` and `results/`.

## Data card

- **Schema:** 29 columns. `crash_date` is DATE, `crash_time` TIME, latitude/longitude DOUBLE, eight injury/fatality count fields INTEGER, collision ID BIGINT, and remaining fields VARCHAR. Collision IDs are distinct for all rows.
- **Quality:** borough is null for 30.47%; either coordinate is null for 10.61%; first contributing factor is null for 0.36%. Factor fields 3–5 are sparse: 92.76%, 98.34%, and 99.55% null respectively. Full per-column rates, distinct counts, and top values are in [`results/profile.md`](results/profile.md).

## Trap catalog

| ID | Verdict and evidence | Vague question it can break | Query |
|---|---|---|---|
| T1 | **Partly confirmed.** From 2019 to 2020 total crashes fell from 211,486 to 112,918; strict PDO fell 166,047 to 79,556, while injury crashes also fell 45,439 to 33,362. The decline is larger in PDO, but not limited to it; counts alone do not establish a reporting cause. Rows with unresolved outcomes are shown separately. | “Did crashes become safer after 2019?” | [`T01`](queries/T01_reporting_break.sql) |
| T2 | **Confirmed.** First/last crash dates are 2012-07-01 and 2026-06-11. 6 months appear for 2012 (July–December); 6 appear for 2026, and June ends on day 11. | Full-year or year-over-year comparisons at either edge | [`T02`](queries/T02_partial_periods.sql) |
| T3 | **Confirmed.** Borough is missing on 691,375 rows (30.47%) overall; annual peak is 38.12% in 2017. A borough `GROUP BY` omits null/empty-borough crashes. | “Which borough has the most crashes?” | [`T03`](queries/T03_missing_borough.sql) |
| T4 | **Confirmed.** Either coordinate is null on 240,806 rows (10.61%). Zero-coordinate share peaks at 2.25% in 2026; nonzero rough-bound violations peak at 75 rows in 2017. | Neighborhood maps, hotspot comparisons, or mapped crash rates | [`T04`](queries/T04_invalid_location.sql) |
| T5 | **Confirmed.** Vehicle 1 cause is `Unspecified` in 33.34% of crashes (756,643); empty/null factor 1 is 0.36%. Among non-unspecified labels, the leading factor is Driver Inattention/Distraction (462,105 rows); for crashes with a death, it is Driver Inattention/Distraction (434). | “What causes the most crashes/deaths?” | [`T05 yearly`](queries/T05_unspecified_factor.sql), [`T05 top factors`](queries/T05_top_factors.sql) |
| T6 | **Confirmed.** Pattern matching returns 94 distinct candidate labels across vehicle fields 1–5 and 30,490 occurrences. Literal `E-Bike` alone finds 12,366; an exact one-spelling match misses 59.44% of pattern matches. | “How many crashes involved e-bikes/scooters?” | [`T06`](queries/T06_micromobility_types.sql) |
| T7 | **Partly confirmed.** Counts do not provide exposure rates. Cyclist injuries/deaths were 4,075/11 in 2013 and 5,358/23 in 2025; pedestrian injuries/deaths were 11,988/176 and 9,134/119. These are burden counts, not per-trip safety. | “Are cyclists/pedestrians safer than before?” | [`T07`](queries/T07_vulnerable_road_users.sql) |
| T8 | **Control verified.** Persons killed per year (not fatal crashes): see exact series below. | Clear control question: “How many people were killed each year?” | [`T08`](queries/T08_persons_killed.sql) |

### T1 series: crash counts

| Year | All crashes | PDO crashes | Injury crashes | Outcome unresolved |
|---|---|---|---|---|
| 2013 | 203,742 | 163,469 | 40,273 | 0 |
| 2014 | 206,046 | 168,342 | 37,704 | 0 |
| 2015 | 217,708 | 179,668 | 38,040 | 0 |
| 2016 | 229,833 | 185,592 | 44,239 | 2 |
| 2017 | 231,007 | 186,314 | 44,681 | 12 |
| 2018 | 231,564 | 185,781 | 45,774 | 9 |
| 2019 | 211,486 | 166,047 | 45,439 | 0 |
| 2020 | 112,918 | 79,556 | 33,362 | 0 |
| 2021 | 110,558 | 71,748 | 38,809 | 1 |
| 2022 | 103,887 | 64,551 | 39,336 | 0 |
| 2023 | 96,607 | 56,135 | 40,472 | 0 |
| 2024 | 91,316 | 51,087 | 40,229 | 0 |
| 2025 | 85,546 | 48,126 | 37,420 | 0 |

### T8 control answer: persons killed

| Year | Persons killed |
|---|---|
| 2016 | 246 |
| 2017 | 256 |
| 2018 | 231 |
| 2019 | 244 |
| 2020 | 269 |
| 2021 | 297 |
| 2022 | 290 |
| 2023 | 280 |
| 2024 | 268 |
| 2025 | 229 |

## Data engineering effort

Measured with `time.perf_counter()` in [`run_experiment.py`](run_experiment.py); report/log generation time is recorded by [`finalize_report.py`](finalize_report.py).

| Step | Wall time (minutes) |
|---|---:|
| Load/type and row-count parity | 0.10330 |
| Profile | 0.01035 |
| Trap queries (T1–T8) | 0.00410 |
| Report and log generation | 0.00006 |
| Pipeline total (excluding this report write) | 0.11787 |
| Total measured processing | 0.11793 |

## Open issues

- No cycling, walking, or traffic-volume exposure denominator is present, so outcome counts cannot answer per-trip risk.
- The 2019–2020 step change is descriptive; this table cannot identify a reporting-policy or behavior cause.
- Coordinate bounds are a rough NYC screen, not a geocoding validation. The 2026 data is partial through 2026-06-11.
