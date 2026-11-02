# E009 follow-ups: three experiments on arm D (team decision 2026-11-01)

Order agreed: (1) free number of options + per-option reason and interpretation → (2) rephrased questions → (3) reverse inference. Bo runs (1) now; the phase-2 inventory (`docs/v2-design-inventory.md`) is drafted meanwhile so decisions follow right after.

Common rules: GPT-6 Luna; the 6 pilot questions; D v1 (`D_enumerate.v1.md`, k = 3, cap 25) is the baseline for every comparison; one change per variant; acceptance is format and boundaries (as for D v1); effects are reported with the MDE caveat (6 questions: screens only); repeats K = 3 minimum, 5 when time allows; every variant's prompt committed before its first run.

## 1. E009-F1 — free k and fuller interpretation (D v2)

**Change from D v1 (two things, deliberately, because the team wants their joint effect first):** (a) no fixed k: "produce every framing a careful analyst would consider defensible, and no more"; the probabilities still sum to about 1; (b) each option carries `reason` (why an analyst might choose it, as in v1) **and** `interpretation`: two or three sentences on what the chart shows and what it does not (v1's `answer` field becomes the one-sentence conclusion; `interpretation` is new).

**Why it matters:** VS's k is a free parameter in the paper (5 for creative text); the model's own choice of k tells us how many defensible framings it believes exist, and whether extra options are real or padding. The interpretation field tests whether disclosure improves when the model is asked to say what the chart does not show.

**Outputs:** as v1 plus `interpretation`; `n_options` free. Harness: `PILOT_K=0` → free k; `PILOT_STEPS=35` (measured on K1 and A2 first; recorded in meta).

**Measures:** number of options per question (and its spread over repeats); distinct analytic framings; duplicates; option accuracy (gold match where a reading matches gold; human otherwise); disclosure in `interpretation` checked against the trap sheet (TR05 on A1, TR01 on A1/I1, exposure on A1/A2/I1); probability concentration (max p); steps and time vs v1 (direction only).

**Pre-registered predictions:** median k on clear questions 2–3, on ambiguous 3–5; beyond 3 options the share of cosmetic duplicates rises; `interpretation` raises exposure disclosures (already 9/9 in v1) and may raise TR05/TR01 disclosures from 0/6 to some, but not most; steps rise roughly linearly with k.

**Acceptance:** ≥ 5/6 runs complete (every option has chart + values + all fields, options.json parses); no boundary violation; duplicates ≤ 1 per run.

## 2. E009-F2 — rephrased questions

**Change:** the same six questions in 2–3 alternative phrasings each (same information need; different surface form: casual / formal / with an explicit "show me alternatives" / with a news-report framing), written by a teammate, committed before the runs. D's prompt unchanged (the winner of F1).

**Why:** phase 1 compared arms on one phrasing; a robust D should produce the same framing *set* under paraphrase. Sensitivity to phrasing is itself a finding (prompt brittleness).

**Measures:** framing-set overlap across phrasings (Jaccard on hand-coded analytic framings), top-option stability, option count stability, accuracy; per phrasing: completion.

**Prediction:** the top option is stable across phrasings on clear questions and unstable on ambiguous ones; "show me alternatives" phrasing raises k.

## 3. E009-F3 — reverse inference ("does this option answer the question that was asked?")

**What the team proposed:** give each option's output (chart, values, answer) to an independent model, have it infer the question, and compare the inferred question with the original to judge the option's credibility.

**Sharpened purpose (Bo's analysis):** this is a **reference-free question-alignment check**, the cycle-consistency idea (back-translation in MT; "intent recovery" in NL2VIS). It measures criterion 1 ("question answered") and part of criterion 2 ("appropriate measure") **without a gold plan**, and it is the one check that can catch an option that silently answers a different question: an I1 option that answers "deaths per crash" when asked "deaths per mile", or an A1 option that answers "Brooklyn-assigned records" when asked "Brooklyn". It does **not** measure correctness, readability or disclosure; those stay with the other checks. Its value grows with the number of options (F1), because each extra option needs an alignment verdict and no human wants to write one per option.

**Design decisions that make it valid:**
1. **Leakage control.** Chart titles and the written answer usually restate the question; an inference from them is trivial. Run two conditions: *full* (chart + values + answer) and *stripped* (values.csv + chart with title/axis labels removed by the figure hook, no answer). The stripped condition is the real test; the full condition is the ceiling.
2. **Output of the inferring model:** not only a question string but a structured guess: `{question, metric, denominator, grouping, time_window, population}`; the structured fields are compared to the asked question's gold plan fields (exact for denominator and population; judge for the free text).
3. **Comparison:** binary judge "would the original question be a reasonable prompt for this output?" (position-free, reference-guided by the original question), plus field-level agreement; report per option and aggregated per question.
4. **Independence:** the inferring model must not be the generator in the same run; use Luna for mimo outputs and mimo (or a third model) for Luna outputs, or Luna with a fresh context and no access to the run folder (the review sandbox).
5. **Validation before trust:** 30–40 options hand-labelled "answers the asked question / answers a neighbouring question / unrelated"; report TPR/TNR of the alignment verdict; the known cases (I1 per-crash options, A1 borough-filtered options) must be caught in the stripped condition.

**Measures:** alignment rate per option, per arm (A/B/C single outputs can be scored the same way, giving a cross-arm criterion-1 score without humans); mismatch types (denominator / population / time window / topic); agreement with human labels.

**Prediction:** full condition ≈ 100% alignment (leakage); stripped condition separates options: K-type options align, I1 per-crash and A1 borough-filtered options are classified as neighbouring questions; the top-probability option aligns more often than the others.

**Where it lands in phase 2:** an evaluation-layer check (question alignment, reference-free) usable on every arm, and a candidate selection signal for D.
