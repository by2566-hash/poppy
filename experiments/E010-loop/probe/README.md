# Embedding probe (design §4, "Validation before use"), 2026-11-08

**Question.** Does a local sentence-embedding model order cosine distance as paraphrase < neighbour < unrelated? If it fails on neighbours (hard negatives), the judge class is the only alignment measure and embedding distance stays a diagnostic (design §4).

**Inputs.**
- Paraphrases: the three phrasings (original, casual, formal) of the six pilot questions from F2, giving 18 pairs.
- Neighbours: `neighbours.draft.json`, 19 questions, each changing one field of the original phrasing. Each is paired with the 3 phrasings of its base, giving 57 pairs. **Drafted by Claude. A teammate still has to check them** (one field changed; a plausible question; not a legitimate reading of the base question).
- Unrelated: phrasings from different bases, giving 135 pairs.
- The design's A2 example ("crashes per hour" vs "casualty share") is two *legitimate* readings of an ambiguous question. It is reported separately as a reading pair and is not counted as a negative.

**Setup.**
- Models already cached locally, run offline (`HF_HUB_OFFLINE=1`), no API: `sentence-transformers/all-mpnet-base-v2` and `sentence-transformers/all-MiniLM-L6-v2`.
- Separate venv `~/.poppy/embed-venv` (`requirements-embed.txt`) so the team venv the agent runs in is not touched.
- Run with `HF_HUB_OFFLINE=1 ~/.poppy/embed-venv/bin/python experiments/E010-loop/probe/probe_embedding.py`. Raw output is in `probe_results.json`.

**Result.**

| | all-mpnet-base-v2 | all-MiniLM-L6-v2 |
|---|---|---|
| mean distance: paraphrase / neighbour / unrelated | 0.069 / 0.110 / 0.414 | 0.057 / 0.126 / 0.407 |
| AUC paraphrase < unrelated | 1.000 | 1.000 |
| AUC neighbour < unrelated | 0.996 | 1.000 |
| **AUC paraphrase < neighbour** (95% CI, bootstrap over the 6 bases) | **0.729** (0.69–0.79) | **0.853** (0.75–0.97) |
| per base K1 / K2 / K3 / A1 / A2 / I1 | 0.70 / 0.89 / 0.82 / 0.67 / 0.78 / 0.78 | 0.74 / 0.89 / 0.93 / 0.72 / 1.00 / 1.00 |
| reading pair (A2) | 0.111 | 0.140 |

Neighbours sitting inside the paraphrase range:
- all-mpnet-base-v2: K1-n3 "in each borough" 0.016; K3-n3 "across boroughs" 0.016; K1-n2 "injured" instead of "killed" 0.025; A1-n4 Queens instead of Brooklyn 0.041.
- The largest paraphrase distance is 0.04 on K1 and 0.14 on A1.

**Reading.**
- Embedding distance cleanly separates "about the same question" from "about a different question" (AUC ≈ 1.0).
- It does **not** reliably separate a paraphrase from a one-field substitution (AUC 0.73–0.85). The cases that matter most are exactly where it fails: killed vs injured, borough vs year, Brooklyn vs Queens, and the Brooklyn-code filter.
- By the design rule, embedding stays a diagnostic for coarse drift. Alignment on hard cases (substitution) needs the judge.
- MiniLM scores higher here, but on 18 positive pairs from 6 bases. Choosing a model on this probe would overfit it, so both are reported.

**Limits.** The neighbours are hand-written and still unchecked. In use, the distance will be between the asked question and a question *inferred from values.csv*, whose wording differs more than these pairs. So this probe is an upper bound on how separable the classes are.
