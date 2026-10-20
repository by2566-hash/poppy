# Direction v2 — candidates, evidence, and a recommendation (2026-10-18)

- **Status:** Bo's working document for the team and for Ryan. Built from the mentor's asks (four meetings), the phase-1 pilot findings, the parked v2 design, and a literature/industry scan done on 2026-10-18 (sources linked inline; items marked [?] are unverified).
- **Purpose:** choose the next phase so that it (1) does what the mentor asked, (2) produces evidence nobody has published yet, (3) is what applied AI engineers and forward-deployed engineers do in 2026, and (4) is feasible for three people with free models plus one cheap frontier model.

## 1. Inputs

### 1.1 What the mentor asked for (complete list, 4 meetings)

Kickoff / meeting 2: evaluation is the most valuable part; pairwise > absolute judgment; small simple rule set for "good"; LLM-judge vs human correlation; record traces; FDE framing; open source, OpenCode + free inference, public data; one voice; ~80% evaluation; pick one scenario, log every bad case; handle vague questions; visualization is more than a chart in chat; deliverables = MVP, private repo, experiment log (3–5/week), field guide, Medium post, report/poster, ~10-min video.

Meeting 3 (10-09): two-level system (simple toy pipeline + the evaluation layer above it, which is the point); baseline first, 2–3 variants per step; improvement loop (extract *why*, feed back as prompt/rule/skill, re-run, compare per part); narrow scope; 3 models is enough (to attribute failure to capability vs prompt); cost/latency not the focus but the structure transfers; a boxes-and-arrows diagram.

Meeting 4 (10-16): aligned on phase 1; in-context-learning loop is the preferred improvement method; repeat everything with GPT-6 Luna (key provided); 80% of the problem is accuracy, then widen the options (3 accurate ways + why); Verbalized Sampling, 3–5 options with probabilities, render, let the reflective loop choose; 8 binary criteria fine, add creativity; do not optimize cost now; report trade-offs as arrows; "LLMs are untrustworthy for viz" is also a result; the generalizable part is the evaluation loop; slides to him Thu 10-22 5 pm, midterm Fri 10-23.

### 1.2 What phase 1 found (pilot, E006–E007)

Agents fix errors that crash (6/10 A runs) but not silent ones: NULL-dropping sums, wrong rankings, "gap" that is only a ratio, unsupported causal asides, invented or downloaded exposure data (vehicle-miles). An independent read-only reviewer with the chart caught these in iteration 3 (K2, A2, I1) with zero invented issues and zero unflagged changes; it missed one (K3). Infrastructure facts: free gateway stalls silently; a client cannot tell reasoning from a stall; sandbox leaks (web, repo reads) had to be closed with an OS sandbox; acceptance had to be a contract, not an effect.

### 1.3 What the scan found (2026-10-18)

