# E009-lite — arm D iterations

## Measurement runs: K1 and A2 on GPT-6 Luna (2026-10-19, not an iteration)

Prompt `D_enumerate.v1.draft.md`, k = 3, step cap 30 (only to measure). Pre-checks the same day: `check_env.py` READY for `openai/gpt-6-luna` (key from `.env`, git-ignored), `check_model_vision.py` PASS (Luna reads an attached chart).

| Item | Complete | Options | Distinct (4 fields) | Distinct analytic (metric × denominator × grouping) | Steps | Time | Tokens (total / cache read / output) | Network |
|---|---|---|---|---|---|---|---|---|
| K1 | yes | 3/3 | 3 | **1** (bar, line, dot plot of the same series) | 11 | 76 s | 122k / 99k / 3.1k | 0 |
| A2 | yes | 3/3 | 3 | **3** (crash counts; share of crashes with injury or death; people harmed per 100 crashes) | 12 | 108 s | 164k / 133k / 4.4k | 0 |

Checked by hand:
- K1: all three options carry the exact gold series (176 … 119). The only variation available on a clear count question is the chart type, and that is what the model produced. Expected, not a defect.
- A2: genuinely different analytic framings; every option's answer states that per-trip or per-mile risk cannot be judged without exposure data (no unsupported claim). Option 3 (people injured or killed per 100 crashes: night 39.29, day 30.25) matches DuckDB with `COALESCE`; the NULL-dropping sum that mimo's A used in iteration 1 would give 39.01 / 30.02. Charts start at zero and carry a footnote on the missing exposure denominator. Minor: option 1's y axis uses scientific notation (1e6).
- Probabilities sum to 1. A2: counts 0.2, the two rate framings 0.4 each (a tie at the top).
- ANSWER line neutral, one sentence per option in order, as instructed.

