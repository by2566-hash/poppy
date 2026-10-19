# E007 iteration log

Protocol: `PROTOCOL.md` (pre-registered). Config: mimo-v2.6-flash-free, bounded agent run, steps ≤ 15, timeout 600 s, per-run sandbox.

| Iter | Prompt files | Runs | Notes |
|---|---|---|---|
| 1 | A.v1 (2 repeats), C_selfcheck.v1 | A 12, C 6 | see below |

## Iteration 1 — A.v1 baseline and C_selfcheck.v1 (scored 2026-10-14)

| | A.v1 (12 items) | C v1 (6 items) |
|---|---|---|
| Compliant (chart + values + answer, no step-cap narration) | 7 / 12 | 4 / 6 |
| Gate pass (ITT; non-completion = fail) | 7 / 12 | 4 / 6 |
| Clear Qs K1–K3 | 6 / 6 pass, 6–7 steps | 3 / 3 pass, 9–15 steps |
| Ambiguous A1, A2 | 1 / 4 | 1 / 2 |
| Insufficient I1 | 0 / 2 | 0 / 1 |
| Timeouts | 1 | 2 |
| Flips vs A (A pass → C fail) | — | 0 |

Failures that motivated the C edit: (1) C adds ~60% more steps on clear questions without changing the gate; (2) timeouts on the ambiguous items where A also struggled. Not fixed by any C edit allowed under the protocol: A and C both import recalled mileage numbers on I1 (unsourced), and both fail to produce a chart on A1 within the step cap.

Observations (informational): K2 gold coverage 0.93 is a weekday-index offset (Mon=1 vs Sun=0), not an error. A2 answers differ on the night window (9pm–6am vs 10pm–6am vs 7am–6pm day) and none mentioned time-of-day data quality.

