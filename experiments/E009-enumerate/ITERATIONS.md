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
