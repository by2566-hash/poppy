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

## g6 re-score of D v1 and D v2 (2026-11-04, Bo's request)

Both labels re-scored from scratch with g6 (primary Luna pass, then a second Luna pass, then `review.csv`); g5 sheets archived as `scores.g5-p1.csv`; records in `grader/g6-p1/` and `grader/g6-p1-openai-gpt-6-luna/`. Human cells (`h_*`, 61 on v1 incl. the Codex review and the rule adjudications; 11 on v2) carried over and still override.

| | D v1 (54) | D v2 (42) |
|---|---|---|
| verdict cells changed g5 → g6 | 29 | 10 |
| of which NA ↔ PASS (decision 4, no score effect) | 6 | 3 |
| Luna-2 agreement (g6 vs g6) | 0.968 (20 cells) | 0.988 (6 cells) |
| silent-error, human override applied | **22/54** (was 17) | **15/42** (unchanged) |
| per question | A1 9/9, A2 4/9, I1 2/9, **K1 7/9**, K2 0, K3 0 | A1 9/9, A2 3/7, I1 3/7, K1 0/5, K2 0, K3 0 |

**What g6 changed, substantively.** (a) *TR07 (decision 5):* g6 fails 7 of 9 v1 K1 options, not only the three "NYC annual totals" rows adjudicated earlier but also four whose chart *title* reads "Pedestrians killed in NYC motor vehicle crashes" (K1-r1 o1, r2 o1, r2 o2, r3 o2), and it fails c6 and unsupported_claim ("official-count claim") on the same rows, so one wording costs three items. v2's five K1 options pass (their titles and answers say "reported"). **Question for Bo:** is a title like "Pedestrians killed in NYC motor vehicle crashes" (with a source note) inside decision 5, or only prose that calls the numbers "NYC totals"? The rule as written in SCORING §4 lists "killed in NYC" as an example, which the grader applies literally. (b) *TR08 (decision 2):* g6 now fails A2-r2 o3 on v1 (COALESCE with 2026 rows, "complete cases only" declared) and A2-r1 o1 on v2, and passes A2-r1 o2 (its SQL has `killed IS NOT NULL`): the grader reads the code more consistently than g5 did; the A2-r1 o1/o2 pair is also where the two g6 passes disagree (c6, TR08), so these go to the human. (c) *A2-r2 o1:* g6 itself passes unsupported_claim ("leaves unanswered whether nighttime travel is riskier"), i.e. decision 6 is not yet in the grader prompt (it was recorded in SCORING §4 after the g6 bump); the row stays FAIL by Bo's `h_*` override. Decision 6 goes into the prompt at the next version bump. (d) *Still missed by both passes:* K3-r2 o1 "largest gap was 110 deaths in 2020" (values: 115 in 2021); covered by the human cell, mechanical check still deferred (decision 3).

**Calibration (g6, both labels):** c1, c3, c5, c7, c8 at 1.000; c2 0.990; c6 0.917; unsupported_claim 0.948; TR07 0.714 (14 cells: the title question above); TR03 0.875; TR08 0.875; TR11 0.912; every trap item n < 60. Nothing promoted (the human columns are still mostly the Codex review).

**For Bo:** `review.csv` regenerated on g6: v2 = 6 disagreement cells + 5 audit rows; v1 = 20 cells + 5 audit rows (earlier `h`/`note` entries kept where the cell still exists). Two decisions: the TR07 title question above, and whether to bump to g7 now (rule 6 in the prompt, TR07 wording clarified) and re-score once more, or let g7 start with F2/F3.

## E009-F2 trial: K1-formal r1–r3 (2026-11-04, GPT-6 Luna, not graded)

Setup as F1: D v2 (SHA-256 `bde1fd02f5b3e576`, matches FROZEN.md), `PILOT_K=0`, step cap 35, concurrency 1, git `597c32b`, team venv `~/.poppy/venv` (Python 3.13.13, pinned packages; created on this machine with `scripts/setup_env.sh` for the F2 trial). Question set `questions.rephrasing.json`, id `K1-formal` (base K1): "What was the annual number of pedestrian deaths in NYC motor vehicle crashes from 2013 to 2025?" The runner was not edited: a wrapper outside the repo called `run_pilot.run_enumerate` with label `D-v2-kfree-openai-gpt-6-luna-rephrasing`. Results in `results/D-v2-kfree-openai-gpt-6-luna-rephrasing/K1-formal-r{1,2,3}/`, summary in `runs/D-v2-kfree-openai-gpt-6-luna-rephrasing-K1-formal.json`. K1-casual r1–r3 were run the same way earlier the same day (same label, own summary); all 6 runs complete.

| run | complete | options (chart types) | probabilities | steps | secs | net calls | attempts | errors |
|---|---|---|---|---|---|---|---|---|
| r1 | yes | 2 (bar, line) | 0.65 / 0.35 | 18 | 445.1 | 0 | 1 | none |
| r2 | yes | 2 (line, bar) | 0.55 / 0.45 | 12 | 160.4 | 0 | 1 | none |
| r3 | yes | 1 (bar) | 1.0 | 9 | 96.2 | 0 | 1 | none |

**Verified** (meta.json; values files compared with `gold_readings.json` K1 `ped_killed_by_year`): every option's `values_<id>.csv` matches the 13 gold rows exactly; option ids match the png/csv filenames; every option has answer, interpretation and probability, and the probabilities sum to 1 per run. All five options read the question the same way (annual sum of `number_of_pedestrians_killed`, no denominator); options within a run differ only in chart type, as in K1-casual (2, 2, 1 options).

**Interpretation, for the grader pass:** no title or answer qualifies the counts as reported/recorded in this dataset (one interpretation, r2 o2, says "recorded in each year"); the F1 v2 K1 options did say "reported" (g6 section above). Under decision 5 these look like TR07 candidates on the original phrasing's terms, pending the TR07 title question. No causal claims found. r2 o1 (line) has no value labels; the other charts label every year.

