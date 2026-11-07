# V2 reconciliation (2026-11-07): what was decided, what changed, what is not done, what is open

- **Purpose:** one place that lines up every V2 idea and decision from 2026-10-13 to 2026-11-06 against what exists now, so the next V2 step starts from facts. Written at Bo's request after the 11-06 mentor meeting.
- **Sources:** this working session (Bo's messages 10-15 → 11-07), memory notes, and the repo: `docs/pipeline-v2-design.md` (Bo's own design, 10-13), `docs/v2-eval-layer-architecture.md` (10-19), `docs/v2-design-inventory.md` (11-01), mentor brief of 10-27 (in git history), `docs/v2-plan.md` (11-02 + amendments), `experiments/E009-enumerate/{FOLLOWUPS,ITERATIONS}.md`, `experiments/E007-pilot-prompts/SCORING.md` §4, `docs/problem-register.md`, `docs/mentor-meeting-2026-11-06.md`.
- **Status labels:** **done** = built/run as decided · **changed** = decided, then replaced or reduced (with who/when) · **pending** = decided, not done · **open** = never decided · **deferred** = parked with a return trigger.

## 0. How V2 evolved (versions and the decisions that moved it)

| Date | Version / event | What it said |
|---|---|---|
| 10-13 | `pipeline-v2-design.md` v2.0 → v2.1 (Bo, parked) | a new 5–7-step pipeline: S0 PROFILE, S1 PLAN (JSON), S2 CHECK variants, S3 SQL + gate, S4 chart, S5 narrate, S6 VERIFY; per-step evals with gold plan + gold SQL; dev/test split; oracle substitution |
| 10-18 | direction discussion | evaluation layer = main line (Bo: "① and ④ necessary", trust-based evaluation feedback); E008 model contrast and E009 enumerate as mentor-requested experiments; Jev/CLM decide-layer retired; **phase 2 timeboxed "to mid-November (three weeks)"** |
| 10-19 | `v2-eval-layer-architecture.md` | agent unchanged except a plan declaration; observation points per stage; must-build: recompute oracle, claim judge, framing check (plan vs gold plan + traps), taxonomy, regression runner, arrows report |
| 10-21 | eval research; Bo's idea | **automated, standard-based scoring as the primary scorer; humans do analysis, decisions and the final freeze review** |
| 10-27 | mentor brief (in-person) | E010 builds the layer and scores phase-1 runs; E008 generator × reviewer cross; E009 framing sets + plan declaration arm; 7 build items |
| 11-01 | team decision + inventory | three temporary experiments on D: F1 free k + interpretation → F2 rephrasing → F3 reverse inference; V2 module decisions follow them |
| 11-02 | `v2-plan.md` (Bo: "minimal implementation") | detection first, prevention as treatments; gold = correct numbers (keyed readings) + trap sheet; v0 = one script, one gold file, one sheet; grader in shadow until promoted |
| 11-04 | Bo | standard decisions 1–6; fewer human labels: two-grader disagreement triage + 5-row audit; second grader = Luna second pass as a stopgap |
| 11-06 | Bo | decision 7; g8; harness end rule frozen; F2 completion reclassified |

## 1. Done as decided

