# Phase 2 — minimal plan (decided 2026-11-02)

- **Status:** this is the working plan. It replaces the option space in `docs/v2-design-inventory.md` (kept as the record of what was considered; §8 below lists what was deferred and why). Decisions here follow Bo's replies of 2026-11-02: detection as a minimal implementation; gold = correct numbers, framing stays a human check; the loop as the smallest version that fits the current experiments; every adopted method carries its source.
- **Principle:** build only what phase 1's observed failures need, score it on runs we already have, and let the loop decide the next addition. Nothing is built for a failure we have not seen.

## 1. The four replies, analysed

**(a) Detection first, prevention as treatments — agreed, minimal.** Phase 1's failures were of four kinds and all four are visible in saved runs: numbers plotted that do not match the gold (clear questions), numbers in prose that come from nowhere in the run's own table (I1 imported vehicle-miles; K1 "official" tolls), framings that are correct but undisclosed (A1 borough filter in 6/6 runs; per-crash rates across the 2020 recording change), and unsupported claims (causes, exposure-based risk). The minimal detection layer is one check per kind, machine where the check is cheap and precise, human where it is not (§3). The figure hook, plan declaration, pandas-assertion generator, fault injection and VisJudge are not needed to score those four kinds and are deferred (§8).

**(b) Gold = correct numbers — yes for the machine standard, with one thing kept.** A gold plan schema per question is dropped: it is heavy, and nothing in the current experiments can consume it. The machine standard is the gold series we already have, re-derived independently on 2026-10-21 (6 pilot + 10 held-out, all matching), put into one keyed file so that an option of D can be matched to *the reading it chose* (§4). What stays is the per-question trap sheet (`experiments/E007-pilot-prompts/SCORING.md` §4): phase 1's main finding is that numbers can be correct while the framing misleads, and the trap sheet is the already-written, already-used human check for that. No new ground-truth artifact beyond the keyed file.

**(c) The per-question-type feasibility plan is literature-based; sources are listed in §7** and in the deep dive (`docs/eval-layer-deep-dive-2026-10-21.md`). The plan document names the source next to each adopted item from now on.

**(d) The three prototypes each change one design item (§3):** derivability → replaced by a *provenance* check on the run's own table; code-level framing flags → kept as evidence pointers for the human trap verdict, no plan.json; the claim judge → shadow mode, logged against human labels, promoted only when recall reaches the floor.

**(e) The loop — minimal mapping in §5.** What is added: one score sheet per experiment that doubles as the labelling sheet, a 50-line summary script, a written keep/revert rule. What is not added: a second labeller with κ, a gate script, a re-scoring framework.

## 2. Workflow (what is evaluated)

