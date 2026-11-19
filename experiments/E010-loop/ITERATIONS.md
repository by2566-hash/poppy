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

## 2026-11-13: g8.1 rescoring, hermetic harness, C5 v2 vs same-day baseline

Bo accepted all four proposals on 2026-11-13: g8.1, TR01 wording, C5 v2, hermetic harness (FROZEN.md, `a5a8ff2`).
- All 8 labels from 11-08 were rescored with g8.1, two Luna passes each; agreement 0.971–0.986. Only the A1 / I1 units were re-graded; the others reuse g8 verdicts on byte-identical prompts.
- Today's runs are hermetic. First-step prompt tokens: baseline 5,400–5,415 (= F1), C5 v2 5,924–5,939 (constant).

| item (g8.1) | **baseline 11-13** | **C5 v2 11-13** | baseline 11-08 | hermetic 11-08 | C1 cov | C3 jit | C4 cov+jit | C5 |
|---|---|---|---|---|---|---|---|---|
| options | 43 | 37 | 43 | 46 | 41 | 42 | 44 | 39 |
| silent-error (g8.1) | **42%** | **41%** | 51% | 50% | 80% | 48% | 80% | 44% |
| traps + UC only | 42% | **22%** | 49% | 50% | 32% | 45% | 32% | 31% |
| unsourced (options) | 0 | 8 | 1 | 1 | 30 | 1 | 33 | 7 |
| TR05 / TR08 / TR07 | 9/9, 3/7, 3/5 | **2/7, 0/7, 0/3** | 7/7, 6/7, 4/5 | 9/9, 6/6, 3/5 | 2/8, 1/5, 1/6 | 4/8, 4/6, 3/6 | 0/8, 1/6, 3/5 | 2/6, 0/5, 0/5 |
| TR01 / TR15 | 5/5, 3/3 | 4/4, 3/3 | 4/4, 3/3 | 5/5, 3/4 | 7/7, 3/4 | 3/3, 3/3 | 7/7, 3/3 | 5/5, 2/3 |
| PERMILE / UC | 1/3, 4 | 3/4, 5 | 1/4, 5 | 0/5, 4 | 2/4, 3 | 0/3, 5 | 0/5, 3 | 1/5, 2 |
| NIGHTDEF | 0/10 | **0/7** | 0/9 | 0/8 | 0/7 | 3/9 | 0/9 | 3/7 |

**C5 v2 fixes.** The leak is closed: 0 check rows count by an outcome value (C5: 136). NIGHTDEF falls from 3/7 to 0/7.

**Day-to-day noise.** The same D v2 prompt gave 51% (11-08), 50% (11-08 hermetic) and 42% (11-13); the pooled baseline is 59/132 (45%). This is why the keep rule uses the same-day baseline.

**What is left in C5 v2, read by hand:**
- 7 of its 8 unsourced options are machine false positives: "31" (days in a month, K2 / K3 / I1) and "1,000" (the unit in "per 1,000"). These are not data claims. K2's 5/6 silent-error comes entirely from "31". Without them, silent-error would be 22%. This is a provenance-rule question for Bo; the scorer was not changed.
- 2 of its 5 unsupported-claim FAILs are grader errors. A1-r2 o2 and I1-r3 o3 say "0 missing death values in the selected population"; that population is 2013–2025, and the 2026 NULLs lie outside it, so the statement is true. These are for human review.
- Real residuals sit on I1 only: "this per-crash proxy did not decline" (decision 6; PERMILE 3/4), and TR01 4/4. Even under g8.1, the per-crash options do not mention the 2020 fall.

**Keep rule, by the letter.**
- The targets fall: TR05 9/9 → 2/7, TR08 3/7 → 0/7, TR07 3/5 → 0/3.
- Some other criteria rise: PERMILE 1/3 → 3/4, unsupported claim 4 → 5, unsourced 0 → 8.
- So C5 v2 is **not kept as written**.
- Read by hand, the unsourced and UC rises are machine or grader false positives, and the real cost is I1 PERMILE, about +2 options at n = 3–4.
- Decision is Bo's: (a) keep C5 v2 as E010-v3, with I1 as the next target; or (b) first settle the "31" / unit-number provenance rule and the 2 UC review cells, then apply the rule.

## 2026-11-19: Bo chose (a) — C5 v2 is E010-v3; E010-v4 targets I1

Decision (Bo): C5 v2 becomes the base (E010-v3).
- This is an exception to the letter of the keep rule. The rises in UC and unsourced numbers are machine and grader false positives (SUMMARY M7, M8); the real cost is I1.
- One-page record of everything since 11-08: `SUMMARY.md`.

