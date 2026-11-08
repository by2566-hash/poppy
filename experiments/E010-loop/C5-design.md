# C5 / E010-v3: Plan → Data check → Final plan. Boundaries and responsibilities

Bo's design (2026-11-08). Analysis and boundary proposal by Claude. Prompt `D_enumerate.v2-plan.md` (hash in FROZEN.md). It is run as a diagnostic candidate next to C1–C4; Bo reviews it before it becomes an E010 iteration.

## Why this design follows from today's evidence

| Evidence (ITERATIONS.md) | What it implies for C5 |
|---|---|
| E010-1: a code profile in context is not acted on, and it replaces the agent's own checks (NULL queries 0.7 → 0.1 per run) | Facts must be produced *for the plan in hand*, not handed over in advance. The data check is plan-driven and run by the agent, which keeps the exploration alive. |
| C1: a required slot "rows not used" takes TR05 7/7 → 1/8 | Every step ends in a written artifact the grader or the harness can see. |
| C2 ≈ C1: once there is an action hook, the profile adds nothing | C5 has no profile; the data check replaces it. |
| Controls TR01 / TR15 move in no arm | They need a decision about the *denominator and the claim*, not a coverage fact. That is the Plan / Final plan's job (answerable, denominator, limitations). |
| Coverage numbers collide with g8 provenance | The check facts go to a file (`check_<id>.csv`), so they have a source that can be verified. |
| Profile audit: missing ≠ NULL only (33% "Unspecified", 00:00 heaping, 70% of NULL-borough rows have coordinates) | The data check asks for missing *in any form* and for pile-ups, in general terms (no trap words). |

## The steps

| Step | Responsibility | May | May not | Artifact | Who checks |
|---|---|---|---|---|---|
| Framings | candidate readings of the question (as D v2) | read the dictionary | — | (in options.json later) | g8 distinctness |
| **Plan** | commit to what the framing needs *before seeing data*: answerable (yes / partly / no, which part), metric, denominator, population, filters, years, grouping | use the dictionary | query the data | `plan_<id>.json` → `initial_plan` | harness: plan written before the first data query |
| **Data check** | facts about *which rows* the plan uses, for the planned columns and years only: rows, rows per year, missing in any form, pile-ups, partial years; their consequence (rows dropped, population really counted); a decision per fact (keep and disclose / exclude / own group); plan changes with reasons | COUNT(*), counts of NULL / empty / placeholder / impossible values in planned columns, date coverage | any injury or death sum, rate or share; **any count of rows by an outcome value** (see leak below) | `check_<id>.csv` (fact, value); `plan_<id>.json` → meaning and decisions | harness: no outcome query before analysis starts; machine: check values recomputed from the data |
| **Final plan** | the plan the analysis must follow, with limitations from the check | change the initial plan, giving the reason | add results | `plan_<id>.json` → `final_plan`; options.json fields metric / denominator / grouping = final plan | machine: options fields equal the final plan |
| Analysis | code for the final plan | — | silent deviation from the final plan | values, chart | self-review; gold match |
| Chart | title = final plan's metric + population; subtitle = main limitation (P10) | — | — | png | g9 `chart_self` (when added) |
| Interpretation | carries the data-check conclusion: rows not used, why, counts from the check file, the decision | — | — | options.json | g8 grader (TR05, TR08, TR07 …) |
| Self-review | code, chart title and interpretation follow the final plan; numbers trace to values or check file | — | — | — | — |

## Design choices

1. **Facts by code, decisions by the model.** Every number in the check is computed by code. The model does what code cannot: decide what the facts mean for the plan and what to do about them. This is Bo's "LLM profile": the model chooses *which* facts matter for *this* plan, which solves the missing link between "borough NULL 30%" and `borough='BROOKLYN'` (NoLiMa) that the static profile left open.
2. **Outcome-blind until the final plan** (Bo's rule). Row decisions are taken before any result is seen. This is the pre-registration idea: the choice of rows cannot be steered by which result looks better.
3. **One agent, one run, not a separate check agent, for now.** Plan, check and final plan need the same context. A second agent adds a handoff that can drop facts. Independence matters for *measurement* (cleared-context reverse inference), not for row checking, because the check is verified by code anyway. Switch to a separate agent only if the traces show steps being skipped or rationalised.
4. **Artifacts over self-report.** The faithfulness evidence (models disclose 25–39% of what they use) means the plan and check files are what the harness verifies. The interpretation is what the reader and grader see.
5. **No trap words.** Missing "in any form", "piled up at a default value", "rows per year": general data-quality terms. Nothing names borough, 2020, 2026, Unspecified or 00:00.

## Found in the first C5 run: a leak path in the boundary

On K1-r1 the agent checked "pile-ups" on the outcome column by counting rows where `number_of_pedestrians_killed = 0` per year (2013: 203,569 of 203,742). The complement, 173 crashes with a pedestrian death, is almost K1's answer (176). The rule "no outcome numbers" was kept literally and broken in substance. Proposed fix for the next C5 version: *for outcome columns (injured / killed counts) check only whether the value is missing; never count rows by an outcome value*. `diagnosis/c5_process.py` measures how often this happens across the 18 runs (`check_rows_by_outcome_value`, and outcome-value queries before analysis).

## What Bo decides

- **Provenance source:** does `check_<id>.csv` count as a source for numbers in the answer (a scorer change → g8.1), with its facts recomputed from the data by a machine check? Without it, every arm that discloses coverage numbers looks worse under g8.
- **Leak fix** above (prompt wording for C5 v2).
- **Single agent vs separate check agent:** recommendation is single, revisit if traces show skipped steps.
- **Chart self-caption:** C5 already asks for it. `chart_self` (g9) can be scored on all arms afterwards.