C edit for iteration 2 (`C_selfcheck.v2.md`): replace the single generic sentence by three generic review questions (does the chart answer the question; do the answer's numbers match values.csv; are labels, units and time range correct) placed after the files are saved. No domain content, no efficiency advice.

## Attempt log — 2026-10-14, after iteration 1

| Run | Result | Status |
|---|---|---|
| B.v1 critique + revise on A-v1 r1 (6 items, 12 calls) | 4 / 6 critiques empty (agent spent 11 steps scripting PIL pixel analysis and wrote no text); 1 revised chart; 3 items with no answer | **Not scored.** Free endpoint was degraded: a trivial "reply OK" call timed out at 120 s minutes later. Cannot separate prompt effect from service effect. Kept as `runs/B-v1-v1.json` |
| C.v2 (6 items) | 6 / 6 timed out at 600 s; 3 of them never started a step | **Invalid (infrastructure).** Kept as `runs/C-v2.json`, to be re-run, not counted toward C's 3-iteration budget |

Rule applied: protocol section 6 of `phase1-abc-design.md` (call failures are retried, not scored). Liveness is checked with a trivial call before every batch from now on.

Design observation worth keeping (not an iteration result): the B critique step, as an agent run with tools, will use its budget to *re-derive* the chart from pixels. The original ③ is a review, not a re-execution. A critique prompt may state that this step reviews the saved artifacts and does not run code (allowed under the protocol: it says which artifacts to look at).

### Root cause found (same day, later)

The "stalled endpoint" was **rate limiting**: `AI_RetryError: Failed after 3 attempts. Last error: Rate limit exceeded. Please try again later.` OpenCode retries and then keeps waiting, so from outside the run looks hung and the JSON event stream stays empty; the error is visible only with `--print-logs`. mimo and big-pickle were limited for ≥ 45 min; nemotron-3-ultra-free still answered (4.8 s).

- **C.v2 (6/6 timeouts, 3 with 0 steps)**: rate limited, not a prompt result. Re-run; does not count toward C's budget.
- **B.v1**: calls were made while the quota was being exhausted; the 4 empty critiques cannot be separated from rate limiting. Re-run.
- The harness now detects the limit (stderr, within seconds), stops the call, and retries with 90 s / 240 s backoff only if no step had started; the result carries `rate_limited` and `attempts`.
- Iteration 1 (A baseline, C v1) completed before the limit and stands.

Volume so far on mimo today: E006 ≈ 66 agent runs + 5 vision + E007 iteration 1 = 18 runs + 12 B calls. The free tier's limit is undocumented; plan for lower throughput.

## Scope v2 and B v2 (2026-10-14)

Scope narrowed to A and B (see PROTOCOL amendment). A frozen at v1. C v2 run is void (rate limited) and C is now written after the freeze.

B v2 prompts, and the failure each change targets:

| Change | Failure it targets |
|---|---|
| Review run cannot execute code (`opencode.review.json`) | B v1 reviews spent 11 steps scripting pixel analysis and wrote no review |
| Chart attached; values, answer and code embedded in the prompt | B v1 told the model where the files were, which invited re-analysis |
| `ISSUES:` numbered list or `ISSUES: NONE`; "do not invent problems; say when you cannot verify" | Need a parseable, honest review |
| Revise lists each change; "keep everything not flagged unchanged"; skipped when no issues | Protect correct outputs from being changed (flips) |

Mechanics test on one item with nemotron passed (see PROTOCOL). Next: B v2 iteration on mimo when its quota allows.

## B v2, iteration 1 on mimo (run by Chloe, 2026-10-15; checked by Claude)

Results: `results/B-v2-validation/` (commit c72142f), prompts B_critique.v2 / B_revise.v2, A input = A-v1 r1.

| Item | A-v1 r1 | Review issues | Real errors found | Revise | Values flipped |
|---|---|---|---|---|---|
| K1 | correct | 2 | 0 (1 "prose doesn't list every year", 1 "cannot verify") | ran, 7 steps, numbers unchanged | 0 |
| K2 | prose ranks Wed above Tue | 2 | 1 (+1 "cannot verify") | fixed sentence | 0 |
| K3 | "gap widest in 2013" true only as ratio | 1 | 1 | fixed sentence | 0 |
| A2 | `harmed` = SUM(injured+killed) drops rows with NULL killed | 5 | 3 (+1 minor rounding, +1 "cannot verify") | fixed all; only `harmed` changed | 0 |
| A1, I1 | step cap, no answer | not run | — | — | — |

Checked independently: A2's corrected `harmed` matches DuckDB (hour 0: 29,606; hour 16: 50,492); K2 / K3 corrections match `values.csv`. Review used 0 tool calls on all 4.

Observed failures (inputs to B v3):
1. "Cannot verify" statements are numbered as issues (K1 #2, K2 #2, A2 #5). They inflate `n_issues`, make `ISSUES: NONE` impossible, and trigger a revise run: on K1, where A was correct, revise spent 7 steps / 102 s re-verifying.
2. K1 #1 flags that the prose does not repeat every yearly number, although the chart and values answer "each year".
3. No critique says anything about the chart image itself, so we cannot tell whether the image was inspected.
4. K2's `CHANGES:` omits issue 2 (no change needed), so the handling of that issue is not recorded.

Not run: A1 and I1, because A did not finish (step cap). Decided 2026-10-15 (Bo): B runs only when A produced an `ANSWER:`; otherwise the item fails in both arms (PROTOCOL amendment, `run_B` records `b_skipped`).

### Correction: I1 used the internet (found by Chloe)

Iteration 1 recorded that A "imports recalled mileage numbers on I1". That is wrong for A: A-v1 I1 r1 and r2 **downloaded** them. The `websearch` tool was not denied, and `python` scripts called `urllib` (13 and 19 completed external calls; data.cityofnewyork.us, data.ny.gov, fhwa.dot.gov, dot.ny.gov). `webfetch: deny` covers neither. No other committed run made external calls (checked all `results/*/events.jsonl`). C-v1's I1 numbers were recalled, not fetched.

A-v1 I1 r1/r2 are void and moved to `results/A-v1/_void/`; I1 is re-run with the unchanged A.v1 prompt. The same check over every committed trace found two more cases, in E004 (big-pickle Q02, Q03 used `websearch`; corrected in E004's REPORT and SCORES).

Harness fix (not yet in any scored run): `websearch: deny` in both configs, and the model's `python`/`python3` now run the runner's own interpreter under `sandbox-exec` with outbound network denied (`run_screen.python_shims`). Tested on mimo: no 403, `websearch` absent from the tool list, `urllib` → `Operation not permitted`, duckdb works. This also fixes the teammate PATH issue (sandbox `python3` resolving to a host interpreter without the pinned packages).

## B v3 draft: mechanics test on mimo (2026-10-15, not an iteration)

Inputs: A-v1 **r2** of K1 and K2 (not the iteration's r1 inputs). Prompts `B_critique.v3.draft.md`, `B_revise.v3.draft.md`. Purpose: does the v3 format work, and is the chart actually used.

| Run | Result |
|---|---|
| K1-r2 (A correct), chart attached | `ISSUES: NONE`; CHART CHECK filled; 2 UNVERIFIED (the "pandemic driving" aside; source coverage); 0 tool calls; revise skipped. The v2 false trigger did not recur |
| K2-r2 (A wrote "32% fewer on Sundays than Fridays"; true: 24% fewer, or Fridays 32% more), chart attached | 1 issue, exactly that error, with arithmetic; 1 UNVERIFIED; revise 8 steps: `1. fixed`, only that phrase changed, values.csv identical |
| K1-r2, image withheld, `chart.png` still on disk | The model searched the folder, found `chart.png`, read it: control invalid (harness fixed: the file is no longer written) |
| K1-r2, image withheld and absent | `CHART CHECK: no chart`; "the chart itself" moved to UNVERIFIED. It did **not** describe the chart from the code |

Image evidence: first-step input ≈ 9.3k tokens with the chart, ≈ 7.6k without (the image is sent), and with no image the reviewer says so instead of inventing a chart description. Caveat: every detail in K1's CHART CHECK is also in the code, so a single CHART CHECK is not proof; the control is.

**Boundary defect found (harness):** OpenCode merges `opencode.json` from parent folders. The review folder sat inside A's sandbox, so it inherited the analysis config: in a test it ran `python3` and wrote a file. B v2 reviews made 0 tool calls, so no result is affected. Fix: the review runs in `poppy-sandbox/E007/_review/<label>/<item>/` and is copied into the item's `review/` afterwards; `run_B` refuses to start if any parent folder has an OpenCode config; `check_env.py` fails if the global config sets permissions. Re-tested: `ls` and `python3` denied, no file written.

Open logic point: unsupported claims (K1 "pandemic driving", K2 "fewer commuters") went to UNVERIFIED or were not mentioned. For insufficient-evidence questions an unsupported claim must be an issue, not UNVERIFIED. Decided by Bo: fix the routing definition only (which list a finding goes to), not push the review to find more; see below.

## Contract verification and B v3 draft end-to-end (2026-10-15, not an iteration)

Acceptance changed to the B contract (PROTOCOL amendment "B contract, sandbox v2"). This round tested the contract, not B's effect.

**Boundary audit (all committed traces + red-team).** Beyond the I1 web leak: C-v1 I1 listed the repo root with `ls` and tried to `cat` `AGENTS.md` and list `docs/` (denied); python could read `gold_pilot.json` and write into the repo; the review folder inherited the analysis config. Sandbox v2 closes all of these (PROTOCOL). Red-team with nemotron in both folders: every escape blocked, DuckDB works.

**Harness changes.** Review output parsed by section into `review.json`; revise receives the ISSUES list only; unparseable review → B fails, no revise; `review_input.json` / `review_prompt.md` / `revise_prompt.md` / `changes.json` saved; A's files read-only during revise and compared with the repo copy; each item ends in one of `B_STATES`; `check_contract.py` prints the contract per item and writes a labelling sheet for scoring the review on its own. A subset run (`PILOT_QIDS`) no longer overwrites the full run summary.

**Prompt changes in the v3 draft, each tied to a failure or a logic gap:**

| Change | Why |
|---|---|
| `{dictionary}` in review and revise | design §2 gives ③ the data dictionary; v2 omitted it |
| "do not redo the analysis; you may check arithmetic on the values shown" (was "do not recompute anything") | v2 forbade the arithmetic that found A2's bug and asked "what it should be" |
| judge chart, values and answer together; text need not repeat plotted numbers unless explicitly asked | K1 v2 false trigger |
| `CHART CHECK:` line | no v2 critique said anything about the image |
| ISSUES = shown from the material, **including statements the data cannot support**; UNVERIFIED = only checks that need the data file or code | "cannot verify" numbered as issues (K1, K2, A2); unsupported causes went to UNVERIFIED; routing must be unambiguous because the list decides the path |
| "only ISSUES is passed on and each will be acted on; no problems is a normal result" | v2 never said NONE |
| revise: fixed / kept / cannot address per issue; keep unflagged wording; save both files even if only text changes | K2 v2 omitted an issue; no exit for a wrong issue |

**End-to-end on mimo with the final harness** (A-v1 r2 inputs): K1 → 1 issue ("pandemic driving" is a cause the data cannot show), revise removed only that parenthetical; K2 → 2 issues (32% vs 24%; "fewer commuters" cause), both fixed, values.csv identical. Contract: 2/2 pass. Earlier runs on the same draft before the routing sentence: K1 NONE, K2 1 issue; image control as above. Stored under `results/B-v3draft-*`.

**A-v1 I1 re-run under sandbox v2** (replaces the void runs): r1 8 steps, r2 11 steps, both complete (before: both hit the 15-step cap while downloading data). Each tried the network once (`curl` denied by OpenCode, `urllib` blocked by the sandbox) and then answered from the data only. Both answers still draw a per-mile conclusion without mileage data (r1 assumes driving is back to pre-pandemic levels; r2 uses injury crashes as an exposure proxy): an A-side unsupported claim, kept as baseline behaviour, and B's input for I1 in iteration 2.

## B v3, iteration 2 on mimo (2026-10-15, Bo approved the prompts; checked by Claude, second review by the team pending)

Prompts `B_critique.v3.md`, `B_revise.v3.md` (identical to the tested drafts). Inputs A-v1 r1. Format self-check before the run: placeholders complete, no stray braces, headers and status words intact, no trap words, all six prompts render. `check_contract.py results/B-v3-v3`:

| Item | End state | Review | Revise | Claude's human checks (invented? / unflagged change?) |
|---|---|---|---|---|
| K1 | none_carried_forward | NONE, CHART CHECK, 2 UNVERIFIED | skipped | no / no |
| K2 | revised | 1: Tue/Wed ranking and "steady build" (true) | fixed; only those sentences changed; values identical | no / no |
| K3 | none_carried_forward | NONE, 1 UNVERIFIED | skipped | no / no |
| A1 | skipped_no_A_answer | — | — | — |
| A2 | **review_failure** | no output: step 1 used 14k reasoning tokens and re-read the attached chart; step 2 produced nothing until the 600 s timeout; no error logged | not run (gate) | — |
| I1 (re-run A) | revised | 3, all true: unsupported "driving back to pre-pandemic levels"; "injuries stayed flat" contradicts values.csv (−19%); background shading in the right panel unlabeled and on the wrong side of the 74% break-even (visible only in the image) | all 3 fixed; answer made conditional; shading moved and labelled; values identical | no / no |

Contract: 5 items B could run; boundaries held on all (no side effects, no network, A's files intact, Gate 2 routed A2 to failure without a revise run). One item did not finish (A2). Under §9 a timeout after a completed step is non-completion, not an infrastructure failure, so A2 counts as B failing the item; it is not re-run. The acceptance rule did not name this case: read as a completion slip (≤ 1 allowed) the iteration passes; read strictly it does not. Team decision, not changed after the fact.

Not acceptance items (effect, for the formal run): K1's "(pandemic)" aside and K3's "gap widest in 2013" (true only as a ratio) were not flagged; v2 flagged K3, and in the end-to-end test v3 flagged K1-r2's "(pandemic driving)". The v3 line "finding no problems is a normal result" may lower sensitivity; measure it in the formal run, do not tune it on pilot items.

### A2 review timeout: root cause (2026-10-15, diagnostic, not scored)

Evidence (`results/B-v3-v3/A2-r1/events_review.jsonl`, OpenCode's session DB): step 1 ran 18:34:24–18:37:29 (185 s) and produced 37,770 characters of reasoning (14,060 tokens): arithmetic on all 24 rows, then an attempt to verify "cut-off or overlapping elements" by estimating pixel coordinates of the legend box and the 4 am peak marker; it ended with "I need to re-read the image" and a `read` of the attached chart (25 ms). Step 2 started at 18:37:43; the provider opened a reasoning stream and sent nothing for the remaining 401 s; no error, no rate-limit line, `opencode.log` empty; the harness killed the run at 600 s as designed. Not the step cap (2 of 15 used), not a rate limit (the request was accepted), not the sandbox (the review runs no commands), not a harness defect (the wait was the configured timeout).

Two diagnostic re-runs, same prompt and input: both finished in one step with 0 tool calls, 164 s (7.7k reasoning tokens, 3 issues) and 399 s (2 issues). Both found the "8× the midday rate" error and the `harmed` NULL-sum bug (v2 found both too; the v2 review took 214 s). So the stall is not deterministic; the provider stalling a streamed response is intermittent, and the trigger was a long first step that ended in a tool call, which forced a second request. Decision on how A2 counts in iteration 2 stays with the team; the diagnostic runs are stored under `results/B-v3-v3-diagA2-*` and are not scored.

### Corrections to the iteration-2 record (2026-10-15, after a second look at the traces)

1. **K2's revise did not spend 403 s on 9 steps.** By event timestamps the model worked for 100 s (18:31:34–18:33:14); the preceding 300 s were a stalled stream that OpenCode reported as `[502] Network connection lost` and retried internally. So iteration 2 had two provider stalls, not one. The earlier statement "revise re-ran the chart for 9 steps / 403 s" was wrong about the cause; the 9 steps themselves are agent overhead (list folder, read files, write `revise.py`, run it, verify the CSV is identical) plus the required re-run, about 100 s.
2. **Reviser isolation leak.** K2's reviser read `critique.md` (and `revise_prompt.md`) from its folder, so it saw the UNVERIFIED and CHART CHECK sections that Gate 2 withholds. Diagnostic A2-2 did the same; v2's A2 reviser `cat`-ed it. No other run. Contract item "revise receives the ISSUES list only" was therefore not fully enforced in iteration 2; its outcome on K2 was unaffected (one fix, matching the one issue). Fixed in the harness (records written outside the item folder until revise ends).
3. Harness changes from the stall analysis: review timeout 420 s; `stalled` / `attempts` fields in every meta (detector present but off, see below).

### Stall detection and review steps=1: tried, measured, rejected (2026-10-15)

- Unit test with a fake `opencode` that goes silent after one event: the detector kills at the threshold, retries once, reports `stalled`, `attempts=2`. The mechanism works.
- Validation on a real review (A2, steps=1, detector at 120 s): run 1 killed twice as "stalled" with 0 tokens; run 2 finished in 173 s with a parseable review but step-limit narration in front.
- Liveness probe: an A2 review watched every 5 s with `--log-level INFO`, then a K3 review with `DEBUG`: `events.jsonl`, the SQLite WAL and stderr all stayed unchanged for 225 s and 165 s respectively while the model reasoned, then the whole reply arrived. There is no client-side signal that separates "reasoning" from "stuck".
- Conclusion: detector off by default; steps stay 15; review timeout 420 s is the only safe cost cap. Evidence under `results/diag-2026-10-15/`.
- Variance note: the same K3 review took 62 s in iteration 2 and 198 s in the probe; A2 reviews took 164–399 s. Review time on mimo varies 3× for identical input.


## B v4: prompt for iteration 3 (2026-10-16, decided by Bo)

`B_critique.v4.md` = v3 with two edits; `B_revise.v3.md` unchanged. Diff against v3:

| Edit | Observed failure it targets |
|---|---|
| Removed "Only the ISSUES list is passed on … Finding no problems is a normal result; do not list something just to have an issue." | Iteration 2: K1 "(pandemic)" and K3 "gap widest in 2013" (ratio only) not flagged; v2 and the v3 end-to-end test flagged the same kind. Bo: on ambiguous / insufficient-evidence questions this sentence suppresses exactly the findings we need |
| CHART CHECK: "write down what you see: axes and units, labels and legend, and whether the numbers shown match values.csv. If a part of the image is unclear to you, say so under UNVERIFIED." (dropped "cut-off or overlapping elements") | Iteration 2 A2: pixel-geometry reasoning on overlap (37k characters), a second image read, then a stalled second request |

Known trade-off: edit 1 may bring back some v2-style false triggers on correct answers; edit 2 may lose chart-only findings such as I1's misplaced shading. Both are effects, observed in the formal run, not tuned here.

Harness for iteration 3: zero-output timeout retried once (unit-tested with a fake `opencode`: silent run retried once, run with partial text not retried); review timeout 420 s; reviser isolation fix in place.

## B v4 + v3, iteration 3 on mimo (2026-10-16): contract passes; B frozen

`check_contract.py results/B-v4-v3`: 6 items, 0 machine-checked contract failures; no zero-output retry needed; no reviser read review files (scanned); every review 1 step, 0 tool calls.

| Item | End state | Review (claims checked by Claude against the material) | Revise | Invented? / unflagged change? |
|---|---|---|---|---|
| K1 | revised | 1: "(pandemic)" is a cause the data cannot show (true) | removed the parenthetical only | no / no |
| K2 | revised | 1: Tue/Wed order and "steady build" (true) | those two sentences only | no / no |
| K3 | none_carried_forward | NONE ("gap widest in 2013", ratio only, still not flagged) | — | no / no |
| A1 | skipped_no_A_answer | — | — | — |
| A2 | revised (164 s review) | 2: `harmed` NULL-sum (true, matches DuckDB); "8× the midday rate" should be 4 pm (true) | `harmed` column and one answer phrase; chart unchanged | no / no |
| I1 | revised | 4: unlabeled shading on the wrong side of the 74% break-even (true, image); "driving back to pre-pandemic levels" unsupported (true); column `motorist_deaths_per_mile_index` is a deaths index, not per mile (true, code line 30); "injuries stayed flat" contradicts values.csv (true) | shading moved and labelled; answer made conditional; column renamed with identical values; caveat corrected | no / no |

What the two v4 edits did (observations, not acceptance): K1's "(pandemic)" is flagged again and A2's review finished in one 164 s step without pixel-geometry reasoning; K3's "gap" is still missed; no false trigger on a correct item appeared in this run. A2 needed 2 issues where v2 listed 5: v4's review no longer reports the 6.3 vs 6.4 rounding or the legend hour labels.

Decision (PROTOCOL 2026-10-16): iteration 3 is the last; B is frozen at critique v4 + revise v3 (`FROZEN.md`). Team second review of iteration 2 and 3 records is still welcome and is logged here; it can correct a score but not the prompt.

## C v3: the one format check (mimo, 6 pilot questions, 2026-10-19)

Decided by Bo: C = `C_selfcheck.v3.md` (A.v1 plus one self-check sentence whose categories mirror the review's: chart, values and answer agree; numbers traceable to values.csv; every statement something the data can show). Per PROTOCOL scope v2, C gets one format check and no effect tuning.

| Item | Chart + values | ANSWER | Steps | Verdict (step-cap narration = not an answer) |
|---|---|---|---|---|
| K1 | yes | yes | 7 | complete |
| K2 | yes | present but after narration | 15 | not complete: spent the last steps on an extra pandas re-check |
| K3 | yes | yes | 8 | complete |
| A1 | no | no | 15 | not complete (same as A: exploration drift) |
| A2 | yes | after narration | 15 | not complete |
| I1 | yes | after narration | 15 | not complete |

2/6 complete under the strict rule; 5/6 produced chart and values; no network calls; sandbox held. For comparison, A-v1 r1: K1–K3 and A2 complete in 6–7 steps, A1 and I1 at the cap; C-v1 (pre-freeze draft): 4/6 at 9–15 steps.

Reading: the self-check sentence makes mimo spend its budget on verification passes; on clear questions it roughly doubles the step count (6–7 → 7–15). That is C's cost on this model, and under the fixed 15-step budget it shows up as non-completion. This is a result, not a format defect: the format (chart, values, ANSWER line) was followed whenever the run finished. No edit is made to C (protocol). Expectation for GPT-6 Luna (teammates' E008-lite): faster, fewer steps, so C should complete where mimo did not.
