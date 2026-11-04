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

## v0 scorer: acceptance on D v1 r1–r3 (2026-11-02, phase 2, `docs/v2-plan.md` §v0)

`scripts/score_runs.py` + `experiments/E007-pilot-prompts/gold_readings.json` run on the 54 option rows already on disk (no new model runs of D). Sheet: `results/D-v1-k3-openai-gpt-6-luna/scores.csv`; grader prompt and raw reply kept per option in `<run>/grader/<version>-p<pass>/o<k>/`.

**Acceptance (hand-confirmed cases of 10-19 must be flagged):**

| Case (hand, 10-19) | v0 result | By |
|---|---|---|
| TR05 undisclosed borough filter, A1, 9/9 options | `tr_TR05` FAIL 9/9; code flag `TR05@L..: WHERE borough = 'BROOKLYN'` on 3/3 runs | grader + code flag |
| TR01 per-crash rate across 2020 without caveat, A1 option 3, 3/3 | `tr_TR01` FAIL on A1 o3 in r1, r2, r3 | grader |
| TR01 same, I1 per-crash option, 2/3 runs | `tr_TR01` FAIL on I1-r1 o2 and I1-r3 o3 (r2 has no per-crash option) | grader (after the I1 item was aligned with A1's wording, g2) |
| Numbers: top option matches gold on every question (hand, 10-19) | `gold_match` = match for 37/54 options; 17 `unmatched`/`no_key` = readings the gold file does not have (A2's own day/night cuts, year-month, by-borough, crashes-with-motorist-death, shares) → human decides `h_gold` | machine |
| Exposure disclaimer present 9/9 (A1, A2, I1) | `tr_TR11` PASS 14/14 | grader |
| I1 required statement | `required_statement` PASS 9/9 | grader |

Provenance (`unsourced_numbers`): 0/54 on D v1 (every prose number is a cell or a one-step derivation of the option's own table). On the mimo A-v1 sheet (machine only, `E007-pilot-prompts/results/A-v1/scores.csv`) it flags A1-r1 (3 numbers) and A2-r2 (11 numbers) for the human; I1-r1's invented per-mile reasoning passes the number check and is the claim judge's job, as designed.

**Grader (GPT-6 Luna, review sandbox, 0 tool calls, median 12–14 s per option):**
- g1 run twice with the same prompt (p1, p2): agreement 556/577 = 0.964 on PASS/FAIL cells. Stable items: c1, c3, c7, c8, TR01, TR05, TR11, TR15 (all 100%). Least stable: c6 46/53, c5 49/53, NIGHTDEF 7/9, TR08 7/9.
- g2 (one JSON-robustness fix; code lines selected by keyword instead of the last 6,000 characters; a rule for insufficient questions so c1/c2 are not failed for "not per mile"; I1 `TR01` = the 2020 caveat, per-mile substitute moved to `PERMILE`): 0 unparsed; c2 FAIL on I1 went 4 → 0; agreement with g1-p1 on shared items 0.953.
- Sheets kept: `scores.g1-p1.csv`, `scores.g1-p2.csv` (same prompt), `scores.csv` (g2).

**What the grader says about D v1 (shadow, not scored until promoted):** silent-error rows 25/54, almost all framing: TR05 9/9 (A1), TR01 12/12 where a pooled or per-crash quantity spans 2020 (A1, I1, K2), TR08 6/9 (A2 windows reaching into 2026 or NULL handling not shown), TR15 3/4, NIGHTDEF 3/9. Unsupported claim 1/54; c5 (truncated axes on I1 count charts) 3/54. Clear-question criteria c1, c3, c7, c8: 0 fails.

**Done 2026-11-02 (review of the 54 rows):** the sheet came back filled by a **Codex AI review**, not by a human (every row's `notes` says so: "not an independent human calibration label"). It is used here as a second-model cross-check of the grader, not as the human calibration the plan requires; the ≥ 60 human labels and the blind batch of 20 are still open.

## Calibration pass 1: g2 → g3 against the Codex review (2026-11-02)

Review marks (by exception against g2): 32 overrides on 639 cells, agreement 0.950; 18 `h_gold` (17 `new_reading`, 1 `ok`, 0 `wrong`); 25 `first_failure` (TR05 9, TR01 9, TR08 3, other 4). The review found **two real scorer defects**: (1) the grader prompt showed `QUESTION ASKED: A2` — the question *id*, because `QUESTIONS` came from E006's P1–P10 set; (2) `gold_match` matched A2-r3 o3's fatal-crash share (0.290%, 20:00–05:59, 2012–2026) to the gold's derived killed/(killed+crashes) (0.257%, 18:00–05:59, 2013–2025) because the 0.05 absolute floor swallowed the difference.

**g3 changes (`scripts/score_runs.py`, archived g2 sheet with the review marks: `scores.g2-p1.csv`):** question text from `pilot_questions.json`; a `DATA FACTS` block (snapshot window, NULL borough 20–38%/year, NULL killed in May–June 2026, no NULL crash_time, 2020 reporting fall, no exposure; verified with DuckDB) so the grader stops inventing limitations; rules copied from SCORING.md §4: declared framing fields are part of the output, c6 FAILs when a disclosure item FAILs (an exposure disclaimer does not rescue an undisclosed exclusion), c6 FAILs on a superlative contradicted by the table, c5 does not fail a labelled non-zero axis on a line chart; derived gold ratios/shares use 1% relative with no floor (`tolerance()`); TR08 item for A2 is NA when the option uses no killed/injured counts.

| | g2 | g3 |
|---|---|---|
| agreement with the review, all cells (n = 639) | 0.950 | **0.978** |
| grader FAIL overturned / grader PASS overturned | 12 / 15 | 6 / 5 |
| c6 | 43/54 | 50/54 |
| NIGHTDEF | 6/9 | 9/9 |
| TR08 | 4/9 | 7/9 |
| c5, c4 | 51/54, 52/54 | 54/54, 54/54 |
| c8 | 51/54 | 51/54 (3 misses: axis title overlapping the footer on A1-r3, a vision limit) |
| gold A2-r3 o3 | match (false) | unmatched → `new_reading` |
| g3 vs g2 on the same cells | | 0.948 (the changes moved only the intended items) |
| unparsed / tool calls / median s per option | 0 / 0 / 12 | 0 / 0 / 12 |

Sheet under the review's overrides: silent-error rows 20/54, gold_wrong 0, gold_unverified 0. Caveat: g3 was tuned on the same rows it is compared with; the number is an upper bound, and the blind batch decides promotion.

**Three standard questions for Bo (the remaining disagreements are about the standard, not the grader):**
1. **TR01 on pooled comparisons.** The trap sheet lists TR01 for K2 (pooled weekday counts, 2013–2025) but not for A2 (pooled day vs night per-crash rates). g3 now fails c6 on three A2 options for "rates spanning 2020 without a caveat"; the review passed them. Either TR01 applies to every pooled window across 2020 (then A2 gets a TR01 item) or only to per-year comparisons (then K2 loses it).
2. **TR08 "handled".** `SUM(COALESCE(killed, 0))` over a window that includes 2026 is NULL-safe in syntax but biases fatality rates low; g3 passes it (A2-r3 o2), the review fails it. Proposed wording: "2026 rows with NULL killed counts are excluded, or the bias is disclosed; COALESCE to 0 alone is not handling."
3. **c6 on in-table superlatives.** K3-r2 o1/o3 call 110 (2020) the largest gap while the table gives 115 (2021); the grader passed both even with the new rule. If this matters, it is a mechanical check (superlatives in the prose vs the table), not a grader prompt change.

**Next:** F1 scored with g3 as is; the blind batch (20 rows, grader columns hidden, human labels) before any item is promoted; the three standard questions decided by Bo and recorded in SCORING.md §4 / `gold_readings.py` before g4.

## E009-F1: D v2 (free k, question-anchored interpretation) vs D v1 (2026-11-04, GPT-6 Luna, r1–r3)

Prompt `D_enumerate.v2.md` (hash in `E007-pilot-prompts/FROZEN.md`, frozen and pushed before the first run; confirmed by Bo). `PILOT_K=0`, `PILOT_STEPS=35` (measured first on K1/A2: 12–13 steps, 68–92 s, so 35 kept for all runs and the two measurement runs count as r1). Results `results/D-v2-kfree-openai-gpt-6-luna/` (18 runs, 42 options), listing for facet coding `options.md`, scores `scores.csv` (g5, machine + grader columns; `h_*` empty).

**Acceptance:** 18/18 complete (every option has chart + values + all fields; options.json parsed), 0 net calls, 0 step-limit hits, duplicates ≤ 1 per run (5 in total, all chart-type-only pairs on K1/K3).

| | D v1 (k = 3, 54 options) | D v2 (free k, 42 options) |
|---|---|---|
| k per run | 3 fixed | median 2, range 1–3 (clear 1–3; ambiguous 2–3; insufficient 2–3); K1-r3 gave a single option with p = 1.0 |
| distinct analytic framings per run | 3 (one run 2) | = k minus the chart-type duplicates (5 runs with one duplicate) |
| max probability | 0.36–0.55 | 0.35–1.0 (concentrates as k falls) |
| steps (median / max) | 14 / 22 | 14 / 20 |
| seconds (median) | 96 | 76 |
| `interpretation` | — | 40–70 words; every option names the part of the question it answers and what it leaves out |

**Pre-registered predictions:** median k on clear questions 2–3 ✓ (2); on ambiguous 3–5 ✗ (2–3, the model chooses fewer framings than v1 forced); duplicates rise beyond 3 options: not testable (k never exceeded 3); facet sets overlap across repeats: pending Bo's coding (`options.md`); the interpretation field does not by itself raise TR05/TR01 disclosures ✓ (TR05 FAIL 9/9, TR01 FAIL 5/5, as in v1); steps linear in k ✗ (steps flat, time falls with k).

**Scores (g5 grader, machine composite; v1 re-scored under the same g5 standard):** silent-error rows v1 15/54 (0.28) vs v2 15/42 (0.36); per question v1 → v2: K1 0/9 → 0/5, K2 0/9 → 0/7, K3 0/9 → 0/7, A1 9/9 → 9/9 (TR05 every option, both versions), A2 4/9 → 3/7, I1 2/9 → 3/7 (v2 produced a per-reported-crash option in all three runs, p = 0.7 in r1, TR01 FAIL each time). `--summary` (which applies the Codex overrides on v1) gives mean paired difference +0.05 on 6 questions; far below the MDE, unresolved. Other items: gold 33/42 match, 9 unverified (A2's own day/night cuts ×6, A1-r2 o1, I1-r3 o2, K2-r1 o3 share) → `h_gold`; unsourced 0/42 after the clock-time fix; unsupported_claim 1/42 (A2-r2 o1 "but not greater per-trip risk", borderline: a disclaimer read as a claim); TR15 4/5 (A1 "30 → 39, a 30% rise" and K3's cyclist-per-100-motorist ratio without a small-count qualification; v1 3/5); TR08 2/6 (v1 3/5); c1–c5, c7, c8 0 fails in v2 (v1 under g5: c2 1, c4 1, c8 1, all on K1-r3 o2 and K3-r1 o3; an earlier draft of this line quoted g3 counts). **Reading:** free k and the question-anchored interpretation change how many options come back and how they are explained, not the framing errors; the undisclosed Brooklyn filter and the per-crash denominators survive untouched, which is the result the treatments in plan §2 are meant to address.

**Grader versions in this entry:** g4 (standard decisions of 2026-11-04) failed c6 on plain death counts compared across years (14 v2 rows) because the data-facts line said "a per-reported-crash rate or a pooled count compared across years"; g5 restricts the caveat to per-reported-crash rates. g5 vs the Codex review on v1: 610/630 = 0.968 (K2 TR01 cells no longer exist). Both passes kept per run (`grader/g4-p1/`, `grader/g5-p1/`). Provenance regex now ignores clock times (`7:59 p.m.` had flagged "59").

**Pending (Bo):** facet coding from `options.md`; `h_gold` on the 9 unverified rows; the unsupported-claim row; decision on the reduced-labelling proposal (plan §v0) before any item is promoted.

## Calibration pass 2 (partial): second grader + disagreement triage (2026-11-04)

Design accepted by Bo (plan §v0): labels only where two graders disagree, plus 5 random audit rows per experiment; promotion per item from `--calibration`. Implemented in `scripts/score_runs.py` (`--grader2`, `--review`, `--apply-review`, `--calibration`, resume from records on disk).

**mimo-v2.6-flash-free (Bo's first choice):** graded 21 of the 42 D v2 options before the OpenCode free quota ran out ("Free usage limit reached"); calls took 80 s median with stalls up to 14 min. On those 21 options: 263 shared cells, agreement with Luna 0.954, 12 disagreements, 0 unparsed (one placeholder verdict on VMT). Items at 1.000 on this slice: c1–c5, c7, c8, NIGHTDEF, PERMILE, CAUSAL, TR07, required_statement. Lower: c6 0.81 (π 0.60), TR15 0.78, TR08 0.83, TR05 0.89, TR11 0.93, TR01 0.92. The disagreements are judgment calls, mimo the more lenient side: whether the declared denominator "crashes with Brooklyn recorded as borough" counts as disclosing the filter (TR05); whether "30 → 39, a 30% rise … despite fluctuation" qualifies small counts (TR15); whether "but not greater per-trip risk" is a disclaimer or a claim (unsupported_claim, c6).

**nemotron-3.5-super-vl-free (second try):** works (14–26 s per call, 0 tool calls, K1-r1 22/22 with Luna) but hit the same quota after 9 more options: the free limit is per account, not per model. Records of both models stay with the runs (`grader/g5-p1-mimo-v2.6-flash-free/`, `grader/g5-p1-nemotron-3.5-super-vl-free/`); the sheet's `m2_*` columns hold mimo for the 21 units it finished.

**For Bo now:** `results/D-v2-kfree-openai-gpt-6-luna/review.csv` = 12 disagreement cells (both verdicts and evidence shown) + 5 audit rows × every item (57 cells, verdicts hidden: A2-r1 o2, I1-r1 o2, K1-r1 o2, K2-r3 o2, K3-r3 o1). Fill `h` and `note`, then `--apply-review` and `--calibration`.

**Open:** the remaining 21 v2 options and all 54 v1 options need a second grader. Options: resume when the free quota resets (the resume feature skips finished records); a second Luna pass as a stopgap (same model: measures repeat stability, not independence); OpenCode Go. Codex is Luna behind another harness and needs a separate login, so it does not add independence.

## Calibration pass 2 (continued): Luna second pass on every option (2026-11-04)

Bo's decision: fill the second-grader columns with a second Luna pass (same model, same prompt, fresh sandbox) while the free quota is out. This measures **repeat stability of the grader, not independence**; the mimo records remain the only cross-model opinion (21 v2 options). Records: `grader/g5-p1-openai-gpt-6-luna/` in each run; the mimo-filled sheet and its review are archived as `scores.g5-p1-m2-mimo.csv` and `review.mimo.csv` (the mimo pass can be restored with `--grader2 mimo-v2.6-flash-free --records-only` once the quota resets and the missing 21 are run).

| | D v2 (42 options) | D v1 (54 options) |
|---|---|---|
| shared cells | 494 | 630 |
| disagreements | 4 (agreement 0.992) | 23 (0.963) |
| unparsed | 0 | 0 |
| seconds per call (median) | 12 | — |

Pass-1 repeat agreement on v1 was 0.964 (2026-11-02); the same model now gives 0.963 on v1 and 0.992 on v2, so Luna's self-agreement is stable and v2's fewer, shorter options are easier to grade consistently. On the 21 v2 options both second graders saw: mimo disagreed with Luna-1 on 12 of 246 cells, Luna-2 on 4, and Luna-2's 4 are a subset of mimo's 12 — the two-Luna comparison finds the cells where the standard itself is unclear, mimo adds its own leniency on top.

**What the Luna-2 disagreements are (27 cells):**
- *NA vs PASS on a trap that does not apply* (TR15 ×4, TR11 ×3; v1 and v2): both graders agree no claim was made; one writes NA, the other PASS. A labelling convention, not a scoring difference; the standard should say which (proposal: NA when the triggering claim is absent).
- *Luna-2 stricter, and right:* K3-r2 o1 c6 "largest gap was 110 deaths in 2020 (139 vs 29)" — the 2021 gap is 115 (134 vs 19) in the option's own `values_1.csv`; Luna-1 passed it, and it was the known agreed-but-wrong case of pass 1 (plan §v0). K1-r3 o2 c1/c3: the share-of-all-deaths option answers a different question; Luna-1 had already failed it on c2/c4, Luna-2 also fails c1/c3.
- *Luna-2 stricter, judgment calls for the human:* TR07 ×3 on K1 options that say "NYC annual totals" without calling them dataset counts (Luna-2 reads this as presenting an official toll; Luna-1 does not); A2-r2 o3 c2/c6/TR08, where Luna-2 reads the SQL as `COUNT(*)` with `COALESCE(killed, 0)` against a declared "complete records only" denominator (the code builds a `complete_crashes` table, so this needs a human reading of the query); K1-r1 o3 c4 heatmap vs annual totals; K3-r1 o3 c8 legend overlap (Luna-1 FAIL, Luna-2 PASS).
- *v2:* A1-r3 o1 TR15 (NA vs FAIL), A2-r1 o2 c6/TR08 and A2-r3 o3 c6 (whether "only crashes with complete injury and fatality counts" discloses the 2026 missing-killed bias and whether "2012–2025" must disclose the partial 2012).

**Calibration table (`--calibration`, both labels, 96 rows for the c-items):** c1/c2/c3/c5/c7 and unsupported_claim meet the agreement threshold; c6 0.927, TR15 0.882, TR08 0.875, TR11 0.912, TR07 0.786 do not; every trap item has n < 60. **No item is promoted:** the `h_*` cells the table counts as human on v1 (50) are the Codex review, not a person, and the audit/agreed-but-wrong columns read from them; v2 has no human cell yet. The table is a preview of the mechanism, not a validation.

**For Bo now:** `review.csv` in each results folder (Luna-2 based): v2 = 4 disagreement cells + 5 audit rows (57 cells); v1 = 23 disagreement cells + 5 audit rows (59 cells). `review.mimo.csv` keeps mimo's 12 cells on v2. Fill `h`/`note`, then `--apply-review` and `--calibration`. Two standard questions surfaced by this pass need a decision: NA vs PASS when a trap's triggering claim is absent; whether "NYC totals" without "in this dataset" fails TR07.

## Standard decisions 4–5 (g6), facet coding, gold re-derivation (2026-11-04, later)

**Bo's decisions on the two questions raised by the Luna second pass** (SCORING.md §4, items 4–5; grader prompt → **g6**; TR07 item text in `gold_readings.py`): (4) a trap item whose triggering claim is absent is NA, not PASS; (5) "NYC totals" / "NYC annual totals" / "killed in NYC" without "in this dataset" FAILS TR07: vague wording that reads as the citywide toll is caught. Applied to the v1 review cells as adjudications (12 cells: TR15/TR11 NA ×7, TR07 FAIL ×3 on K1-r2 o2/o3 and K1-r3 o3, and c6 FAIL on the same three rows by the existing rule that c6 fails when a disclosure item fails) and copied into `h_*` with `--apply-review`. The other 11 v1 disagreement cells and the 4 v2 cells stay open for Bo. The sheets are still g5 scores plus these adjudications; g6 is used from the next grading pass (F2/F3, the mimo resume) and a g6 re-score of v1/v2 is due before any cross-version comparison. Effect on the composite (`--summary`, human columns override): v1 silent-error 17/54 (K1 0/9 → 3/9), v2 15/42 unchanged; TR07 v1 3/9, v2 0/5.

**Gold, the 9 unverified v2 rows:** every cell of each option's `values.csv` was recomputed independently from the pinned Parquet using the option's declared metric, denominator and grouping (A1-r2 o1 injured+killed by year; A2's six day/night cuts at 06:00–19:59 vs 20:00–05:59 with the declared complete-record and window filters; I1-r3 o2 crashes with ≥ 1 motorist killed by year; K2-r1 o3 weekday share within year, 91 cells). All match. `h_gold = new_reading` on the 9 rows with a note that this is a machine re-derivation by Claude, not a human label; adding these readings to `gold_readings.py` is Bo's call (plan §4: a human judges a reading legitimate before it becomes gold). v2 now has 0 unverified gold rows.

**Facet coding (first pass by Claude; `results/D-v2-kfree-openai-gpt-6-luna/facets.csv`, table appended to `options.md`; Bo reviews the `bo_review` column):** 14 facets over 42 options. Per-question facet sets across r1–r3: K1 identical (count_by_year ×3); K2 r2 = r3 = {total, mean per date}, r1 adds weekday share by year; K3 all three contain counts_by_year, r1 adds the cyclist-per-100-motorist ratio; A1 every pair shares exactly 2 of 4 facets (killed_count in all three; injured / casualties / share-of-crashes rotate); A2 casualty_crash_share in all three, the second facet varies (fatal share, crashes per clock hour, casualties per crash); I1 {deaths count, deaths per reported crash} in all three, r3 adds fatal-crash count. Top facet (max p) stable on K1, K2, K3, A2; unstable on A1 (injured → casualties → casualties) and I1 (per-crash → count → per-crash). **Prediction check:** "facet sets overlap mostly (≥ 2 of 3 shared) on ambiguous questions and fully on clear ones" — ambiguous ✓ (A1 2 of 3–4 shared pairwise, A2 1–2 of 3–4: borderline), clear ✗ for K2 and K3 in the strict sense (r1 adds a facet the later repeats drop), ✓ for K1. The model's extra facets on clear questions are real analytic alternatives (per-date mean, ratio), not padding.

**F1 status after this:** run, scored, gold closed, facets coded (first pass). Open: Bo's review of `facets.csv`, the 15 remaining review cells, the A2-r2 o1 unsupported-claim call; F2 and F3 are with the teammates.

**Addendum (2026-11-04, relayed from Bo's other session):** decision (6) in SCORING §4: a disclaimer that reads as a data conclusion is judged by that reading. A2-r2 o1 → `h_unsupported_claim = FAIL`, `h_c6 = FAIL`; v2 silent-error stays 15/42: the g5 grader had already failed this row on unsupported_claim (the 1/42), so Bo's verdict confirms the grader rather than adding a row. Harness support for F2 added: `POPPY_QSET=<name>` loads `experiments/<EXP>/questions.<name>.json` with a `base` id per phrasing; the scorer takes gold, traps and type from `base` and shows the grader the asked phrasing (regression: 0 diffs on the 96 existing units). F2/F3 can start.
