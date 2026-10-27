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
| contract checks, end states, hashes, sandbox, 88 committed traced runs, 16 gold series, trap sheet, figure-introspection prototype, 32-sentence judge calibration set | 1 executed claim checks (STAT-TO-TEXT pattern) · 2 framing assertions on plan + code · 3 figure checks wired into the harness · 4 fault-injection set for reviewers · 5 per-question rubrics (ambiguous Qs) · 6 paired-stats + gate script · 7 taxonomy from ≥ 30 hand-coded traces |

## 4. Three questions for you

1. **Scoring boundary by question type.** Clear questions by code (gold match, chart introspection); ambiguous questions by a per-question rubric written by a human and graded by the frontier model; insufficient-evidence questions by an abstain judge plus executed claim checks; aesthetics, disagreements and the freeze decision by humans. Reasonable for a three-person team? (Note on power: with 6 dev questions and 5 repeats the minimum detectable effect is ≈ 48 points, ≈ 30 with 16 questions, so dev comparisons are screens and the 10 held-out questions confirm.)
2. **Reviewer leniency.** The frontier reviewer flagged issues on 2 of 6 items, the small model's reviewer on 5 of 5. With six items we cannot separate precision from leniency. We would plant 20–30 known faults into correct outputs and measure recall per reviewer and per fault type. Worth it, or is the generator × reviewer 2×2 enough?
3. **VisJudge-7B.** A teammate found an open-weight (Apache-2.0) chart judge for readability and aesthetics, the slot where frontier judges correlate only 0.43 with experts. We would calibrate it on ~40 of our charts (two human labels, three runs) before using it as a ranker, never as a target. Yes or skip?
