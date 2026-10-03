# Poppy — Direction v1 (working record)

- **Status:** Bo's working direction after mentor meeting 2. Not yet team consensus.
- **Date:** 2026-10-03
- **Next decision point:** team meeting, Monday 2026-10-05 (evening): lock scenario + dataset bundle.
- **Rule:** everything below is a hypothesis to be confirmed or killed by experiments. See `experiments/LOG.md`.
- **Changelog:** 2026-10-03 (later) — scenario and data proposal in `docs/scenario-data-v1.md` (NYC, journalist / fact-checker persona, 3-table bundle, 17-trap catalog); decision-layer plan in `docs/decide-layer-v1.md`; E001 done and independently reviewed.

---

## 1. What mentor meeting 2 changed

1. One voice: the team gives mentors one consistent answer.
2. Effort split: ~20% agent development, ~80% evaluation.
3. Public data only. No enterprise or private data.
4. Pick one specific scenario. Record detailed traces. Log every bad case and experiment, then verify or explain it.
5. The agent must handle **vague questions**: when the asker does not know exactly what to ask, the agent uses the scenario and the question to surface concrete directions and find what the user actually wants.
6. Visualization is more than a chart pasted into a chat.

## 2. Core research question (tentative)

> For vague analytical questions over real public data, when should a visualization agent **ask** a clarifying question, **enumerate** interpretations, or **proceed** — and how do we measure whether it chose well?

Why this is a real gap (verified 2026-10-03):

- Agents rarely ask even when they detect ambiguity ("Knowing but Not Showing", arXiv 2605.25284); only ~50% of generated clarifying questions are helpful (CLAMBER, ACL 2024); frontier models score < 17% on BIRD-Interact when they must ask (arXiv 2510.05318).
- Agents converge on the safe default analysis: BLADE reports < 13% coverage of statistical-modeling decisions; InsightEval shows precision > recall for every agent tested.
- VisInteract (arXiv 2609.15182) measures interactive clarification for charts, but nobody measures the **cost of unnecessary questions**, i.e., ask vs. enumerate vs. proceed as one decision.

What comes along for free:

- Real-domain ambiguity set (existing benchmarks use BIRD, ServiceNow, or synthetic data).
- Open-source eval harness (Data Formulator and LIDA ship none).

Explicitly not pursuing: evaluating exploration paths against expert paths (needs expert ground truth; too costly).

## 3. Scenario (tentative): road traffic safety

- Chosen over "AI agent trace analytics" (candidate E) because public trace datasets lack timestamps, cost, or tool detail; E is deferred to phase 2 as "Poppy analyzing its own traces".
- Honda alignment: Honda's public goal of zero traffic-collision fatalities involving Honda vehicles by 2050, halving by 2030 (announced 2021-04-23).
- **Proposed (see `docs/scenario-data-v1.md`):** NYC traffic safety; persona = data journalist / fact-checker; MVP bundle = NYC Crashes (2.27M rows) + injured/killed Persons (760k) + monthly East River bridge bike counts (exposure); analysis window 2013–2025; snapshot pinned because the city froze updates at 2026-06-15. Chicago = phase-2 transfer test; FARS = phase-2 Honda/Ohio layer; Ohio state data is not scriptable.
- **Constraint: DE-light.** ≤ 1 working day from download to an analysis-ready DuckDB with ≤ 3 tables. Measured so far: the crashes table took 7 s of compute and 12 min of agent time (E001).

## 4. Poppy behavior (v1 sketch)

Example question: *"Are cyclists safer in NYC than they used to be?"*

