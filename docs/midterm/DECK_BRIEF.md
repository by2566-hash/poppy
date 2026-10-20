# Midterm deck brief (for the slide builder)

You are building the team's midterm presentation deck for **Poppy** (NYU CDS × Honda Research Institute / 99P Labs). Audience: mentors Ryan Lingo (Applied AI Research Engineer, cares about evaluation, context engineering, agentic systems) and Rajeev Chhajer, possibly an NYU faculty member. In person, Friday 2026-10-23; Ryan reviews the slides on Thursday 2026-10-22 5 pm ET.

## 0. Rules for you (read first)

1. **Every number on a slide must come from a file listed below.** Open the file and check it. If you cannot find a number, write `[TBD]`. Never invent, round up, or "estimate" a result.
2. **Teammates' parts are not finished.** Slides marked **PLACEHOLDER** must contain the layout, the title, the axis/column headers and `[TBD: <owner> – <what>]` boxes, nothing else. Do not fill them with guesses.
3. Language: English. Short slide text (≤ 25 words of body text per slide where possible); detail goes into speaker notes.
4. Output: a `.pptx` (python-pptx) at `docs/midterm/poppy-midterm.pptx`, 16:9, plus `docs/midterm/speaker-notes.md`. The team's existing deck is Google Slides; the `.pptx` must import cleanly into Google Slides (standard fonts, no SmartArt, images as PNG).
5. Visual style: white background, one accent colour, large charts, one idea per slide. Reuse the colours of `docs/figures/phase1-workflow.png` (blue = model run, green = harness check, orange = evaluation, purple border = differs from A).
6. Presentation rules from the course: **[TBD: Bo to paste the official midterm rules here: time limit, required sections, grading rubric]**. Until then assume **12 minutes + Q&A, ~14 slides**; adjust the slide count when the rules arrive.

## 1. Story in one paragraph (the spine of the deck)

An analyst hands a question about NYC crash data to an AI agent and takes its chart and answer. The agent fixes errors that crash its code, but not errors that run silently. Phase 1 asks: when the output is not good enough, do you **fix it in the prompt** (C: self-check instruction) or **build a step** (B: independent read-only review + revision)? We added D at Ryan's request (Verbalized Sampling: ask for three framings with probabilities) and a second model (GPT-6 Luna vs the free mimo model). Before any formal comparison we built and verified the harness, because the first runs showed the agent could reach the internet and read our answer key. Key findings so far: an independent reviewer catches silent errors the agent does not; a self-check in the prompt mostly costs steps; asking for three framings gives real alternatives but the model's first choice is still the typical answer; and **numbers can be right while the framing misleads**, which no current check catches. Phase 2 builds the evaluation layer that does.

## 2. Sources (read these; they hold every number)

| Topic | File |
|---|---|
| Design A/B/C, workflow, predictions | `docs/phase1-abc-design.md`, figure `docs/figures/phase1-workflow.png` |
| Data and trap catalog (TR01–TR17) | `docs/scenario-data-v1.md` |
| Model screen (why mimo) and vision test | `experiments/E006-mimo-screen/REPORT.md`, `experiments/LOG.md` (E005 entry) |
| Pilot protocol, amendments, contract acceptance | `experiments/E007-pilot-prompts/PROTOCOL.md` |
| Pilot iterations, every result and correction | `experiments/E007-pilot-prompts/ITERATIONS.md` |
| Frozen prompts with hashes | `experiments/E007-pilot-prompts/FROZEN.md`, `prompts/frozen/` |
| Scoring rules, per-question trap sheet | `experiments/E007-pilot-prompts/SCORING.md` |
| Luna A/B runs (teammates) | `experiments/E008-model-contrast/README.md`, `results/`, `experiments/LOG.md` (2026-10-19 "arms A and B on GPT-6 Luna") |
| Arm D design and results | `experiments/E009-enumerate/DESIGN.md`, `ITERATIONS.md`, `results/D-v1-k3-openai-gpt-6-luna/` |
| Mentor asks | `docs/mentor-meeting-2026-10-16.md` |
| Phase 2 architecture | `docs/v2-eval-layer-architecture.md`, `docs/direction-v2-candidates-2026-10-18.md` |
| The full experiment log | `experiments/LOG.md` |

## 3. Slide plan (~14 slides)

Each entry: title · on-slide content · visual · speaker-note points · source.

