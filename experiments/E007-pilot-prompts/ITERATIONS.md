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
