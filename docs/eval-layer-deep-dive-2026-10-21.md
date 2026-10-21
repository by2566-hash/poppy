# Evaluation layer, deep dive (2026-10-21)

Three questions, answered with sources and with tests on our own data. Nothing here is decided.

1. Can automated evaluation be the primary scorer, per question type (clear / ambiguous / insufficient-evidence)?
2. Is the evaluate → analyse → change → re-run → keep-or-revert loop a standardized, documented process, and is the analyse-and-decide step human?
3. Are the fixes proposed in `docs/problem-register.md` the right ones for this project? (reviewed as a senior FDE/SDE would)

Sources are linked; [?] = not verified. Local tests: `experiments/E007-pilot-prompts/judge_calibration_2026-10-21.csv`, `scripts/prototypes/`.

---

## Part 1 — Automated evaluation by question type

### 1.1 CLEAR questions (one correct series; K1–K3, P1–P6)

| Method | Scores | Agreement with humans | Code | Fits us |
|---|---|---|---|---|
| DABstep quasi-exact match: strip `$`/`,`, numeric tolerance, order-insensitive lists, Levenshtein ≥ 0.95 for strings ([paper](https://arxiv.org/html/2506.23719), [code](https://huggingface.co/spaces/adyen/DABstep/tree/main/baseline)) | final answer / series | designed to need no judge | yes | **yes: the template for `values.csv` vs gold** (add column-name and unit canonicalisation) |
| InfiAgent-DABench: tagged answers → regex → exact match; rounding fixed in the question ([paper](https://arxiv.org/html/2401.05507), [repo](https://github.com/InfiAgent/InfiAgent)) | scalars | reformatter 0 errors on 50 checks | yes | yes |
| VisEval: ground truth is a *feasible region* (allowed channel swaps, stacked ↔ grouped); legality from the chart spec; readability from layout checks + GPT-4V ([paper](https://arxiv.org/html/2407.00981v1), [repo](https://github.com/microsoft/VisEval), MIT) | chart executes, matches data and type, readable | readability SRCC 0.843 vs humans (human–human 0.782); overlap 100%, ticks 99% | yes (matplotlib) | **yes for chart checks**; our `figure.json` hook supplies the spec without SVG parsing |
| DataSciBench TFC/IFC: programmatic rules + VLM 5-point chart check vs gold chart ([paper](https://arxiv.org/html/2502.13897v1), [repo](https://github.com/THUDM/DataSciBench/)) | tables + chart | none reported | yes | partial |
| ConDABench G-Eval-style correctness judge ([paper](https://arxiv.org/html/2510.13835v1)) | answer ≈ reference | GPT-4o 88.1% match, r = 0.748 | partial | only as an answer extractor |

**Verdict: automation primary.** Numbers by normalised matching, chart by introspection + VisEval-style checks; humans audit mismatches only.

### 1.2 AMBIGUOUS questions (several legitimate framings; A1, A2, P7, P8)

| Method | Scores | Agreement with humans | Code | Fits us |
|---|---|---|---|---|
| HealthBench: per-example expert-written binary criteria with weights ([paper](https://arxiv.org/html/2505.08775v1), [code](https://github.com/openai/simple-evals)) | expert criteria coverage | GPT-4.1 grader macro-F1 0.709 vs physicians; physician–physician raw agreement 55–75% | yes | **yes: the template for per-question rubrics built from the trap sheet** |
| Rubrics as Rewards: 7–20 weighted binary items incl. "pitfall" items ([paper](https://arxiv.org/html/2507.17746)) | weighted checklist | rubric judges beat Likert judges at all sizes | data only | yes |
| CheckEval: decompose Likert into binary questions ([paper](https://arxiv.org/html/2403.18771v3), [repo](https://github.com/yukyunglee/CheckEval)) | binary checklist | ρ 0.50 vs G-Eval 0.32; inter-judge α 0.48 vs 0.09 | yes | yes (pattern) |
| BLADE: coverage of expert analysis decisions (variables, transforms, model), LM matcher ([paper](https://arxiv.org/html/2408.09667v1), [repo](https://github.com/behavioral-data/BLADE)) | were the framing choices defensible | matcher 92–97% correct on 615 items; agents' coverage of expert choices < 13–27% | yes | partial: needs 2–3 expert framings per question first (= our gold plans) |
| Set-level / multiverse: Agentic Garden of Forking Paths ([paper](https://arxiv.org/abs/2607.01507)); Many AI Analysts ([paper](https://arxiv.org/pdf/2602.18710)) | is the chosen framing inside the defensible set | AI review vs human expert review gap ≈ 8 pts | [?] | partial: use to *generate* the defensible set |
| Ambig-DS: paired specified/ambiguous tasks; scores silent misframing ([paper](https://arxiv.org/abs/2605.09698)) | did the agent flag the framing | scorer not validated | no [?] | design pattern only |
| Disclosure / assumption scoring | stated caveats | **no validated benchmark exists** (closest: LimGen 1–5 judge, SOC-report criteria) | no | write as HealthBench-style binary items; pilot with human spot checks |

**Verdict: partial.** Per-question binary rubrics graded by the frontier model reach roughly expert-level agreement (macro-F1 ≈ 0.7, which is the physician–physician noise level). Writing the criteria and adjudicating "defensible framing" stay human. Disclosure scoring has no precedent to copy; it must be piloted with human checks.

### 1.3 INSUFFICIENT-EVIDENCE questions (I1, P9, P10)

| Method | Scores | Agreement with humans | Code | Fits us |
|---|---|---|---|---|
| AbstentionBench: judge "did it abstain / caveat / partially answer" + correctness; recall of should-abstain, precision = over-abstention ([paper](https://arxiv.org/html/2506.09038v1), [repo](https://github.com/facebookresearch/AbstentionBench)) | correct decline vs fabricate vs over-refuse | 88% vs manual labels | yes | **yes: reuse the judge prompt** |
| STAT-TO-TEXT: the LLM writes a pandas checker per quantified claim and executes it on the table ([paper](https://arxiv.org/abs/2609.23966)) | is each numeric claim supported by the table | 91.5–97.5% agreement with humans; errors skew to false negatives (172 of 211 disagreements) | [?] | **yes: fits `values.csv` exactly** |
| Two Axes of Abstention: separate answerability and correctness; unanswerable-answer rate, wrong-answer rate, coverage ([paper](https://arxiv.org/abs/2607.08456)) | metric design | probe AUROC 0.69–0.77 | no | adopt the metrics |
| SelfAware / UnknownBench ([2305.18153](https://arxiv.org/html/2305.18153v2), [2311.09731](https://arxiv.org/abs/2311.09731v2)) | self-knowledge | human F1 84.9 vs GPT-4 75.5 | yes | partial |
| FActScore / VeriScore atomic claims ([repo](https://github.com/shmsw25/factscore), [paper](https://www.alphaxiv.org/abs/2406.19276)); TabVer ([repo](https://github.com/Raldir/TabVer)) | claim precision / table entailment | FActScore < 2% error vs humans; TabVer 71.4 on FEVEROUS | yes | partial (swap retrieval for CSV lookup) |
| Numeric robustness warning: frontier zero-shot 74% vs fine-tuned small model 98.7% on perturbed numeric claims ([paper](https://arxiv.org/abs/2610.00689)) | — | — | — | **do not let a judge eyeball numbers; execute** |
| BIRD-Interact, DV-Interact (user simulators) | asking vs guessing | — | yes | no for abstention |

**Verdict: partial to yes.** AbstentionBench's binary abstain judge + execution checks of every numeric claim cover most of it; humans still judge whether the "what the data can show" fallback and the stated limitation are the right ones.

### 1.4 Cross-cutting evidence

- Binary beats Likert: CheckEval (α 0.48 vs 0.09), Rubrics-as-Rewards, HealthBench; Husain's pass/fail + critique ([post](https://decodingml.substack.com/p/the-5-star-lie-you-are-doing-ai-evals)). Counterpoint: a calibrated 7-point Likert ≈ pairwise ([2604.11581](https://arxiv.org/pdf/2604.11581)).
- Judge agreement on visualization outputs: Text2Vis GPT-4o r = 0.85 answer / 0.84 readability / 0.81 chart correctness, κ 0.78 ([paper](https://arxiv.org/html/2507.19969)); VisJudge-Bench aesthetics r = 0.43 ([paper](https://arxiv.org/abs/2510.22373)); ChartJudgeBench accept/reject 74–79% for the best models, judges over-accept ([paper](https://arxiv.org/html/2609.24210)). Judges rank better than they score ([2604.25235](https://arxiv.org/abs/2604.25235)).
- Frontier error detectors are high-precision, low-recall (ReaLMistake: GPT-4 P 100 / R 6.8 on context faithfulness; "detect errors" wording adds ≈ 17 points of recall) ([Kamoi et al. COLM 2024](https://arxiv.org/abs/2404.03602)). Validators are "agreeable": TPR > 96% but TNR < 25% across 14 LLM validators; fix = minority veto, not majority vote ([Beyond Consensus](https://arxiv.org/abs/2510.11822)).

### 1.5 Local verification on our runs (2026-10-21)

| Prototype | What it did | Result | What it means |
|---|---|---|---|
| Recompute oracle (number derivability) | 307 numbers in every phase-1 written answer checked for derivability from `values.csv` (direct, sum, mean, min/max, difference, ratio, % change, per-k scaling) | 99% derivable; the 4 flags were false positives ("5:59 am", "24 hours"); **the three known errors (K2 "32% fewer", A2 "8× the midday rate", I1 per-mile) were not flagged** because their numbers are derivable with the wrong base or label | a membership check catches invented numbers (none occurred after the sandbox fix) but not mis-based claims; the check must be **claim-level with an executed checker** (STAT-TO-TEXT), not number-level |
| Trap assertions (code + answer text) | TR05: borough filter in code without disclosure in the answer; TR01: per-crash rate in the answer without a reporting-change caveat | TR05 flagged on **all 6** A1 runs that produced code (mimo A/C, Luna A/C/D); TR01 regex hit mimo B's I1 (caveat present) and missed D's "per 100,000 reported crashes" wording | the check works and finds the framing problem everywhere; regex over free text is brittle; a plan declaration (`plan.json`) makes it exact |
| Claim judge calibration (GPT-6 Luna, read-only config, data dictionary, 32 sentences from phase-1 answers; labels by Claude, not yet by a human) | SUPPORTED vs UNSUPPORTED (cause, exposure-based risk, external number) | **TPR 4/7 = 0.57, TNR 25/25 = 1.00**; misses: "safety improved vs 2013" from counts, and the compound "Yes — … night crashes are far deadlier" overclaim | exactly the literature's pattern (high precision, low recall); recall needs per-claim decomposition, a "detect errors" framing and a forbidden-claim list; **not usable as a primary scorer until recall ≥ 0.8 on human labels** |
| Figure introspection (`savefig` hook) | per-axes title, labels, limits, ticks, legend, bar heights, line data, text overlaps | bar heights = `values.csv`; y-axis starting at 70 flagged; overlaps listed | criteria 3, 5, 7 can be code |

---

## Part 2 — The loop: is it standardized, and is the analysis step human?

### 2.1 Standards compared

| Source | Loop | Artifacts | Keep / revert gate | Human-mandatory | URL |
|---|---|---|---|---|---|
| Husain & Shankar, Field Guide (2025) + Evals FAQ (2026) | look at data → custom viewer → open coding → axial coding (taxonomy + counts) → fix top modes → dataset → binary judge calibrated to humans → change and re-run | ≥ 100 traces to saturation; taxonomy; judge labels split 10–20 / 40–45 / rest; prompts in Git; CI set 100+ | CI pass-all | domain expert does open coding (≥ 30 traces before any LLM help); "benevolent dictator"; outsourcing error analysis is "a big mistake" | [field guide](https://hamel.dev/blog/posts/field-guide/), [FAQ](https://hamel.dev/blog/posts/evals-faq/), [evals-skills](https://github.com/hamelsmu/evals-skills) |
| Anthropic, Demystifying evals (Jan 2026) | 20–50 tasks from real failures → unambiguous tasks + reference → balanced sets → isolated harness → graders (deterministic > LLM > human) → read transcripts → watch saturation → maintain | task set, graders, references, transcripts; pass@k vs pass^k | regression suite beside capability evals; no numeric gate | "you won't know if your graders are working unless you read the transcripts" | [link](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) |
| OpenAI cookbook, Agent Improvement Loop + trace grading | traces → human + LLM feedback → generated promptfoo evals → gate → ranked harness changes → implementation → re-run | JSONL traces, feedback tied to trace ids, eval defs | promptfoo gate must pass | SME feedback; reviewer gates at trace review, eval refinement, PR, merge | [cookbook](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop), [trace grading](https://developers.openai.com/api/docs/guides/trace-grading) |
| LangChain, Better Harness (2026) | tag evals → optimization / holdout split → baseline both → diagnose → **one change** → validate → human review | tagged evals, holdout | accept iff net-positive on new evals without regressing | review before acceptance | [link](https://www.langchain.com/blog/better-harness-a-recipe-for-harness-hill-climbing-with-evals) |
| Hex, Hill climbing + Evals docs | agent proposes changes; 10 runs per case; ~40% holdout hidden | baseline vs hill-climbing suites | accepted only when holdout improves; 3 runs too noisy, 10 → 0.2 pp noise | human reads the first ~150 cases, sets metric priorities | [blog](https://hex.tech/blog/we-used-evals-to-improve-ai-feature/), [docs](https://learn.hex.tech/docs/agent-management/evals) |
| EvalGen / ChainForge / EvalLM / LLM Comparator | human grades a subset → align evaluators; criteria drift | confusion matrices per criterion | — | humans grade; "iterate over criteria and implementations simultaneously" | [EvalGen](https://arxiv.org/abs/2404.12272), [2309.09128](https://arxiv.org/abs/2309.09128), [2309.13633](https://arxiv.org/abs/2309.13633), [2402.10524](https://arxiv.org/abs/2402.10524) |
| EDDOps (arXiv 2411.13768) | plan → test cases → offline / online eval → analyse and improve | versioned plan, test catalog, slices, change entries | runtime changes "bounded, logged, reversible"; verified on the same slices | D6: humans retain agency over ambiguous, high-impact or contested cases | [link](https://arxiv.org/abs/2411.13768) |
| Google Rules of ML; Ng, ML Yearning | error patterns (#26), quantify (#27), measure delta (#24), launch when all metrics improve (#39); ~100 misclassified dev examples in a spreadsheet | — | all metrics better | manual error analysis | [Rules](https://developers.google.com/machine-learning/guides/rules-of-ml), ML Yearning ch. 14–18 |

### 2.2 The canonical loop (synthesis; each step cites who prescribes it)

1. **Freeze a versioned baseline** [automated]: prompts, context, harness in Git; runs tagged with the commit; several trials per item (Hamel; Anthropic; Hex; [2602.07150](https://arxiv.org/abs/2602.07150)). *We have this: FROZEN.md, hashes in meta.json.*
2. **Run and log traces** [automated] (OpenAI; Inspect; Braintrust). *We have this.*
3. **Open coding by the domain expert** [human]: ≥ 30 traces by hand, ~100 in total, note the first upstream failure (Hamel; Ng; Anthropic "read transcripts"). *Started in ITERATIONS.md; not systematic yet.*
4. **Axial coding → taxonomy with counts** [human; an LLM may propose clusters] (Hamel; LLM Comparator). *Not done.*
5. **Pick one top failure, state the hypothesis, make one change** [human] (LangChain; Hamel; Rules #26/#27). *Phase-1 protocol already does this.*
6. **Re-run paired on the same items, same trials** [automated]; item-level paired differences with intervals (Miller 2024; 2602.07150; Rules #24). *Harness can; the statistics script does not exist yet.*
7. **Gate: keep iff the target failure improves and the baseline suite does not regress; else revert** [automated; human overrides edge cases] (Hex; LangChain; Rules #39; EDDOps). *Not implemented.*
8. **Log the change entry; re-validate the judge on the untouched test split** [human] (Hamel; EvalGen; EDDOps). *Partially (ITERATIONS).*
9. **Stop / freeze** when the taxonomy or the suite saturates, or the timebox ends [human] (Hamel; Anthropic).

### 2.3 Adopt as the team's process references

1. **Husain & Shankar (Evals FAQ + Field Guide + evals-skills)**: the only source that says who annotates, how many traces, which splits, and how to validate a judge; matches the mentor's "the human extracts the why".
2. **LangChain "Better Harness"** (with Hex's holdout rule and 10-run noise floor): the only practitioner write-up with the one-change-at-a-time rule, optimization/holdout split and net-positive acceptance for a harness.
3. **Anthropic "Demystifying evals" + Miller 2024 + 2602.07150**: task design, pass^k, and the statistics of the re-run step.

### 2.4 Is the analyse-and-decide step human?

**Yes, in every practitioner standard.** Husain/Shankar require a domain expert for error analysis and are explicit that automated optimizers "hill-climb a fixed metric and cannot discover new failures"; Anthropic requires reading transcripts; OpenAI keeps "human feedback central" even where an agent ranks and implements changes; EvalGen shows that grading changes the criteria, so human grading is irreducible; EDDOps D6 and Rules of ML #23/#26 agree.

**Counter-evidence, and why it does not apply yet:** GEPA ([2507.19457](https://arxiv.org/abs/2507.19457)), ACE ([2510.04618](https://arxiv.org/abs/2510.04618)), Opik's optimizer and Hex's change-proposing agents automate the *propose* step, but each presupposes an already-validated metric and hundreds of labelled or held-out items, which is precisely what the human step produces. No source automates the taxonomy-building step without a human-validated judge first. For us: human analysis now; automated proposal is a phase-3 option once judges are validated and the regression suite exists.

---

## Part 3 — Critical review of the proposed fixes (senior FDE / SDE lens)

| ID | Proposed | Evidence and local test | Verdict | Revised recommendation |
|---|---|---|---|---|
| P1 silent errors: recompute oracle | numbers in prose derivable from values | **Local test: 99% derivable, 0 true positives, 4 false positives; the known errors are base/label errors.** STAT-TO-TEXT (91–98% agreement) works at *claim* level by executing a checker per statement; frontier judges eyeballing numbers reach only 74% on perturbed claims ([2610.00689](https://arxiv.org/abs/2610.00689)) | **partial: as proposed, low yield** | replace with a claim-level checker: split the answer into quantified statements, have the frontier model write a pandas assertion per statement against `values.csv` (STAT-TO-TEXT), execute it; log unmatched statements for human triage; expect false-negative skew. Effort 2–3 days |
| P1 silent errors: claim judge | binary judge for "data cannot support this" | **Local test: TPR 0.57, TNR 1.00** (32 sentences, Claude labels). Literature: judges have high precision, low recall; "detect errors" wording +17 pts recall (Kamoi); causal overclaiming detectable with human-validated pipelines ([Isch et al. 2026](https://www.nature.com/articles/s41562-026-02553-x)); CausalPitfalls rubric grader gap 0.11 vs statisticians | **partial** | keep, but as a *flagging* aid until recall ≥ 0.8 on ≥ 60 human labels; decompose compound sentences into atomic claims before judging; give an explicit forbidden-claim list; measure recall on ~20 injected unsupported sentences |
| P2 misleading framing: plan vs gold plan + trap catalog | framing check | **Local test: TR05 flagged on 6/6 A1 runs.** Misviz: rule linters with metadata beat MLLMs (rule EM 51.4 on synthetic; GPT-o3 F1 80 image-only); Silent Failures: "correlation ≠ causation" failed at rate 1.0 in every config; sqlglot gives WHERE predicates, pandas needs a small AST visitor; **no published disclosure scorer** | **yes, and novel** | build it as per-question assertions keyed on a 5–10 item trap catalog, on `plan.json` + code (not free text); the "reporting change inside the window" trap cannot be inferred from code, it must be in the catalog. Effort 3–4 days |
| P3 exploration drift: plan declaration with answerability | agent declares plan first | nvAgent's 83.8 → 24.0 ablation conflates planning with code scaffolding (not pure planning evidence); AbstentionBench: reasoning budgets worsen abstention, system prompts help only partly; "Plans Fade Fast" ([2606.22953](https://arxiv.org/abs/2606.22953)): a plan in context strongly shifts the next step; **declaring a plan changes the subject being measured** | **yes for observability; it is a treatment, not a free observation** | run it as an arm (A with / without plan declaration), not as a silent harness change; `answerable: no` will be rare without an explicit instruction; collect the plan JSON *after* free-text reasoning (format restriction can degrade small-model reasoning, [2408.02442](https://arxiv.org/abs/2408.02442) [?]) |
| P9 lenient Luna reviewer | diagnose with scoring + code checks | Kamoi: stronger models → higher precision, lower recall, so "flags less" may be precision, not laziness; Beyond Consensus: validators agreeable (TNR < 25%); CriticGPT / AgenTracer: **inject known faults** to measure recall; with 6 items × 1 run strength and leniency cannot be separated | **partial** | fault injection: plant ~20–30 known faults (numeric, filter, causal) into correct outputs, report recall per reviewer and per fault type plus human-adjudicated precision. Effort 2–3 days |
| H13 provider stalls | treat as timeout | no client-side signal exists (measured) | accept | report zero-output timeouts separately; expect fewer on Luna |
| H18 free-text framing fields | controlled vocabulary | OpenCode SDK supports `json_schema` output with retries; the CLI does not; post-hoc `jsonschema` + retry works; vocabularies: BLADE decisions, VisEval chart types, Vega-Lite channels | **yes** | enum fields for metric family, denominator type, grouping, chart family; validate post hoc; collect after reasoning. Effort 1–2 days |
| H20 two files in git history | force-push purge | mechanical (`git filter-repo`) | decision only | purge or accept; no analysis needed |
| R1 B tuned on the comparison set | caveat + held-out | LangChain / Hex: optimization vs holdout split is the standard | accept | phase 2 edits from dev only; P1–P10 run once per freeze candidate |
| R2 single runs, small n | 3 repeats, paired tests | Miller 2024: K resamples cut variance by (1 + 2/K)/3; **MDE ≈ 30 pts at n = 16, K = 5; ≈ 48 pts at n = 6**; Bowyer et al. ICML 2025: CLT under-covers below a few hundred items → Wilson / Beta-Binomial, paired Bayesian ([2503.01747](https://arxiv.org/abs/2503.01747)); evalci for paired tests ([2607.04429](https://arxiv.org/abs/2607.04429)); pass^k from τ-bench ([2406.12045](https://arxiv.org/abs/2406.12045)) | **yes for honest reporting; no for detecting modest effects** | per-item paired outcomes, K ≥ 5, Wilson / Beta-Binomial intervals, pass@5 and pass^5, and **state the MDE explicitly** (≈ 30 pts) instead of p-values; comparisons on 6 questions are screens |
| R6 pushes to main | reminder | process | accept | branch protection on main if the team agrees |
| R8 blind scoring slow and unstable | three-layer scoring | Part 1 | **yes with the per-type limits** | clear: code; ambiguous: rubric judge after human rubric writing; insufficient: abstain judge + executed claim checks; human for criterion 8, disagreements, freeze |

### 3.1 What this changes in the earlier proposal

- "Recompute oracle" as number membership is dropped; the claim-level executed checker takes its place.
- The claim judge is a flagging aid, not a scorer, until its recall is measured on human labels.
- Plan declaration becomes an experimental arm, because it changes the agent's behaviour.
- Reviewer leniency is measured by fault injection, not inferred from counts.
- Every comparison states its minimum detectable effect; on 6 questions, the loop screens, it does not prove.

---

## Part 4 — Decisions for the evaluation-layer design (not phase 2 as a whole)

1. Scoring by question type as in Part 1 (clear: code; ambiguous: rubric judge with human-written rubrics; insufficient: abstain judge + executed claim checks; human for aesthetics, disagreements, freeze).
2. Process reference = Husain/Shankar + LangChain Better Harness + Anthropic/Miller; the nine-step loop with the human steps marked.
3. Comparison protocol: K ≥ 5, paired per item, Wilson / Beta-Binomial intervals, pass@5 and pass^5, MDE stated; screens on dev, confirmation on held-out once per freeze candidate.
4. Judge rule: no judge scores anything until TPR and TNR are measured on ≥ 60 human labels (test split untouched); agreeable-validator failure mode handled by minority veto.
5. The four builds, in order: claim-level checker (P1), framing assertions on plan + code (P2), figure introspection hook (criteria 3/5/7), fault-injection set for reviewers (P9); plan declaration as an arm.