**1. Title.** "Fix it in the prompt, or build a step? Evaluating an AI data-analysis agent on NYC crash data". Team names [TBD: names], NYU CDS × HRI / 99P Labs, Midterm, 2026-10-23.

**2. The problem.** One line: agents fix errors that crash, not errors that run silently. Three real examples from our runs, one line each: a sum that silently dropped rows with missing values (mimo, A2); "32% fewer crashes on Sunday" when the data says 24% (mimo, K2); "risk per mile fell 26%" from a dataset with no mileage (I1). Visual: three small callouts. Notes: in 10 baseline runs the agent fixed 6 crashing errors itself; none of the silent ones. Source: `ITERATIONS.md`, `LOG.md`, `docs/phase1-abc-design.md` §1.

**3. Setup.** Data: NYC Motor Vehicle Collisions, 2,269,187 crashes, snapshot pinned (fingerprint in `scripts/env_expected.json`). Agent: OpenCode, one bounded run (≤ 15 steps, 600 s), writes and runs its own code, outputs chart + plotted values + written answer. Models: mimo-v2.6-flash-free (free, the only free model that reads images) and GPT-6 Luna (Ryan's key). Sandbox: own folder and data copy only, no internet. Visual: simple left-to-right strip (question → agent run → chart/values/answer). Source: `docs/phase1-abc-design.md` §2, §10; `E006 REPORT.md`; `PROTOCOL.md` sandbox v2.

**4. The four arms.** Use `docs/figures/phase1-workflow.png` (A/B/C). Add D as a fourth lane in the same style: "C + produce 3 framings, each with chart, values and a probability". One sentence per arm under the figure. Notes: B is paired with A (reviews A's exact output); C and D change only the prompt. Source: `docs/phase1-abc-design.md`, `E009 DESIGN.md`.

**5. How we kept it honest.** Pilot on 6 questions disjoint from the 10 formal ones; protocol pre-registered and committed before results; at most 3 prompt iterations; prompts frozen with SHA-256; acceptance = **contract** (inputs, outputs, boundaries, end states), not effect, so we do not tune B to win. Visual: a 4-step timeline (pilot → iterate ≤ 3 → freeze + hash → compare). Notes: why contract acceptance (tuning on effect would favour B). Source: `PROTOCOL.md` (scope v2 and the 2026-10-15 B contract amendment), `FROZEN.md`.

**6. What the harness caught before any result counted.** Four findings, one line each, with how each was fixed: (1) the agent searched the web and downloaded vehicle-mile data (web search + Python `urllib` bypassed "webfetch: deny") → OS-level sandbox; (2) the agent's Python could read our gold answers and docs → repo reads denied; (3) the read-only reviewer silently inherited the analyst's permissions from a parent config → isolated folder + guard; (4) the free gateway stalls silently; a client cannot tell long reasoning from a stall → timeout rule, zero-output retry. Visual: 2×2 grid. Notes: all four verified by red-team tests; this is what an applied/FDE team does before trusting any number. Source: `PROTOCOL.md` amendments 2026-10-15/16, `ITERATIONS.md` (stall analysis), `LOG.md`.

**7. Pilot results on mimo (A, B, C).** Small table, one row per arm, 6 pilot questions, single runs:
- A (A-v1, r1): complete on K1, K2, K3, A2, I1 (I1 re-run under the fixed sandbox); A1 hit the step cap. Check `results/A-v1/*-r1/meta.json` and the I1 re-run note in `ITERATIONS.md`.
- B (critique v4 + revise v3, iteration 3): contract met on all 5 runnable items; real issues fixed on K1, K2, A2, I1; K3 returned NONE; A1 not run (A had no answer). Check `ITERATIONS.md` "iteration 3".
- C (v3): 2/6 complete; the self-check roughly doubled steps on clear questions and hit the 15-step cap. Check `ITERATIONS.md` "C v3: the one format check".
Notes: state single runs; B tuned on these 6 questions. Source: as listed.

**8. What the reviewer caught (example).** Before/after images: `experiments/E007-pilot-prompts/results/B-v4-v3/I1-r1/out/initial.png` and `.../revised.png`. Caption: the review flagged unlabelled shading on the wrong side of the 74% break-even (visible only in the image), an unsupported "driving back to pre-pandemic levels" claim, and an "injuries stayed flat" sentence contradicted by the values (−19%); the revision fixed all four issues without changing a plotted value. Second small callout: A2's NULL-dropping `harmed` column found and fixed. Source: `ITERATIONS.md` iteration 3 table.

**9. PLACEHOLDER — mimo vs GPT-6 Luna (A, B, C).** Layout: a table with rows A, B, C and columns mimo | Luna, per cell "complete x/6, [TBD: score]". Already known for Luna (fill these): A 6/6 complete (11–13 steps); B: K2 and A2 revised (2 issues each), K1, K3, A1, I1 returned NONE. Everything else `[TBD: teammates – Luna C runs, repeats r2/r3, blind scores (8 criteria)]`. Source: `experiments/E008-model-contrast/results/`, `LOG.md` 2026-10-19.

**10. D: three framings with probabilities (Verbalized Sampling).** Left: what D asks (3 framings that each answer correctly; differ in metric, denominator, grouping or chart type; probability = how likely a careful analyst picks it). Right: the three A2 option charts side by side from `experiments/E009-enumerate/results/D-v1-k3-openai-gpt-6-luna/A2-r1/out/option_1.png`, `option_2.png`, `option_3.png`. Key numbers: 18/18 runs complete (6 questions × 3 runs, Luna), 3 analytically distinct framings in 17 of 18 runs, every ambiguous/insufficient answer states that per-trip/per-mile risk cannot be judged without exposure data. Source: `E009 ITERATIONS.md`.

**11. The model's first choice is still the typical answer.** One statement + small table: on 5 of 6 questions the highest-probability option is the plain count in all 3 runs (only A2 ranks a rate first). Notes: matches the Verbalized Sampling claim that alignment favours the typical answer; the alternatives exist but come second and third. Source: `E009 ITERATIONS.md` "Repeats r2, r3".

**12. Right numbers, misleading framing.** Table from `E009 ITERATIONS.md` (trap incidence): A1 filters Brooklyn and silently drops the 19.9–38.1% of crashes with no borough, in 3/3 runs; A1 and I1 use "per reported crash" across the 2020 recording change without a caveat (3/3 and 2/3). Every number was checked against DuckDB and is correct. Message: the in-run self-check does not catch this; it needs an evaluation layer that knows the data's traps. Source: `E009 ITERATIONS.md`, `SCORING.md` §4, `docs/scenario-data-v1.md` (TR01, TR05).

**13. PLACEHOLDER — trade-offs (Ryan's arrows table).** Rows: B, C, D vs A; columns: quality ↑/↓/→, cost ↑/↓/→, time ↑/↓/→; one row per model. Cost and time directions can be read from recorded steps/time (`meta.json`), but quality needs the blind scores: `[TBD: team – after scoring]`. Notes: cost and time are reported as direction only, as Ryan asked. Source: `SCORING.md` §3.

**14. Evaluation plan and limits.** Left: blind scoring with the team's 8 binary criteria; D compared as D-top (headline), D-best, D-all; per-question trap sheet for criterion 6. Right (limits): 6 pilot questions; B tuned on them; mimo arms single runs; small n, no significance claims. Source: `SCORING.md`, `PROTOCOL.md`.

**15. Phase 2: the evaluation layer.** Draw two layers: (1) the agent workflow, unchanged except for a short plan declaration; (2) the evaluation layer with one check per step: contract, plan vs gold plan + trap catalog, values vs gold SQL, numbers in the answer recomputed, claims the data cannot support, chart rubric. Silent error = unsourced number ∨ unsupported claim ∨ gold mismatch ∨ misleading framing (the fourth found by D). Loop: run regression set → per-step checks → failure taxonomy → one change → re-run → keep/revert. Notes: P1–P10 kept untouched as the held-out set. Source: `docs/v2-eval-layer-architecture.md` §1–§3.

**16. Next steps and asks.** Next: finish Luna C and repeats; blind scoring; phase-2 build (recompute oracle, claim judge calibrated on human labels, framing check, regression suite). Asks for the mentors (from `docs/v2-eval-layer-architecture.md` §5 and `mentor-meeting-2026-10-16.md`): feedback on the four-part silent-error definition; how 99P calibrates LLM judges; whether to show one chart or a set in a product. [TBD: Bo to confirm the asks].

## 4. Checks before you finish

- Every number on slides 2, 3, 6, 7, 8, 10, 11, 12 traced to a file; list the file next to it in `speaker-notes.md`.
- Placeholders 9 and 13 contain only structure and `[TBD]` text.
- No mention of results that are not in the repo (no Luna C, no scores, no significance).
- The deck runs ~12 minutes at ~50 s per slide; trim slides 5 and 14 first if the rules give less time.
