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
| H6 harness not hermetic | first-step prompt tokens with identical `prompt.md`, model id, OpenCode 1.18.34, Python, step cap | F1 5,401; today 5,638 (+237); F2 8,579 (+3,178). OpenCode auto-loads `~/.claude/skills/*/SKILL.md` into the agent's skill list (`opencode debug skill`); `architecture-scout` was created 2026-11-07 03:23. With `OPENCODE_DISABLE_EXTERNAL_SKILLS=1` the first step is 5,400 (= F1). No run called the skill. F2's +3,178 is not explained by this skill (it predates it) and cannot be reconstructed now | **supported**: cross-day comparisons are confounded by context the harness does not control. Same-day arms share it, so today's comparisons stay valid. Hermetic baseline (`diagnosis/run_hermetic.py`, label `D-v2-kfree-hermetic`, first step 5,399–5,414 tokens = F1): silent-error **23/46 (50%)**, two passes 0.969; TR08 6/6, TR07 3/5, TR05 9/9. The skill description has **no measurable effect** (50% vs 51%), and F1's 33% does not reproduce under F1's context. F1 differs on the two disclosure items that flip between runs (TR08 1/6, TR07 0/5), and F2, the same prompt on the same day, gave 50%. F1 was most likely a favourable draw. Pooled same-day baseline: 45/89 (51%). Keep rule from here on: compare with the same-day baseline, not F1. Hermeticity fix for the harness (set `OPENCODE_DISABLE_EXTERNAL_SKILLS=1`, `OPENCODE_DISABLE_CLAUDE_CODE=1`, record first-step prompt tokens in meta) proposed, Bo to decide |

**Correction (2026-11-08, after H5):** E010-1 did not make things worse. Against the same-day baseline it is flat on silent-error (55% vs 51%), TR05 unchanged, TR08 3/5 vs 6/7, PERMILE 3/3 vs 1/4. The revert stands (the target did not move), but the reason is "no effect", not "harmful". The F1 baseline is not a valid comparator for runs made after 2026-11-07 (H6); every candidate is compared with the same-day baseline.

**Root cause (current reading):** a prompt problem, not a data, delivery or grader problem. The profile is descriptive context with no link to an action. Nothing in D v2 asks the agent to say which rows a framing does not use, and no output field holds that statement. On top of that, the profile substitutes for the agent's own data checks. The literature points the same way (research note): facts change behaviour when they are tied to an action, arrive at the point of action, or are checked by the harness.

**Candidates** (one change each against D v2; 18 runs; g8 two Luna passes; same keep rule; TR01 and TR07 are named by none of them and serve as untargeted controls):

| | Change | Question it answers |
|---|---|---|
| C1 `D-v2-cov` | `interpretation` must state rows not used (NULL in a needed value; years covered in part), share computed by code; self-review checks it | does an action-tied slot suffice? |
| C2 `D-v2-cov-profile` | C1 + profile | once there is a slot, does the profile add anything? (C2 vs C1; C2 vs E010-1 isolates the prompt) |
| C3 `D-v2-jit` | D v2 prompt; harness prints NULL / partial-period notes next to the agent's own DuckDB query output | does timing + column link suffice without a slot? |
| C4 `D-v2-cov-jit` | C1 + C3 | both |

### Candidate results C1–C4 (2026-11-08, same day as the baseline; 18 runs each; g8 two Luna passes)

Same environment for every arm (OpenCode loads the `architecture-scout` skill, H6), so the arms are comparable with each other and with the same-day baseline, not with F1. Agreement of the two Luna passes: baseline 0.984, E010-1 0.987, C1 0.965, C2 0.980, C3 0.988, C4 0.967 (longer interpretations, more judgement).