**E010-v4 candidate** (`D_enumerate.v2-plan3.md`, hash in FROZEN.md). The final plan binds the conclusion:
- if the plan says the data cannot fully answer the question, the answer may not state a direction for the asked quantity (targets I1 PERMILE and the decision-6 failures);
- if the denominator is a row count, the change in rows per year must be stated together with its effect on cross-year comparison (targets TR01, the control that no earlier arm moved).

**Run.** Paired, same day, hermetic: C5 v2 re-run (base) vs E010-v4, 18 runs each, label tag `1119`, g8.1 two Luna passes.
**Keep rule.** PERMILE and TR01 fall on I1, and no other criterion rises against the same-day C5 v2. The M7 / M8 false positives are reported separately.

## 2026-11-19: g8.2 — calendar and unit numbers are not unsourced (Bo)

Decision (Bo): "日历和单位数字不算无出处" (closes SUMMARY M7). SCORING §4 decision (10); scorer **g8.2** (hash in FROZEN.md; first committed as "m2", renamed g8.2 the same day so all arms sit on one named instrument). The rendered grader prompt is byte-identical to g8.1, so no verdict was re-graded; only the machine columns were recomputed (`--no-grader`) for all 10 arms. Rate scales also cover "times / × 100"; no arm changed from that.

**Rule (read from context, not from the value).** Exempt: a day in a written date ("December 31", "2025-12-31"); a length in calendar units ("13 years", "365 days", "14-hour window", "182 of 366 calendar days"); the scale of a rate ("per / by / to 1,000"). Days / weeks / months count only as a calendar length (7, 28–31, 365/366, 52/53, 12) or with "calendar / complete / full / whole". Still checked: "9,700 rows", "1,000 crashes had a death", "crashes on 182 days", "365 deaths", "5.0-percentage-point". Every exempt number is listed per option in `exempt_numbers` for audit.

**Audit before the change.** All 221 unsourced entries across the 10 E010 arms were listed, and every value that could be calendar or unit was read in context. Those were dates (31: 17 entries), calendar lengths (13, 14, 182 / 366, 203 / 365) and rate scales (1,000, 10,000). After the change 106 numbers are exempt across the 10 arms (31 date ×52, 13 years ×31, 365 / 366 ×12, 182 / 203 ×6, 14-hour ×2, rate scales ×3); most of them had been matched to a value by coincidence before and so were never flagged. Data numbers among them (9,700, 42, 36, 29, 24, 5.0, 5.06) stay unsourced.

**Re-score (machine columns only; grader columns identical before and after).**

| Arm | unsourced options | silent-error g8.1 → g8.2 |
|---|---|---|
| baseline 11-08 | 1 → 0 | 51% → **49%** |
| hermetic 11-08 | 1 → 1 | 50% → 50% |
| E010-1 profile | 2 → 0 | 55% → **50%** |
| C1 cov | 30 → 29 | 80% → 78% |
| C2 cov + profile | 23 → 23 | 71% → 71% |
| C3 jit | 1 → 1 | 48% → 48% |
| C4 cov + jit | 33 → 33 | 80% → 80% |
| C5 plan | 7 → 5 | 44% → **38%** |
| baseline 11-13 | 0 → 0 | 42% → 42% |
| **C5 v2 11-13** | **8 → 0** | **41% → 22%** |

Consequence for decision (a): C5 v2 against its same-day baseline is now 22% vs 42% on silent-error with no provenance cost, so it passes the keep rule on silent-error, all targeted traps and NIGHTDEF. The only remaining exception is `unsupported_claim` 5/37 vs 4/43, of which 2 are the grader errors in M8 (human review still open). C1 / C2 / C4 stay high because their unsourced numbers are real coverage counts typed without a check file (the reason decision 9 exists), not calendar or unit numbers.

The 1119 pair (C5 v2 vs E010-v4) is scored with g8.2 from the start; the M7 cases are no longer excluded by hand.

### E010-v4: attribution and keep rule (tightened 11-19, review from Bo's other session)

- v4 bundles **two** changes (direction ban when the plan says the data answers only partly → PERMILE; rows-per-year disclosure for row-count denominators → TR01). A result on v4 alone cannot say which change did what.
- **Keep v4 only if both targets fall** (I1 PERMILE and TR01) **and no other criterion rises** against the same-day C5 v2, judged on g8.2 (no hand exclusions). M8 (2 UC grader errors) is still reported separately until the human review is done.
- **If the result is mixed** (one target falls, the other does not, or something else rises): do not keep; split into two single-change arms (v4a direction ban, v4b rows-per-year) next round.
- Infrastructure: 5 runs ended on OpenAI 503 "overloaded" (v3: A2-r3, I1-r1; v4: A2-r3, I1-r2, I1-r3). Rule: a run ending incomplete on a provider 5xx is re-run (up to 3 attempts, `diagnosis/rerun_infra.sh`); an incomplete run without a provider error is a model failure and is kept.