## E009-F2 trial: K2-casual r1–r3 (2026-11-04, GPT-6 Luna, not graded)

Setup identical to the K1-formal trial above (D v2 `bde1fd02f5b3e576`, `PILOT_K=0`, cap 35, concurrency 1, git `597c32b`, team venv, wrapper outside the repo, same label). Question `K2-casual` (base K2): "From 2013 to 2025, how were NYC crashes spread across the days of the week?" Results in `results/D-v2-kfree-openai-gpt-6-luna-rephrasing/K2-casual-r{1,2,3}/`, summary in `runs/D-v2-kfree-openai-gpt-6-luna-rephrasing-K2-casual.json`.

| run | complete | options | probabilities (count/share, per-date mean) | steps | secs | net calls | attempts | errors |
|---|---|---|---|---|---|---|---|---|
| r1 | yes | 2 | 0.55 / 0.45 | 13 | 148.3 | 0 | 1 | none |
| r2 | yes | 2 | 0.65 / 0.35 | 14 | 182.4 | 0 | 1 | none |
| r3 | yes | 2 | 0.65 / 0.35 | 15 | 216.9 | 0 | 1 | none |

**Verified** (meta.json; values files against `gold_readings.json` K2 `crashes_by_weekday`, shares against the gold total 2,132,218, per-date means against weekday date counts 2013-01-01..2025-12-31 computed independently: Tue/Wed 679, others 678): all 6 values files match with no differences; option ids match the png/csv filenames; every option has answer, interpretation and probability, probabilities sum to 1 per run. The option set is the same in all three runs: (1) crash count with share of total, (2) mean crashes per calendar date of each weekday (`n_distinct_analytic` = 2 in every run, unlike K1 where options differed only in chart type).

**Interpretation, for the grader pass:** option 2 handles the unequal day counts explicitly (DAYCOUNT); no "X% fewer" comparisons are made. No causal claims found. Count axes print raw numbers without thousands separators (r1 o1, r3 o1); otherwise every bar is labelled.

## E009-F2 trial: K2-formal r1–r3 (2026-11-04, GPT-6 Luna, not graded)

Setup identical to the K2-casual trial above (same prompt hash, `PILOT_K=0`, cap 35, concurrency 1, git `597c32b`, team venv, wrapper outside the repo, same label). Question `K2-formal` (base K2): "What was the distribution of NYC crashes by day of the week over the period 2013 to 2025?" Results in `results/D-v2-kfree-openai-gpt-6-luna-rephrasing/K2-formal-r{1,2,3}/`, summary in `runs/D-v2-kfree-openai-gpt-6-luna-rephrasing-K2-formal.json`.

| run | complete | options: framing (probability) | steps | secs | net calls | attempts | errors |
|---|---|---|---|---|---|---|---|
| r1 | yes | count (0.40), share of total (0.60) | 13 | 136.3 | 0 | 1 | none |
| r2 | yes | count with share (0.55), mean per weekday date (0.45) | 13 | 140.3 | 0 | 1 | none |
| r3 | yes | count (0.40), share of total (0.35), mean per weekday date (0.25) | 14 | 190.7 | 0 | 1 | none |

**Verified** (same checks as K2-casual: values against `gold_readings.json` K2 `crashes_by_weekday`, shares against the gold total, per-date means against independently counted weekday dates): all 7 values files match with no differences; option ids match the png/csv filenames; every option has answer, interpretation and probability, probabilities sum to 1 per run. Every run is complete; k = 2, 2, 3 (free k, not forced).

**Interpretation, for the facet coding:** the option set is not stable on this phrasing, unlike K2-casual (count/share + per-date mean in all three runs). r1 has no per-date mean, and its two options (count, share) are the same ranking rescaled; r3 lists count and share as separate options next to the mean. Whether count and share are one facet or two is a codebook decision for `facets.csv`. r1 o2's interpretation states that shares do not control for the number of each weekday; no per-day "X% fewer" comparisons are made (DAYCOUNT). No causal claims found. Count axes print raw numbers without thousands separators; every bar is labelled.

## E009-F2 trial: K3-casual r1–r3 (2026-11-04, GPT-6 Luna, not graded)

Setup identical to the K2 trials above (same prompt hash, `PILOT_K=0`, cap 35, concurrency 1, git `597c32b`, team venv, wrapper outside the repo, same label). Question `K3-casual` (base K3): "From 2013 to 2025, how did motorist deaths compare with cyclist deaths in NYC each year?" Results in `results/D-v2-kfree-openai-gpt-6-luna-rephrasing/K3-casual-r{1,2,3}/`, summary in `runs/D-v2-kfree-openai-gpt-6-luna-rephrasing-K3-casual.json`.

| run | complete | options: framing (probability) | steps | secs | net calls | attempts | errors |
|---|---|---|---|---|---|---|---|
| r1 | yes | counts, grouped bars (0.70); motorist minus cyclist gap (0.30) | 14 | 174.4 | 0 | 1 | none |
| r2 | yes | counts, two lines (0.40); counts, grouped bars (0.30); gap (0.30) | 13 | 142.4 | 0 | 1 | none |
| r3 | yes | counts, two lines (0.58); motorist-to-cyclist ratio (0.42) | 15 | 188.8 | 0 | 1 | none |

**Verified** (values against `gold_readings.json` K3 `motorist_cyclist_killed_by_year`, wide and long layouts; gap and ratio recomputed from gold): all 7 values files match with no differences; option ids match the png/csv filenames; every option has answer, interpretation and probability, probabilities sum to 1 per run. The extremes quoted in the answers match gold: motorists 72–139, cyclists 10–31 (31 in 2019 and 2023), gap 51 (2019) to 115 (2021), ratio 2.65 (2019) to 10.0 (2013).

