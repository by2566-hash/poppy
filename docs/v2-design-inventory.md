# Phase 2 — design inventory (what has to be decided, by module)

- **Status (2026-11-02):** superseded by `docs/v2-plan.md` (the minimal plan decided on Bo's replies of 2026-11-02). Kept as the record of the option space; items not in the plan are listed there as deferred with their return trigger.
- **Status (2026-11-01):** inventory, not decisions. Phase 2 is open. Each module lists what exists, what must be designed or chosen, the options with evidence, and dependencies. Decisions are taken module by module after the D follow-up experiments (`experiments/E009-enumerate/FOLLOWUPS.md`) finish.
- **Evidence base:** `docs/phase1-summary.md`, `docs/problem-register.md`, `docs/ground-truth-audit-2026-10-21.md`, `docs/eval-layer-deep-dive-2026-10-21.md` (with the 10-27 addendum), `docs/mentor-brief-phase2-2026-10-27.md`, `docs/v2-eval-layer-architecture.md`.

## 0. Two framing answers that shape everything below

**Detection vs prevention of silent errors and misleading framing.** Both matter for the final output, but they live in different places:
- *Detection* belongs to the evaluation layer: it has to exist first, because without it no prevention can be shown to work (phase 1 proved that neither the agent's self-check nor the reviewer catches framing errors, and nothing published scores them).
- *Prevention* is a change to the workflow (a data profile in the context, a plan declaration, a review step, a rule in the harness). In phase 1 such changes were forbidden to keep the arms fair; in phase 2 they are **the treatments the loop tests**, one at a time, scored by the same detection layer. So: build detection, then let the loop decide which prevention earns its place.

**Ground truth needs a finer standard.** One gold series per question was enough to check plotted numbers; it cannot score framings, disclosures or prose numbers. Phase 2 replaces it with a **gold plan per question** (§3).

## 1. Workflow (the thing under evaluation)

| Exists | To decide | Options and evidence |
|---|---|---|
| A (agent run), B (review + revise), C (self-check), D (k framings with probabilities); frozen prompts with hashes | Which arms continue into phase 2 | all four as the baseline set; D variants from the follow-up experiments; the generator × reviewer cross (mimo / Luna) |
| D v1: k = 3, neutral ANSWER, `reason` + `answer` per option | D's final form: free k or fixed; interpretation depth; question phrasing | decided by the three follow-up experiments (`E009-enumerate/FOLLOWUPS.md`) |
| — | **Plan declaration** (metric, denominator, grouping, chart family, answerable) | run as an arm, not as a silent harness change: a plan in context changes the next steps ([Plans Fade Fast](https://arxiv.org/abs/2606.22953)); collect the JSON after free reasoning (format constraints can hurt small models, [2408.02442](https://arxiv.org/abs/2408.02442)) |
| — | **Data profile in the context** (null shares, partial periods, category drift; v2 design's S0) | a treatment: the only context-side prevention of framing errors that does not name specific traps; LIDA's summarizer ablation is the precedent |
| B's reviser re-runs the full analysis for text-only fixes | scope-declared revise (text-only → copy the chart) | next-phase candidate (design doc §7); not before the detection layer exists |
| D has no selection step | selection after enumeration (pairwise judge with position swap, or the reverse-inference check from follow-up 4) | depends on follow-up 4's result |

## 2. Evaluation layer

| Check | Exists | To decide | Evidence |
|---|---|---|---|
| Contract / end states | yes (`check_contract.py`, `B_STATES`) | extend to D and to plan-declaration arms | — |
| Plotted numbers vs gold | half (`gold_cover`, lenient) | key-aware matching with tolerance; column/unit canonicalisation (DABstep pattern) | [DABstep](https://arxiv.org/html/2506.23719) |
| Chart: type, encoding faithful to values, readability | prototype (`scripts/prototypes/figure_introspect_sitecustomize.py`) | wire the hook into the sandbox shim; which VisEval-style checks (overlap, ticks, zero baseline, dual axis) | VisEval SRCC 0.843; Misviz linter 99.7% precision |
| Numbers in prose | nothing that works (derivability: 0 true positives) | **claim-level executed checker**: split into quantified statements → model writes a pandas assertion per statement → execute on `values.csv`; false-negative skew; unmatched → human | [STAT-TO-TEXT](https://arxiv.org/abs/2609.23966) 91–98% agreement; do not let a judge eyeball numbers ([2610.00689](https://arxiv.org/abs/2610.00689)) |
| Unsupported claims (cause, exposure-based risk, external numbers) | calibration prototype: TPR 0.57 / TNR 1.00 on 32 sentences (Claude labels) | atomic-claim decomposition; "detect errors" framing; forbidden-claim list; ≥ 60 human labels; used as a flag until recall ≥ 0.8 | [ReaLMistake](https://arxiv.org/abs/2404.03602); [CausalPitfalls](https://arxiv.org/abs/2505.13770) |
| Misleading framing (undisclosed exclusions; denominators that change meaning inside the window) | prototype assertion: TR05 flagged 6/6 A1 runs | assertions keyed on a 5–10 item trap catalog, applied to `plan.json` + code, not free text; which traps are in scope per question | no published scorer; Misviz shows rules beat MLLMs when metadata exists |
| Ambiguous questions: per-question rubric | trap sheet (`SCORING.md` §4) | write HealthBench-style binary items per question (human), grade with Luna; who writes them (non-tuner) | HealthBench macro-F1 0.709 ≈ expert noise |
| Insufficient-evidence questions: abstention | nothing | AbstentionBench judge prompt + executed claim checks; metrics = unanswerable-answer rate, wrong-answer rate, coverage | [AbstentionBench](https://arxiv.org/html/2506.09038v1) 88%; [Two Axes](https://arxiv.org/abs/2607.08456) |
| Reviewer quality (B) | human checks; 2/6 vs 5/5 unexplained | fault injection: 20–30 planted faults, recall per reviewer and fault type | CriticGPT; AgenTracer |
| Readability / aesthetics ranker | addendum: VisJudge-7B assessed | calibrate on ~40 charts (two human labels, 3 runs) before use as a ranker, never a target | [VisJudge](https://arxiv.org/abs/2510.22373) r 0.68 |
| Question alignment without a reference | — | **reverse inference** (follow-up 4): infer the question from the output, compare with the asked question | new; see FOLLOWUPS §4 |
| Primary metric | defined: silent-error rate = unsourced number ∨ unsupported claim ∨ gold mismatch ∨ misleading framing | confirm the four components and their operational definitions once the checks exist | — |

## 3. Ground truth (the standard the checks compare against)

| Exists | To decide | Proposal |
|---|---|---|
| 16 gold series (all independently re-derived), trap catalog TR01–TR17, per-question trap sheet | **Gold plan schema per question** | `{question_id, type, readings: [{metric, denominator, grouping, chart_family, series_ref, disclosures_required: [TRxx…]}], not_answerable_as_asked: bool, required_statement (for insufficient questions), forbidden_claims: [...], tolerance}`: every legitimate reading listed, each with the disclosure it must carry; the gold series becomes `series_ref` of a reading |
| gold written by the prompt tuner | authorship rule | dev set (6 pilot) gold plans may be written by Bo; **held-out P1–P10 gold plans by a teammate who tunes no prompt**; both reviewed by a second person |
| `gold_cover` lenient | matching rule | key-aware, tolerance per field (counts exact, rates ±1% relative, percentages ±0.5 pp), extra columns ignored, order-insensitive |
| none for prose | — | covered by the executed claim checker, not by gold |

## 4. Harness

| Exists | To decide |
|---|---|
| sandbox v2, team venv, provider switch, `POPPY_EXP` / `POPPY_QSET` / `PILOT_REPS` / `PILOT_K`, token fields, end states | `PILOT_STEPS` override for D variants (free k needs more budget); figure hook on the shim's `PYTHONPATH`; plan-declaration capture; a scoring runner that re-scores saved runs without the model (own code or Inspect AI: decide after the first scorer exists) |
| contract checker | a per-run **scorecard** (`score.json`): every check's verdict + evidence pointer, so humans review from one file |
| — | paired-stats script: per-question paired differences, Wilson / Beta-Binomial intervals, pass@K and pass^K, MDE statement (Miller 2024; [2503.01747](https://arxiv.org/abs/2503.01747); [evalci](https://arxiv.org/abs/2607.04429)) |
| — | gate script: keep iff target failure improves and regression items do not regress; else revert (LangChain Better Harness; Hex) |

## 5. Protocol and process (the loop)

| Step | Who | Exists | To decide |
|---|---|---|---|
| 1 freeze baseline (hashes, commit) | auto | yes | — |
| 2 run and trace | auto | yes | — |
| 3 open coding ≥ 30 traces, first upstream failure | human | partial | labelling sheet format; who (one principal labeller); dev traces only |
| 4 taxonomy with counts | human | no | seed: TR catalog + silent-failure classes + MAST verification modes; κ check with a second labeller on 10 traces |
| 5 one change, hypothesis written | human | yes (phase-1 rule) | change entry template |
| 6 paired re-run, same items, K ≥ 5 | auto | harness yes, stats no | K per experiment; which questions are dev |
| 7 gate keep / revert | auto (human on edge cases) | no | thresholds: CI excludes 0 **and** zero regression on the frozen regression items |
| 8 change log; judge re-validation on untouched test split | human | partial | — |
| 9 stop / freeze | human | — | saturation rule or timebox |

References adopted: Husain & Shankar (FAQ, Field Guide, evals-skills); LangChain Better Harness + Hex holdout rule; Anthropic Demystifying evals + Miller 2024 + [2602.07150](https://arxiv.org/abs/2602.07150).

## 6. Reporting

| To decide |
|---|
| The arrows table (quality / cost / time direction per change) as the standard summary (Ryan) |
| Per-question-type reporting (clear / ambiguous / insufficient), since the scorers differ |
| Honest statement of MDE with every comparison (≈ 48 points on 6 questions, ≈ 30 on 16, K = 5) |
| Field guide entries per finding; problem register kept current |

## 7. Order of work (proposal)

1. D follow-up experiments (team decision, running now) → fixes D's form.
2. Gold plan schema + dev gold plans → unblocks framing assertions and rubrics.
3. Claim-level executed checker → the largest missing detector.
4. Figure hook wired into the shim; key-aware gold match → clear questions fully automated.
5. Scorecard + paired-stats + gate → the loop can run.
6. Fault-injection set; judge calibration (claims, abstention, VisJudge) → judges earn their place.
7. Treatments as arms: plan declaration, data profile, generator × reviewer cross.
