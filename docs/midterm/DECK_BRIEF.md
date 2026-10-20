# Midterm deck brief (for the slide builder)

Build the team's midterm presentation: **one title slide + four content slides**, delivered as a PDF. Read the course rules (§0) and the content rules (§1) before writing anything.

## 0. Course rules (verbatim requirements, 2026-10-20)

- PDF with **one title slide and up to four content slides**.
- **Title slide: only the project title and the group number.** No project code name (do not write "Poppy"), no sponsor or team names, no logos, no other identifiers.
- Cover, in this order: **Problem and data** (goals, understanding of the data); **Progress and findings** (exploratory work, what we learned, initial results, current approach); **Next steps** (plans for the rest of the semester and **how responsibilities are divided** in the group).
- Finalized results are not expected; focus on what we learned and how it shapes the next steps.
- Audience with **varied technical backgrounds**.
- Slide design: **one main idea per slide, supported by evidence**; visuals, diagrams and figures over text; explain what the results reveal. Use the **assertion–evidence** style: the slide title is a full-sentence claim (≤ 2 lines); the body is visual evidence for that claim, with minimal text.
- Graded on Presentation (structure, visual effectiveness, easy to follow; 5 pts) and Content (well scoped, meaningful exploratory checks and results, clear and appropriate approach; 5 pts).
- Presenting time is not stated; write speaker notes for **about 1 minute per content slide** (each slide may be presented by a different member).

## 1. Rules for you

1. **Every number on a slide must come from a file listed in §3.** Open the file and check it. If you cannot find it, write `[TBD]`. Never invent, estimate or round up a result. Results are pilot-scale: say "in pilot runs", never "significant".
2. **Teammates' parts are not finished.** Cells or boxes marked **[TBD: …]** stay as visible placeholders; do not fill them with guesses.
3. Plain language for a mixed audience. Avoid: SHA-256, sandbox-exec, OpenCode internals, "contract", "harness", TR codes, model-internal jargon. Say instead: "locked prompts", "isolated workspace with no internet", "automatic checks", "known data pitfalls".
4. Output: `docs/midterm/midterm-deck.pptx` (16:9, python-pptx, standard fonts, images as PNG so it imports into Google Slides) **and** `docs/midterm/midterm-deck.pdf`. If you cannot export PDF locally, say so; the team will export from Google Slides. Also `docs/midterm/speaker-notes.md` with ~120–150 words per content slide and, next to every number, the file it came from.
5. Visual style: white background, one accent colour plus the workflow figure's palette (blue = model run, green = automatic check, orange = evaluation, purple = differs from the baseline). Large figures; titles ≥ 28 pt; body ≥ 16 pt; no paragraph text blocks.
6. When done, render every slide to PNG, look at each one, and fix overlaps, cut-off text and unreadable images.

## 2. The story (one paragraph)

An analyst gives a question about NYC crash data to an AI agent and takes its chart and answer. The agent fixes errors that crash its code, but not errors that run silently and give wrong or misleading results. We ask which remedy helps: **changing the prompt** (a self-check instruction, or asking for three alternative framings), or **adding a step** (an independent reviewer that sees the chart and a revision step). Before comparing anything we locked the setup down, because the first runs showed the agent downloading outside data and able to read our answer key. In pilot runs, the separate reviewer caught silent errors the agent had missed; the self-check prompt mostly spent budget; asking for alternatives produced real alternatives but did not catch misleading framings, which happen even when every number is correct. Next we build an automatic evaluation layer that checks each step against the data's known pitfalls, and finish the stronger-model comparison.

## 3. Sources (every number is in one of these)

| Topic | File |
|---|---|
| Design of the arms, workflow figure | `docs/phase1-abc-design.md`, `docs/figures/phase1-workflow.png` |
| Data, data pitfalls (trap catalog) | `docs/scenario-data-v1.md`; per-question pitfalls `experiments/E007-pilot-prompts/SCORING.md` §4; fingerprint `scripts/env_expected.json` |
| Why the free model (only one that reads images) | `experiments/E006-mimo-screen/REPORT.md`, `experiments/LOG.md` (E005) |
| Pilot rules, lock-down findings | `experiments/E007-pilot-prompts/PROTOCOL.md` (amendments 2026-10-15/16), `experiments/LOG.md` |
| Pilot results A/B/C on the free model | `experiments/E007-pilot-prompts/ITERATIONS.md` ("iteration 3", "C v3: the one format check", I1 re-run), `results/` |
| Stronger model (GPT-6 Luna) A/B | `experiments/E008-model-contrast/README.md`, `results/`, `experiments/LOG.md` (2026-10-19, "arms A and B on GPT-6 Luna") |
| Alternatives arm D | `experiments/E009-enumerate/DESIGN.md`, `ITERATIONS.md`, `results/D-v1-k3-openai-gpt-6-luna/` |
| Next phase | `docs/v2-eval-layer-architecture.md` |
| Mentor asks | `docs/mentor-meeting-2026-10-16.md` |

## 4. The five slides

### Title slide
"Fix It in the Prompt or Add a Step? Catching Silent Errors in an AI Data-Analysis Agent" · **Group [TBD: group number]**. Nothing else.