### E010-v4 result (2026-11-19; g8.2; same day, hermetic; 18 + 18 runs; Luna two-pass agreement 0.988 / 0.984)

All 5 runs interrupted by OpenAI 503 were re-run on the first attempt (`diagnosis/rerun_infra.sh`); no arm was scored with an infrastructure failure in it.

| | C5 v2 (v3) 11-13 | **C5 v2 (v3) 11-19** | **E010-v4 11-19** |
|---|---|---|---|
| options | 37 | 36 | 37 |
| silent-error | 22% | **22%** | **38%** |
| traps + UC only | 22% | 22% | 35% |
| PERMILE (target) | 3/4 | 1/2 | **0/5** ↓ |
| TR01 (target) | 4/4 | 3/3 | **6/7** (not fixed) |
| TR05 | 2/7 | 5/8 | **7/8** ↑ |
| TR08 / TR07 / NIGHTDEF | 0/7 / 0/3 / 0/7 | 0/5 / 0/4 / 0/6 | 0/5 / 0/3 / 0/7 |
| unsupported_claim | 5/37 | 1/36 | 1/37 |
| SE A1 / I1 | 4/7 / 4/8 | 6/8 / 2/6 | 8/8 / 5/6 |
| process: plan / check files, outcome-value rows in check | 36 / 36, 0 | | 36 / 36, 0 |

**Decision by the keep rule: revert. v3 (C5 v2) stays the base.** Only one target fell; TR05 and silent-error rose.

What the evidence says:
1. **PERMILE fixed.** 5/5 applicable I1 options now say what the crash-based measure does not estimate ("does not estimate deaths per mile", "cannot establish whether … per mile declined"). The direction ban works as written.
2. **TR01 moved behaviour, not to the standard.** v4 options now state rows per year ("denominator rose from 203,742 in 2013 to 231,564 in 2018, then reached 85,546 in 2025"; "ratios over changing crash-row totals"), but they do not say the change is sharp around 2020 *and* that it affects comparing the per-crash rate (decision 8). The prompt asked for "how rows per year change … and what that change does"; the agents gave the first part and a generic version of the second. Borderline cells (I1-r3 o2, I1-r1 o1) are candidates for the human review; even if both passed, TR01 would be 4/7.
3. **TR05 rise is plausibly caused by v4 (hypothesis).** In v4 the A1 agents computed the denominator rows *after* the Brooklyn filter and checked missing borough inside that set ("0 of 483,501 Brooklyn rows missing/unknown borough"), which by construction finds none. The rows-per-year instruction appears to pull the data check onto the filtered population. Not proven on 8 A1 options.
4. **v3 replicates.** C5 v2 gave 22% on 11-13 and 22% on 11-19 (D v2 baseline was 42% on 11-13). Its TR05 varies by day (2/7 vs 5/8).
5. **Measurement note (M10, for Bo).** 2 of v3's 5 TR05 FAILs on 11-19 disclose an overall share ("30.8% … excluded") and fail only because the grader reads the reference range in the item ("19.9–38.1% per year") as required. Whether an overall share is enough is a standard question; no change made.

Next (not started; the post-v4 plan is under discussion with Bo): the recorded rule is to split v4 into v4a (direction ban only; expected to keep the PERMILE gain) and v4b (rows-per-year, reworded to name the effect on cross-year comparison and to count rows before any population filter).

## 2026-11-19 (T1): lock the version. Root cause of v4, g8.3, nested candidates A / AC / ACB

Bo approved T1 (and T2–T5; T6 pending) and delegated the v3→v4 fix and the rule update.

### What v4 taught (lock the problem)

