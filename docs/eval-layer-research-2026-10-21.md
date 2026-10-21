# Evaluation layer: research for two questions (2026-10-21)

- **Status:** research record for the design discussion; nothing here is decided. Sources are linked inline; items marked [?] were not verified.
- **Q1.** Can objective / automated evaluation become the primary scorer, with humans doing the final review before a freeze?
- **Q2.** Can comparisons across experiments and across repeated runs of one experiment be done that way, and which methods and projects standardize the evaluate → feedback → optimize loop?

## Q1 — Automated evaluation of chart + values + answer

### 1.1 What the literature says per criterion (team's 8 binary criteria)

| # | Criterion | Scorer | Best available method | Reliability reported | Buildable in days? |
|---|---|---|---|---|---|
| 1 | Question answered | code | `values.csv` keys and values vs the gold series within tolerance (VisEval data-legality idea; DABench closed-form matching) | deterministic | yes; we have `gold_cover`, needs a key-aware version |
| 2 | Appropriate measure | code + judge | gold lists the accepted measures (metric × denominator × grouping); BLADE matches analysis decisions to expert ground truth with an LM | BLADE GPT-4o matcher 92–97% on 615 reviewed outputs ([BLADE](https://arxiv.org/html/2408.09667v2)) | yes once gold plans exist |
| 3 | Appropriate chart type | code | read the chart from the Figure object, not the pixels: bars / lines / collections, axes, legend; compare to allowed types | deterministic ([VisEval](https://arxiv.org/html/2407.00981v2), [matplotcheck](https://github.com/earthlab/matplotcheck)) | yes; **prototyped 2026-10-21** (below) |
| 4 | Useful comparison | judge → human | reference-guided binary judge (expected baseline / comparison from the trap sheet); pairwise with position swap across arms | Text2Vis judge r = 0.81–0.91 vs humans ([Text2Vis](https://arxiv.org/abs/2507.19969v1)) | prompt yes; needs ≥ 20 pass + 20 fail labels |
| 5 | Faithful visual encoding | code | bar heights / line data from the Figure vs `values.csv`; axis linter (truncated or inverted axis, inconsistent ticks, dual axis) | axis linter 99.7% precision with true axes ([Misviz](https://arxiv.org/html/2508.21675v2)); pixel extraction worse (DePlot RMS-F1 ≈ 91, MLLM extraction has y-axis bias [2604.24987](https://arxiv.org/abs/2604.24987)) | yes (2–3 d); prototyped |
| 6 | Evidence-aware presentation | code (trap assertions) + judge + human | per-question assertions on code/SQL (NULL borough handled? 2020 break mentioned?) and on text (caveat present?); claim decomposition → recompute ([STAT-TO-TEXT 2609.23966](https://arxiv.org/abs/2609.23966), [VeriGraph 2606.16603](https://arxiv.org/abs/2606.16603) 87.6% grounding); causal-language rubric judge ([CausalPitfalls](https://arxiv.org/abs/2505.13770)) | misleading-chart detection by MLLM 83.5% acc on real Misviz; LLMs near chance on causal-language classification ([UncertaiNLP 2025](https://preview.aclanthology.org/setup/2025.uncertainlp-main.19)); chart–caption consistency checker weak (τ-c 0.18, [CHOCOLATE](https://arxiv.org/html/2312.10160v2)) | assertions 2–3 d; claim decomposition longer |
| 7 | Clear and readable | code + judge | text overflow / overlap from rendered bounding boxes; tick and scale checks; GPT-4V overall 1–5 | VisEval readability SRCC 0.843 vs 3 experts (inter-expert 0.782); drops to 0.507 without the code sub-checks; `pip install vis-evaluator` (MIT) | yes (2–3 d); overlap detection prototyped |
| 8 | Visually well presented | human (judge only for ranking) | pairwise VLM judge with position swap, never absolute scores | GPT-5 r = 0.43 on VisJudge-Bench, fine-tuned judge 0.687 ([2510.22373](https://arxiv.org/abs/2510.22373)); judges rank but cannot score ([2604.25235](https://arxiv.org/abs/2604.25235)); ChartJudgeBench specificity 42–50%, position bias = 35% of errors ([2609.24210](https://arxiv.org/html/2609.24210v1)) | keep human |

**Judge practice that is evidence-based:** code before judge; one binary judge per failure mode; pairwise beats pointwise ([TrustJudge](https://arxiv.org/pdf/2509.21117)); report Cohen's κ, not raw agreement (exact-match agreement overstates by 33–41 pp, [2606.19544](https://arxiv.org/abs/2606.19544)); correct pass rates with TPR/TNR ([judgy](https://pypi.org/project/judgy/)), target > 0.9, floor 0.8; small open judges (≤ 10B) agree 10–80% with GPT-4 ([Judging the Judges](https://arxiv.org/abs/2505.08468)), so the judge must be the stronger model (Luna), not mimo.

**Nothing in 2025–26 scores undisclosed filters, denominators that change meaning, or exposure-less risk claims directly** (closest: CausalPitfalls, Hex's "trap" tasks at 54% ([Hex DataBench](https://hex.tech/blog/databench-agentic-analytics-benchmark/))). Our framing check would be new.

### 1.2 Local verification (2026-10-21)

- **Figure introspection prototype** (`scripts/prototypes/figure_introspect_sitecustomize.py`): a `sitecustomize.py` on the model's `PYTHONPATH` makes every `savefig` also write `<file>.figure.json` (title, labels, limits, scale, ticks, legend, bar centres/heights, line series, overlapping text boxes). On a test chart: bar heights equal `values.csv`; a y-axis starting at 70 is flagged (the I1 miss the Luna reviewer made); overlapping labels listed. No pixels, no judge, no change to the agent: the hook lives in the harness shim.
- **Ground truth** (`docs/ground-truth-audit-2026-10-21.md`): all 16 gold series recomputed independently and match; the interpretive choices the gold encodes are listed, so an automated check can be told which alternative readings are legitimate.

### 1.3 Answer to Q1

Yes, with a boundary that the literature draws clearly:

| Layer | Criteria | Who scores | Status |
|---|---|---|---|
| Deterministic | 1, 3, 5, most of 7; the trap assertions of 6 | code | gold + prototype exist; 1–2 weeks to wire |
| Judge (calibrated) | 4, the text part of 6, overall 7 | one binary judge per criterion, Luna, reference-guided, pairwise for arm comparisons | needs 40–60 human labels per criterion to validate |
| Human | 8; every judge–human disagreement; every unparseable chart; the freeze decision | scorer | stays |

So the proposal "automation as the primary scorer, humans as the final review before freezing" matches how VisEval, Text2Vis and the industry eval guides are built, provided (a) the judges are validated against human labels before they are trusted, (b) criterion 8 stays human, and (c) the human review covers disagreements, not a random sample.

## Q2 — Comparing experiments and runs; the evaluate → feedback → optimize loop

### 2.1 Methodologies (fit for a 3-person team with 6 dev + 10 held-out questions)

| Method | Loop | How "it helped" is shown | Data needed | Fit |
|---|---|---|---|---|
| [Husain/Shankar error-analysis-first](https://hamel.dev/blog/posts/llm-judge/) | open-code traces → taxonomy → binary pass/fail + critique → judge → TPR/TNR | human-labelled dev/test split | ~30 traces to start, ~100 per failure mode to validate a judge | **primary** |
| [Anthropic, Demystifying evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | capability evals (low pass) graduate into a regression suite (~100%) | pass@k vs pass^k; read transcripts | 20–50 tasks from real failures | **framework** |
| [EvalGen / Who Validates the Validators](https://arxiv.org/abs/2404.12272) | grade → discover criteria → align assertions to human grades | human grades on a subset | tens | yes: version the rubric, expect drift |
| [GEPA](https://arxiv.org/abs/2507.19457) (ICLR'26) | reflect on traces + textual feedback → mutate one prompt → minibatch check → Pareto front | per-instance Pareto front; +6% avg over GRPO with ≤ 35× fewer rollouts | a metric returning score + feedback; small valset | partial: copy the pattern (one edit, Pareto check, keep lineage); the optimizer needs a callable program |
| [ACE](https://arxiv.org/abs/2510.04618) (ICLR'26) | generator → reflector → curator; append delta bullets with helpful/harmful counters | held-out benchmark, +10.6% on agents, no labels | traces only | yes for "what goes into the context": a versioned playbook of bullets with hit counters |
| DSPy MIPROv2, TextGrad, Trace, PromptAgent | automatic optimizers | valset score | 100s of examples; programmatic system | no (too little data; human-split steps break them) |
| Reflexion | per-episode reflection | retry pass@1 | none | = our arm B, not a cross-experiment loop |

### 2.2 Comparison protocol for small n (what the statistics literature says)

1. **The unit is the question, not the run.** Repeats of one question are correlated (trajectories diverge early; single-run pass@1 shifts 2–6 pp, [2602.07150](https://arxiv.org/abs/2602.07150)). Effective n ≈ number of questions; repeats are within-cluster samples.
2. **Per candidate change:** same model, same dev questions, baseline vs change, K = 5 repeats each (10 to detect < 15 pp). Do not lower temperature to cut variance ([Miller 2024](https://arxiv.org/abs/2411.00640)).
3. **Scores:** per-question mean over K; paired per-question differences; clustered standard error (Miller); report Δ, SE, 95% CI, pass@K and pass^K.
4. **Binary tests:** exact McNemar on discordant questions; paired bootstrap or permutation on per-question Δ ([evalci 2607.04429](https://arxiv.org/abs/2607.04429)); Holm correction across arms.
5. **Power honesty:** with 16 questions and K = 10, the minimum detectable effect is ≈ 20–30 pp. The loop is a *screen*: accept a change only if the CI excludes 0 (or exact McNemar p < 0.05) **and** there is no regression on the frozen regression items (pass^K); otherwise "inconclusive, add questions or repeats".
6. **Held-out hygiene:** edits come from the dev questions only; the 10 held-out run once per freeze candidate; never edit from held-out failures.

### 2.3 Tooling

| Need | Recommendation | Why |
|---|---|---|
| Re-score saved traces without re-running the model; code and judge scorers; mean/stderr; log viewer | **Inspect AI** (MIT, local; `inspect score log.eval --scorer … --action append`, [docs](https://inspect.aisi.org.uk/scoring-workflow.html)) | fits a team that already has a runner: wrap the JSONL traces as a replay "solver" |
| YAML assertions + CI gates + pairwise `select-best` + diff between evals | promptfoo (MIT, local) | alternative if the team prefers CI-style gates |
| Annotation queue with a UI | Opik (Apache-2.0, self-host) | only if a UI is wanted; a CSV sheet works for ~100 items |
| Keep custom | runner, contract checks, prompt hashes / freeze registry, paired-stats script (numpy or evalci), human review sheet | already exist or small |

Not recommended: hosted-only platforms (Braintrust, LangSmith) for a reproducible, open-source capstone.

### 2.4 Judge-validation checklist

1. One principal labeller; binary pass/fail with a one-line reason; ~30 items to start, continue until no new failure modes appear.
2. Split train 10–20% / dev 40–45% / test 40–45%; aim for 30–50 of each label per split (< 60 labels → CIs too wide).
3. Iterate the judge prompt on dev only; freeze; run test once; report **TPR and TNR separately** (target > 90%, floor 80%) and Cohen's κ ≥ 0.8 (AgentEval κ = 0.84, MAST κ = 0.88 as reference points).
4. Self-consistency: run the judge 3–5× on the same items; Krippendorff α ≥ 0.8 ("Rating Roulette": MT-Bench α as low as 0.27–0.56, [2510.27106](https://arxiv.org/abs/2510.27106)).
5. Correct observed pass rates with Rogan–Gladen (judgy); the CI widens when TPR + TNR − 1 is small.
6. Re-validate after any judge-model or rubric change.
7. Humans stay for every judge–human disagreement, all held-out failures, the freeze decision, and items the judge marks ambiguous.

### 2.5 Agent-specific pieces to copy

- [AgentEval](https://arxiv.org/abs/2604.23581): judge each step as a DAG node; tag errors root vs propagated (2.17× failure recall vs end-to-end, κ = 0.84).
- [AgenTracer](https://arxiv.org/abs/2509.03312): counterfactual replay — rerun from the suspected step with an oracle fix to confirm the decisive step.
- [MAST](https://arxiv.org/abs/2503.13657): the inter-annotator discipline (κ = 0.88) for building a taxonomy.
- [TRAIL](https://arxiv.org/abs/2505.08638), [Who&When](https://arxiv.org/abs/2505.00212): LLMs localize the failing step at ≈ 11–14%: humans localize, LLMs score.

### 2.6 Answer to Q2

Yes for *scoring* and *comparing*; no for *deciding what to change*. The validated pattern is: automation scores every run and computes the paired comparison; humans do the error analysis, pick the one change, and sign the freeze. That is also the division of labour Ryan described (humans extract the "why", the system re-runs and compares).

## 3. Read first

1. Anthropic, Demystifying evals for AI agents. 2. Miller 2024, Adding error bars to evals. 3. Husain, LLM-as-a-judge post + evals-skills repo. 4. EvalGen. 5. GEPA. 6. ACE. 7. Bjarnason, On randomness in agentic evals ([2602.07150](https://arxiv.org/abs/2602.07150)). 8. Inspect AI scoring workflow docs. 9. VisEval (and `vis-evaluator`). 10. Misviz axis linter.

## 4. Open-source to reuse

[microsoft/viseval](https://github.com/microsoft/viseval) (MIT), [UKPLab/acl2026-misviz](https://github.com/UKPLab/acl2026-misviz), [earthlab/matplotcheck](https://github.com/earthlab/matplotcheck), [behavioral-data/BLADE](https://github.com/behavioral-data/BLADE), [vis-nlp/Text2Vis](https://github.com/vis-nlp/Text2Vis), [judgy](https://pypi.org/project/judgy/), [hamelsmu/evals-skills](https://github.com/hamelsmu/evals-skills), Inspect AI, promptfoo. Not needed: DePlot/SIMPLOT pixel extraction (we have the Figure object), fine-tuned chart judges (no training data).
