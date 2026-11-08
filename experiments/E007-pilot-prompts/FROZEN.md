# Frozen prompts and configs (2026-10-16)

Frozen after pilot iteration 3 (protocol limit: 3 iterations). No edits from here on; a change needs a new protocol version and a re-run of every arm that uses it. Every formal run records these hashes in `meta.json` (`env.prompt_sha`, `env.config_sha`, 16-character prefixes).

| Prompt | SHA-256 |
|---|---|
| `A.v1.md` | `5ea316c0265121d0278a9ef4c09d182c13c010a1d4afb19b35973cd81756c935` |
| `B_critique.v4.md` | `f8bfefe032067c9d89463f90a7349c9b0afb29521daedae4e06c2592de17d038` |
| `C_selfcheck.v3.md` | `96250d0fc29b340f4b69992275499071ca39f4aae89472be29bec10664824cf9` |
| `B_revise.v3.md` | `38af1935bf2f386e79331ab7880d4391aebad6d95257bdbac07aa31e5da4f919` |

| Config | SHA-256 |
|---|---|
| `config/opencode.analysis.json` | `51a2bdaf303e06c45af1bba6a8dca5eb749a633c5ddcec211b0b8c2f888aef75` |
| `config/opencode.review.json` | `beba3f25da37e6afffc3817718a20a99124725c85dc96f9bd591179d44792814` |

- A: `A.v1.md` (frozen since 2026-10-14, never edited).
- B: review `B_critique.v4.md`, revise `B_revise.v3.md`, run as `run_pilot.py B v4 v3 <A_label>`.
- C: `C_selfcheck.v3.md`, fixed 2026-10-19 after one format check on mimo (see ITERATIONS.md); not tuned. SHA-256 `96250d0fc29b340f4b69992275499071ca39f4aae89472be29bec10664824cf9`.
- Harness at freeze: sandbox v2, review in its own folder, review timeout 420 s, other runs 600 s, 15 steps per run, zero-output timeout retried once, B end states `B_STATES`.

Iteration 3 total model time on 5 runnable items: 13.8 min.

## Phase 2 prompts (arm D)

| Prompt | SHA-256 | Frozen |
|---|---|---|
| `D_enumerate.v1.md` | `a18643123c55bfd00cabea8dcbb4f806463a50d79723d3e5e42ef355e3b14e19` | 2026-10-20 (k = 3, cap 25; baseline for every D comparison) |
| `D_enumerate.v2.md` | `bde1fd02f5b3e576618cf5f2429d6e9d31904328a8c3dfce675a3c753b598d0a` | 2026-11-04 (free k, `interpretation` = which part of the asked question the option answers and why; confirmed by Bo from `D_enumerate.v2.draft.md`; run as `PILOT_K=0 run_pilot.py D v2`) |

## Harness for arm D from E009-F3 on (frozen 2026-11-06, Bo)

| File | SHA-256 |
|---|---|
| `experiments/E007-pilot-prompts/run_pilot.py` | `edd5532fd8eb4ef34965a4128edab4113b06da3e94a6ce2d84669c0a8cbc7479` |
| `experiments/E006-mimo-screen/run_screen.py` | `7616f48b5d3be9db98bbabe9142afc69fbabd36da602658f74c65d3c1845d118` |

Change from the F1/F2 harness: `run_enumerate` passes `done=enumerate_done` to `call_model`. When `out/options.json` parses and the final step wrote `ANSWER:` without a tool call, the harness ends an OpenCode process that does not exit: 10 s after a `step_finish` with reason `stop`, or 120 s after the stream ends on the ANSWER text. Such a run is `answered_no_exit = true`, `timed_out = false`, and counts as `call_ok`. Every other arm calls `call_model` without `done` and is unchanged. Checked on all 73 stored D runs: the 67 normal completions give `stop`; the 3 F2 runs that answered and then hung give `stop` / `text`; the 2 timeouts without a final answer and the stopped attempt give none. A fake-OpenCode test covers the kill path (stop 6 s, text 10 s with a test grace of 8 s, no answer: timeout). Teammates check these hashes before an F3 run.

## Harness for E010 (frozen 2026-11-08, Bo passed gate G1)

