# Mentor meeting 2026-10-16 — notes, and the plan that follows

- **Status:** Bo's integration draft after the meeting (transcript + teammates' notes), for team discussion. Decisions marked *(team)* are open.
- **Next:** Thursday 2026-10-22, 5 pm ET: show the midterm slides to Ryan (replaces the Friday meeting). Midterm presentation Friday 2026-10-23, in person.

## 1. What Ryan said

| Topic | Ryan's point | Consequence |
|---|---|---|
| Overall | "Totally aligned on everything." Of the two ways to improve a model (fine-tune on failure modes vs in-context learning), the project is the second, which he prefers: generate runs, use an LM to produce feedback, update prompts, re-run. | Phase 1's design stands. |
| Frontier model | Use the API key he put in the shared Drive and repeat everything with **GPT-6 Luna** through OpenCode: a free open-weight model vs a lower-tier frontier model. Does the frontier model reduce hallucination, produce better output, and avoid the rate limits. | Add the model as a second factor (E008). |
| Creativity | Two parts to the problem: (1) ~80% is "can it generate an accurate visualization" (charts that look right but use made-up miles are "deeply problematic"); (2) once accurate, **widen the options**: "these are three ways that accurately represent the data, and why you would pick each". Pointed to **Verbalized Sampling** (verbalized-sampling.com; Zhang et al., arXiv 2510.01171): ask for k responses with probabilities. Suggestion: generate 3–5 ways to visualize the data with a probability for accuracy / strategic fit, render them (the key removes the limit problem), then let the reflective loop choose. "Not heavy work: one line in the prompt." | New arm and a new evaluation dimension (E009). |
| Evaluation table | The 8 binary criteria are fine. The missing category is creativity / alternative views. | Keep the team's 8 criteria; add a separate diversity dimension, not folded into the accuracy score. |
| Cost | The teammate asked whether to stop the revise run from re-running all the code (half of B's cost): prompt fix or harness fix? Ryan: no direct visualization experience; **do not optimize cost or latency now**. First find out whether something works; optimize later. Report trade-offs as direction arrows: cost ↑ / ↓ / flat, quality ↑ / ↓ / flat. | B's architecture stays as frozen (Bo's decision stands). Report format: arrows table. |
| What success means | No expectation that we "solve" it. "LLMs are not trustworthy for visualizations" would also be a win. Try things, record outputs, put numbers on prompt changes ("hallucinations −10 or −20%"). The evaluation loop (capture traces → augment → re-run) is the generalizable part. | Matches the parked v2 design (improvement loop with per-step checks). |

## 2. How this maps onto what we have

- **Phase 1 (A/B/C, frozen prompts, contract-verified harness)** is the "accuracy" 80%. Ryan validated it; nothing changes except that it now runs on two models.
- **"Widen the options"** is the *enumerate* step from `docs/direction-v1.md` §4 (2–4 legitimate interpretations, one chart each) and the `interpretations[]` field of S1 PLAN in `docs/pipeline-v2-design.md`. Verbalized Sampling is a prompting technique for that step. Ryan arrived at our phase-2 question from the product side.
- **"Reflective loop over traces, generalizable to any LLM use"** is v2's principle 3 and §5 (findings become versioned changes, proven on re-runs). v2 can now be presented as the plan Ryan asked for, not as Bo's side project.
- **Arrows table** is a presentation of the ITT summary table we already planned (§5 of the design doc): per change, cost and quality direction with the numbers underneath.

## 3. Proposed experiments

### E008 — model contrast (Ryan's ask)

- Same frozen A/B/C prompts, same sandbox, same questions, on **GPT-6 Luna via OpenCode** (provider config, key from the environment, never in the repo). B's prompts were tuned on mimo and are **not re-tuned** for the frontier model; this is stated as a transfer condition, not a weakness to fix.
- Pre-checks before any scored run: (1) the provider works inside our sandbox config (tools present, 403-free); (2) the model reads images (E005 procedure) so B's review can see the chart; (3) step and time profile on K1 (budget may be generous for a faster model; keep 15 / 600 for comparability).
- Design: 10 questions × 3 repeats × 3 arms × 2 models. Mimo stays, because the whole pilot was done on it and because "free model vs frontier" is the contrast Ryan wants.
- Predictions, written now: frontier model raises A's completion on ambiguous items (A1-type exploration drift shrinks), lowers silent errors, and leaves B with less to find; B's review precision stays high; C's gain, if any, is larger on the frontier model (self-check needs capability).
- Cost: logged per run (tokens, time), reported as arrows plus numbers; not optimized.

### E009 — enumerate with Verbalized Sampling (Ryan's ask; our phase-2 question)

- **Arm D ("enumerate")**: A's prompt plus one instruction asking for **k = 3 different charts that each correctly answer the question**, each with a short reason and a probability, following the VS "magic prompt" structure (separate `<response>` blocks with `<text>` and `<probability>`), adapted so that the probability is "how likely a careful analyst would choose this view". Two variants, one lever at a time *(team)*: D1 = VS wording verbatim (tail sampling, p < 0.10 each); D2 = the adapted accuracy-conditioned wording.
- Execution: one agent run that saves `out/option_1..k.png`, `values_1..k.csv` and `options.json` (text, probability, chart type, metric, denominator). The step cap for D is raised in proportion (k × 15 is too loose; propose 30) and reported as D's cost.
- **Selection**: D's own reflective step can be B's frozen reviewer used as a chooser ("which option best answers the question and why"), which reuses tested code. Whether the product shows one chart or the set is a later decision; for the experiment we score both the chosen chart and the set.
- Questions: the 10 formal questions, with emphasis on the ambiguous ones (7–8), where multiple legitimate readings exist.
- **Gold for diversity**: for each question the gold author lists the legitimate interpretations (metric × denominator × grouping × chart family) before the run, as in direction v1 §4. Written by someone who does not tune prompts.

### Metrics for the creativity dimension (separate from the 8 accuracy criteria)

| Metric | Definition | Why |
|---|---|---|
| Accuracy per option | each option passes the correctness gate | diversity only counts among correct options; VS must not buy diversity with wrong charts |
| Distinct interpretations | number of options that differ in metric, denominator, grouping or chart family (not cosmetic variants) | the quantity Ryan asked for |
| Coverage | distinct correct options ∩ gold legitimate interpretations / gold | recall of the expert's list |
| Mode share | whether the highest-probability option equals A's single output | tests the "model gives the average answer" claim directly |
| Cost | steps, tokens, time vs A | arrows |

Caveats to state up front: verbalized probabilities are not calibrated and are used for ranking only; the VS paper reports larger gains for more capable models, so D is expected to work on the frontier model and may only burn steps on mimo (that difference is itself a result); the creativity criterion must never be scored before the accuracy gate.

### Pipeline v2 (after the midterm)

The toy pipeline with per-step checks (`docs/pipeline-v2-design.md`) is the generalizable evaluation loop Ryan described. Proposed order after E008/E009 produce a corpus of failures: S0 profile + S1 plan + S2 checks first (the enumerate arm already produces S1-like plans), S6 verify (recompute every number in the answer) second, since unsupported numbers were the most common finding in the pilot. *(team)*

## 4. Schedule to the midterm

| When | What | Who |
|---|---|---|
| 10-17 | C prompt written and format-checked; provider config + E008 pre-checks (sandbox, vision, K1 profile) | Bo (C); Bo + one teammate (provider) |
| 10-17 → 10-20 | Formal run on mimo: 10 Q × 3 reps × A/B/C, split across three machines by question; results by PR | all |
| 10-18 → 10-20 | Formal run on GPT-6 Luna, same split | all |
| 10-19 → 10-21 | Blind scoring (8 criteria + flips + review labels); arrows table | all |
| 10-20 → 10-21 | E009 smoke test: D on 2–3 ambiguous questions, both models; gold interpretation lists | Bo + gold author |
| 10-22 5 pm | Slides to Ryan | all |
| 10-23 | Midterm | all |

If the formal run slips, the midterm shows the pilot results plus the E008 pre-checks and the E009 smoke test; that is already more than the current deck.

## 5. Decisions for the team

1. Confirm E008: two models, frozen prompts not re-tuned, mimo kept.
2. E009 arm D: k = 3; wording D1 (verbatim VS) and/or D2 (accuracy-conditioned); step cap 30.
3. Who writes the gold interpretation lists (must not be a prompt author).
4. Evaluation: the 8 binary criteria are the final-view rubric; the 0–12 scale in the design doc is retired *(team)*. Flips, review labels and the creativity metrics are reported next to it.
5. Slides: replace the B and C charts in the deck with frozen-version outputs (`results/B-v4-v3/`) and drop the C-v1 chart on Q6 (it used recalled mileage numbers and predates the sandbox fix).
