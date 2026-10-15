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
