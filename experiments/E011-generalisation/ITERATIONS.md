# E011 iterations (T2: E010-v4 on held-out questions)

## 2026-11-19: question set drafted

**Goal.** Test E010-v4 on questions it was not designed on. All E010 changes were designed on the 6 pilot questions (K1–K3, A1, A2, I1), so their result is a development-set result (`E010-loop/ITERATIONS.md`, 11-19 T1, "Limits").

**Starting state (repo at `6cc6bd1`):**
- E010-v4 = `D_enumerate.v2-plan4-ACB.md` is locked and frozen. Its SHA-256 `80677c78…` matches `FROZEN.md`.
- The scorer `scripts/score_runs.py` is g8.3 (`GRADER_VERSION = "g8.3"`). Its SHA-256 `97503507…` matches `FROZEN.md`.

**Question set (`questions.json`, version `generalisation-v1`):**
- **20 ambiguous (TA01–TA20).**
  - Subjects: cyclists in Queens; weekends vs weekdays; speeding; distraction; SUVs vs cars; the Bronx vs Manhattan for drivers; rush hour; summer; multi-vehicle crashes; motorcycles; Staten Island; severity over time; ZIP codes; trucks; late-night weekend pedestrians; alcohol; end-of-year holidays; deadliness in Manhattan; failure to yield; Manhattan streets.
  - Each has draft readings and the trap ids that are likely to apply (`docs/scenario-data-v1.md` §3).
- **5 insufficient (TI01–TI05).** Each lacks a different input:
  - TI01, taxi vs private car per trip: no trip counts.
  - TI02, borough crash rate per resident: no population.
  - TI03, rain and crash risk: no weather data and no traffic volume.
  - TI04, lives saved by Vision Zero: needs a counterfactual.
  - TI05, congestion pricing and crash risk per vehicle: no traffic volume, and a before/after difference is not a cause.

**Checks:**
1. **Wording.** Compared with all 37 original question texts: pilot (6), E006 P1–P10 (10), E002 Q01–Q08 (8), E009 rephrasings (12) and one string from the E003/E004 scripts. There is no exact match, and the highest similarity ratio is 0.74. Every high ratio comes from the shared endings ("Make a chart for a local news story…", "…based on this crash data").
2. **Subject (read by hand).** Four ambiguous questions are close to an original and are marked `near_original`:
   - TA01 ~ A1 / Q02;
   - TA11 ~ Q03, inverted;
   - TA18 ~ A1;
   - TA19 ~ Q07 / P5.
3. **Type labels.** The labels match the repo's values (`ambiguous`, `insufficient`).
4. **Insufficient standard.** The insufficient questions match the grader rule in `score_runs.py`: the data cannot answer the question as asked; the output states that and shows a supported measure. They also match the I1 gold structure (`required_statement` + traps).
   - First draft: two questions failed this check, because the data holds nothing the answer could show. One asked about driver age and sex, which are not in the crash table. The other asked about the share of crashes never reported, which cannot be in the data by definition.
   - Both were replaced by TI02 and TI05.
   - TI03 is borderline: the nearest supported measure is the "Pavement Slippery" factor, which is not weather.
5. **Loader.** `run_pilot.py`'s question loader accepts the file when `POPPY_QSET` is set to its path (25 questions, every entry has `base`). No harness change is needed.

**Not yet done:**
- No runs.
- No gold readings or trap items in `gold_readings.json`, so g8.3 cannot score these questions yet.
- The 20 clear questions are not written.

**Next:**
- Write the clear questions.
- Bo decides on the `near_original` questions and approves the gold entries.
- Smoke test: v4 on TA01 and TI01, 1 repeat.

## 2026-11-19: TA01 r1 smoke run (v4), re-run once

Label `D-v2-plan4-ACB-kfree-openai-gpt-6-luna-1119`; GPT-6 Luna, `PILOT_K=0`, `PILOT_STEPS=50`, concurrency 1, team venv; prompt SHA-256 `80677c78…` (matches `FROZEN.md`).

**Pre-check.** `POPPY_MODEL=openai/gpt-6-luna check_env.py` had one FAIL, "openai/gpt-6-luna NOT listed by opencode". It comes from this machine's broken global OpenCode database (`opencode models` fails with "Database is not empty and has no session table"). The harness does not use that database (`run_screen.py` sets `XDG_DATA_HOME` to a fresh folder per run). With a fresh data folder, `opencode models` returns 0 and lists `openai/gpt-6-luna`. The only WARN was the documented raw-CSV checksum.

**First attempt.** Timed out at 601.4 s after 18 steps (22 tool calls, 371,681 tokens), with no provider error (`errors: []`, `rate_limited: false`). It had written 2 complete options (annual cyclist injury and death counts; share of Queens crash rows with a cyclist casualty) but had not exited, so `complete: false`. Kept in `results/<label>/_void/TA01-r1-timeout-601s/` and `runs/_void/<label>-TA01-timeout-601s.json` (repo precedent: `E007-pilot-prompts/PROTOCOL.md`).

**Re-run (once, identical settings).** Timed out again, at 601.3 s after 20 steps (22 tool calls, 233,838 tokens), with no provider error. It wrote `plan_1.json`, `plan_2.json`, `check_1.csv` and `check_2.csv` (same two framings as the first attempt), but no `options.json`, values files or charts, so `n_options: 0`, `complete: false`. No network calls (`net_calls: 0`) and no paths outside the sandbox in `events.jsonl`. Not retried further.

**Reading.** Both attempts hit the 600 s per-run time limit well before the 50-step limit. On TA01, v4 does not finish within the harness time limit. Not scored (no gold entry for TA01).
