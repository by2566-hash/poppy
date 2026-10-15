# Phase 1 — Experiments A, B, C: "fix it in the prompt, or build a step?"

- **Status:** agreed scope for phase 1 (v2.0, 2026-10-15): A is an agent run (§10), B's review is read-only and its output typed (§2), failure handling decided (§9). A and B are the team's design; C added by Bo; pilot round from teammate suggestions. Phase 1 runs **A, B and C only**.

## 1. The story

An analyst asks an AI agent a question about a data file and takes its answer: that is what using Codex, Claude Code or OpenCode on data looks like today. When the answer is not good enough, a team has two options: **add a step to the pipeline** (an independent reviewer, then a revision) or **change the prompt** (tell the agent to check its own work). Phase 1 measures both on the same task.

- **A — Baseline agent.** One bounded agent run: the model writes and runs its own code on the NYC crash data, sees its errors and numbers, and finishes with a chart, the plotted values and a written answer.
- **B — Add a review step.** A's run, then an independent **review run** (fresh context, sees A's chart image and A's values, answer and code, cannot run code) that lists problems, then a **revise run** that fixes only what was listed. Up to three runs.
- **C — Self-check prompt.** The same single agent run as A; only the prompt changes: it also tells the agent to check its own work before answering.

The three comparisons:

| Comparison | What changes | What it tells us |
|---|---|---|
| A → B | an independent review run and a revise run | whether a separate reviewer adds value on top of an agent that already runs its own code, and at what cost |
| A → C | only the prompt | whether telling the agent to check itself helps, at no extra runs |
| **B vs C** | two complete designs | **"build a review step" vs "ask the agent to check itself"**: quality gained per unit of cost |

**What the agent already does, and what it does not.** Inside its run the agent fixes errors that announce themselves (a wrong column name or function makes DuckDB fail, the agent reads the error and retries; 6 such fixes in 10 A-v1 runs). It does not catch errors that run silently: a sum that drops rows with NULLs, a ranking sentence that contradicts the values, a "gap" that is only a ratio (A2, K2, K3 in the pilot). More steps do not fix this. Silent errors are what an independent review is for.

**Wording rule for results.** B vs C compares two designs, not one factor. B differs from C in three ways at once: a fresh context, an image-reading reviewer, and up to 3× the runs. Report it as "a review step vs a self-check prompt", with cost next to quality. Do not claim "separate calls beat prompting" or "execution feedback helps": all three arms run their own code (see §10).

## 2. Workflow

![Phase 1 workflow: A, B and C side by side](figures/phase1-workflow.svg)

Figure source: `docs/figures/phase1-workflow.svg` (edit this); `phase1-workflow.png` is a 2× export for slides. Every run is an OpenCode run of `mimo-v2.6-flash-free`, ≤ 15 steps, 600 s.