| Decision | Choice |
|---|---|
| Arms in phase 2 | A, B (A + review/revise) and D in its final form from the follow-ups; C stays frozen as a phase-1 record (2/6 on mimo, 6/6 on Luna; no phase-2 question needs it). |
| Model | GPT-6 Luna for all phase-2 runs (phase 1 showed mimo's format failures dominate its results). mimo only if a question needs the small-model contrast. |
| D's final form | fixed by E009-F1 (free k + `interpretation`) and F2 (phrasing); F3 adds a selection signal if it validates. |
| Treatments (prevention) | **not pre-decided.** A treatment is chosen only from the taxonomy count of step 4 of the loop (§5), one per iteration, as an arm variant with its own prompt or harness hash. Candidates already named (data profile in context, plan declaration, scope-declared revise) wait for a count that justifies them. |
| Questions | dev = the 6 pilot questions (all tuning and open coding); held-out = P1–P10, run once at the end of phase 2 with the frozen workflow and scorer. |

## 3. Evaluation layer (minimal detection)

One score sheet per experiment, `results/<label>/scores.csv`, one row per run (per option for D). Machine columns are filled by `score_runs.py`; human columns by the scorer. The sheet is the record; nothing else is needed for a review.

| Failure kind (silent-error component) | Check | Machine / human | Verdict or flag | Source |
|---|---|---|---|---|
| Plotted numbers wrong | `gold_match`: the option's `values.csv` against the keyed gold readings; key-aware (sorted on the key column), tolerance: counts exact, rates ±1 % relative, shares ±0.5 pp; extra columns ignored. Result = `match:<reading>` / `no_reading` / `mismatch:<reading>` | machine | verdict for match / mismatch; `no_reading` goes to the human, who either adds the reading to the gold (with its query) or marks it wrong | DABstep quasi-exact match ([2506.23719](https://arxiv.org/html/2506.23719)) |
| Prose number unsourced | `provenance`: every number in `answer` / `interpretation` (normalised: commas, %, ~, k) must equal a cell of the option's own table, or a difference, ratio or percent change of two cells, within ±1 %. Unsourced numbers are listed | machine | **flag** (human confirms); replaces the derivability idea, which had 0 true positives because every number *can* be derived from the data; what matters is whether it came from the run's own table | STAT-TO-TEXT: check numbers by execution, never by a judge's eye ([2609.23966](https://arxiv.org/abs/2609.23966), [2610.00689](https://arxiv.org/abs/2610.00689)) |
| Framing correct but undisclosed | `framing_flags`: code-level patterns for the code-visible traps of the catalog: TR05 borough filter, TR01 per-crash denominator with a window spanning 2020, TR08 window including 2026 / non-NULL-safe sums | machine | **flag** with the line of code; the verdict is the human trap-sheet item ("disclosed / not disclosed / avoided"); no plan.json | prototype: TR05 found on 6/6 A1 runs; Misviz: rules beat models when metadata exists ([2604.11581](https://arxiv.org/pdf/2604.11581)) |
| Unsupported claim | human binary per run: "any causal claim, exposure-based risk claim, external number or official-count claim?" with the sentence quoted. The Luna judge ("detect errors" wording, atomic sentences) runs on the same text **in shadow**: its verdict is logged next to the human's in `judge_calibration.csv` and never scored | human (judge shadow) | verdict; judge promoted to a flag when TPR ≥ 0.8 on ≥ 60 human labels (phase-1 prototype: TPR 0.57, TNR 1.00 on 32) | ReaLMistake ([2404.03602](https://arxiv.org/abs/2404.03602)); CausalPitfalls ([2505.13770](https://arxiv.org/abs/2505.13770)); judgy TPR/TNR correction |
| Insufficient-evidence question (I1 type) | `required_statement` present? ("cannot be determined from this data" in the option's own words) — human binary, plus provenance on any number given | human | verdict | AbstentionBench judge ([2506.09038](https://arxiv.org/html/2506.09038v1)); Two Axes metrics ([2607.08456](https://arxiv.org/abs/2607.08456)) |
| The team's 8 binary criteria | scored by the human on the top option (D-top) and on the best option (D-best), as in `SCORING.md` §1 | human | verdict | HealthBench-style binary items ([2505.08775](https://arxiv.org/html/2505.08775v1)) |
| Contract / completeness / boundaries | existing: `check_contract.py`, `B_STATES`, `parse_options` (complete, n_options, distinct, duplicates), `net_calls` | machine | verdict | — |
| First failure | free text: the first upstream thing that went wrong, coded with a TR code, one of the four silent-error components, or `crash/incomplete` | human | label for the taxonomy (§5) | Husain & Shankar error analysis |

Primary metric unchanged: silent-error rate = unsourced number ∨ unsupported claim ∨ gold mismatch ∨ undisclosed framing, per run, reported per question type.

## 4. Ground truth

| Decision | Choice |
|---|---|
| Artifact | one keyed file `experiments/E007-pilot-prompts/gold_readings.json`: `{question: {reading_name: {"key": "year", "columns": {...}, "rows": [...], "query": "<DuckDB SQL>", "source": "audit 2026-10-21"}}}`; populated from the series already in `gold_pilot.json` (6) and E006 `gold.json` (P1–P10), plus the second series the audit already derived for A1 (killed) and A2 (killed, injured). A new reading is added only when a run produces one that a human judges legitimate; the query is recorded with it. |
| Tolerance | counts exact; rates ±1 % relative; shares ±0.5 pp. |
| Framing standard | the trap sheet, as is. Not a gold artifact; a human check. |
| Authorship | dev readings by Bo; held-out readings exist (E006, re-derived 10-21); any new held-out reading is written by a teammate who tunes no prompt. |

## 5. The loop (minimal)

| Step | Exists | Phase-2 minimal | Source |
|---|---|---|---|
| 1 freeze baseline | yes (`FROZEN.md`, hashes in meta) | — | Hamel; Anthropic |
| 2 run and trace | yes | — | — |
| 3 open coding | partial | the human columns of `scores.csv` + the `first_failure` column; Bo labels; dev runs only; ≥ 30 rows before the first taxonomy | Husain & Shankar field guide |
| 4 taxonomy with counts | no | `summarize_scores.py` prints the count of `first_failure` codes; the code set is fixed in advance: TR01–TR17, the four silent-error components, `crash/incomplete`, `other` (free text, re-coded when ≥ 3 agree) | same |
| 5 one change | yes (phase-1 rule) | `ITERATIONS.md` entry: observed failure (code + count) → one change → prediction → acceptance | LangChain Better Harness |
| 6 paired re-run | harness yes, stats no | same questions, K = 3 (5 when time allows); `summarize_scores.py` prints per-question paired differences, the pooled rate with a Wilson interval, and the MDE line (≈ 48 pts at 6 questions, K = 5) | Miller 2024 ([2411.13768](https://arxiv.org/abs/2411.13768)); Bowyer ([2503.01747](https://arxiv.org/abs/2503.01747)) |
| 7 keep / revert | no | a written rule, applied by Bo and recorded in `ITERATIONS.md`: **keep iff the targeted failure count falls on dev and no other criterion's failure count rises**; no script | Better Harness; Hex |
| 8 change log | yes (`ITERATIONS.md`) | add the judge-calibration update when the shadow judge is involved | — |
| 9 stop | — | timebox: phase 2 ends with the final presentation; the held-out set is run once at the end | — |

Not done now: a second labeller and κ (one labeller; the risk is recorded), a gate script, a re-scoring framework (Inspect AI), per-run `score.json`.

## 6. Reporting

Arrows table per change (quality / time direction; cost not scored, per Ryan); per-question-type rows; the MDE line under every comparison; problem register kept current.

## 7. Sources adopted (what each one gave us)

| Item | Source |
|---|---|
| numeric matching with tolerance, order-insensitive | DABstep ([2506.23719](https://arxiv.org/html/2506.23719)) |
| numbers in prose checked by execution, not by a judge | STAT-TO-TEXT ([2609.23966](https://arxiv.org/abs/2609.23966)); numeric-robustness warning ([2610.00689](https://arxiv.org/abs/2610.00689)) |
| rule checks beat models when metadata exists | Misviz ([2604.11581](https://arxiv.org/pdf/2604.11581)) |
| binary per-question criteria, graded by a model, reach expert-level agreement | HealthBench ([2505.08775](https://arxiv.org/html/2505.08775v1)) |
| judges are high-precision / low-recall; "detect errors" wording; calibrate with human labels | ReaLMistake ([2404.03602](https://arxiv.org/abs/2404.03602)); judgy (TPR/TNR correction) |
| causal-claim detection needs a human-validated pipeline | CausalPitfalls ([2505.13770](https://arxiv.org/abs/2505.13770)); Isch et al. 2026 |
| abstention judged separately from correctness | AbstentionBench ([2506.09038](https://arxiv.org/html/2506.09038v1)); Two Axes ([2607.08456](https://arxiv.org/abs/2607.08456)) |
| error-analysis-first loop; open coding; one labeller | Husain & Shankar (FAQ, field guide, evals-skills) |
| one change at a time, holdout, net-positive rule | LangChain Better Harness; Hex |
| small-n error bars, MDE, Wilson / Beta-Binomial, paired tests | Miller 2024 ([2411.13768](https://arxiv.org/abs/2411.13768)); Bowyer ([2503.01747](https://arxiv.org/abs/2503.01747)); evalci ([2607.04429](https://arxiv.org/abs/2607.04429)) |
| freeze, trace, several trials per item | Anthropic Demystifying evals; [2602.07150](https://arxiv.org/abs/2602.07150) |
| reverse inference as cycle consistency (F3) | back-translation; intent recovery in NL2VIS (see FOLLOWUPS §3) |

Full tables with scores, agreement figures and what was rejected: `docs/eval-layer-deep-dive-2026-10-21.md`.

## 8. Deferred (and the trigger that would bring each back)

| Deferred | Would return if |
|---|---|
| gold plan schema per question | a treatment needs a machine check of the framing itself (not only of disclosure) |
| plan declaration as an arm; `plan.json` | the taxonomy count shows framing failures are the top failure after disclosure is scored |
| data profile in context | same |
| pandas-assertion claim checker (STAT-TO-TEXT) | provenance flags miss a prose-number error that a human catches |
| figure introspection hook | a chart-encoding failure appears in the 8-criteria scores (none in phase 1); F3 no longer needs it (stripped condition = values only) |
| reviewer fault injection | B is chosen as the phase-2 workflow and the reviewer's recall becomes the target |
| VisJudge-7B ranker | D needs an automatic readability ranking for selection |
| second labeller + κ; gate script; Inspect AI; `score.json` | the sheet grows past what one person can label, or a teammate joins scoring |

## 9. Order of work

1. **E009-F1** (now): step measurement on K1/A2 → cap → 6-question acceptance → repeats r2, r3. Scored by hand with the existing sheet (completion, n, distinct, gold by eye, trap sheet).
2. **M1 scorer** (`score_runs.py`, `gold_readings.json`, `summarize_scores.py`, `scores.csv` format): built once, then run on D v1 r1–r3 and F1. Check: the D v1 cases already recorded by hand (A1 TR05 on options 1–3, A1 option 3 / I1 option 2 TR01, I1 imported numbers) must be flagged. The scorer earns its place on runs that already exist.
3. **E009-F2** rephrasings (teammate writes and commits the phrasings first; D = F1's winner).
4. **E009-F3** reverse inference; stripped condition = `values.csv` only; validated on 30–40 hand labels before any use.
5. **E010 loop, iteration 1**: open-code the dev rows of F1–F3 (≥ 30), taxonomy count, one change, paired re-run K = 3, keep / revert by the §5 rule, log.
6. Shadow judge accumulates labels through 1–5; promotion decided when ≥ 60 labels exist.
7. Held-out P1–P10 once, at the end, with the frozen workflow and scorer.