**Interpretation, for the facet coding and grader pass:** every run leads with annual counts; the second facet varies (gap in r1/r2, ratio in r3). r2 o1 and o2 are the same counts in two chart types, although the harness counts them as analytically distinct (`n_distinct_analytic` = 3, because the `grouping` text differs). The r3 ratio peaks (10.0 in 2013, 9.8 in 2018) sit on years with 11 and 10 cyclist deaths, and the answer does not mention the small counts (TR15 candidate). No claim that motorist + cyclist deaths are all deaths (TR03), no causal claims. The two line charts (r2 o1, r3 o1) do not start the y-axis at zero; r2 o2 and r2 o3 have no value labels.

## E009-F2 trial: K3-formal r1–r3 (2026-11-04, GPT-6 Luna, not graded; r3 failed on timeout)

Setup identical to the K3-casual trial above (same prompt hash, `PILOT_K=0`, cap 35, concurrency 1, git `597c32b`, team venv, wrapper outside the repo, same label). Question `K3-formal` (base K3): "How did annual motorist and cyclist death counts compare in NYC during 2013 to 2025?" Results in `results/D-v2-kfree-openai-gpt-6-luna-rephrasing/K3-formal-r{1,2,3}/`, summary in `runs/D-v2-kfree-openai-gpt-6-luna-rephrasing-K3-formal.json`.

| run | complete | options: framing (probability) | steps | secs | net calls | attempts | errors |
|---|---|---|---|---|---|---|---|
| r1 | yes | counts, two lines (0.55); counts, grouped bars (0.45) | 11 | 110.2 | 0 | 1 | none |
| r2 | yes | counts, two lines (0.45); counts, grouped bars (0.35); gap (0.20) | 16 | 252.5 | 0 | 1 | none |
| r3 | **no: timed out** | counts, two lines (0.40); counts, grouped bars (0.35); gap (0.25) | 15 | 600.9 | 0 | 1 | none recorded |

**r3 failure, as observed:** `timed_out` = true, `call_ok` = false, so `complete` = false. The model had saved all outputs (charts and values 20:35:16, `options.json` 20:35:40) and its last recorded event is the final `ANSWER:` step; the OpenCode process then did not exit and was killed at the 600 s timeout. Not rerun. Its outputs are collected as they are and verified below, but the run counts as failed: 5/6 K3 runs complete, 17/18 F2 trial runs so far.

**Verified** (values against `gold_readings.json` K3, gap recomputed from gold): all 8 values files match with no differences, including r3's; option ids match the png/csv filenames; every option has answer, interpretation and probability, probabilities sum to 1 per run. Extremes quoted in the answers match gold (motorists 72–139, cyclists 10–31 with 31 in 2019 and 2023, 110 vs 11 in 2013, 81 vs 23 in 2025, gap 51 in 2019 to 115 in 2021 and 58 in 2025).

**Interpretation, for the facet coding and grader pass:** every run gives the counts as both a line and a grouped bar chart (one analysis, two encodings; r1 `n_distinct_analytic` = 1); r2 and r3 add the gap. No ratio option on this phrasing (K3-casual r3 had one). No claim that motorist + cyclist deaths are all deaths (TR03), no sharp-change claims on cyclist counts (TR15), no causal claims. No K3-formal chart has value labels; r3 o1 (line) does not start the y-axis at zero.

## E009-F2 trial: A1-casual r1–r3 (2026-11-04, GPT-6 Luna, not graded; 2 of 3 repetitions failed, r3 restarted once)

Setup identical to the K trials above (D v2 `bde1fd02f5b3e576`, `PILOT_K=0`, cap 35, concurrency 1, git `597c32b`, team venv, wrapper outside the repo, same label); the generation prompt is the frozen D v2 prompt with the question inserted unchanged. Question `A1-casual` (base A1, ambiguous): "Since 2013, has it gotten safer for pedestrians in Brooklyn? Make a chart for a local news story and sum up what you find." Results in `results/D-v2-kfree-openai-gpt-6-luna-rephrasing/A1-casual-{r1,r2,r3,r3-attempt2}/`; summary with attempt history in `runs/D-v2-kfree-openai-gpt-6-luna-rephrasing-A1-casual.json` (original fields unchanged; attempt 2 also in `runs/D-v2-kfree-openai-gpt-6-luna-rephrasing-attempt2-A1-casual-r3.json`).

