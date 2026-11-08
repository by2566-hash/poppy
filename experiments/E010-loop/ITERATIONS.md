# E010 iterations (docs/v2-design-2026-11-07.md §3, §6)

## E010-1 data profile (2026-11-08)

**Setup.** G1 passed (Bo, 2026-11-08). D v2 prompt unchanged (`bde1fd02f5b3e576`); harness `run_pilot.py` `9b9f9458adf42540` with `POPPY_PROFILE=experiments/E010-loop/profile.md` (profile `0596d2a7bf974a11`, appended after the data dictionary); hashes in `E007-pilot-prompts/FROZEN.md`, section "Harness for E010". `POPPY_MODEL=openai/gpt-6-luna`, `PILOT_K=0`, `PILOT_STEPS=35`, concurrency 1, git `8ca5667`, team venv. Pilot questions K1, K2, K3, A1, A2, I1, original phrasings, 3 repeats each. Command:

`POPPY_EXP=E010-loop POPPY_PROFILE=experiments/E010-loop/profile.md PILOT_K=0 PILOT_STEPS=35 run_pilot.py D v2 3`

Results `results/D-v2-kfree-profile-openai-gpt-6-luna/` (18 runs, 38 options), summary `runs/D-v2-kfree-profile-openai-gpt-6-luna.json`. All 18 runs complete; no timeouts, no `answered_no_exit`; median 70 s and 14 steps (F1: 76 s, 14 steps).

**Scoring.** Grader g8, two Luna passes (`--grader2 openai/gpt-6-luna`, repeat stability, not independence): 448 shared cells, 6 disagreements (agreement 0.987), 0 unparsed. `review.csv`: 6 disagreement cells + 5 audit rows, not yet reviewed. No `h_*` columns filled. 9 options have `gold_match` other than `match` and are not yet re-derived (does not enter silent-error unless a re-derivation finds a wrong number).

**Result vs F1 baseline** (`E009-enumerate/results/D-v2-kfree-openai-gpt-6-luna`, g8, human overrides applied):

| | F1 (42 options) | E010-1 pass 1 (38) | E010-1 pass 2 (38) |
|---|---|---|---|
| silent-error options | 14 (33%) | 21 (55%) | 20 (53%) |
| TR05 (A1) | 9/9 | 8/8 | |
| TR01 | 5/5 | 4/4 | |
| TR08 (A2) | 1/6 | 3/5 | |
| TR07 (K1) | 0/5 | 3/4 | |
| TR15 | 3/3 | 3/3 | |
| PERMILE (I1) | 1/3 | 3/3 | |
| unsupported_claim | 2/42 | 8/38 | |

Per question, silent-error (pass 1): K1 0/5 → 3/4, K2 0/7 → 1/6, K3 0/7 → 0/6, A1 9/9 → 8/8, A2 2/7 → 6/8, I1 3/7 → 3/6. Six questions × 3 runs: screening only (MDE about 48 points); F1 and F2 with the same prompt already differ by 17 points (33% vs 50%).

**What happened (read from the runs, not from the grader):**
- A1 / TR05: none of the 3 runs mentions NULL borough anywhere (options, reply, tool calls); every option filters `borough='BROOKLYN'` as in F1. The profile states the NULL share per year; the agent did not connect it to its filter.
- A2 / TR08: both F1 and E010-1 use the whole file (the question gives no years). F1 filtered NULL killed counts in 2 of 3 runs (counted as handling, decision 2); E010-1 in 0 of 3. The profile's 24.4% NULL killed in 2026 was not acted on.
- K1 / TR07: same 2013–2025 window as F1; failures are wording ("Pedestrian deaths by year were 176 (2013)…", no "reported"). This item moves with wording without any change (F1 0/5, F2 9/10).
- I1: "this crash-based proxy did not decline" (decision 6), the F2 failure pattern; PERMILE and unsupported_claim fail together on the same 3 options.
- A1-r2 includes 2026 (`BETWEEN 2013 AND 2026`) although the profile lists 2026 as partial by month.

**Keep rule** (design §3: the targeted failure count falls and no other criterion rises): TR05, TR01 and TR08 did not fall; TR07, PERMILE and unsupported_claim rose. By the rule: **revert** (the profile is not carried into E010-2). Waiting for Bo's decision.