Consequences (measurement, not prompt):
1. **Distinctness is reported at two levels**: `n_distinct_framings` (with chart type) and `n_distinct_analytic` (without). On clear questions D is expected to vary only the encoding; on ambiguous ones the analytic level is the one that matters for Ryan's "three accurate ways to represent the data".
2. **Free-text framing fields over-count distinctness** when the same framing is worded differently. For scoring, the 18 options of the acceptance round are coded by hand into framing labels; the code count is a first pass.
3. **Token accounting fixed in the harness**: `call_model` summed only `input` and `output`. Luna reports almost the whole prompt as cache reads/writes ("input" ≈ 35 tokens per run), so cost was understated ~40×. All six fields are now recorded (`input, output, reasoning, cache_read, cache_write, total`); `scripts/token_totals.py` recomputes them from `events.jsonl` for older runs (mimo runs and the teammates' Luna runs alike).

Step cap: **25** (Bo, 2026-10-19), ≈ 2× the largest observed (11, 12; a parallel K1 run started from another terminal took 14). A run that hits the cap during the acceptance round is logged as a finding, not fixed by raising the cap mid-round.

## Iteration 1: acceptance round (6 pilot questions, GPT-6 Luna, 2026-10-19)

Prompt `D_enumerate.v1.md` (identical to the measured draft), k = 3, step cap 25, config `opencode.enumerate.json`. Committed before the run.
Acceptance (format and boundaries only): ≥ 5/6 complete; no network or out-of-folder access; duplicate framings (all four fields equal) ≤ 1 across the round.

**Result: acceptance met in iteration 1; D v1 frozen.**

| Item | Complete | Steps | Time | Distinct (4 fields) | Distinct analytic | Duplicates | Network | Hit cap |
|---|---|---|---|---|---|---|---|---|
| K1 | yes | 12 | 92 s | 3 | 3 | 0 | 0 | no |
| K2 | yes | 14 | 80 s | 3 | 3 | 0 | 0 | no |
| K3 | yes | 13 | 84 s | 3 | 3 | 0 | 0 | no |
| A1 | yes | 10 | 128 s | 3 | 3 | 0 | 0 | no |
| A2 | yes | 13 | 124 s | 3 | 3 | 0 | 0 | no |
| I1 | yes | 11 | 96 s | 3 | 3 | 0 | 0 | no |

6/6 complete (≥ 5/6 required), no boundary violation, 0 duplicate framings, steps 10–14 under the cap of 25. Frozen: `prompts/frozen/D_enumerate.v1.md` SHA-256 `a18643123c55bfd00cabea8dcbb4f806463a50d79723d3e5e42ef355e3b14e19`; config `opencode.enumerate.json` SHA-256 `49a78d1b921d89e93cb3b046d05ca74ef72464357764467bc3822ff5979fc69f`. No prompt edit was needed, so iterations 2–3 are not used.

Spot checks against DuckDB (Claude): K2 shares 15.89% / 12.08%; K3 gap 51 (2019) to 115 (2021); I1 54.0 → 94.7 motorist deaths per 100k crashes and motorist share 37.0% → 35.4%; A1 Brooklyn pedestrians injured 3,641 → 2,835, killed 30 → 39; A2 injured per 100 crashes night 40.45 / day 31.01, fatal crashes per 1,000 2.90 / 1.08. All match.

Observations (effect, not acceptance; inputs for phase 2):
1. Clear questions also got analytic variety on Luna (K1: totals, by borough incl. unknown, month × year heatmap; K2: counts, shares, per-year shares; K3: counts, difference, shares). The measurement run's K1 varied only the chart type; the same prompt gives different kinds of variety from run to run.
2. Every answer on A1, A2 and I1 states that per-trip / per-mile risk cannot be judged without exposure data. The unsupported per-mile claim of A (mimo and Luna-free runs) does not appear.
3. **Silent framing errors remain** and are not caught by the in-run self-check: A1 filters `borough = 'BROOKLYN'`, dropping the 20–23% of crashes with no borough (TR05), without saying so; A1 option 3 (pedestrian casualties per 1,000 crashes, +51.5%) and I1 option 2 (deaths per 100k crashes, "did not decline") divide by total reported crashes, whose count collapsed after the 2020 reporting change (TR01), without a caveat. Numbers are computed correctly; the framings mislead. This is the class of error the phase-2 evaluation layer targets (claim checks and gold plans), and a case for B's reviewer on top of D.
4. Probabilities: the plain count framing is usually ranked first on clear questions (0.45–0.5) and not on ambiguous ones (A2: 0.3, ties at 0.3/0.4). Ordinal only.

## Repeats r2, r3 (D v1 frozen, GPT-6 Luna, 2026-10-19)

Added with `PILOT_REPS=2,3`, so every question has 3 runs (SCORING.md §2).

| Q | Complete | Steps (r1, r2, r3) | Distinct analytic framings | Top-probability framing (all 3 runs) |
|---|---|---|---|---|
| K1 | 3/3 | 12, 14, 14 | 3, 2, 3 | annual count of pedestrians killed |
| K2 | 3/3 | 14, 14, 12 | 3, 3, 3 | crash count by weekday |
| K3 | 3/3 | 13, 18, 22 | 3, 3, 3 | annual deaths per road-user group |
| A1 | 3/3 | 10, 16, 13 | 3, 3, 3 | annual count of pedestrians injured (Brooklyn) |
| A2 | 3/3 | 13, 19, 19 | 3, 3, 3 | a per-crash severity rate (injured per 100 / any death / harmed per crash) |
| I1 | 3/3 | 11, 18, 15 | 3, 3, 3 | annual count of motorist deaths |

18/18 complete; steps 10–22 (one run ≥ 20: K3 r3 at 22, under the cap of 25); no network calls.

**Mode share:** on 5 of 6 questions the top-probability option is the plain count, in all three runs: the framing a single-answer run gives first. Only A2 ranks a rate first. This matches the "the model's first choice is the typical answer" prediction; the alternatives come second and third.

**Trap incidence, confirmed by hand (heuristic scan over-flagged three I1 options that use deaths or crash counts, not per-crash rates):**

| Trap | Where | Runs affected | Note |
|---|---|---|---|
| TR05 undisclosed borough filter | A1, all options | 3/3 (9/9 options) | none mentions the 19.9–38.1% of crashes per year with no borough |
| TR01 per-reported-crash denominator across 2020, no caveat | A1 option 3 | 3/3 | 78.1 → 118.3 per 1,000 crashes, or 7.4% → 11.4% of crash records; largely the 2020 recording change |
| TR01 same | I1 option with a per-crash rate | 2/3 | r2 chose crash counts instead |
| Exposure disclaimer (no per-trip / per-mile risk) | A1, I1, A2 | 9/9 runs, every option | consistent |

These are systematic, not run-to-run noise: the in-run self-check does not catch them. They are the phase-2 fourth silent-error component (misleading framing).