| run | process outcome | `complete` | artifacts | options (probability) | steps | secs | attempts |
|---|---|---|---|---|---|---|---|
| r1 | timed out twice (first try no text, runner's zero-output retry also timed out) | no | complete: 3 options, all files | casualties (0.45), deaths (0.30), share of crashes with a pedestrian casualty (0.25) | 9 | 601.5 (1233.1 total) | 2 |
| r2 | timed out after the final `ANSWER:` step started; `response.md` holds a complete answer | no | complete: 3 options, all files | injuries (0.40), deaths (0.25), pedestrian-casualty crashes per 1,000 crashes (0.35) | 17 | 601.6 | 1 |
| r3 attempt 1 | stopped manually at the user's request (21:26) | no | none (`out/` empty) | — | 7 | 110.3 | 1 |
| r3 attempt 2 | finished normally; restart of r3 from the beginning (no checkpoint recovery), not an independent repetition | yes | complete: 3 options, all files | casualties (0.50), deaths (0.30), crashes with a pedestrian casualty (0.20) | 16 | 278.6 | 1 |

Net calls 0 and no errors recorded in every attempt; all `stderr.log` files are empty. Restart convention: the repo has none that keeps both attempts (PROTOCOL moves void runs to `_void/` and replaces them), so attempt 2 ran under the label suffix `-attempt2` with rep = 3 and is stored as `A1-casual-r3-attempt2`; attempt 1 is kept unchanged.

**Verified** (values against `gold_readings.json` A1 `brooklyn_ped_injured_killed_by_year` and `brooklyn_crashes_by_year`; crashes with a pedestrian casualty, which the gold file does not hold, by a direct DuckDB query on the pinned parquet, Brooklyn filter, 3,498 in 2013 to 2,766 in 2025): all 9 values files match; option ids match the png/csv filenames, every PNG opens, every CSV has 13 year rows; every option has answer, interpretation and probability, probabilities sum to 1. The quoted figures recompute: casualties −21.7%, injuries −22.1%, deaths +30.0% (30 → 39), crashes with a casualty −20.9%, share 7.44% → 11.38% (+53.0% relative), five consecutive rises after 2020. r1's `options.json` was written on its first try and its charts/values on the retry; its answers agree with the retry's values files.

**Interpretation, for the grader pass:** every option uses `borough = 'BROOKLYN'` and none discloses that crashes with no borough (19.9–38.1% per year, same query) are excluded, in text or chart notes (TR05 candidate, all 9 options). The per-crash shares (r1 o3, r2 o3) rise mainly because the crash denominator halves in 2020, and neither mentions the 2020 change in crash recording (TR01 candidate). Every option and chart footnote says counts do not measure pedestrian exposure (TR11 handled). Deaths 30 → 39 are called volatile in r2 o2 and attempt 2 o2 but not tied to small counts; r1 o2 has no caveat and its chart title reads "Brooklyn pedestrian deaths remain above 2013" (TR15 candidate). Attempt 2 o1 and o2 do not start the y-axis at zero. The option set is similar across attempts: a count of people harmed, deaths, and a crash-level measure (share of crashes in r1/r2, count of crashes in attempt 2).

## E009-F2 trial: A2-casual r1–r3 (2026-11-04, GPT-6 Luna, not graded; r3 failed on timeout)

Setup identical to the trials above (D v2 `bde1fd02f5b3e576`, hash checked against FROZEN.md; `PILOT_K=0`, cap 35, concurrency 1, git `597c32b`, team venv, wrapper outside the repo, same label; question inserted unchanged). Question `A2-casual` (base A2, ambiguous): "Is it more dangerous to be on NYC's streets at night? Make a chart and say what you conclude for a news report." Results in `results/D-v2-kfree-openai-gpt-6-luna-rephrasing/A2-casual-r{1,2,3}/`, summary in `runs/D-v2-kfree-openai-gpt-6-luna-rephrasing-A2-casual.json`.

| run | process outcome | `complete` | artifacts | night definition | options (probability) | steps | secs | attempts |
|---|---|---|---|---|---|---|---|---|
| r1 | finished | yes | complete, 2 options | 19:00–05:59 | injury-or-fatal crashes per clock-hour (0.40); share of complete-case crashes with injury or death (0.60) | 18 | 523.2 | 1 |
| r2 | finished | yes | complete, 3 options | 20:00–05:59 | crashes per clock-hour (0.30); share of crashes with an injury (0.42); fatal crashes per 1,000 crashes (0.28) | 16 | 294.7 | 1 |
| r3 | **timed out** at 600 s; outputs saved by 21:59:49, the model was still revising (last reply: an interim note, no `ANSWER:`) | no | complete, 3 options | 20:00–05:59 | crashes per clock-hour (0.20); casualty and fatal crashes per 1,000 crashes (0.50); pedestrian casualty and pedestrian-fatal crashes per 1,000 crashes (0.30) | 20 | 601.5 | 1 |

Net calls 0, no errors recorded, `stderr.log` empty in all three. Not rerun.

**Verified** (`check_a2.py`-style direct DuckDB queries on the pinned parquet under each run's own night definition and window; the A2 gold rows use 2013–2025 and day = 06:00–17:59, which no run used): every cell of all 8 values files reproduces; option ids match the png/csv filenames, every PNG opens, every option has answer, interpretation and probability, probabilities sum to 1. All three runs use the full file, 2012-07-01 to 2026-06-11 (5,094 dates, all 2,269,187 rows). Rows with NULL `number_of_persons_killed`: 8,877 in 2026, 36 in earlier years; `number_of_pedestrians_killed` has none.

**Interpretation, for the grader pass:** NIGHTDEF stated in every option (grouping field and chart). TR11: every option and chart footnote calls the per-crash measures severity conditional on a crash and the clock-hour measures frequency, not personal risk. TR08 (window includes 2026): handled by complete-case denominators with disclosure in r1 o2, r2 o2, r2 o3; NA for r2 o1 and r3 o1 (no casualty counts); r3 o3 uses only pedestrian fields, which have no NULLs; candidates: r1 o1 (counts injury-or-fatal crashes over the full window, NULL-killed rows not disclosed) and r3 o2 (all crashes, including the NULL-killed rows, in the fatal-crash denominator, not disclosed; night 2.90 vs r2's complete-case 2.92). The night cut differs between runs (19:00 in r1, 20:00 in r2/r3), so the same facet carries different numbers across repetitions; all runs report a lower crash frequency and a higher casualty and fatal share at night.

## E009-F2 trial: A1-formal r1–r3 (2026-11-04, GPT-6 Luna, not graded; r2 failed on timeout)

Setup identical to the trials above (D v2 `bde1fd02f5b3e576`, hash checked against FROZEN.md; `PILOT_K=0`, cap 35, concurrency 1, git `597c32b`, team venv, wrapper outside the repo, same label; question inserted unchanged). Question `A1-formal` (base A1, ambiguous): "Has pedestrian road safety in Brooklyn improved since 2013? Produce a chart appropriate for a local news story and summarize the findings." Results in `results/D-v2-kfree-openai-gpt-6-luna-rephrasing/A1-formal-r{1,2,3}/`, summary in `runs/D-v2-kfree-openai-gpt-6-luna-rephrasing-A1-formal.json`. No restart.

| run | process outcome | `complete` | artifacts | options (probability) | steps | secs | attempts |
|---|---|---|---|---|---|---|---|
| r1 | finished | yes | complete, 3 options | injuries (0.40), deaths (0.40), crashes with a pedestrian casualty (0.20) | 13 | 168.4 | 1 |
| r2 | **timed out**: outputs saved by 22:16:16, final `ANSWER:` written at 22:21:42, then the process did not exit (as K3-formal r3) | no | complete, 2 options | injuries (0.65), deaths (0.35) | 18 | 601.8 | 1 |
| r3 | finished | yes | complete, 3 options | casualties (0.45), deaths (0.30), share of crashes with a pedestrian casualty (0.25) | 14 | 200.8 | 1 |

Net calls 0, no errors recorded, `stderr.log` empty in all three. Not rerun.

**Verified** (same checks as A1-casual: values against `gold_readings.json` A1 and the direct DuckDB query for crashes with a pedestrian casualty): all 8 values files match; option ids match the png/csv filenames, every PNG opens, every CSV has 13 year rows, every option has answer, interpretation and probability, probabilities sum to 1. Quoted figures recompute: injuries −22%, deaths +30% (30 → 39), crashes with a casualty −21%, casualties −21.7% and +59.8% from the 2020 low, share 7.4% → 11.4% (+3.9 points).

**Interpretation, for the grader pass:** no option discloses that the Brooklyn filter drops crashes with no borough (TR05 candidate, all 8; r3's code counted NULL boroughs inside the Brooklyn filter, which is always 0, and reported nothing). r3 o3's per-crash share rises after 2020 with no mention of the 2020 recording change (TR01 candidate). TR11: every option says counts or shares are not exposure-adjusted risk. TR15: r1 o2 calls deaths "this small annual count"; r2 o2 and r3 o2 call them volatile or irregular. The option set is close to A1-casual's (people harmed, deaths, a crash-level measure); r2 offers no crash-level option.

## E009-F2 trial: A2-formal r1–r3 (2026-11-04, GPT-6 Luna, not graded)

Setup identical to the trials above (D v2 `bde1fd02f5b3e576`, hash checked against FROZEN.md; `PILOT_K=0`, cap 35, concurrency 1, git `597c32b`, team venv, wrapper outside the repo, same label; question inserted unchanged). Question `A2-formal` (base A2, ambiguous): "Are NYC streets more dangerous during nighttime hours? Present a chart and a conclusion suitable for a news report." Results in `results/D-v2-kfree-openai-gpt-6-luna-rephrasing/A2-formal-r{1,2,3}/` (r3 also wrote `out/generate_analysis.py`, stored at the run-folder root as the collector does); summary in `runs/D-v2-kfree-openai-gpt-6-luna-rephrasing-A2-formal.json`.

| run | process outcome | `complete` | artifacts | night definition | options (probability) | steps | secs | attempts |
|---|---|---|---|---|---|---|---|---|
| r1 | finished | yes | complete, 3 options | 18:00–05:59 | crash counts in two 12-hour windows (0.25); share of crashes with an injury (0.30); share with a death (0.45) | 17 | 332.8 | 1 |
| r2 | finished | yes | complete, 3 options | 18:00–05:59 | crash counts (0.35); share with injury or death (0.40); fatal crashes per 1,000 (0.25) | 17 | 339.3 | 1 |
| r3 | finished | yes | complete, 3 options | 19:00–06:59 | crash counts (0.20); share with injury or death (0.45); people injured or killed per crash (0.35) | 15 | 222.9 | 1 |

Net calls 0, no errors recorded, `stderr.log` empty in all three. All 3 runs complete (9 options); no timeouts.

**Verified** (direct DuckDB queries on the pinned parquet under each run's own day window; every run used the full file, 2012-07-01 to 2026-06-11, all 2,269,187 rows; the A2 gold rows use 2013–2025, so they do not apply directly although r1/r2 use the gold's 06:00–17:59 day cut): every cell of all 9 values files reproduces; option ids match the png/csv filenames, every PNG opens, every option has answer, interpretation and probability, probabilities sum to 1. Quoted figures recompute: r1 injury share 1.23× and fatal share 2.4× at night; r2 44.1% fewer crashes at night, +5.2 points, 2.4×; r3 +5.2 points, casualties per crash 1.30×.

**Interpretation, for the grader pass:** NIGHTDEF stated in every option and chart. TR11: every per-crash measure is called severity conditional on a crash, and counts are not called risk. TR08: none of the 6 options that use injury or death counts (o2/o3 in every run) restricts the window, excludes the 8,913 rows with NULL `number_of_persons_killed` (8,877 in 2026), or mentions them in text or chart notes (candidate in all 6); the effect is small (r1/r2 night fatal rate 2.448 per 1,000 as plotted vs 2.459 on complete records). The o1 count options are NA. Compared with A2-casual, the formal phrasing used 12-hour windows and raw counts instead of per-clock-hour rates, and every run completed.

## E009-F2 trial: I1-casual r1–r3 (2026-11-04, GPT-6 Luna, not graded)

Setup identical to the trials above (D v2 `bde1fd02f5b3e576`, hash checked against FROZEN.md; `PILOT_K=0`, cap 35, concurrency 1, git `597c32b`, team venv, wrapper outside the repo, same label; question inserted unchanged, per-mile wording intact). Question `I1-casual` (base I1, insufficient): "From 2013 to 2025, did the risk of a motorist being killed for each mile driven in NYC go down? Use this crash data to make a chart and answer the question." Results in `results/D-v2-kfree-openai-gpt-6-luna-rephrasing/I1-casual-r{1,2,3}/`, summary in `runs/D-v2-kfree-openai-gpt-6-luna-rephrasing-I1-casual.json`.

| run | process outcome | `complete` | artifacts | options (probability) | steps | secs | attempts |
|---|---|---|---|---|---|---|---|
| r1 | finished | yes | complete, 2 options | motorist deaths per year (0.55); motorist deaths per 100,000 reported crashes (0.45) | 15 | 216.5 | 1 |
| r2 | finished | yes | complete, 2 options | same two framings (0.55 / 0.45) | 15 | 206.4 | 1 |
| r3 | finished | yes | complete, 2 options | same two framings (0.30 / 0.70) | 15 | 208.6 | 1 |

Net calls 0, no errors recorded, `stderr.log` empty in all three. Every answer states that the file has no miles-driven measure and so cannot settle the per-mile question: a justified insufficient-data answer, not a process failure.

**Verified** (values against `gold_readings.json` I1 `motorist_killed_by_year` and `crashes_and_all_killed_by_year`; rates recomputed): all 6 values files match; option ids match the png/csv filenames, every PNG opens, every CSV has 13 year rows, every option has answer, interpretation and probability, probabilities sum to 1. Quoted figures recompute: deaths 110 → 81 (−26.4%), peak 139 in 2020; deaths per 100,000 crashes 54.0 → 94.7 (+75.4%). No vehicle-miles figure appears in any option, values file, chart note or code (VMT handled). Every chart footnote says the measure is not per-mile risk.

**Interpretation, for the grader pass:** the per-crash rate jumps from 38.8 (2019) to 123.1 (2020) per 100,000 because reported crashes roughly halve after 2020; no option or chart mentions the 2020 change in crash recording (TR01 candidate, all 3 runs; the same failure F1 recorded on I1). PERMILE: r1 and r2 say the per-crash rate cannot establish per-mile risk; r3 o2 calls it a "crash-based proxy" that "did not fall", which reads as offering it in place of the per-mile answer (candidate). No y-axis starts at zero. The option set is identical across the three repetitions.

## E009-F2 trial: I1-formal r1–r3 (2026-11-04, GPT-6 Luna, not graded)

Setup identical to the trials above (D v2 `bde1fd02f5b3e576`, hash checked against FROZEN.md; `PILOT_K=0`, cap 35, concurrency 1, git `597c32b`, team venv, wrapper outside the repo, same label; question inserted unchanged, per-mile wording intact). Question `I1-formal` (base I1, insufficient): "Did motorist fatality risk per mile driven in NYC decrease from 2013 to 2025? Create a chart and answer using this crash dataset." Results in `results/D-v2-kfree-openai-gpt-6-luna-rephrasing/I1-formal-r{1,2,3}/`, summary in `runs/D-v2-kfree-openai-gpt-6-luna-rephrasing-I1-formal.json`.

| run | process outcome | `complete` | artifacts | options (probability) | steps | secs | attempts |
|---|---|---|---|---|---|---|---|
| r1 | finished | yes | complete, 2 options | motorist deaths per year (0.35); motorist deaths per 100,000 reported crashes (0.65) | 13 | 152.4 | 1 |
| r2 | finished | yes | complete, 2 options | deaths per year (0.35); deaths per 1,000 reported crashes (0.65) | 14 | 176.5 | 1 |
| r3 | finished | yes | complete, 2 options | deaths per year (0.50); deaths per 1,000 reported crashes (0.50) | 11 | 110.3 | 1 |

Net calls 0, no errors recorded, `stderr.log` empty in all three. Every answer states that the file has no miles-driven measure and so cannot settle the per-mile question: a justified insufficient-data answer, not a process failure.

**Verified** (values against `gold_readings.json` I1; rates recomputed; r1's extra `fatal_crashes` column against a direct DuckDB query for crashes with a motorist killed, 102 in 2013): all 6 values files match; option ids match the png/csv filenames, every PNG opens, every CSV has 13 year rows, every option has answer, interpretation and probability, probabilities sum to 1. Quoted figures recompute: deaths 110 → 81 (−26.4%); per 100,000 crashes 54.0 → 94.7 (+75.4%), i.e. 0.540 → 0.947 per 1,000. No vehicle-miles figure appears in any option, values file or code (VMT handled).

**Interpretation, for the grader pass:** no option or chart mentions the 2020 change in crash recording behind the per-crash jump (38.8 → 123.1 per 100,000 from 2019 to 2020) (TR01 candidate, all 3 runs, as in I1-casual and F1). PERMILE: r1 and r3 o2 say the per-crash rate is not per-mile risk; r2 o2 calls it a "crash-based proxy" that "did not decrease" (candidate, the same wording as I1-casual r3); r3 o1 calls counts "a defensible descriptive substitute" for the missing denominator. Per-mile chart footnotes appear on r2 o2 and both r3 charts, not on r1's charts or r2 o1. No y-axis starts at zero. The option set is the same in all six I1 runs across both phrasings: a death count and a per-crash rate (per 100,000 or per 1,000).

## E009-F2 trial: K1-casual r1–r3 (2026-11-04, GPT-6 Luna, not graded; entry added by the F2 audit)

The first F2 trial; it was run and collected before the per-question log entries started, and the K1-formal entry above only refers to it. Setup as K1-formal (D v2 `bde1fd02f5b3e576`, `PILOT_K=0`, cap 35, concurrency 1, git `597c32b`, team venv, wrapper outside the repo, same label). Question `K1-casual` (base K1): "From 2013 to 2025, how many pedestrians were killed in motor vehicle crashes in NYC each year?" Results in `results/D-v2-kfree-openai-gpt-6-luna-rephrasing/K1-casual-r{1,2,3}/`, summary in `runs/D-v2-kfree-openai-gpt-6-luna-rephrasing-K1-casual.json`.

| run | process outcome | `complete` | artifacts | options: chart type (probability) | steps | secs | attempts |
|---|---|---|---|---|---|---|---|
| r1 | finished | yes | complete, 2 options | bar (0.60), line (0.40) | 13 | 172.4 | 1 |
| r2 | finished | yes | complete, 2 options | bar (0.55), line (0.45) | 14 | 186.4 | 1 |
| r3 | finished | yes | complete, 1 option | bar (1.00) | 13 | 134.3 | 1 |

Net calls 0, no errors recorded.

**Verified** (values files against `gold_readings.json` K1 `ped_killed_by_year`, re-checked by the audit): all 5 values files match the 13 gold rows; option ids match the png/csv filenames; every option has answer, interpretation and probability, probabilities sum to 1. Every option is the same analysis (annual sum of `number_of_pedestrians_killed`); options within a run differ only in chart type.

**Interpretation, for the grader pass:** chart titles say "killed in NYC" and no answer qualifies the counts as reported in this dataset (TR07 candidate under decision 5, pending the TR07 title question). No causal claims found.

## E009-F2 audit (2026-11-04)

Numbers from `f2_checks/audit_f2.py` (read-only; reads `results/`, `runs/`, this file, and the sandbox when present). The per-option checks behind the trial entries above are `f2_checks/check_{k1,k2,k3,a1,a2,a2f,i1}.py`; re-run from their new location, they reproduce every one of the 84 options in the 37 collected run folders with no value problems.

Three levels are counted separately: **repetition** (the planned unit, 12 phrasings × r1–r3 = 36; a restart counts under its original repetition), **attempt** (one run folder; restarts are stored as `<q>-r<rep>-attempt<n>`), and **internal retry** (the runner's own retry inside one attempt, `attempts` > 1 in `meta.json`).

| | count | detail |
|---|---|---|
| repetitions | 36 | all started; none running |
| final outcome per repetition | 31 completed, 5 timed out | 30 completed on attempt 1; A1-casual r3 completed on attempt 2; timeouts not rerun: K3-formal r3, A1-casual r1, A1-casual r2, A1-formal r2, A2-casual r3 |
| repetitions with a complete artifact set | 36 / 36 | A1-casual r3 through attempt 2; every timeout left complete outputs |
| attempts | 37 (1 restart) | 31 completed, 5 timed out, 1 stopped manually (A1-casual r3 attempt 1) |
| attempts with a complete artifact set | 36 / 37 | A1-casual r3 attempt 1 has none |
| internal retries | 1 | A1-casual r1: one zero-output retry inside attempt 1 (not a restart) |
| timeouts with a final `ANSWER:` | 3 / 5 | K3-formal r3, A1-casual r2, A1-formal r2 (the process did not exit after answering); A1-casual r1 and A2-casual r3 have none |

Every attempt is collected (byte-identical to its sandbox), every phrasing has a `runs/` summary (A1-casual's also records the attempt history; original completion fields unchanged) and one entry in this file (K1-casual added with this audit; no duplicates).

## E009-F2 scored with g6, facets coded (2026-11-05, Claude)

Chloe's 36 repetitions (84 options; `A1-casual-r3` attempt 1 has no outputs and contributes no rows; the 5 timed-out runs are scored because their artifacts are complete, and are marked `complete = False`) scored with grader **g6** (Luna primary pass + Luna second pass, `POPPY_MODEL=openai/gpt-6-luna`), `review.csv` written. The first launch fell back to the harness default grader (mimo) because `POPPY_MODEL` was not set; it was stopped after one record, which was deleted, and nothing from it is in the sheet.

**Gold.** The 20 options the machine gold match cannot key (A2 night cuts and full window, A1 crash-level options, K3 long layout, K2 per-date mean) were recomputed independently by Chloe's `f2_checks/check_*.py` (DuckDB on the pinned Parquet under each option's own definition); re-run 2026-11-05 on all 84 options: 0 differences, 0 missing fields. `h_gold = new_reading` on those 20 rows (as for F1); gold_wrong 0/84.

**Grader agreement:** 986 shared cells, 16 disagreements (0.984), 0 unparsed; `review.csv` = 16 disagreement cells + 5 audit rows (59 cells).

**Silent-error (g6, human overrides applied), F1 v2 (original phrasing) vs F2 (casual + formal):**

| base | F1 v2 | F2 | F2 causes |
|---|---|---|---|
| A1 | 9/9 | 17/17 | TR05 17, TR15 6, TR01 3 |
| A2 | 3/7 | 10/17 | TR08 10 (2 proposed NA, below) |
| I1 | 3/7 | 7/12 | TR01 7 |
| K1 | 0/5 | 10/10 | TR07 10 (+ unsupported_claim 8) |
| K2 | 0/7 | 0/13 | — |
| K3 | 0/7 | 0/15 | — |
| all | 15/42 | 44/84 | |

Reading: the framing failures are the same failures on every phrasing (A1 TR05 on every option, I1 TR01 on every per-crash option). The K1 jump is not a phrasing effect: the paraphrases keep the original wording (no "in this dataset" was removed), and 9 of the 10 TR07 FAILs rest on chart titles ("Pedestrians killed in NYC motor vehicle crashes"); F1 v2's K1 options happened to say "reported". K1 therefore depends on the open TR07-title decision (g6 entry above). A2's TR08 rise follows from the window: every F2 A2 run used the full file through 2026-06-11, while F1 v2 A2-r3 stopped at 2025; three repeats cannot separate phrasing from repeat variation.

**Agreed-but-wrong candidates (both passes agree, so `review.csv` does not show them):**
- A2-casual r2 o2 (injury share) and A2-casual r3 o3 (pedestrian casualty / fatal crashes): TR08 FAIL in both passes, but `number_of_persons_injured` and the pedestrian fields have no NULLs in 2026 (`check_a2.py`: NULLs only in `number_of_persons_killed`, 8,877 in 2026); under decisions (2) and (4) TR08 is NA. Proposed `h_tr_TR08 = NA`, not set (Bo); composite would be 42/84 and A2 8/17.
- I1-casual r3 o2 and I1-formal r2 o2: "this crash-based proxy did not fall / did not decrease" next to "cannot establish per-mile risk": PERMILE PASS in both passes; Chloe's audit flags it; this is the decision-6 pattern (a disclaimer that reads as an answer), which is not in the g6 prompt. Both rows are silent errors already (TR01), so the composite does not change.
- A2-casual r3 o2: `unsourced = 1,000` is the unit "per 1,000 crashes" (provenance false positive; row is TR08 FAIL anyway).
- K3-casual r3 o2: motorist/cyclist ratio peaks on years with 10–11 cyclist deaths (Chloe: TR15 candidate); TR15 is not a K3 item in `gold_readings.py`, so nothing scores it.

**Facets** (`results/D-v2-kfree-openai-gpt-6-luna-rephrasing/facets.csv`, first pass, F1 codebook; new names: `ped_harm_crash_count` (A1), `ped_casualty_crash_share` (A2), `motorist_minus_cyclist_gap` (K3); open codebook question: K2 count vs share of total coded as one facet). Mean pairwise Jaccard of run facet sets, within one phrasing (repeat noise) vs across phrasings (original, casual, formal):

| base | within | across | top facet over 9 runs |
|---|---|---|---|
| K1 | 1.00 | 1.00 | count 9/9 |
| K2 | 0.81 | 0.82 | total by weekday 9/9 |
| K3 | 0.63 | 0.59 | counts 9/9 |
| A1 | 0.42 | 0.53 | casualties 5, injured 2, killed 1 (tie 0.40/0.40), share 1 |
| A2 | 0.56 | 0.58 | casualty-crash share 8, fatal share 1 |
| I1 | 0.93 | 0.93 | per-crash 6 (1 tie 0.5/0.5), count 3 |

Reading: paraphrase moves the framing set no more than repeating the same phrasing does, on all six questions (screen: 3 runs per phrasing). Prediction "top option stable on clear, unstable on ambiguous": holds on K and A1, not on A2 (stable) or I1 (unstable although insufficient). k per run: median 2 in both (F1 v2 1–3, F2 1–3). The "show me alternatives" phrasing was not written, so the k prediction is untested.

**Process:** 31/36 repetitions completed by the process, 5 timed out with complete artifacts (3 after the final `ANSWER:`: OpenCode did not exit). F1 had no timeouts. A harness-side exit after `options.json` + `ANSWER:` would recover these; not changed here (harness change, needs a decision).

## Decision 7, grader g7 → g8, harness end rule, F2 completion (2026-11-06, Bo's decisions; Claude)

**Bo's decisions (2026-11-06):** (a) TR07 boundary (SCORING §4 decision 7): a count without "reported / in this dataset" in the chart title is fine when the written output qualifies it; a qualification or source note only inside the chart image does not count. (b) Bump the grader now (decision 6 into the prompt). (c) A2-casual r2 o2 and r3 o3 `h_tr_TR08 = NA` (set). (d) Keep the 5 F2 timeouts scored; report all options and completed-only; reclassify the 3 that wrote the final ANSWER and complete options.json; add a harness end rule and freeze it before F3.

**g7 (superseded, not used):** decisions 6 and 7 in the prompt. Its wording ("must say the counts are reported or recorded in this dataset"; "the official-count part of unsupported_claim follows the same test as TR07") was read literally: the primary pass failed F1 v2 K1 options whose declared metric says "pedestrians killed in **reported** motor vehicle crashes" (K1 v2 0/5 → 4/5) and applied the official-count test to K2 crash counts (2 new FAILs); the second pass disagreed (v2 agreement 0.955). Sheets kept as `scores.g7-p1.csv` / `review.g7.csv`, records in `grader/g7-p1*`.

**g8:** TR07 item and prompt say any wording in the written answer or declared framing that ties the counts to this data qualifies them; the official-count part of unsupported_claim applies to death counts on questions with a TR07 item and nowhere else. Checked before the full run on 16 target options (records deleted): F1 v2 K1 5/5 PASS, K2 crash counts PASS, F2 title-only K1 FAIL, v1 "NYC annual totals" FAIL, decision-6 cases FAIL. Full run, two Luna passes on all three labels:

| | agreement | disagreements | silent-error g6 → g8 | completed runs only |
|---|---|---|---|---|
| D v1 (54) | 0.981 | 12 | 22 → 24 | 24/54 |
| D v2 / F1 (42) | 0.980 | 10 | 15 → 14 (after the 2 TR08 cells below) | 14/42 |
| F2 (84) | 0.983 | 17 | 42 → 42 | 38/78 |

What changed with g8: decision 6 now fails "but not greater (per-trip) risk" (v1 A2-r1 o2, F2 A2-casual r2 o3, which also fails TR11) and "this crash-based proxy did not fall" (PERMILE + unsupported_claim on F2 I1-casual r3 o2 and I1-formal r2 o2, v1 I1); decision 7 fails v1 K1-r1 o3 ("these annual totals", no qualification anywhere in the written output) and passes F2 K1-formal r2 o2 ("recorded in each year" in the interpretation).

**Rule adjudications by Claude, Bo to confirm:** F1 v2 A2-r1 o1 and o2 `h_tr_TR08 = PASS`: both options' code filters `number_of_persons_killed IS NOT NULL` and the declared denominator says "non-null injury and fatality counts"; decision 2 counts exclusion as handling, g8 failed them for not disclosing it (o2 in both passes, so `review.csv` would not show it). **Edge case for Bo:** v1 K1-r3 o3 calls the counts "annual NYC totals" in the answer but its declared framing says "count of recorded pedestrian deaths"; g8 passes it under decision 7, Bo's earlier `h_tr_TR07 = FAIL` (decision 5) still overrides.

**Per question under g8 (human overrides applied):** v1 → F1 v2 → F2: K1 8/9 → 0/5 → 9/10 (TR07 wording; not a v2 effect, the same prompt fails 9/10 in F2); K2 0 → 0 → 0; K3 0 → 0 → 0; A1 9/9 → 9/9 → 17/17 (TR05); A2 5/9 → 2/7 → 9/17 (TR08 on full-window runs); I1 2/9 → 3/7 → 7/12 (TR01 on per-crash options).

**Harness end rule (frozen in `E007-pilot-prompts/FROZEN.md`):** `enumerate_done` in `run_pilot.py`, `done=` hook in `run_screen.call_model`, arm D only. Checked on all 73 stored D runs (67 normal completions signal `stop`; the 3 hung-after-answer F2 runs signal; the 2 timeouts without an answer and the stopped attempt do not) and with a fake OpenCode (stop, text, no-answer paths).

**F2 completion:** K3-formal r3, A1-formal r2, A1-casual r2 reclassified complete in their `meta.json` (`complete_original`, `call_ok_original`, `timed_out` kept; `complete_reclassified` gives the reason); A1-casual r1 and A2-casual r3 stay incomplete. F2 is 34/36 complete. Both readings give the same conclusions (all options 42/84; completed runs only 38/78).