| Item | Where |
|---|---|
| D v1 (C + k = 3 framings, neutral ANSWER, Luna only) | E009 DESIGN, FROZEN.md |
| D v2 prompt (free k; `interpretation` = which part of the asked question the option answers, why, what it leaves open; Bo's wording 11-02) frozen; F1 18/18 | FROZEN.md; ITERATIONS "E009-F1" |
| F2 (casual + formal phrasings) run by Chloe; harness question sets keyed on `base` | `questions.rephrasing.json`; ITERATIONS F2 entries |
| v0 scorer: gold match, provenance, framing flags (TR05/TR01/TR08), standard-based grader (c1–c8, trap items, unsupported claim, required statement), `--summary`, records per run | `scripts/score_runs.py`, `gold_readings.json` |
| Second grader, disagreement triage, 5-row audit, `--calibration`, versioned grader (g1 → g8) | same; SCORING §4 decisions 1–7 |
| Gold for new readings re-derived independently (`h_gold = new_reading`, F1 9 rows, F2 20 rows) | ITERATIONS |
| Facets coded, first pass (F1, F2); F2 overlap within vs across phrasings | `facets.csv` ×2 |
| Harness: free k, step cap, question sets, D end rule (frozen) | `run_pilot.py`, `run_screen.py`, FROZEN.md |

## 2. Decided, then changed (replacements and reductions)

| # | Originally decided | Now | Changed by / when | Kind |
|---|---|---|---|---|
| C1 | **Recompute oracle**: every prose number derivable from values/gold (10-19 must-build) | **provenance**: every prose number must come from the option's own table; the claim-level executed checker (STAT-TO-TEXT) deferred | prototype found 0 true positives (10-21); Bo agreed 11-02 | replaced; narrower |
| C2 | **Claim judge** as its own check, calibrated on 60–200 labelled sentences, TPR ≥ 0.8 before it counts | `unsupported_claim` is one item of the standard-based grader; calibrated by two-grader triage, not by labelled sentences | 11-02 (v0), 11-04 | merged; calibration path changed |
| C3 | **Framing check**: `plan.json` vs a gold plan + trap catalog (10-19, 10-27) | code flags as evidence pointers + per-question trap items graded by Luna; no `plan.json`, no gold plan | 11-02 (Bo: minimal) | reduced |
| C4 | **Gold plan per question** (all readings, disclosures, forbidden claims, tolerance) | keyed gold readings + the existing trap sheet ("correct numbers are enough") | Bo 11-02 | reduced |
| C5 | Human reviews every row by exception; **blind batch of 20** before any promotion | human labels only on grader disagreements + 5 random audit rows per experiment | Bo 11-04 | reduced (by design) |
| C6 | Second grader = **a different model** (independence, "Juries") | second **Luna** pass (repeat stability 0.98, not independence); mimo/nemotron records partial (free quota) | Bo 11-04, stopgap | downgraded; restore pending |
| C7 | Grader **in shadow** until promoted per item (≥ 60 rows, agreement ≥ 0.95, human sides ≥ 0.8) | every reported silent-error number uses grader verdicts with human overrides; nothing is promoted (no human labels yet) | drift in practice since 11-04 | **de facto primary without promotion** (see §5) |
| C8 | `summarize_scores.py`: failure-code counts, paired differences, Wilson interval, MDE line | `score_runs.py --summary`: item counts, paired differences, MDE line; no failure-code counts, no Wilson | 11-02 (v0 scope) | reduced |
| C9 | Repeats **K ≥ 5** per comparison (10-21 protocol) | K = 3 in F1–F3 | FOLLOWUPS common rules (11-01: "3 minimum, 5 when time allows") | reduced |
| C10 | D diversity measured as **coverage of an expert framing list** (BLADE) + **mode share** (top option = A's single answer) | hand-coded facets + Jaccard overlap; mode share not measured in phase 2 | 11-02 (Bo: interpretation tied to the asked question) | replaced |
| C11 | D **selection step** by a pairwise judge with position swap (10-18) | not built; F3 to provide a selection signal if it validates | v2-plan §2 | postponed |
| C12 | VS **D1 tail-sampling** variant | dropped | 10-19 (k = 3, D2 wording only) | dropped |
| C13 | F2 phrasings incl. **"show me alternatives"** and news framing | casual + formal only; the k prediction untested | Chloe's question file, 11-04 | reduced |
| C14 | F3: **values-only stripped** condition + full condition, structured guess, independent model, 30–40 hand labels | deck trial: chart only (title included, so close to the leaky full condition), top option only, Luna, no labels, not in the repo | teammate, week of 11-02 | reduced; not yet the designed test |
| C15 | Phase-2 arms **A, B and D** (v2-plan §2) | only D has been run in phase 2 | — | not exercised |
| C16 | Human 8-criteria score of **D-top and D-best** (v2-plan §3) | the grader scores every option; D-top / D-best not reported | 11-02 v0 | replaced |
| C17 | First-failure open coding through a **blind-scoring sheet with two extra columns** (10-21) | `first_failure` column in `scores.csv`; empty (the 11-02 sheet came back as a Codex pass) | 11-02 | pending in new form |

## 3. Decided, not done yet (pending)

| Item | Blocks | Owner |
|---|---|---|
| Human labels: `review.csv` for D v1 (12 cells), F1 v2 (10), F2 (17) + 15 audit rows; `bo_review` in two `facets.csv`; whether the new readings enter `gold_readings.py`; the two TR08 rule cells (F1 v2 A2-r1 o1/o2) and v1 K1-r3 o3 | every promotion (C7), the PPI estimate, the "human final review" claim | Bo |
| **Open coding ≥ 30 rows (`first_failure`) and the taxonomy count** (v2-plan §5 steps 3–4) | the loop's "one change chosen from counts" | Bo |
| **E010 loop iteration 1**: one change, paired re-run, keep/revert by the written rule | the core V2 claim (detection → change → proven effect) | Bo |
| **Score the phase-1 runs** (mimo and Luna A/B/C) with the scorer, as the 10-27 brief planned (E010: "phase-1 runs are scored without re-running") | phase 1's own question ("fix it in the prompt, or build a step?") still has no quality scores; the blind scoring listed in `phase1-summary.md` is not recorded as done | Bo / team |
| PPI-corrected silent-error estimate (needs ≥ 30 labelled audit rows) | an honest headline number | after the labels |
| mimo (independent) second grader restored | C6 | Bo (quota) |
| F3 as designed (C14), committed to the repo | F3 conclusions; any selection signal | F3 teammate |
| Held-out P1–P10 once at the end with the frozen workflow and scorer | generalization claim | team, at the end |
| Arrows table (quality / time direction per change) | reporting format Ryan asked for | at E010 |
| H20 (purge two mistakenly committed drafts, needs a force push) | — | Bo's call |

## 4. Never decided (open)

| Question | Why it matters now |
|---|---|
| **Timebox:** 10-18 said phase 2 runs to mid-November (≈ 11-14); `v2-plan.md` says phase 2 ends with the final presentation (≈ 12-18, unconfirmed) | decides whether next week is the end of phase 2 or its middle |
| **D's final form:** is D v2 the winner of F1? (FOLLOWUPS: "D = F1's winner") | every later run and the E010 baseline depend on it |
| **Grader status:** keep reporting grader-based numbers as "shadow, pending promotion", or promote items now on agreement alone | §5 point 1 |
| **E008 generator × reviewer cross** (mentor-requested 10-16, in the 10-27 brief) | silently absent from `v2-plan.md` (Luna only, not in the deferred table) |
| **E010 iteration-1 treatment:** data profile in context vs plan declaration (trigger met: 85 of 127 failure instances are undisclosed data facts) | the first prevention result |
| **Selection for D** (pairwise judge, F3 signal, or none) | whether D ends as "a list of options" or "options + a choice" |
| **Ryan's 11-06 spectrum:** measure drift vs explain change; drift metric design | the phase-2b thesis |
| Facet codebook calls (K2 count vs share one facet; new facet names) | F2 overlap numbers |
| Standalone-chart check (F3's I1 finding) vs decision 7 (qualifications count only in text) | grading consistency |
| A1-tie presentation rule (show options within Δp of the top) | product behaviour of D |
| What of Bo's pipeline-v2 (S0–S6) returns: only S0 PROFILE as a treatment, or more steps | architecture of the final system |

## 5. Inconsistencies to resolve before the next step

1. **Shadow vs primary (C7).** The plan says grader columns are never scored until promoted; every number we reported (24/54, 14/42, 42/84) is grader-based. Either label them "machine estimate, not yet validated by human labels" or finish the labels and promote. Bo's 10-21 goal (automated primary) is reachable, but only through the pending labels.
2. **"Two automatic evaluations before the human"** (told to Ryan 11-06) are two Luna passes: they measure stability, not independence (C6).
3. **Timebox conflict** (§4 first row).
4. **E008 and arms A/B** were planned for phase 2 and have no decision record (C15, §4).
5. **Decision 7 vs F3:** the standard grades the written answer; F3 shows charts are read without their text.
6. **Phase 1's question is unanswered in quality terms** (§3): the final presentation needs either the phase-1 runs scored or an explicit statement that phase 1 reports machine-checkable results only.

## 6. What the next V2 step needs first (dependency order)

1. Decide the timebox, D's final form and the grader status (§4 rows 1–3): one-line decisions, everything else depends on them.
2. Labels (§3 row 1) and the first open-coding pass (§3 row 2): small, and they unlock promotion, the PPI number and the evidence-based choice of the first treatment.
3. E010 iteration 1 with the chosen treatment, scored by g8 (+ the drift metric if Ryan's route is adopted).
4. In parallel, owned by teammates: F3 as designed; phase-1 runs scored with the scorer; E008 decided or formally dropped.
