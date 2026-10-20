# Phase 2 architecture — the evaluation layer (record, not yet decided)

- **Status (2026-10-18; amended 2026-10-19 with the fourth silent-error component):** recorded after a team meeting where the team agreed with the overall idea and chose not to go deeper until phase 1 is closed. Nothing in this document is frozen. Decisions are listed at the end and will be taken after the midterm (2026-10-23).
- **Related:** `docs/direction-v2-candidates-2026-10-18.md` (evidence and candidates), `docs/pipeline-v2-design.md` (Bo's earlier design; its "every step is a tool-less call" premise is superseded by §1 below), `docs/phase1-abc-design.md` (phase 1).

## 1. Two layers

```
Layer 1  the workflow under evaluation (the agent; kept simple, not rebuilt)
──────────────────────────────────────────────────────────────────────────
  input ──► [plan declaration]* ──► analysis run (writes code, runs it,  ──► artifacts
  question    plan.json            sees errors and numbers, fixes crashes)   chart.png
  dictionary                       trace: steps, tool calls, code,          values.csv
  data file                        errors, tokens                            code, ANSWER
  B appends:  review (CHART CHECK / ISSUES / UNVERIFIED) ──► revise (CHANGES, revised artifacts)
  C:          same run, the prompt adds one self-check instruction
  D:          same run, the prompt asks for k framings; artifacts become options.json + k charts and value files

Layer 2  the evaluation layer (what phase 2 builds)
──────────────────────────────────────────────────────────────────────────
  one check per observation point ──► per-run record of pass/fail per step
  ──► failure taxonomy + transition matrix (which step broke)
  ──► one change (prompt line / context content / harness rule)
  ──► re-run on a fixed regression set ──► per-item, per-step diff ──► keep or revert ──► field guide
```

\* The only change to the agent: one prompt block asking it to state its plan before writing code. Every other stage already leaves an artifact. Attribution to steps is therefore a property of the evaluation layer, not of the agent architecture.

## 2. Observation points and checks

| Stage | Artifact | Check | Grader | Ground truth | Status |
|---|---|---|---|---|---|
| Whole run | meta, events | budget, sandbox, format, end state (the contract) | code | config | have (`check_contract.py`) |
| Plan | `plan.json` | denominator, grouping, answerable match the gold plan; **framing check**: rows excluded (e.g. a borough filter that drops records with no borough) and denominators whose definition changes inside the window (e.g. reported crashes across the 2020 recording change) are disclosed | code + trap catalog | gold plan (human, one per question) + trap catalog (TR01–TR17) | to build; needs the plan declaration |
| Compute | `values.csv` | plotted numbers match gold SQL | code | gold SQL | half (`gold_cover`) |
| Narrate: numbers | numbers in ANSWER | each derivable from values / gold (direct, sum, mean, ratio, % change) within tolerance; otherwise "unsourced number" | code | values + gold SQL | to build (recompute oracle) |
| Narrate: claims | sentences in ANSWER | asserts something the data cannot show (cause, exposure, external number) | LLM judge, binary, calibrated on human labels | data dictionary + human labels | to build (claim judge) |
| Chart | `chart.png` | readable; agrees with values; team's 8 criteria | human (blind); a little code | rubric | have (team rubric) |
| Review (B) | `review.json` | each ISSUE true?; share of oracle-found errors caught | human + oracle | oracle output | have manually; to connect to the oracle |
| Revise (B) | `changes.json`, diff | only flagged parts changed; flips | code diff + human | before/after | have |
| Options (D) | `options.json`, k artifacts | each option passes the oracle; framings distinct; coverage of an expert framing list | code + human list | expert framing list | to build (only with E009) |

**Silent-error rate** of a run = unsourced number ∨ unsupported claim ∨ gold mismatch ∨ **misleading framing**. This is the primary new metric; the team's 8 criteria stay the final-view rubric.

*Why the fourth component (added 2026-10-19, from E009-lite):* arm D on GPT-6 Luna produced options whose numbers were all correct and traceable and whose sentences were supported by those numbers, yet the framing misled: A1 filtered `borough = 'BROOKLYN'` and silently dropped the 19.9–38.1% of crashes per year with no borough (TR05); A1 option 3 and I1 option 2 divided by total reported crashes, a count that collapsed after the 2020 recording change (TR01), and reported "+51.5%" and "did not decline" without a caveat. None of the first three components fires on these. **Misleading framing** = an exclusion of rows, or a denominator whose definition or coverage changes inside the analysis window, that the output does not disclose. It is checked at the plan step (plan.json vs gold plan and the trap catalog), not at the number level. The trap catalog belongs to the evaluation layer only; prompts never contain it (phase-1 protocol rule 4).

**Must build:** recompute oracle, claim judge with human labels, framing check (plan vs gold plan + trap catalog), failure taxonomy, regression-set runner, arrows report. **Should:** plan declaration + gold plans. **Optional:** selection step for D, trace viewer, oracle substitution (replace one step with gold and replay).

## 3. The loop

1. Run the regression set (fixed items with gold, dev/test split; test items written by someone who tunes no prompt).
2. Score every run with the checks above; produce the per-step pass/fail record.
3. Open-code failures by hand (≥ 30 traces), group into a taxonomy, count; draw the transition matrix (last step passed × first step failed).
4. Pick one change (a prompt line, what goes into a step's context, a harness rule), tied to the top failure class.
5. Re-run the regression set; diff per item and per step; keep or revert; report as an arrows table (quality ↑↓→, cost and time ↑↓→ as direction only: Ryan asked for the trade-off trajectory, not optimization or precise cost).
6. Write the finding into the field guide; freeze the prompt version with its hash.

## 4. How the three experiments use the layer

- **E010** builds the layer and answers: silent-error rate of A/B/C; share caught, missed and introduced by review. Phase-1 runs are scored without re-running.
- **E008** varies the model per role (generator × reviewer: mimo / GPT-6 Luna), same prompts, same layer.
- **E009** adds arm D (k framings with verbalized probabilities); the layer gains the two option checks.

## 5. Decisions to take after the midterm

1. Build list in §2 as stated (five must, one should, three optional).
2. Plan declaration added to A → A becomes a new version under a phase-2 protocol; A-v1 stays the phase-1 baseline.
3. Definition of silent error: four components (unsourced number, unsupported claim, gold mismatch, misleading framing; the fourth added 2026-10-19 from E009-lite evidence) — to confirm.
4. One judge only (unsupported claims), calibrated on 60–80 labelled sentences; fall back to human labels if TPR/TNR are poor.
5. E009 v1 without a selection step; wording D2 (accuracy-conditioned) first.
6. Retire the Jev/CLM decide-layer plan (agreed 2026-10-18).
