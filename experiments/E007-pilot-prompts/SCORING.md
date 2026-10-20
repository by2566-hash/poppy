# Scoring the phase-1 comparison (6 pilot questions; mimo and GPT-6 Luna; arms A, B, C, D)

- **Status:** agreed 2026-10-19 (Bo). For whoever scores; written before any scoring.
- **Rubric:** the team's 8 binary criteria (question answered, appropriate measure, appropriate chart type, useful comparison, faithful visual encoding, evidence-aware presentation, clear and readable, visually well presented). Blind: hide the arm and model; shuffle the order.
- **Caveat to state with every result:** B's prompts were tuned on these 6 questions, so B is favoured on them. P1–P10 stay untouched for phase 2.

## 1. How D (three options) is compared with the single-answer arms

Decided before scoring; report all three readings, **D-top is the headline**:

| Reading | What is scored | Compared with | Answers |
|---|---|---|---|
| **D-top** | the option with the highest `probability` in `options.json` (tie: lowest id) | A, B, C one-to-one | does asking for options change the answer the model ranks first? |
| D-best | the best of the three options, per the scorer | A, B, C | the ceiling if a user picks (Ryan's product idea) |
| D-all | each option scored, then averaged | A, B, C | does producing three options lower the quality of each? |

Score each D option as its own chart + values + `answer` field. D's `ANSWER:` line lists the options neutrally and is not scored as an answer.

## 2. Repeats

Luna: each arm 3 runs per question (r1–r3), so differences can be told from run-to-run variation; report per-question pass counts out of 3 (pass^3 = all three pass). mimo: the existing single runs (A-v1, B-v4-v3, C-v3); state that they are single runs. Runner: `PILOT_REPS=2,3 … run_pilot.py <arm> …` adds repeats without touching r1.

## 3. Cost

Use the full token fields (`input, output, reasoning, cache_read, cache_write, total`). Runs recorded before 2026-10-19 kept only input/output in `meta.json`; recompute with `python3 scripts/token_totals.py <results dir>`. Luna reports almost all input as cache (≈ 99%), so input/output alone understates cost about 40×. Report direction arrows (cost ↑↓→, quality ↑↓→) with the numbers beneath, as Ryan asked.

## 4. Known traps per question (for criterion 6, "evidence-aware presentation", and criterion 2)

The trap catalog is evaluation ground truth, not a hint to the model; prompts never mention it. Numbers checked with DuckDB on the pinned snapshot (2026-10-19) or taken from `docs/scenario-data-v1.md` (verified 2026-10-03). A chart or answer that *uses* a trapped quantity without saying so fails criterion 6; saying so, or avoiding the trapped quantity, passes.

| Q | Question (short) | Traps that apply | What to look for |
|---|---|---|---|
| K1 | Pedestrians killed per year, 2013–2025 | TR07 open-data deaths ≠ official counts (2025: 229 all deaths here vs 205 NYC DOT) | Fine to report the open-data counts; claiming they are the official toll is a flag. Causal asides ("pandemic") = criterion 6 fail. Gold: 176 … 119 |
| K2 | Crashes by day of week, 2013–2025 | TR01 recording change (crashes 211,486 in 2019 → 110,558 in 2021 → 85,546 in 2025); unequal day counts (Tue and Wed occur 679 times, other weekdays 678) | Pooled counts are dominated by pre-2020 years; per-day averages need the 678/679 denominators; "32% fewer on Sunday" type arithmetic (true: 24% fewer, or Friday 32% more) |
| K3 | Motorist vs cyclist deaths per year | TR15 small numbers (cyclist deaths 10 in 2018 → 31 in 2019); TR03 deaths outside the three mode columns (residual 6–20 per year, 2021–2025) | "Tripled", "gap widest in 2013" (true only as a ratio: absolute gap is widest in 2021, 115) |
| A1 | Brooklyn pedestrian safety since 2013 | **TR05** borough missing for 19.9–38.1% of crashes per year (2013–2025): `borough = 'BROOKLYN'` silently drops them; TR11 no pedestrian exposure (counts are not risk); **TR01** per-crash denominators collapse after 2020; TR02 COVID 2020; TR15 deaths are small (30 → 39) | Undisclosed borough filter, per-crash rates across 2020 without a caveat, and "safer" / "less safe" claims from counts each fail criterion 6 |
| A2 | Are streets more dangerous at night? | TR11 no traffic volume by hour (per-crash severity ≠ risk per trip); **TR08** killed count NULL in 87.8% of May-2026 and 100% of June-2026 rows (8,877 of the file's 8,913 NULL-killed rows are outside 2013–2025): a window that includes 2026 biases fatality rates low, and `SUM(injured + killed)` drops those rows; TR13 time heaping (00:00 is 1.12% of crashes 2013–2025); TR01 changes the crash mix behind per-crash rates | Window used (2012–2026 vs 2013–2025); NULL-safe sums; the definition of "night" stated; severity-per-crash described as such |
| I1 | Motorist risk per mile driven, 2013–2025 | Insufficient evidence: no vehicle-miles in the data; **TR01** "per reported crash" is not a substitute for per mile; TR07; TR15 | The correct answer says per-mile risk cannot be determined from this data. Any per-mile number, VMT assumed or imported, or a per-crash rate presented as risk fails criterion 6 |

Recorded so far (Claude, D v1 on Luna): A1 option 1–3 use `borough = 'BROOKLYN'` without disclosure (TR05); A1 option 3 and I1 option 2 use per-reported-crash rates across 2020 without a caveat (TR01). Numbers in those options are correct; the framing misleads.