| item | baseline (D v2) | E010-1 profile | C1 cov | C2 cov+profile | C3 jit | C4 cov+jit |
|---|---|---|---|---|---|---|
| options | 43 | 38 | 41 | 38 | 42 | 44 |
| silent-error (g8 standard) | 22 (51%) | 21 (55%) | 33 (80%) | 26 (68%) | **19 (45%)** | 35 (80%) |
| sensitivity: traps + unsupported claim only | 21 (49%) | 19 (50%) | 12 (29%) | **9 (24%)** | 18 (43%) | 13 (30%) |
| options with unsourced numbers | 1 | 2 | 30 | 23 | 1 | 33 |
| TR05 (target) | 7/7 | 8/8 | 1/8 | 3/7 | 3/8 | **0/8** |
| TR08 (target) | 6/7 | 3/5 | 1/5 | 1/5 | 4/6 | 1/6 |
| TR07 | 4/5 | 3/4 | 1/6 | 0/4 | 3/6 | 3/5 |
| TR01 (control, named by no arm) | 4/4 | 4/4 | 7/7 | 4/4 | 3/3 | 6/6 |
| TR15 (control) | 4/4 | 3/3 | 3/4 | 3/4 | 3/3 | 3/3 |
| PERMILE | 1/4 | 3/3 | 3/4 | 2/3 | 0/3 | 0/5 |
| unsupported claim | 5 | 8 | 4 | 2 | 5 | 3 |
| NULL-inspecting queries per run | 0.7 | 0.1 | 3.4 | 2.3 | 1.6 | 3.6 |
| options stating rows left out | 2/43 | 2/38 | 41/41 | 38/38 | 5/42 | 44/44 |

**Reading.**
1. The action hook is the cause. The slot alone (C1, no profile) takes TR05 from 7/7 to 1/8 and TR08 from 6/7 to 1/5. The profile alone (E010-1) moves neither. Before today TR05 had failed on every option ever scored (D v1, F1, F2: 35/35 + 9/9; baseline 7/7).
2. Once the slot exists the profile adds nothing measurable: C2 vs C1, TR05 3/7 vs 1/8, traps + UC 24% vs 29%, within noise.
3. Just-in-time notes alone (C3, no prompt change) move TR05 to 3/8 and restore the agent's own NULL checks (1.6 per run). They are the only arm that lowers g8 silent-error, because they add no new numbers to the text. C3 passes are disclosures in the agent's own words ("borough-missing crashes are excluded"); r3 wrote "Brooklyn crashes with borough recorded" and failed (borderline, for review).
4. The effect is specific: the controls TR01 and TR15 do not move in any arm. Per-crash rates across 2020 (TR01) and small-number claims (TR15) need something else (the plan step, C5).
5. **Measurement conflict.** The slot makes the agent write coverage numbers (rows, NULL shares). The g8 provenance check only accepts numbers found in `values_<id>.csv`, so these numbers count as unsourced and drive g8 silent-error to 68–80%. They are true: A1 "659,713 of 2,132,218 rows with NULL borough (30.9%)" in C1 and C4 matches DuckDB exactly; C2's 136,969 / 6.04% / 49.73% / 55.62% match too. This is a gap in the standard (no source for coverage facts), not hallucination. Resolution is Bo's: let a check file be a source (C5 writes `out/check_<id>.csv`), and/or verify coverage numbers directly against the data.

### Profile completeness audit (asked by Bo, 2026-11-08)

Question: was the profile complete, or partial in a way that could mislead the agent? Checked with DuckDB on the same file.

The facts TR05 and TR08 need were all in the profile: borough NULL per year, 2026 partial by month, killed NULL 24.4% in 2026. So E010-1's TR05 result is not explained by missing content.

The profile is partial, though: it measures one kind of missing value (NULL). It omits the following.

| Not in the profile | Fact | Possible misreading |
|---|---|---|
| placeholder values | `contributing_factor_vehicle_1` "Unspecified" 33.3% (profile: NULL 0.4%); `vehicle_type_code1` UNKNOWN / OTHER variants ≈ 43k rows | column looks almost complete |
| heaping at defaults | `crash_time` = 00:00 on 1.08% of rows (≈ 16× a typical minute); 19% of times on the hour | "no NULL" suggests precise times (A2 night) |
| recoverability | 70.5% of NULL-borough rows have coordinates | only "30% NULL" is visible, so a handling option is missing |
| invalid values | 7,591 rows with a 0 coordinate | not flagged |
| internal consistency | 84 rows where persons killed ≠ pedestrians + cyclists + motorists killed | minor |

Consequence: C5's data check asks for missing *in any form* and for pile-ups, in general terms.

### Record for later optimisation (Bo's reading, with the same-day correction)

- **Holds:** a descriptive profile in context is not used by Luna without an explicit instruction tied to an action (TR05 8/8, no run mentions NULL borough). It also displaces the agent's own checks (NULL queries 0.7 → 0.1 per run). With an explicit action hook the profile is used (C2: TR05 3/7), but it adds nothing over the hook alone (C1: 1/8).
- **Does not hold:** "the profile made results worse". Against the same-day baseline, silent-error is flat (55% vs 51%). The gap to F1 (33%) comes from the date and the harness context (H5, H6), not from the profile.

### C5 = E010-v3 (Bo's design, 2026-11-08)

