# E001 — NYC crashes data card and trap verification

**Role:** you are the engineer on this experiment. Work only inside `experiments/E001-data-card/` and `data/processed/`. Read `AGENTS.md` and `docs/direction-v1.md` first.

## Goal

Turn the raw NYC Motor Vehicle Collisions Crashes table into an analysis-ready Parquet file, then produce a data card and a **verified trap catalog**. The trap catalog becomes the ground truth for scoring how agents handle vague questions (experiment E002), so every claim needs a saved query and a number.

Also measure how light the data engineering really is: record wall-clock time per step.

## Input

- `data/raw/nyc_crashes_h9gi-nx95.csv` — full export of NYC Open Data dataset `h9gi-nx95` (downloaded 2026-10-03; the city froze updates at 2026-06-15 pending a pipeline fix).

## Steps

1. **Load and type** with DuckDB into `data/processed/nyc_crashes.parquet`:
   - snake_case column names; `crash_date` as DATE; `crash_time` as TIME (or minutes since midnight); counts as INTEGER; latitude/longitude as DOUBLE; keep text columns as-is.
   - Save the conversion as `build_parquet.sql` (or `.py`). Record row count before and after; they must match.
2. **Profile** (`profile.sql` → `results/profile.md`): row count, date range, null rate per column, distinct counts, top 25 values for `borough`, `contributing_factor_vehicle_1`, `vehicle_type_code1`.
3. **Verify these candidate traps.** For each: the query (saved under `queries/Txx_*.sql`), the result table (CSV under `results/`), and a one-paragraph verdict: confirmed / not confirmed / partly, with numbers.
   - **T1 Reporting break 2019→2020:** crashes per year 2013–2025. Is the drop concentrated in crashes with zero injuries and zero deaths (property-damage-only) or also in injury crashes? Show both series per year.
   - **T2 Partial periods:** first and last dates; crashes per month for 2012 and 2026. Which years are incomplete?
   - **T3 Missing borough:** share of crashes with null/empty borough, per year. What would a naive `GROUP BY borough` silently drop?
   - **T4 Missing or invalid location:** share with null latitude/longitude, and with latitude = 0 or outside roughly (40.4, 41.0) / (-74.3, -73.6), per year.
   - **T5 "Unspecified" cause:** share of `contributing_factor_vehicle_1` = 'Unspecified' (and empty), per year; top 10 specific factors overall and for crashes with ≥1 death.
   - **T6 Messy vehicle types for e-bikes:** all distinct `vehicle_type_code1..5` values that plausibly mean e-bike / e-scooter / moped (case-insensitive patterns like `e-b`, `ebike`, `e bike`, `scoot`, `moped`); their counts; first year each spelling appears. How much would an exact match on one spelling undercount?
   - **T7 Cyclist and pedestrian outcomes:** cyclist injured/killed and pedestrian injured/killed per year 2013–2025.
   - **T8 Persons killed per year 2016–2025** (this is the answer to a "clear" control question; report the exact numbers).
   - Add any other trap you discover while profiling (name it T9+), but keep the list tight.
4. **Write `REPORT.md`** (≤ 800 words + tables): schema summary, data-quality summary, the trap catalog as a table (id, trap, evidence number, which vague questions it would break, detection query file), DE effort (minutes per step, total), and open issues.

## Constraints

- No network access needed; do not download anything.
- No geospatial joins, no fuzzy matching beyond simple lowercase/regex normalization.
- Do not modify `data/raw/`.
- Append one entry to `experiments/LOG.md` in the existing format when done.