| File | SHA-256 |
|---|---|
| `experiments/E007-pilot-prompts/run_pilot.py` | `9b9f9458adf42540681e0af555209374779867960da05aea1573b858bb8cf34b` |
| `experiments/E006-mimo-screen/run_screen.py` | `7616f48b5d3be9db98bbabe9142afc69fbabd36da602658f74c65d3c1845d118` (unchanged) |
| `experiments/E010-loop/profile.md` | `0596d2a7bf974a11b55abe1057896bddcb15ec12edc012e2e2c96c1a2c52ef90` |

Change from the E009-F3 harness: `POPPY_PROFILE=<repo-relative path>` makes arm D append that file to the data dictionary (dictionary + blank line + profile), adds `-profile` to the label, and records `profile` (`file`, `sha` prefix) and `rendered_prompt_sha` in `meta.json`. Unset, nothing changes: the prompts rendered for K1, K2, K3, A1, A2, I1 are byte-identical to the stored F1 `prompt.md` files (6/6); set, removing the profile block gives the F1 prompt back (6/6). The D v2 prompt file is unchanged (`bde1fd02f5b3e576`). Run E010-1 as `POPPY_EXP=E010-loop POPPY_PROFILE=experiments/E010-loop/profile.md PILOT_K=0 PILOT_STEPS=35 run_pilot.py D v2 3`.

## E010 diagnostic candidates (2026-11-08; written by Claude with Bo's go-ahead of 2026-11-08 to create one E010 prompt per candidate experiment; Bo reviews a candidate before it becomes an E010 iteration)

| Prompt | SHA-256 | Change from D v2 |
|---|---|---|
| `D_enumerate.v2-cov.md` | `c4c3d343c9a2c28367473d4ae326b126c64ae268a53eb21ffb4360d7af30cc11` | `interpretation` must also state which rows the framing does not use (NULL in a value its filters, groups or sums need; years the file covers only in part), with the share computed by its code; the self-review checks that statement against the code. The statement sits in a field the g8 grader already reads, so neither the harness nor the grader changes. |

Candidate C3 (just-in-time data notes, harness side; same G1 rule as the profile: column facts only, every column by one rule, no advice, no outcome aggregates):

| File | SHA-256 |
|---|---|
| `experiments/E007-pilot-prompts/run_pilot.py` | `4b45c5f5c67352ba56e592cdf0f844736ec2da012b2da8695ce2bd7fd2af9ee1` (adds `POPPY_JIT=1`; unset path re-checked: 6/6 prompts byte-identical to F1) |
| `experiments/E010-loop/jit/sitecustomize.py` | `9732ae740dc1588e0e5f7b3f6785db6308597282e563b6007ef3cb32403af4af` |
| `experiments/E010-loop/jit/facts.json` | `295ccc418ca811098dd2bff8a6fa3406792109526f6881949c483779a04d8321` (from `make_facts.py`) |

`POPPY_JIT=1` copies both files into `<sandbox>/.jit` and sets `PYTHONPATH` to it for that run only (concurrency 1). The agent's DuckDB queries on the crash file then print, once per process, to stderr: the NULL share (file and per-year range) of each column the query filters, groups or aggregates, and a note when the query has no date bound that leaves out 2012 or 2026. Queries and results are unchanged. Checked inside the real sandbox shim: note printed, repository reads still denied. Label suffix `-jit`; `meta.jit` records both hashes and the number of notes in the trace.

Candidate C5 = Bo's E010-v3 design (2026-11-08): per framing Plan → Data check → Final plan between choosing framings and writing analysis code.

| Prompt | SHA-256 | Change from D v2 |
|---|---|---|
| `D_enumerate.v2-plan.md` | `2b0aa0ecdebd5ae3b2e167fd1ad89a79971562f373efbdfe0b9ad7f2659ce32a` | Plan to `out/plan_<id>.json` without querying data; Data check by code on the planned columns and years only (rows, rows per year, missing in any form, default pile-ups, partial years) to `out/check_<id>.csv` (fact, value), with consequence and decision (keep and disclose / exclude / own group) and plan changes with reasons; Final plan with limitations from the check. No outcome numbers in the three steps. Analysis, chart title (metric and population) and subtitle (main limitation), options fields and self-review follow the final plan; the data-check conclusion is written in `interpretation`. Run with `PILOT_STEPS=50` (more steps; the other arms never exceeded 24). |
