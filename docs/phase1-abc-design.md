# Phase 1 — Experiments A, B, C: "fix it in the prompt, or build a step?"

- **Status:** agreed scope for phase 1 (v1.2, 2026-10-13). A and B are the team's design; C added by Bo. Phase 1 runs **A, B and C only**.

## 1. The story

Every applied AI team hits the same fork: when a model's output is not good enough, do you **rewrite the prompt** or **add a step to the pipeline**? Phase 1 measures both on the same task.

- **A — Baseline.** One model call writes plotting code and a text answer for a question about NYC crash data; Python runs the code. This is what a single call produces today.
- **B — Add a review step.** Same as A, then the model reviews its own executed result (the chart and the values it actually plotted), lists specific problems, and revises the code. Two extra calls, and the reviewer sees **evidence from execution**.
- **C — Ask for a self-check in the prompt.** Same single call as A, but the prompt also tells the model to check its work for specific problems and fix them before answering. Same architecture and output format as A; only the prompt changes.

The three comparisons:

| Comparison | What changes | What it tells us |
|---|---|---|
| A → C | only the prompt | how much a self-check instruction buys, at no extra cost |
| A → B | two extra calls; review sees execution results | how much a review step with evidence buys, and at what cost |
| **B vs C** | two complete designs | **"build a step with execution feedback" vs "prompt a self-check"**: quality gained per unit of cost |

**Wording rule for results.** B vs C compares two designs, not one factor. B differs from C in three ways at once: its reviewer sees execution results, it uses separate calls, and it costs 3× the calls. Report it as "a pipeline with execution feedback vs a single-call self-check prompt", with cost next to quality. Do not claim "separate calls beat prompting": execution results can only reach the model in a new call after the code runs, and prior work attributes most of such gains to that evidence (CRITIC).

## 2. Workflow

![Phase 1 workflow: A, B and C side by side](figures/phase1-workflow.svg)

Figure source: `docs/figures/phase1-workflow.svg` (edit this); `phase1-workflow.png` is a 2× export for slides. The table below gives the exact inputs and outputs of each step.

| Step | Who | Input | Output |
|---|---|---|---|
| 0. Reference answers (once) | human, SQL | question + data | gold numbers per question |
| ① Generate | model, call 1 | prompt template + question + data dictionary | plotting code + text answer |
| ①′ Generate with self-check (C only) | model, call 1 | ①'s template + self-check instruction + question + data dictionary | plotting code + text answer (same format as ①) |
| ② Execute | Python | code + data | `initial.png`, plotted values, run log (errors included) |
| ③ Critique (B only) | model, call 2 | `initial.png` + question + plotted values + data dictionary; "看看这张图，有什么问题？指出具体问题" | numbered issue list |
| ④ Revise (B only) | model, call 3 | code from ① + issues from ③ + question; "根据这些建议修改代码" | revised code + revised text answer |
| ⑤ Execute (B only) | Python | revised code + data | `revised.png`, plotted values, run log |
| ⑥ Evaluate | code + humans | final outputs + gold numbers + logs | scores, cost |

| Arm | Path | Model calls |
|---|---|---|
| A | ① → ② → ⑥ | 1 |
| B | ① → ② → ③ → ④ → ⑤ → ⑥ (reuses A's ① and ②) | 3 |
| C | ①′ → ② → ⑥ | 1 |

B is **paired** with A: it revises A's exact output, so each B item has a before/after pair. C is **unpaired**: it generates independently, so A and C are compared as distributions over 3 repeats.

## 3. Controls

- Same model, temperature, data snapshot (2013–2025 window), data dictionary, questions, tools and rubric for all arms.
- C's self-check instruction is **as generic as ③ and ④**, e.g. "Before giving your final answer, check your code and conclusion for specific problems and fix them. Output only the final code and answer." No checklist of specific traps (denominator, partial years, unknown borough): that would add domain knowledge, a different lever, and make B vs C unfair.
- C does not show its self-check, so C has no discovery data. Accepted, to keep A → C a pure prompt change.

## 4. Image input — decide with the model choice

③ sends `initial.png`. E005: big-pickle and nemotron cannot read images; mimo can. The model is chosen by a stability screen (call success, output-format compliance, repeat consistency), not by answer quality.

- **Non-vision model:** the image is ignored; ③ reviews the plotted values, which are still execution evidence. Record this in every run's metadata.
- **Vision model:** ③ also sees the chart. C never sees an image, because none exists before execution.

## 5. Evaluation

Team rubric, unchanged: correctness gate (values, units, aggregation, conclusion; any important misleading claim → fail), then question alignment, chart design, readability (0–4 each, 0–12 total); blind scoring with arm labels hidden and order randomized; time, tokens and calls per arm.

Additions:
1. ③ outputs a **numbered issue list**; each issue is labelled against the question's trap IDs and gold numbers → **discovery** (real problems found) and **false alarms**.
2. For each B pair: **found and fixed / found but not fixed / not found**.
3. **Correct → incorrect flips** in B, reported separately (B reviews every output, including correct ones; Tyen et al. measured up to −11 points from repairing correct outputs).
4. Output-format failures per arm.

Summary table per arm: gate pass rate, mean 0–12, Δ vs A, improved/same/worse (B), flips (B), discovery and false-alarm rates (B), calls, tokens, time.

## 6. Predictions, written before running

| Comparison | Prediction | Basis |
|---|---|---|
| A → C | ≈ 0 on correctness, possibly slightly negative; may improve wording and chart design | Huang et al. ICLR'24; Self-Refine (GSM8K +0); Self-Debug without execution (Codex 61.4 → 57.6). Caveat: Huang et al. also found a better initial prompt can beat multi-call self-refine, so C is not a foregone loss |
| A → B | gains where plotted values reveal the error; some correct → incorrect flips | CRITIC; Text2Vis (execution feedback 26% → 34–42%); Tyen et al. |
| B vs C | B ≥ C on correctness; C far cheaper | follows from the two rows above |

## 7. Size and limits

- 6 clear questions × 3 runs = 18 items per arm. Calls: A 18 + B 36 + C 18 = **72**. $0 with free models.
- 18 items detect only large effects. B vs A: paired tests (McNemar on gate pass, sign test on score change). C vs A: compare pass rates descriptively. Phase 1 is a pilot.
- Clear questions contain few traps, so B's reviewer has little to find and flips are the main risk. Questions 7–10 (ambiguous / insufficient evidence) are where review should matter; include them when possible.
- B spends 3× the calls of A and C; part of any gain may come from extra compute.
- Not in phase 1: a variant that merges ③ and ④ into one call. It would separate "sees execution results" from "separate calls", and can be added later from A's saved outputs without re-running anything.
