# Phase 2 proposal — an evaluation layer for a data-analysis agent (for Ryan, in-person meeting)

- **Status:** proposal for discussion, not a decision. Figure: `docs/figures/v2-eval-layer.png`. Evidence: `docs/phase1-summary.md`, `docs/eval-layer-deep-dive-2026-10-21.md`, `docs/problem-register.md`, `docs/ground-truth-audit-2026-10-21.md`.
- **Owner:** Bo (harness and evaluation layer); teammates: rubric writing, labelling, scoring, model-contrast analysis.

## 1. What phase 1 established (the reason for this design)

1. The agent fixes errors that crash and not errors that run silently (NULL-dropping sums, wrong rankings, a "gap" that is a ratio, causal asides, invented exposure).
2. An independent read-only reviewer catches some of those; with the same frozen prompt it flags fewer on the frontier model (2/6 vs 5/5) and we cannot yet tell precision from leniency.
3. **Numbers can be right while the framing misleads**: a Brooklyn filter that silently drops 20–38% of crashes per year (6/6 runs), per-crash rates across the 2020 recording change. No check in phase 1 catches it, and nothing published scores it.
4. Asking for three framings yields real alternatives, but the model's first choice is the typical answer (5 of 6 questions, 3/3 runs).
5. The harness is now trustworthy: sandbox verified, prompts frozen with hashes, every run recorded, all 16 gold series independently re-derived.

## 2. The design in one paragraph

The agent stays as it is. Around it we build a layer that (a) checks every observation point of a run with code first, a calibrated judge second and a human last; (b) defines one primary metric, the **silent-error rate** (unsourced number ∨ unsupported claim ∨ gold mismatch ∨ misleading framing); (c) runs a documented improvement loop in which humans do the error analysis and choose one change, and code does the paired re-run, the gate and the regression check. Three experiments run through it: E010 builds the layer and scores all phase-1 runs without re-running; E008 crosses generator × reviewer (mimo / Luna) to separate capability from prompt; E009 scores framing sets and tests the plan declaration as an arm.

## 3. What exists, what is to build (3 weeks)

| Exists | To build (order) |
|---|---|
| contract checks, end states, hashes, sandbox, 70+ traced runs, 16 gold series, trap sheet, figure-introspection prototype, 32-sentence judge calibration set | 1 executed claim checks (STAT-TO-TEXT pattern) · 2 framing assertions on plan + code · 3 figure checks wired into the harness · 4 fault-injection set for reviewers · 5 per-question rubrics (ambiguous Qs) · 6 paired-stats + gate script · 7 taxonomy from ≥ 30 hand-coded traces |

## 4. Where we want your judgement

1. Scoring boundary by question type: clear = code; ambiguous = human-written rubric graded by the frontier model; insufficient = abstain judge + executed claim checks; aesthetics and disagreements human. Reasonable for a 3-person team?
2. The judge rule (no scoring until TPR/TNR on ≥ 60 human labels). Our first claim judge measured TPR 0.57 / TNR 1.00. Is "flagging aid until recall ≥ 0.8" the right bar?
3. Plan declaration changes the agent's behaviour; we treat it as an arm, not a harness feature. Agree?
4. With 6 dev questions the minimum detectable effect is ≈ 30 points at 5 repeats. We propose: dev = screen, held-out 10 = confirmation once per freeze candidate, report pass@5 / pass^5 and the MDE instead of p-values. Would you report it differently?
5. Process reference: Husain & Shankar error analysis + LangChain "one change at a time" + Anthropic capability → regression evals. Is this how 99P would run it?
6. Reviewer leniency: fault injection (20–30 planted faults) to measure recall per reviewer. Worth the effort, or is the 2×2 enough?
7. A teammate found VisJudge-7B (open weights, Apache-2.0) for readability/aesthetics; we would calibrate it on ~40 charts before use. Yes or skip?
8. Deliverables you want to see at the end: field guide, Medium post in the 99P style, the harness as a reusable repo?
