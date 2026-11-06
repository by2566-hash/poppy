# F1 slide (phase-2 deck, slide 2): content to paste

Figure: `f1_v1_vs_v2.png` (from `make_f1_figure.py`, reads the g8 score sheets). Numbers: `experiments/E009-enumerate/ITERATIONS.md` ("E009-F1", "Decision 7, grader g7 → g8").

## Title
F1 · Free k + question-anchored interpretation (D v2 vs D v1)

## Left column (three short blocks)

**Design**
- One prompt change, two parts: no fixed k ("every framing a careful analyst would defend, no padding"), and each option adds an *interpretation*: which part of the question it answers, why that is defensible, what it leaves open.
- GPT-6 Luna, 6 pilot questions × 3 runs, against D v1 (k = 3). Both prompts frozen before the runs.

**Results**
- 18/18 runs complete. k median 2 (range 1–3): fewer options on clear questions; 5 of 42 options are the same analysis drawn as another chart type.
- Runs are faster (median 76 s vs 96 s); steps unchanged (median 14).
- The facets an option claims to answer repeat on clear questions (K1 identical in all runs) and drift on ambiguous ones (A1, A2 share 1 facet across 3 runs; the top option changes on A1 and I1).

**Evaluation**
- Options with a silent error: v1 24/54, v2 14/42. Six questions cannot separate this from noise (MDE at least 48 points).
- Framing errors are unchanged: the Brooklyn filter is never disclosed (A1, 9/9), and the per-crash rate never mentions the 2020 recording change (I1, every run).
- Grader: two Luna passes agree on 98% of verdicts; every plotted value re-derived independently.

## Bottom line (one sentence, bold or in a bar)
Free k and the interpretation field change how many options come back and how they are explained, not the framing errors; prevention has to come from elsewhere (data profile, plan check).

## Speaker notes
- K1 (8/9 → 0/5) is wording, not v2: the same v2 prompt failed 9/10 K1 options in F2 because the text never says the deaths are reported counts in this dataset.
- A2 v2 2/7 includes two TR08 verdicts set by rule (decision 2: NULL-killed rows excluded), pending Bo's confirmation.
- Grader g8 = standard decisions 1–7 (SCORING.md §4); g7 was replaced before use because its wording was read too literally.