- **Nobody has published** an evaluation of whether a reviewer catches silent errors *it did not produce* on real aggregation questions with a deterministic recompute oracle; "Silent Failures in Agentic Data Science" ([2610.14115](https://arxiv.org/abs/2610.14115)) reports that most agent solutions contain ≥ 1 silent failure regardless of model, and the autonomous-research survey ([2608.05179](https://arxiv.org/abs/2608.05179)) calls fabricated plots and unaudited interpretive claims the most consequential and least measured failure.
- **Fresh-context review helps mainly by role relabeling** ("Self-Correction Illusion", [2606.05976](https://arxiv.org/abs/2606.05976): the same claim is flagged +23 to +93 pp more often when presented as external); but reviewer *capability* dominates independence ("When does a second model help?", [2610.01471](https://arxiv.org/html/2610.01471)). No paper isolates one frozen review prompt across a small and a frontier model, and none tests "small generator + frontier reviewer at the review step only" on analysis agents. Per-step routing is an active 2026 topic ([R2V](https://arxiv.org/pdf/2605.16604), [PROGROUTER](https://arxiv.org/pdf/2608.25992)).
- **Verbalized Sampling** ([2510.01171](https://arxiv.org/abs/2510.01171), ICML 2026; [repo](https://github.com/CHATS-lab/verbalized-sampling)): 1.6–2.1× diversity on creative tasks, no accuracy loss reported; gains scale with model capability and smaller models show a larger quality drop; verbalized probabilities are ordinal at best. Diversity for analyses should be measured as coverage of expert-listed framings plus effective diversity among *valid* outputs (NoveltyBench [2504.05228](https://arxiv.org/abs/2504.05228); [2504.12522](https://arxiv.org/abs/2504.12522); BLADE [2408.09667](https://arxiv.org/abs/2408.09667)). Chart judges rank better than they score and over-accept (ChartJudgeBench [2609.24210](https://arxiv.org/abs/2609.24210); [2604.25235](https://arxiv.org/abs/2604.25235)).
- **Industry trust pattern** (Snowflake Cortex Analyst verified queries + evaluations, Databricks Genie benchmarks, Hex Evals Aug 2026, Power BI verified answers, Palantir AIP Evals): semantic layer → verified/reference queries → show the code → benchmark suite with reference SQL and tolerance → regression tracking across versions → human endorsement → abstention for high-stakes numbers. Hiring signals for FDE/applied AI (OpenAI, Palantir, Anthropic, Scale postings): eval suites, traces, customer-data reliability, codifying lessons; portfolio advice: a runnable repo whose "one hard part" is an eval harness with a frozen test set and an honest failure log.
- **99P Labs** (Ryan + Rajeev, Medium, May 2026): "2026 is about governing, evaluating, observing and paying for agents at scale"; Ryan's stated research focus: LLM evaluation, context engineering, agentic systems.
- **Tooling:** Inspect AI (MIT, re-scores saved logs, built-in log viewer), Phoenix (local one-process tracing, Elastic license), promptfoo (CI gates), `judgy` (TPR/TNR-corrected pass rates), Anthropic's agent-evals guide (Jan 2026: pass@k vs pass^k, capability → regression evals). OTel GenAI conventions still unstable. Practice: open-code ≥ 30–100 traces by hand first (Husain/Shankar).
- **GPT-6 Luna:** released 2026-09-22; text + image input; $0.10 / $0.50 per 1M tokens; available on OpenCode Zen with `attachment: true`, so B's image review works unchanged. A full formal run (≈ 1,000 runs) costs on the order of $10.

## 2. Candidates

| | C1 Silent-error evaluation layer | C2 Who should review? (per-step model routing) | C3 Enumerate with VS | C4 Ask-vs-proceed | C5 Tooling migration |
|---|---|---|---|---|---|
| One line | Deterministic recompute oracle for every number and claim; failure taxonomy; regression suite; judge calibration | 2×2 generator × reviewer (mimo / Luna) with frozen prompts; which step needs the frontier model | Arm D: k accurate framings with probabilities, rendered, then chosen; diversity gated by accuracy | Arm that may ask one clarifying question against a scripted user | Move traces/evals to Inspect or Phoenix |
| Mentor fit | Evaluation layer is "the point" (mtg 3); accuracy is 80% (mtg 4); traces, field guide | Model contrast with Luna (mtg 4); "3 models to attribute failures" (mtg 3) | Explicit ask (mtg 4) | "Vague questions" (mtg 2); but not asked for recently | Not asked |
| Novelty vs literature | High: no recompute-oracle eval of reviewers on silent errors exists | High: no frozen-prompt small-vs-frontier reviewer study; no per-step routing on analysis agents | Medium: VS exists; applying it to analysis framings with accuracy-gated diversity is new but expected to work mainly on Luna | Medium-high but crowded in 2026 (BIRD-Interact, VisInteract, DV-Interact, AskBench) | None |
| Bo's ownership | Full: harness, oracle, taxonomy, judges, suite, viewer | Harness + design; analysis shared with the DS teammate | Selection step + metrics; scoring shared | Design + simulated user; scoring shared | Full but low value |
| Industry relevance | Highest: this is the verified-query / regression-suite pattern every AI-analyst product ships | High: routing and "frontier only where needed" is the cost pattern Ryan said industry cares about | Medium: product feature | Medium | Medium (portfolio) |
| Feasibility | High: reuses gold SQL, contract checker, traces; ≈ 3 weeks of Bo's time for a minimal version | High: harness already multi-model; cost ≈ $10; mimo rate limit bounds the mimo cells | Medium: needs expert framing lists; mimo may break format | Low-medium: needs a user simulator and a new question set | Medium; migration risk mid-project |
| Risk | Scope creep into a full pipeline (v2's tool-less design is obsolete: A is an agent run) | Confounds: prompts tuned on mimo; state as transfer condition | Diversity without accuracy gate is meaningless; judges over-accept | Time | Distracts from results |
| What Ryan can mentor | Evals, judge calibration, context engineering — his focus | Attribution logic | VS and product framing — his own suggestion | Less | Less |

## 3. Recommendation: one program, three experiments, Bo owns the layer

**Program name:** *Poppy: an evaluation layer for a data-analysis agent.* The agent (OpenCode, any model) is kept simple on purpose. The contribution is the layer around it: contract checks, a recompute oracle, a failure taxonomy, calibrated judges, a regression suite, and the loop that turns findings into versioned changes.

**E010 — silent-error oracle and taxonomy (C1; Bo).** For each question: gold SQL already exists; add (i) a recompute check that re-derives every number in the written answer and in `values.csv` from the data (v2's S6), (ii) a claim check that flags statements the data cannot support (cause, exposure, external numbers) using the data dictionary, (iii) a plan declaration the agent emits before analysis (metric, denominator, grouping, chart family) so failures can be attributed to a step inside the agent run. (iv) a framing check on the plan: undisclosed row exclusions and denominators that change inside the window (added 2026-10-19 after arm D showed correct numbers with misleading framings; see `docs/v2-eval-layer-architecture.md` §2). Hand-code ≥ 30 traces from the pilot and formal runs into a taxonomy (seed: our TR01–TR17 traps, the "silent failures" categories, MAST verification failures); produce the "last step passed × first step failed" matrix. Calibrate each automated check against human labels (TPR/TNR, `judgy`). Freeze a 20–50 item regression suite (dev = pilot + formal questions; test = new questions written by a non-tuner), report pass@k and pass^k. Output format: the arrows table Ryan asked for, with numbers underneath.

**E008 — who should review? (C2; Bo + DS teammate).** Frozen A/B/C prompts on mimo and GPT-6 Luna, plus the two cross cells: mimo generator + Luna reviewer/reviser, Luna generator + mimo reviewer. Predictions (registered before running): Luna generator lowers silent errors and A1-type exploration drift; Luna reviewer on mimo output recovers most of the gap at a fraction of the cost; mimo reviewer on Luna output adds little and introduces flips. This answers Ryan's capability-vs-prompt attribution and the industry routing question in one design. Scored with E010's oracle, so "silent-error rate" becomes the primary metric, next to the team's 8 criteria.

**E009 — enumerate with VS (C3; shared).** Arm D on the ambiguous questions: k = 3 framings that each answer correctly, with probability and reason, rendered; selection by pairwise judge (Luna), position-swapped. Metrics: accuracy per option (gate), framing coverage against an expert list written by the non-tuner, distinct framings, mode share (is the top-probability option A's single answer?), cost. Expectation stated up front: works on Luna, likely burns steps on mimo; that contrast is the result.

**Not now:** C4 (clarifying questions) is the natural phase 3 if time remains; C5 limited to a small local trace viewer and `judgy`, no framework migration.

## 4. Sequencing (to be fitted to the real end date)

| Window | Deliverable |
|---|---|
| to 10-23 (midterm) | C prompt; formal A/B/C run on mimo; E008 pre-checks (provider, vision, K1 profile); E009 smoke on 2 questions; slides with pilot results + the plan above |
| midterm + 2 weeks | E008 full (4 cells × 10 Q × 3 reps); E010 oracle v1 (recompute + claim check) scoring all runs; first taxonomy from 30+ traces |
| + 2 weeks | E009 full on ambiguous questions; regression suite frozen; judges calibrated; arrows table |
| last 2 weeks | field guide, Medium post (99P house style: problem → design → failure log → numbers), video, final report; repo README leads with the harness |

## 5. Decisions needed

1. Program framing and the three experiments (team; present to Ryan on 10-22).
2. Bo owns E010 and the harness; DS teammate owns scoring and E008 analysis; third teammate owns gold framing lists, test questions, slides/blog.
3. End date and weekly hours (fit §4).
4. Retire the Jev/CLM decide-layer plan.
