# E009 — Arm D: enumerate framings with verbalized probabilities (simplified, phase-1 add-on)

- **Status:** design fixed with Bo on 2026-10-19 for the phase-1 add-on: **k = 3**, **neutral ANSWER (no recommendation inside the run)**, **GPT-6 Luna only** (D is not run on mimo), **prompt tuned on the 6 pilot questions**, **step cap set from one K1 and one A2 run before scored runs**. The formal version (selection step, judge, P1–P10) is a phase-2 decision.
- **Origin:** Ryan (2026-10-16): once a chart is accurate, widen the options; ask for 3–5 ways to visualize with probabilities (Verbalized Sampling, Zhang et al., ICML 2026, arXiv 2510.01171), render them, let the reflective loop choose.

## 1. What D is

D = C's prompt (`C_selfcheck.v3.md`: analysis run with one self-check instruction) + one block: produce **k = 3 different framings** that each correctly answer the question, each with a reason and a probability, each rendered as its own chart with its own values file, plus `options.json`. One run, same sandbox as A/C. Step cap: `config/opencode.enumerate.json` starts at 30 and is set from the K1 and A2 measurement runs; the extra budget over A/C is reported as D's cost. Model: GPT-6 Luna (Ryan's key), because VS gains are reported to scale with model capability and the small model would mostly show format failures.

What is taken from Verbalized Sampling and what is changed, with reasons:

| VS element | In D | Why |
|---|---|---|
| "Generate k responses, each with text and probability" | k framings, each with reason, probability and a short answer | the core of VS: ask for the distribution, not one sample |
| "Sample from the tails, each probability < 0.10" | **not used** in v1 | written for creative text; in analysis it would push toward odd charts. Kept as an optional variant (D1) |
| Probability = model's own estimate | probability = "how likely a careful analyst would choose this framing", values sum to 1 | gives the number a stated meaning; still treated as ordinal (verbalized probabilities are not calibrated) |
| Free-text responses | fixed JSON fields: metric, denominator, grouping, chart_type, reason, probability, answer | distinctness must be checkable by code, and the fields are the plan declaration of phase 2 |
| — | "each framing must correctly answer the question; none the data cannot support" | diversity only counts among correct options |

Base = C rather than A because the self-check instruction already asks the model to look at chart, values and answer together; D asks it to do that per option.

## 2. Output contract (what makes a D run complete)

| File | Content |
|---|---|
| `out/option_<id>.png`, `out/values_<id>.csv` | one chart and one values file per framing, id = 1..k |
| `out/options.json` | `options`: list of k objects with `id, metric, denominator, grouping, chart_type, reason, probability, answer`; no recommendation field |
| reply | `ANSWER:` line: one sentence per framing in options.json order, no preference (the choice is phase 2's selection step, measured outside the run) |

`run_pilot.py D` parses this into `meta.json`: `options_parsed`, `n_options`, `n_complete_options` (png + csv + all fields), `n_distinct_framings` (framing = metric × denominator × grouping × chart_type, lower-cased), per-option records. `complete` = parsed ∧ k complete options ∧ k distinct framings ∧ ANSWER present.

## 3. Acceptance for the D prompt (format, as for B)

On the 6 pilot questions, GPT-6 Luna, one run each: ≥ 5/6 runs `complete`; no run uses the network or leaves its folder (contract); duplicates by framing ≤ 1 across all runs. Prompt tuning follows the pilot rules: one edit per iteration, each tied to an observed failure, logged in `ITERATIONS.md`; at most 3 iterations; A and C untouched. Effect (coverage, accuracy of options) is not an acceptance criterion.

## 4. What is measured in the simplified version (no judge, no selection step)

| Metric | How | Grader |
|---|---|---|
| Option accuracy | for the framing that matches the gold series: `values_<id>.csv` vs gold; other framings: human gate (8 criteria) until the recompute oracle exists | code / human |
| Distinct framings | from `options.json` fields | code |
| Framing coverage | share of an expert list of legitimate framings per question (3–5 per ambiguous question, written by a teammate who does not tune prompts) that the k options cover | human list, code match |
| Mode share | is the highest-probability option's framing the same as A's (and C's) single framing? A/C framings are read off their code and answer by hand (mimo A-v1, C-v3; Luna A/C when the teammates' runs land) | code (framing fields) + human check |
| Cost | steps, tokens, time vs C | code |

Predictions, recorded before the first scored run (Luna): ≥ 5/6 runs complete within the measured step cap; framings are distinct by the four fields in most runs, with at least one cosmetic-duplicate case; the highest-probability option's framing equals A's single framing (mimo A-v1 and, when available, Luna A) in most clear questions; on the insufficient-evidence item (I1) at least one framing's answer states that the per-mile question cannot be answered from this data.

## 5. Variants

- **D2 (this draft):** accuracy-conditioned wording, no tail sampling. Run first.
- **D1 (optional):** VS wording verbatim, including "sample from the tails, probability < 0.10 each". Only if D2 is stable; one lever at a time.

## 6. Decisions (Bo, 2026-10-19)

1. k = 3 fixed.
2. `ANSWER:` neutral; no recommendation inside the run.
3. Prompt tuned on the 6 pilot questions.
4. Step cap measured on K1 and A2 first, then set.
5. Model: GPT-6 Luna only.

## 7. Second check of the prompt against Verbalized Sampling and against phase-1 failures (2026-10-19)

Against the VS site's "magic prompt" ("Generate 5 responses … each with a text and a numeric probability … sample from the tails, probability < 0.10"): kept the k-responses-with-probability structure and the word "probability" (the paper's best-performing wording); replaced XML tags with JSON because the fields must be machine-checked; dropped tail sampling (creative-writing device); k = 3 by decision rather than the paper's 5; added the accuracy condition and a stated meaning for the probability.

Against our own failure log:

| Phase-1 failure | Guard in the D prompt / harness |
|---|---|
| Step-cap narration counted as an answer (E006/E007) | cap measured on K1/A2 before scored runs; `answer_of` still rejects narration |
| Ending the run without the required files | "save options.json before you reply"; `complete` requires all files |
| Format drift (ISSUES numbering, markdown headings) | "plain JSON, no code fences, no comments"; parser tolerates missing optional fields; `options_reason` recorded |
| Unsupported claims and invented exposure data (I1), causal asides (K1) | "do not include a framing this data cannot support"; "if the question cannot be answered from this data, say so in each answer"; per-option self-check sentence from C |
| Cosmetic variants passed off as alternatives | distinctness defined on four fields; duplicates flagged by code |
| Reviewer/agent reading files it should not | same sandbox v2; review material not written into the run folder (not applicable to D, which has no review run) |
| Prompt tuned on effect rather than contract | acceptance is format + boundaries only; one edit per iteration, logged |
| A silently re-tuned | A.v1 and C.v3 untouched; D is a separate prompt file |
