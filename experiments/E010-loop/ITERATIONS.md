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

**Keep rule** (design §3: the targeted failure count falls and no other criterion rises): TR05, TR01 and TR08 did not fall; TR07, PERMILE and unsupported_claim rose. By the rule: **revert** (the profile is not carried into E010-2).

**Decision (Bo, 2026-11-08): recorded and reverted.** The D v2 prompt without the profile stays the base. The `POPPY_PROFILE` hook stays in the harness (unset = F1 prompts byte-identical) so diagnostic candidates can use it. Root-cause analysis and candidate experiments: section "E010-1 diagnosis" below.

## E010-1 diagnosis (2026-11-08, Claude; asked by Bo: profile wrong, not read, misread, prompt, or grader?)

Scripts: `diagnosis/trace_stats.py` (per-run behaviour from the event traces), `diagnosis/compare.py` (one table across labels). Research: `diagnosis/research-2026-11-08.md`.

| Hypothesis | Test | Result | Verdict |
|---|---|---|---|
| H1 profile wrong | NULL shares recomputed with a different query (`avg((col is null)::int)` by year) | borough 22.8–38.1% and killed 24.4% in 2026: identical to `profile.md` | rejected |
| H2 profile not delivered / not read | first-step prompt tokens; `prompt.md` of every run | +2,901 tokens on every run (5,401 → 8,302); profile present in all 18 prompts | rejected (delivered; whether it was *attended to* is not observable, reasoning is hidden) |
| H3 read but not acted on (prompt has no action hook) | trace behaviour | 0 of 18 runs mention NULL borough anywhere; 2 of 38 options state any rows left out; A1-r2 includes partial 2026 | **supported** |
| H3b profile replaces the agent's own checks | NULL-inspecting queries per run; exploration queries before the first chart | 1.0 → 0.1 per run (A2 3.3 → 0); 2.7 → 1.8 | **supported** (A2 lost the `IS NOT NULL` filtering F1 did in 2 of 3 runs) |
| H3c knowing–doing gap exists without the profile | F1 traces | F1 A1-r3 grouped by borough with NULLs visible and A1-r2 checked NULLs; TR05 still 9/9 | **supported**: discovery does not lead to disclosure |
| H4 grader artefact | two Luna passes; K1 TR07 cells read by hand; TR05 cells vs code | agreement 0.987; K1 FAILs follow decision 7 (E010 metric fields say "Annual sum of number_of_pedestrians_killed", F1's say "in reported motor vehicle crashes"); TR05 FAILs match `borough='BROOKLYN'` in code with no disclosure anywhere | rejected (grader consistent with the standard) |
| H4b profile primes column-name wording (TR07) | share of options with "reported / recorded / in this data" | 32/42 (76%) vs 28/38 (74%) | rejected: K1 TR07 is wording noise (F1 0/5, F2 9/10, E010-1 3/4) |
| H5 run-to-run / day-to-day noise | fresh D v2 baseline, same day, 18 runs (`results/D-v2-kfree-openai-gpt-6-luna`, g8 two passes, agreement 0.984) | silent-error **22/43 (51%)** vs E010-1 21/38 (55%) vs F1 14/42 (33%); F2 (same prompt, other phrasings) 50%. TR08 6/7, TR07 4/5, TR05 7/7 | **supported**: most of E010-1's "worsening" vs F1 is not the profile. Against the same-day baseline the profile has no effect on silent-error; TR05 unchanged; NULL queries 0.7 → 0.1 per run still holds |
| H6 harness not hermetic | first-step prompt tokens with identical `prompt.md`, model id, OpenCode 1.18.34, Python, step cap | F1 5,401; today 5,638 (+237); F2 8,579 (+3,178). OpenCode auto-loads `~/.claude/skills/*/SKILL.md` into the agent's skill list (`opencode debug skill`); `architecture-scout` was created 2026-11-07 03:23. With `OPENCODE_DISABLE_EXTERNAL_SKILLS=1` the first step is 5,400 (= F1). No run called the skill. F2's +3,178 is not explained by this skill (it predates it) and cannot be reconstructed now | **supported**: cross-day comparisons are confounded by context the harness does not control. Same-day arms share it, so today's comparisons stay valid. Hermetic baseline (`diagnosis/run_hermetic.py`, label `D-v2-kfree-hermetic`) running to test whether F1's 33% reproduces |

**Correction (2026-11-08, after H5):** E010-1 did not make things worse. Against the same-day baseline it is flat on silent-error (55% vs 51%), TR05 unchanged, TR08 3/5 vs 6/7, PERMILE 3/3 vs 1/4. The revert stands (the target did not move), but the reason is "no effect", not "harmful". The F1 baseline is not a valid comparator for runs made after 2026-11-07 (H6); every candidate is compared with the same-day baseline.

**Root cause (current reading):** a prompt problem, not a data, delivery or grader problem. The profile is descriptive context with no link to an action. Nothing in D v2 asks the agent to say which rows a framing does not use, and no output field holds that statement. On top of that, the profile substitutes for the agent's own data checks. The literature points the same way (research note): facts change behaviour when they are tied to an action, arrive at the point of action, or are checked by the harness.

**Candidates** (one change each against D v2; 18 runs; g8 two Luna passes; same keep rule; TR01 and TR07 are named by none of them and serve as untargeted controls):

| | Change | Question it answers |
|---|---|---|
| C1 `D-v2-cov` | `interpretation` must state rows not used (NULL in a needed value; years covered in part), share computed by code; self-review checks it | does an action-tied slot suffice? |
| C2 `D-v2-cov-profile` | C1 + profile | once there is a slot, does the profile add anything? (C2 vs C1; C2 vs E010-1 isolates the prompt) |
| C3 `D-v2-jit` | D v2 prompt; harness prints NULL / partial-period notes next to the agent's own DuckDB query output | does timing + column link suffice without a slot? |
| C4 `D-v2-cov-jit` | C1 + C3 | both |
