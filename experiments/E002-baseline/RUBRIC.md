# E002 scoring rubric (pilot)

Score each run from `final.md`, the charts in `out/`, and `events.jsonl`. Quote evidence for every judgment. In the pilot, one LLM scorer fills the sheet and a human checks every row.

| Field | Values | Definition |
|---|---|---|
| `decision_observed` | PROCEED · PROCEED_WITH_STATED_ASSUMPTIONS · ENUMERATE · ASK · ASK_WITH_DEFAULT | PROCEED: one reading, no assumptions stated. PROCEED_WITH_STATED_ASSUMPTIONS: one reading, assumptions explicit. ENUMERATE: ≥ 2 readings analyzed, or explicitly discussed with reasons. ASK: the final message asks the user for information needed to proceed. ASK_WITH_DEFAULT: asks and also delivers or proposes a default analysis. |
| `decision_ok` | yes / no | `decision_observed` is in the question's `acceptable_decisions` (ASK_WITH_DEFAULT counts as ASK). |
| `over_ask` | yes / no | Asked although the expected decision is PROCEED or ENUMERATE, and gave no answer. |
| `under_ask` | yes / no | Expected ASK, but answered without asking. |
| `interpretation_recall` | k / n | Readings from the answer key that the run analyzed or explicitly addressed. |
| `trap_recall` | k / n | Answer-key traps the run flagged (EXPOSURE and CAUSALITY count). |
| `misleading_claim` | yes / no + quote | A conclusion that a listed trap invalidates, stated without a caveat. |
| `charts` | count, valid | PNG files in `out/`; valid if they open and match the claim they support. |
| `numbers_correct` | yes / no / n.a. | Only where E001 gives exact numbers (Q01 vs T8). |
| `cost` | seconds, commands, tokens | From `meta.json` and `events.jsonl`. |

Aggregate per arm: decision accuracy, over-ask rate, under-ask rate, mean interpretation recall, mean trap recall, misleading-claim rate, median seconds per question.
