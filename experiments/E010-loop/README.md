# E010: the loop (V2, week of 2026-11-09)

Design: `docs/v2-design-2026-11-07.md` §3 (iterations), §4 (drift metric), §6 (week plan).

## E010-1: data profile in context

- Generator: `make_profile.py` (run with `~/.poppy/venv/bin/python experiments/E010-loop/make_profile.py`); output `profile.md`, computed from `data/processed/nyc_crashes.parquet`, the file every sandbox receives as `./data/crashes.parquet`.
- **Status: G1 passed (Bo, 2026-11-08).** Harness hook `POPPY_PROFILE` added to `run_pilot.py` and frozen (hashes in `E007-pilot-prompts/FROZEN.md`, section "Harness for E010"). Profile SHA-256 `0596d2a7bf974a11`.

**G1 checklist (Bo):**
1. Numbers and column facts only: no judgement words, no advice, no trap names.
2. Every column is treated by the same rule (no selection or highlighting).
3. No outcome aggregates: no sums of injured or killed by year or group, so no question's answer is in the profile.
   *Known overlap:* rows per year equal the `crashes` column of I1's gold reading `crashes_and_all_killed_by_year` (the per-crash denominator). It is a row count, not an answer; the profile has no killed counts.
4. How it enters the prompt: one block after the data dictionary, same text for every run (proposal: the harness appends `profile.md` to the dictionary when `POPPY_PROFILE` is set; the D v2 prompt file stays unchanged; the harness change gets a new hash in `E007-pilot-prompts/FROZEN.md`).

**What the profile shows that the dictionary did not (checked 2026-11-07):** borough NULL 19.9–38.1% per year in 2013–2025 (TR05; the dictionary says only "may be NULL"); rows per year 211,486 (2019) → 112,918 (2020) (TR01: the drop is visible, its cause is not); `number_of_persons_killed` NULL 24.4% in 2026, and 2026 covers 2026-01-01 to 2026-06-11 (TR08). TR07 ("police-reported") is already in the dictionary.