| Step | What Poppy does | Example output |
|---|---|---|
| 1. Classify ambiguity | None / cooperative (system can assume and state it) / uncooperative (must ask) | "Safer" is cooperative: several defensible readings. "Is my street dangerous?" is uncooperative: which street? |
| 2. Enumerate | 2–4 legitimate interpretations, one chart + one-line rationale each | (a) absolute injuries/deaths per year, (b) normalized by cycling volume, (c) severity mix |
| 3. Flag traps | Data issues that would mislead | reporting changes, coverage start dates, missing location, exposure growth |
| 4. Ask only if needed | Ask when it cannot proceed, or when readings contradict and the choice matters | targeted question, ideally with a default plan |
| 5. Output a view | Not a single chart in chat | 2–3 charts with rationale and assumptions, a caveats box, a trace link |

## 5. Evaluation sketch (details decided by experiments)

| Layer | Question | Method | Owner |
|---|---|---|---|
| L1 Validity | Does the chart render; do referenced fields exist? | deterministic checks | Bo |
| L2 Design | Basic design errors? | rule lint on the spec | Bo |
| **L3 Judgment (core)** | Right decision (ask/enumerate/proceed)? Interpretations covered? Traps flagged? Over-asking? | annotated question set + simulated user with hidden intent | Bo |
| L4 Preference | Do people prefer it over the baseline? | pairwise human study | DS teammate |

Candidate metrics: decision accuracy, over-ask rate, interpretation recall, trap detection rate, chart validity rate, pairwise win rate vs. baseline, cost and latency per question.

## 6. Decision layer and Jev

- One interface: `decide(state, question) -> probabilities over typed options`.
- Used in step 1 (ask / enumerate / proceed routing) and in L3 judging.
- Backends to compare: (i) LLM (verbalized confidence, logprobs, or sampling vote), (ii) CLM-8B (open, Apache-2.0), (iii) Jev (closed, limited early access; only if access is cheap and use is confined to experiments).
- Experiment: agreement with human labels, calibration (Brier, ECE), cost, latency.
- Known Jev limits relevant to us: text-only input, weak at arithmetic and dates, literal reading, self-reported benchmarks.
- **Plan (see `docs/decide-layer-v1.md`):** adopt the shared `/v1/systemone` request format as the contract; run local Qwen logprobs (open, $0) and Jev (via OpenRouter or OpenCode Zen; cents or free) first; Clef-flash optional; CLM-8B dropped unless GPU access appears. Compute all trap facts in code before calling any decision model.

## 7. Baselines (to be confirmed by the pilot)

- **B0 one-shot LLM:** question + schema → one chart, no tools.
- **B1 plain coding agent:** a general agent (Codex) with data access and no policy.
- **B2 policy-prompted agent ("Poppy-lite"):** B1 + an ask/enumerate/proceed policy prompt.

The pilot answers the first feasibility question: does prompting alone already close the gap? If yes, the project needs a harder angle. If no, the gap is real and the structured agent + eval harness is justified.

## 8. Career narrative

> Built an open-source, clarification-aware analytics agent and its eval harness on real crash data, and measured when the agent should ask vs. proceed.

Industry parallels: Hex Evals (Aug 2026), Databricks Genie Benchmarks, Anthropic's internal analytics skills + offline evals (21% → 95%), BIRD-Interact; FDE job descriptions ask for eval harnesses with golden datasets and LLM-as-judge.

## 9. Working principles

- Experiment-driven narrowing. Every experiment goes in the log, including failures.
- DE-light (see section 3).
- Open source first; closed models only when cheap and confined.
- Traces for every run.
- Process: GitHub Projects kanban, 1-week sprints, one reviewer per PR. Owner = tech lead / integrator, not task assigner.

## 10. Open questions

- **Team (Monday):** confirm road safety + the core question; pick the data bundle.
- **Ryan:** access to 99P Labs datasets (https://www.99plabs.com/datasets, via research@99plabs.com)? Are closed "System One" models (Jev) acceptable in experiments? How strict is "open source"? FYI: Ohio statewide crash data has no scriptable public bulk download; we propose FARS (STATE 39) for Ohio questions in phase 2.
- **Pilot:** how do frontier agents behave on vague questions today (baseline)? Does a policy prompt fix it?