Plan → Data check → Final plan per framing. Boundaries and the leak found on the first run: `C5-design.md`. Running: label `D-v2-plan-kfree-openai-gpt-6-luna`, `PILOT_STEPS=50`, same environment as C1–C4.

### C5 results (2026-11-08; 18 runs, `PILOT_STEPS=50`, same environment as C1–C4; g8 two Luna passes, agreement 0.974)

| item | baseline | hermetic baseline | C1 cov | C3 jit | C4 cov+jit | **C5 plan** |
|---|---|---|---|---|---|---|
| silent-error (g8 standard) | 51% | 50% | 80% | 45% | 80% | 74% |
| sensitivity A: traps + UC only | 49% | 50% | 29% | 43% | 30% | **28%** |
| sensitivity B: provenance also accepts `check_<id>.csv` | 51% | 50% | 80% | 45% | 80% | **41%** |
| TR05 / TR08 / TR07 | 7/7, 6/7, 4/5 | 9/9, 6/6, 3/5 | 1/8, 1/5, 1/6 | 3/8, 4/6, 3/6 | 0/8, 1/6, 3/5 | 2/6, **0/5, 0/5** |
| unsupported claim / PERMILE | 5, 1/4 | 5, 1/5 | 4, 3/4 | 5, 0/3 | 3, 0/5 | **1, 0/5** |
| TR01 / TR15 (controls) | 4/4, 4/4 | 5/5, 3/4 | 7/7, 3/4 | 3/3, 3/3 | 6/6, 3/3 | 5/5, 2/3 |
| NIGHTDEF | 0/9 | 0/8 | 0/7 | 3/9 | 0/9 | 3/7 |
| steps median / secs median | 13 / 80 | — | 17 / 115 | 15 / 83 | 16 / 114 | 21.5 / 149 |

Process (`diagnosis/c5_process.py`):
- plan and check files exist for 39/39 options;
- the first data query came after the first plan in 18/18 runs;
- outcome-blind rule broken in substance in about half the runs: 136 check rows in 7 runs count rows by an outcome value (zeros or "impossible" values of injured / killed columns), plus the same pattern in queries on A1-r2 and K1-r2. Two other detector hits are false positives (a `>= 0` validity filter; a metric definition in plan text).

**Reading.**
- C5 gives the best disclosure profile: TR08 0/5, TR07 0/5 (the declared population "recorded deaths in police-reported crashes" carries the qualification), UC 1/39, PERMILE 0/5.
- Once its check file counts as a source, C5 is the only plan-type arm below the baseline (41% vs 51%). With the check file, 7/39 options still carry unsourced numbers; all are true coverage facts written outside that option's check file (citywide 2,132,218; 2012 / 2026 row counts).
- What it does not fix:
  - **TR01**: agents see and mention the 2020 fall in records, but the standard asks for the cause ("fewer minor crashes reported"), which is neither in the data nor in the dictionary. No data check can supply it. This is a standard question for Bo.
  - **NIGHTDEF 3/7**: the "main limitation in the chart subtitle" instruction moved the night definition into the chart only; decision 7 does not count chart-only text.
  - **Leak path**: missing-or-impossible / pile-up checks applied to outcome columns.

**Proposed C5 v2 changes (Bo to review):**
1. outcome columns: check missing only, never count rows by an outcome value;
2. the final plan's definitions (e.g. which hours count as night) are written in the interpretation as well as on the chart;
3. no other change.

**Proposed decisions (Bo):**
- (a) g8.1: `check_<id>.csv` is a provenance source, and its facts are recomputed from the data by a machine check;
- (b) TR01 standard: pass when the option discloses the visible 2020 fall in recorded crashes and its effect on per-crash rates, or add the recording change to the dictionary;
- (c) harness hermeticity flags.


### Drift track update (2026-11-13)

*Update 2026-11-13 (Bo, relayed from his branch session):* a teammate is trial-running the embedding method in the evaluation layer on the F3 results (round-trip distance). F3's reverse inference was made from the chart, and P13 found that chart titles leak the question, so F3 is the **leaky** condition, not §4's cleared-context `values.csv`-only condition. Distances from it are optimistic: good for getting the method working, not a result. The formal round-trip distance ratio waits for the `values.csv`-only reverse-inference runner. Probe conclusion unchanged (`experiments/E010-loop/probe/README.md`): embedding is for coarse drift and plainly off-topic options only; mpnet and MiniLM both reported; whether an option answers a different question is the judge's call.