| Step | Who | Input | Output | Boundary |
|---|---|---|---|---|
| 0. Reference answers (once) | human, SQL | question + data | gold numbers per question | — |
| ① Analysis run (A; also B's first run) | model, agent run | prompt A.v1: question + data dictionary | `initial.png`, `values.csv`, code, `ANSWER:` | own folder + own copy of the data file; no network |
| ①′ Analysis run with self-check (C) | model, agent run | ①'s prompt + self-check instruction | same as ① | same as ① |
| Gate 1 (B) | harness | ①'s reply | A has an `ANSWER:` → ③; else the item fails in A and B | — |
| ③ Review run (B) | model | question, data dictionary, `initial.png` attached, `values.csv`, answer and code embedded | text only: `CHART CHECK:`, `ISSUES:` (numbered or `NONE`), `UNVERIFIED:` | read-only: no code execution, no file writes, no other files, no network; runs in its own folder |
| Gate 2 (B) | harness | ③'s reply | `NONE` → A's outputs are B's; numbered list → ④ with the ISSUES list only; no parseable ISSUES block → B fails the item | — |
| ④ Revise run (B) | model, agent run | question, data dictionary, A's code, values, answer, the ISSUES list | `revised.png`, `revised_values.csv`, `CHANGES:` one line per issue (fixed / kept / cannot address), `ANSWER:` | as ①; A's `initial.png` and `values.csv` read-only |
| ⑥ Evaluate | code + humans | final outputs, gold numbers, logs, `review.json` | scores, contract check, cost | — |

| Arm | Path | Runs per item |
|---|---|---|
| A | ① → ⑥ | 1 |
| B | ① → Gate 1 → ③ → Gate 2 → (④) → ⑥ (reuses A's ①) | 2 or 3 (A's run + review, + revise if issues) |
| C | ①′ → ⑥ | 1 |

B is **paired** with A: it reviews A's exact output, so each B item has a before/after pair. C is **unpaired**: it generates independently, so A and C are compared as distributions over 3 repeats.

**The B contract** (what "B ran as designed" means; checked per item by `experiments/E007-pilot-prompts/check_contract.py`): ③ received exactly the inputs above and returned the three sections; ③ made no file change, execution or network call; Gate 2 routed correctly; ④ answered every issue once with a status and produced both files and an answer; no run left the sandbox or the step/time budget; A's files are unchanged. Two human checks per item: did ③ invent an issue, and did ④ change anything not flagged. Every item ends in one of a fixed set of states (`B_STATES` in `run_pilot.py`).

## 3. Controls

- Same model, data snapshot (2013–2025 window), data dictionary, questions, sandbox, step budget and rubric for all arms.
- C's self-check instruction is **as generic as ③ and ④**, e.g. "Before giving your final answer, check your chart, values and conclusion for problems and fix them." No checklist of specific traps (denominator, partial years, unknown borough): that would add domain knowledge, a different lever, and make B vs C unfair. C's agent can run code while it checks; that is part of the design, not a confound.
- C does not show its self-check, so C has no discovery data. Accepted, to keep A → C a pure prompt change.

## 4. Image input

The model is `mimo-v2.6-flash-free`, the only free OpenCode model that reads images (E005). ③ receives A's chart as an attached image. Checked in the pilot: the image is sent (≈ 1.7k more input tokens), and with the image withheld the reviewer writes `CHART CHECK: no chart` instead of describing the chart from the code. C never receives an image from the harness; its agent may open its own chart, as A's may.

## 5. Evaluation

Team rubric, unchanged: correctness gate (values, units, aggregation, conclusion; any important misleading claim → fail), then question alignment, chart design, readability (0–4 each, 0–12 total); blind scoring with arm labels hidden and order randomized; time, tokens and calls per arm.

Additions:
1. **The review (③) is scored on its own**, from its typed record: `review_input.json` (exactly what it received), `review.json` (CHART CHECK, ISSUES, UNVERIFIED). Each ISSUES entry is labelled real error / unsupported claim / invented / taste; each UNVERIFIED entry correct or misrouted (should have been an issue); known defects of A's output that the review did not list are counted as missed. → **discovery**, **false alarms**, **routing errors**. `check_contract.py --issues-csv` writes the labelling sheet.
2. For each B pair: **found and fixed / found but not fixed (kept, cannot address) / not found**, from `changes.json`.
3. **Correct → incorrect flips** in B, reported separately (B reviews every output, including correct ones; Tyen et al. measured up to −11 points from repairing correct outputs).
4. Output-format failures and terminal states per arm (`b_state` for B).

Summary table per arm: gate pass rate, mean 0–12, Δ vs A, improved/same/worse (B), flips (B), discovery, false-alarm and routing-error rates (B), runs, steps, tokens, time.

## 6. Predictions, written before running

| Comparison | Prediction | Basis |
|---|---|---|
| A → C | ≈ 0 on correctness, possibly slightly negative; may improve wording and chart design | Huang et al. ICLR'24 (intrinsic self-correction does not improve reasoning); Self-Refine (GSM8K +0). C's agent can re-run code while checking, which may help a little on silent errors it happens to re-examine |
| A → B | gains on silent errors visible in the chart, values or wording (pilot: A2 NULL-sum, K2/K3 wording); some correct → incorrect flips | independent review with a fresh context and the chart; Tyen et al. (LLMs can correct errors once located, but locating is the hard part) |
| B vs C | B ≥ C on correctness; C far cheaper | follows from the two rows above |

## 7. Size and limits

- 6 clear questions × 3 runs = 18 items per arm (plus questions 7–10 when included). Runs: A 18 + B up to 36 extra + C 18. $0 with free models; each run is several model requests (steps), which the free tier rate-limits.
- 18 items detect only large effects. B vs A: paired tests (McNemar on gate pass, sign test on score change). C vs A: compare pass rates descriptively. Phase 1 is a pilot.
- Clear questions contain few traps, so B's reviewer has little to find and flips are the main risk. Questions 7–10 (ambiguous / insufficient evidence) are where review should matter; include them when possible. Items where A gives no answer do not reach B (§9), so report A's completion rate per question type.
- B spends up to 3× the runs of A and C; part of any gain may come from extra compute.
- Not in phase 1: a variant that merges ③ and ④ into one run. It would separate "independent review" from "separate runs", and can be added later from A's saved outputs without re-running anything.

## 8. Pilot round before the formal runs (teammate suggestion)

Run a few questions first and use the outcomes to write the critique/revise prompt (B) and the self-check prompt (C).

Rules that keep this from contaminating the result:

1. **Disjoint questions.** Pilot questions must not be among the formal questions. Tuning prompts on the questions you then score inflates B and C relative to A. Use a separate pilot set (for example the E002 questions in `experiments/E002-baseline/questions.json`, or 2 held-out questions of the same types).
2. **Equal tuning budget for B and C.** Same number of pilot questions, same number of prompt iterations (suggest at most 3 each). Otherwise B vs C measures tuning effort, not design.
3. **Freeze before the formal run.** Record prompt text and hash in the run metadata; no edits after the first formal call.
4. **Generic wording stays generic.** Outcome-informed edits may fix format, clarity and which artifacts to look at. They must not add trap-specific checklists (denominator, partial years, unknown borough). If domain notes are added, add them to B and C alike and report that run as a different lever.
5. **Log the pilot.** Each prompt version, the failures it fixed, and what it did not fix, in `experiments/LOG.md`.

## 9. Failure handling (teammate question: if A errors, does B continue?)

Classify the failure first; the treatment depends on its kind. Decide the rules now, before seeing data.

| Failure kind | Evidence in the log | Handling | Counts as |
|---|---|---|---|
| **Call failure** (HTTP error, client crash, empty reply, or timeout with **no completed step**) | API error text or crash dump; no model output | Retry the same call up to 2 times | Not a model result. Report retries and unrecoverable failures per arm; exclude symmetrically |
| **Non-completion** (timeout or step cap reached after ≥ 1 completed step, no chart or no answer) | steps and tool calls logged, artifacts missing | No retry | A failed item for that arm (the model was working but did not finish) |
| **Format failure** (reply has no code block or no answer section) | model output exists, parser fails | No retry | Model non-compliance: a failed item for that arm |
| **Execution failure** (code errors, no chart) — *superseded 2026-10-15, see below* | traceback in the run log | ~~B continues~~ | ~~recovery~~ |
| **Wrong but runs** | gate fails on values | B continues as designed | normal paired item |

**Amendment 2026-10-15 (agreed by Bo): B runs only when A produced an `ANSWER:`.** On OpenCode the model fixes its own tracebacks inside the run, so a separate "execution failure" never appears; what appears is non-completion (step cap or timeout, no answer). In that case B is **not run** and the item fails in both arms (ITT, 0 points), recorded as `b_skipped` with the reason. If A has an answer but no chart, B still runs (the review sees the values and answer, with "no chart was produced"). Reasons: B needs a "before" to be a paired design; a revise run on an empty input is a second analysis with 15 more steps, which would measure budget, not review; and C gets no second chance either. The report lists the "A incomplete, B not applicable" count per question type.

How to report:

- **Intention-to-treat first:** every item is counted in every arm; a failed item scores as gate-fail with 0 points. This is the headline table.
- **Stratified second:** (i) A has an answer → B vs A quality change and correct → wrong flips; (ii) A has no answer → counted as "B not applicable", shown per question type, never averaged into the quality-change mean.
- C has no repair step, so a C execution failure stays a failure. That is part of what the prompt-only design buys.
- The diagnosis the teammate asked for ("model call problem or model capability problem?") is exactly the first three rows. Log `failure_kind` for every failed call so it can be answered from data, not memory.
- The stability screen (`experiments/E006-mimo-screen`) keeps call and format failures small before the formal runs.

## 10. What "one call" means on OpenCode (E006) — resolved 2026-10-15

E006 found that the OpenCode free tier cannot give a strict tool-less single call: removing the shell or read tool returns HTTP 403, and forcing one step makes the model narrate instead of answer. Decision (Bo, 2026-10-15): **① is one bounded agent run in which the model writes and executes its own code.** This is also the realistic setting: an analyst asking an agent. The written answer is produced after the model has seen its numbers. Consequence: the original contrast "only B sees execution results" no longer holds; §1 and §6 are written for the agent setting. See `experiments/E006-mimo-screen/REPORT.md`.


### Amendment 2026-10-14 (from E006, ambiguous and insufficient-evidence questions)

- A client crash (Bun runtime dump after 1 step, P10 r2) and a long run that times out while still working (P8 r3, 420 s, 7 steps) are different failures. The first is infrastructure and is retried; the second is non-completion and counts against the arm.
- The 10-step cap and 420 s timeout that sufficed for clear questions were tight for ambiguous ones (8 / 12 runs hit the cap; median 198 s vs 65 s). The formal config is set from the E006 re-screen, and applies to **all** arms and questions alike.

### Amendment 2026-10-14 (pilot scope and B review design)

- The pilot round now tunes **A and B only**. A is frozen at its first prompt. C's self-check prompt is written by Bo after A and B are frozen, checked once for format, and not tuned; the final report states this asymmetry.
- B's review step (③) is a **review, not a re-analysis**: it runs without code execution, sees A's chart (attached) and A's values, answer and code (embedded), and returns a numbered list of issues or `ISSUES: NONE`. The revise step (④) runs only if issues were reported, lists how it handled each one, and keeps everything not flagged unchanged.
- Step budget: 15 steps **per run**, the same for every run. B makes up to three runs per item, so it spends more in total; that spend is reported as B's cost next to its effect.
- Details and acceptance criteria: `experiments/E007-pilot-prompts/PROTOCOL.md`.
