# E009 — Arm D: enumerate framings with verbalized probabilities (simplified, phase-1 add-on)

- **Status:** design draft 2026-10-18, Bo's experiment. To be fixed with Bo before the first scored run. The formal version (selection step, judge, framing coverage against expert lists on P1–P10) is a phase-2 decision.
- **Origin:** Ryan (2026-10-16): once a chart is accurate, widen the options; ask for 3–5 ways to visualize with probabilities (Verbalized Sampling, Zhang et al., ICML 2026, arXiv 2510.01171), render them, let the reflective loop choose.

## 1. What D is

D = C's prompt (analysis run with one self-check instruction) + one block: produce **k = 3 different framings** that each correctly answer the question, each with a reason and a probability, each rendered as its own chart with its own values file, plus `options.json`. One run, same sandbox as A/C, step cap 30 (k charts in one run; the extra budget is reported as D's cost).

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
| `out/options.json` | `options`: list of k objects with `id, metric, denominator, grouping, chart_type, reason, probability, answer`; `recommended`: id + one sentence |
| reply | `ANSWER:` line: the recommended framing's conclusion and one sentence per other framing |

`run_pilot.py D` parses this into `meta.json`: `options_parsed`, `n_options`, `n_complete_options` (png + csv + all fields), `n_distinct_framings` (framing = metric × denominator × grouping × chart_type, lower-cased), `recommended`, per-option records. `complete` = parsed ∧ k complete options ∧ k distinct framings ∧ ANSWER present.

## 3. Acceptance for the D prompt (format, as for B)

On the 6 pilot questions, mimo, one run each: ≥ 5/6 runs `complete`; no run uses the network or leaves its folder (contract); duplicates by framing ≤ 1 across all runs. Prompt tuning follows the pilot rules: one edit per iteration, each tied to an observed failure, logged in `ITERATIONS.md`; at most 3 iterations; A and C untouched. Effect (coverage, accuracy of options) is not an acceptance criterion.

## 4. What is measured in the simplified version (no judge, no selection step)

| Metric | How | Grader |
|---|---|---|
| Option accuracy | for the framing that matches the gold series: `values_<id>.csv` vs gold; other framings: human gate (8 criteria) until the recompute oracle exists | code / human |
| Distinct framings | from `options.json` fields | code |
| Framing coverage | share of an expert list of legitimate framings per question (3–5 per ambiguous question, written by a teammate who does not tune prompts) that the k options cover | human list, code match |
| Mode share | is the highest-probability option's framing the same as A's (and C's) single framing? | code (framing fields) + human check |
| Cost | steps, tokens, time vs C | code |

Predictions, recorded before the first scored run: on mimo, `complete` is harder to reach than for C (format and budget) and framings often collapse to cosmetic variants; the highest-probability option usually equals A's single answer; on GPT-6 Luna (phase 2) coverage is clearly higher than A's with no loss of option accuracy.

## 5. Variants

- **D2 (this draft):** accuracy-conditioned wording, no tail sampling. Run first.
- **D1 (optional):** VS wording verbatim, including "sample from the tails, probability < 0.10 each". Only if D2 is stable; one lever at a time.

## 6. Open points for Bo

1. k = 3 fixed, or 3 for clear and 5 for ambiguous questions?
2. Should the `ANSWER:` line recommend one framing (the model's own reflective choice, kept in v1) or stay neutral?
3. Which questions for tuning: the 6 pilot questions (disjoint from P1–P10, as for B) — proposed.
4. Step cap 30: keep, or measure first on K1/A2 and set from data?