### Slide 1 — Problem and data
**Assertion (title):** "AI analysis agents fix code that crashes, but not answers that are silently wrong."
**Evidence (two panels):**
- Left, "The data": NYC Motor Vehicle Collisions, **2,269,187** police-reported crashes, July 2012 – June 2026, pinned snapshot. Three pitfalls an analyst must know, each one line with its number: borough missing for **19.9–38.1%** of crashes per year (2013–2025); minor crashes stopped being recorded in **2020** (crashes **211,486** in 2019 → **85,546** in 2025); **no traffic volume or miles driven** in the data, so "risk per mile" cannot be computed.
- Right, "Silent errors from our pilot runs" (three callouts, real examples): "Sunday has 32% fewer crashes than Friday" (data: 24%); a "people harmed" column that silently dropped rows with missing values; "risk per mile fell 26%" from data with no mileage.
- Bottom strip, goal: "Which remedy helps: change the prompt, or add a review step?"
**Notes:** in 10 baseline runs the agent fixed 6 crashing errors itself and none of the silent ones.
**Sources:** `SCORING.md` §4, `docs/scenario-data-v1.md`, `ITERATIONS.md` (B v2/v3 records), `docs/phase1-abc-design.md` §1.

### Slide 2 — Approach and exploratory checks
**Assertion:** "We compare four agent designs under identical, locked-down conditions."
**Evidence:**
- Main visual: the four designs as lanes, using `docs/figures/phase1-workflow.png` for A/B/C and adding a fourth lane D in the same style. One-line labels: **A** baseline agent (writes and runs its own code, ≤ 15 steps); **B** + independent reviewer that sees the chart, then a revision of only what it flagged; **C** same agent, prompt adds "check your own work"; **D** same agent, prompt asks for **3 framings**, each with chart and a probability (Verbalized Sampling, suggested by our mentor).
- Side strip "Same for every design": same data and questions; two models (a free model and GPT-6 Luna); isolated workspace with **no internet**; prompts **locked** before comparison; 6 practice questions kept separate from the 10 test questions.
- Small callout "Exploratory checks that changed our setup": the agent searched the web and downloaded outside data; it could read our answer key; the reviewer silently inherited the analyst's permissions; the free service sometimes stalls silently. All four found in our own logs and fixed before results counted.
**Sources:** `docs/phase1-abc-design.md`, `E009 DESIGN.md`, `PROTOCOL.md` amendments, `LOG.md` 2026-10-15/16.

### Slide 3 — Progress and findings
**Assertion:** "In pilot runs, a separate reviewer caught silent errors; prompt changes added cost or options, not correctness."
**Evidence (left: one example; right: one table):**
- Left: before/after of one chart: `experiments/E007-pilot-prompts/results/B-v4-v3/I1-r1/out/initial.png` → `.../revised.png`. Caption (one line): "Reviewer flagged unlabelled shading on the wrong side of the break-even and an unsupported 'driving recovered' claim; revision fixed them without changing a plotted value."
- Right: table, rows = designs, columns = free model | GPT-6 Luna, 6 practice questions:
  - A: free model 5/6 completed (one ran out of steps exploring) | Luna 6/6 completed.
  - B: free model: real errors fixed on 4 questions, none invented, none of A's correct numbers changed | Luna: issues flagged and fixed on 2 questions, 4 judged correct as is.
  - C: free model 2/6 completed: the self-check roughly doubled the steps | Luna **[TBD: teammate – C runs]**.
  - D (Luna only): 18/18 runs completed with 3 genuinely different framings in 17; the top-ranked option was still the plain count on 5 of 6 questions.
  - Footer: "Single pilot runs on practice questions; blind scoring with our 8-point rubric **[TBD: team – scores]**."
**Notes:** explain why the reviewer helps (a fresh context judges the output as someone else's work) and why the self-check costs (the same agent re-checks inside the same budget).
**Sources:** `ITERATIONS.md` (iteration 3; C v3 format check; I1 re-run), `E008-model-contrast/results/` + `LOG.md` 2026-10-19, `E009 ITERATIONS.md`.

### Slide 4 — Next steps and roles
**Assertion:** "Numbers can be correct while the framing misleads, so next we build an evaluation layer that checks every step."
**Evidence (left: the finding; middle: the plan; right: roles):**
- Left, small table "Correct numbers, misleading framing" (arm D, 3 runs each): Brooklyn question: drops the 19.9–38.1% of crashes with no borough without saying so, **3 of 3 runs**; Brooklyn and per-mile questions: "per reported crash" across the 2020 recording change with no warning, **3 of 3** and **2 of 3** runs. Every number checked against the data and correct.
- Middle, simple diagram: agent steps (plan → compute → chart → answer) with one automatic check under each: plan vs known data pitfalls; values vs reference queries; every number in the answer recomputed; claims the data cannot support flagged; chart rubric. Loop arrow: run test set → find failures → change one thing → re-run.
- Right, roles table: **[TBD: Member 1]** evaluation layer and automatic checks, alternatives arm D; **[TBD: Member 2]** stronger-model comparison runs and analysis; **[TBD: Member 3]** self-check runs, scoring and write-up. (Bo to confirm names and split.)
- Footer timeline: finish Luna runs and blind scoring → build checks on the 10 untouched test questions → final report, blog post, demo video.
**Sources:** `E009 ITERATIONS.md` (trap incidence), `docs/v2-eval-layer-architecture.md` §1–§3.

## 5. Checks before you finish

- Exactly 5 slides; title slide has only the title and the group number.
- Each content slide title is a full-sentence claim; the body is mostly visual.
- Every number traced to a file in `speaker-notes.md`; no Luna C results, no scores, no significance claims.
- All `[TBD: …]` placeholders visible and unfilled.
