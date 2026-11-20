# E011 summary: E010-v4 on held-out questions (from 2026-11-19)

This is the one-page record. Detail, commands and per-run evidence live in `ITERATIONS.md`, the setup in `README.md`, and hashes in `../E007-pilot-prompts/FROZEN.md`.

Setup common to every arm:
- **Model and harness:** GPT-6 Luna, D v2 enumerate harness, free k, `PILOT_STEPS=50`, hermetic harness, concurrency 1.
- **Questions:** held-out set `questions.json`: 20 ambiguous and 5 insufficient now, 20 clear to be added.
- **Comparisons:** same-day only (E010 finding M1).
- **Grader:** g8.3, two Luna passes, once gold entries exist (see §4).

## 1. Experiments

| Label (results/) | Date | Arm | Prompt | Questions × repeats | Runs complete | Options | g8.3 silent-error |
|---|---|---|---|---|---|---|---|
| — | — | baseline (D v2) | `D_enumerate.v2.md` | — | not run | — | — |
| — | — | v3 (C5 v2) | `D_enumerate.v2-plan2.md` | — | not run | — | — |
| — | — | **v4 (ACB, frozen)** | `D_enumerate.v2-plan4-ACB.md` | — | not run | — | — |

Reference, development set (6 pilot questions, `E010-loop/SUMMARY.md`): v4 11%, v3 19%, both on 11-19, under g8.3.

Trap counts (FAIL / applicable): to be filled once gold trap items exist for the held-out questions.

## 2. Findings

None yet.

## 3. Decisions

| Date | Decision |
|---|---|
| 11-19 | T2 approved in E010: carry D v2, v3 and v4 to held-out questions; no F2 (`E010-loop/SUMMARY.md` §3). |

## 4. Open items

- **Write the 20 clear questions.** They should be disjoint from K1–K3 and P1–P6 in what they measure.
- **Team decision on the `near_original` questions.** TA01, TA11, TA18 and TA19: keep them or replace them.
- **Gold entries for every held-out question.**
  - Add the SQL readings and the PASS/FAIL trap items (plus `required_statement` for TI01–TI05) to `gold_readings.py`, starting from the `draft_` fields in `questions.json`.
  - Rebuild `gold_readings.json` and record the new hashes in `FROZEN.md`.
- **Smoke test.** v4 on TA01 and TI01, 1 repeat, before the full batch.
- **Number of repeats** for the full batch. E010 used 3 per question; 25 questions × 3 arms × 3 = 225 runs.
- **Same-question check.** Whether P1–P10 also run in T2 (they still need gold readings).
