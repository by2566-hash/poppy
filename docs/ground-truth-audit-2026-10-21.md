# Ground-truth audit (2026-10-21)

Before any optimization is judged against the gold, the gold itself must be right. This audit re-derives every reference series with queries written from the question text (not copied from the gold scripts), checks the data snapshot, and lists the interpretive choices the gold encodes.

## 1. Data snapshot

- `data/processed/nyc_crashes.parquet`: 2,269,187 rows, 2012-07-01 → 2026-06-11; content fingerprint (row count, checksum of ids, date range, injured/killed sums) verified by `scripts/check_env.py` on every machine before a run (`scripts/env_expected.json`). The city stopped updating the source on 2026-06-15, so the snapshot is stable.
- Analysis window for all questions: 2013-01-01 ≤ crash_date < 2026-01-01 (13 full years; the partial years 2012 and 2026 are excluded, which is trap TR09 handled by construction).

## 2. Pilot gold (`experiments/E007-pilot-prompts/gold_pilot.json`, produced by `gold_pilot.py`)

Independent recomputation (DuckDB, own SQL, 2026-10-21): **all 6 series match row for row.**

| Q | Gold series | Interpretive choice encoded in the gold | Numbers affected |
|---|---|---|---|
| K1 | pedestrians killed per year | none | — |
| K2 | crashes per day of week | index 0 = Sunday (DuckDB `dayofweek`); runs that use ISO 1 = Monday are not wrong | — |
| K3 | motorist and cyclist deaths per year | deaths outside the three mode columns (TR03) are not in either series; the gold does not claim they sum to all deaths | 6–20 deaths per year 2021–2025 |
| A1 | Brooklyn pedestrians injured and killed per year | **`borough = 'BROOKLYN'`**: the 19.9–38.1% of crashes per year with no borough are excluded (TR05). The gold is the "Brooklyn-assigned records" reading, not the truth about Brooklyn | 25,354 injured and 567 killed pedestrians (2013–2025) have no borough and are in no borough's series |
| A2 | day (06:00–17:59) vs night: crashes, killed, injured | the day/night cut is one of several defensible ones; runs that choose 20:00–05:59 are compared on their own window, not on this series | — |
| I1 | motorist deaths per year | the question asks per mile; the gold is the count series a correct answer would plot while saying per-mile risk cannot be computed | — |

NULL handling: 36 rows in 2013–2025 have `number_of_persons_killed` NULL (8,877 of the file's 8,913 NULL-killed rows are in 2026); DuckDB `SUM` ignores NULLs, so the gold is unaffected; a run that computes `SUM(injured + killed)` drops those rows (the A2 bug in iteration 1).

## 3. Formal gold (`experiments/E006-mimo-screen/gold.json`, produced by `gold.py`), held out for phase 2

Independent recomputation (2026-10-21): **all 10 series match.**

| Q | Interpretive choice encoded |
|---|---|
| P3, P8 | crashes with no borough form their own `UNKNOWN` group, as the question text requires (no blank-string boroughs exist; only NULL) |
| P5 | `Unspecified` counts as a contributing factor (32.34% of crashes 2013–2025, TR06); a run that excludes it and says so is a different, legitimate reading; the gold does not exclude NULL rows by mistake (there are none with blank factors) |
| P7 | killed, injured and crash counts per year; the crash count crosses the 2020 recording change (TR01), so the gold series is correct and the *trend* drawn from it needs the caveat |
| P9, P10 | count series; the questions themselves are insufficient-evidence (per-ride risk; a hypothetical policy), so correctness is in the caveat, not the numbers |

## 4. Trap catalog numbers

`docs/scenario-data-v1.md` TR01–TR17 were verified on 2026-10-03; the per-question numbers in `experiments/E007-pilot-prompts/SCORING.md` §4 were recomputed on 2026-10-19 (borough NULL share by year 19.9–38.1%; crashes 2019/2021/2025; NULL-killed rows by year; time heaping 1.12%; weekday day-counts 678/679; cyclist deaths 10 → 31; hidden death residual).

## 5. Known limits of the gold as ground truth (to be fixed in phase 2, not before)

1. **The gold is one reading per question.** For A1, A2, P3, P5, P7–P10 several readings are legitimate when disclosed. A scorer must not fail a run for choosing a different disclosed reading; the trap sheet lists what must be disclosed. Phase 2 replaces "one gold series" with a **gold plan** (metric, denominator, grouping, required disclosures) plus the series for that plan.
2. **`gold_cover` is a lenient check.** It tests whether each gold number appears (rounded) anywhere in `values.csv`, ignoring keys and extra columns. It can be satisfied by coincidence and cannot detect a swapped year. Phase 2: key-aware comparison with tolerance.
3. **The gold covers plotted series only.** Derived numbers in the prose (percent changes, ratios, totals) have no gold; K2's "32% fewer" error was in such a number. Phase 2: recompute oracle over the prose.
4. **Gold was written by the same person who tuned prompts.** Acceptable for phase 1 (prompts never saw the gold; sandbox blocks reads), but phase 2's test split should have gold written by a non-tuner.