| Part of v4 | Verdict | Evidence |
|---|---|---|
| Direction ban when the plan says "partly / no" | **works, kept (A)** | PERMILE 0/5 in v4, 0/5 in A |
| Rows-per-year rule | wording too weak, **reworded (B')** | v4 agents listed rows per year but did not tie the change to the comparison (TR01 6/7) |
| TR05 "rise" | **not caused by v4: a flaw in v3's data check (fixed by C)** | The check counted missing values "in the plan's population", i.e. after `borough = BROOKLYN`, which is 0 by construction ("0 of 483,501 Brooklyn rows missing borough"). v3's TR05 was 2/7 and 3/8: partly luck. |

### Ruler

- **Grader hermetic check** (open caveat closed): 48 options of the 11-08 arms (not A1 / I1) re-graded hermetically; 536 cells, 17 differ, agreement **0.968** against the stored pre-hermetic verdicts. Two hermetic passes agree on 0.97–0.99, and the flips have no direction (trap / UC: 3 options towards FAIL, 2 towards PASS). No detectable effect of the skill text on the grader. `diagnosis/grader_hermetic_check.py`, `.json`.
- **g8.3 = decision 11 (TR05 wording).** The grader was inconsistent on the same sentence type: of the options that mention the excluded no-borough rows without a per-year range, 23 passed and 10 failed, 4 solely as "an overall share, not the per-year range". Now: disclosure that no-borough crashes are left out passes; a number is optional; the range is a reference. A1 units re-graded in all 15 arms, everything else reused.
- **Decision 10, extended contexts** (same rule, found on the new arms): the year of an ISO date ("1900-01-01"), the hour of a clock time ("20:00-23:59"), "1,000 times …". A check-file cell that holds several numbers ("0 of 2269187") now yields each number. Still unsourced by rule: a total that is in neither file (2,132,218 = sum of two check rows, 4 + 4 options in A / AC) and a share not in the values file (15.9%).

### Candidates (nested, one change per step; frozen in FROZEN.md)

A = v3 + direction ban. AC = A + a filter column is checked on the rows *before* that filter. ACB = AC + denominator rule reworded (name the largest change in rows per year between neighbouring years and say the measure's rise or fall across them can come from the denominator).

### Result (same day 11-19, hermetic, 18 runs each, no infrastructure failures; g8.3; two-pass agreement 0.984–0.991)

| | D v2 11-13 | v3 11-13 | **v3 11-19** | v4 11-19 | A | AC | **ACB** |
|---|---|---|---|---|---|---|---|
| options | 43 | 37 | 36 | 37 | 39 | 36 | 38 |
| **silent-error** | 42% | 22% | **19%** | 38% | 36% | 22% | **11%** |
| traps + UC only | 42% | 22% | 19% | 35% | 26% | 14% | 11% |
| unsourced options | 0 | 0 | 0 | 1 | 4 | 4 | 0 |
| PERMILE (A) | 1/3 | 3/4 | 1/2 | 0/5 | **0/5** | 0/2 | 0/2 |
| TR05 (C) | 9/9 | 2/7 | 3/8 | 8/8 | 3/7 | **0/7** | 0/9 |
| TR01 (B') | 5/5 | 4/4 | 3/3 | 6/7 | 5/5 | 2/2 | **0/5** |
| TR08 / TR07 / NIGHTDEF | 3/7, 3/5, 0/10 | 0 | 0 | 0 | 0 | 0 | 0 |
| TR15 (control) | 3/3 | 3/3 | 2/3 | 3/3 | 3/3 | 2/2 | 3/3 |
| unsupported_claim | 4/43 | 4/37 | 1/36 | 1/37 | 1/39 | 1/36 | 1/38 |
| SE A1 / I1 | 9/9, 3/6 | 4/7, 4/8 | 5/8, 2/6 | 8/8, 5/6 | 5/7, 5/7 | 4/7, 4/6 | **3/9, 0/6** |

Each step moves its own target and only that:
- **A** fixes PERMILE (0/5) but on its own makes I1 worse overall (SE 5/7): the agent now shows the per-crash rate more often, and every such option fails TR01. A needs B'.
- **C** takes TR05 from 3/7 to 0/7 (0/9 with B'). Agents now write e.g. "borough NULL on 659,713 of 2,132,218 city rows in 2013–2025 (30.9%), so these rows could not be assigned".
- **B'** takes TR01 from 5/5 to **0/5**, the control no arm had moved since E009. Agents find the break themselves: "the denominator fell from 211,486 in 2019 to 112,918 in 2020, so a rise or fall in this measure across those years can come from this denominator change and not the outcome". The prompt names no year.
- What is left in ACB: TR15 3/3 (small counts, untargeted control) and 1 UC (K3-r3 o1, the M8 pattern: "zero missing" in 2013–2025 judged against the 2026 NULLs; for human review).

**Decision (keep rule, same-day v3): ACB is kept and locked as E010-v4** (`D_enumerate.v2-plan4-ACB.md`). All three targets fall, nothing else rises (TR15 is 2–3 of 3 in every arm). The 11-19 `v2-plan3` arm is renamed "v4-draft" in the records. From here the prompt is frozen: no edits before the generalisation test (T2).

Limits, stated plainly: one run of 18 per arm; TR01 0/5 and PERMILE 0/2 are small counts; the six pilot questions were used to design the changes, so this is a development-set result. T2 (held-out questions) is the test.
