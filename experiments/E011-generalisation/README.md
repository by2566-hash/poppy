# E011: generalisation of E010-v4 to held-out questions (T2, from 2026-11-19)

Design: `experiments/E010-loop/SUMMARY.md` §4 (T2). Frozen versions and hashes: `experiments/E007-pilot-prompts/FROZEN.md`.

## Question

Does E010-v4 keep its gain on questions it was not designed on? E010-v4 is `D_enumerate.v2-plan4-ACB.md`, locked 2026-11-19. On the 6 pilot questions its silent-error rate was 11%, against 19% for v3 and 42–50% for the D v2 baseline (`E010-loop/SUMMARY.md` §1). The pilot questions were used to design every change, so that is a development-set result.

## Question set (`questions.json`)

- **20 ambiguous: TA01–TA20.** Several valid readings that the data can answer.
- **5 insufficient: TI01–TI05.**
  - The data cannot answer the question as asked.
  - A correct output says so and still shows a measure the data supports. This is the grader's rule for type `insufficient`, as in I1.
  - Each one uses the fixed 2013–2025 window and the ending "Make a chart and answer based on this crash data", as in I1, P9 and P10.
- **20 clear:** to be added.

How the set was checked:

- **Wording.** No exact match with any original question text: pilot K1–I1, E006 P1–P10, E002 Q01–Q08, E009 rephrasings (37 texts). The highest similarity is 0.74, from the shared question endings.
- **Subject.** Four ambiguous questions are close in subject to an original and are marked `near_original`: TA01, TA11, TA18, TA19. Whether to keep them is a team decision.
- **Format.** Runner format `{id, base, type, text}`, as in `E009-enumerate/questions.rephrasing.json`, with `base = id`.
- **Draft fields.** Fields starting with `draft_` (readings, trap ids, required statement, supported measure) are notes for writing gold entries. They are not the standard: `run_pilot.py` and `score_runs.py` ignore them.

## Arms (same day, same harness as E010)

| Arm | D version | Prompt |
|---|---|---|
| baseline | `v2` | `D_enumerate.v2.md` |
| v3 | `v2-plan2` | `D_enumerate.v2-plan2.md` (C5 v2) |
| **v4** | `v2-plan4-ACB` | `D_enumerate.v2-plan4-ACB.md` (frozen) |

## Run

From the repo root, concurrency 1, team venv, with `scripts/check_env.py` passing first:

```
POPPY_EXP=E011-generalisation \
POPPY_QSET=experiments/E011-generalisation/questions.json \
POPPY_MODEL=openai/gpt-6-luna PILOT_K=0 PILOT_STEPS=50 PILOT_CONCURRENCY=1 \
POPPY_LABEL_TAG=<MMDD> \
~/.poppy/venv/bin/python experiments/E007-pilot-prompts/run_pilot.py D <D version> <repeats>
```

- `PILOT_QIDS=TA01,TI01` restricts the questions.
- The sandbox is `../poppy-sandbox/E011/`.
- Collect each arm with `POPPY_EXP=E011-generalisation python3 scripts/collect_runs.py <label>`. Runs go into `results/<label>/` and summaries into `runs/`.

## Scoring

- `score_runs.py` (g8.3) reads gold only from `E007-pilot-prompts/gold_readings.json`, which covers K1–K3, A1, A2 and I1 only.
- Until the new questions have gold readings and trap items there, only these can be computed:
  - machine checks (`--no-grader`);
  - the generic grader criteria (c1–c8, unsupported_claim).

  These results are not comparable with E010's silent-error rate.
- Adding the gold entries changes the standard. It needs Bo's approval and new hashes in `FROZEN.md`. The grader prompts of the six existing questions do not change.

## Files

| File | What |
|---|---|
| `questions.json` | the question set |
| `SUMMARY.md` | one-page record: arms, results, findings, decisions, open items |
| `ITERATIONS.md` | dated detail, commands and evidence |
| `results/`, `runs/` | collected runs and batch summaries (created by the runner and `collect_runs.py`) |
