# E004 — OpenCode free models as the baseline (B1-open), 8 questions × 3 models

**Result:** free OpenCode models are not uniformly bad at vague questions — they are **inconsistent and expensive**. The best model (big-pickle) made an acceptable ask / enumerate / proceed decision on all 7 questions it finished and flagged most traps, but needed 2–5 minutes and up to 27 tool calls per question and imported unsourced numbers from memory. The fastest (nemotron) answered in seconds but proceeded with one reading on 3 of 7 and made misleading claims. One (mimo) explored without stopping and timed out on 4 of 8, including both questions whose right answer was to ask. Per-run scores: [`SCORES.md`](SCORES.md).

## Setup
- Subjects: `nemotron-3-ultra-free`, `big-pickle`, `mimo-v2.6-flash-free` (OpenCode Zen, $0, no account), plain prompt (`E002-baseline/prompts/plain.md`), 8 questions (`questions.json` pilot-v2).
- Harness: `run_opencode_subjects.py` — one sandbox per run outside the repo, own `XDG_DATA_HOME` (enables parallel runs), restricted `opencode.json`, 900 s timeout, JSON event trace.
- 24 runs, concurrency 3, total wall clock ≈ 50 min; 1 retry.

## Outcomes

| | Runs | Answered | Timed out | Infra failure |
|---|---|---|---|---|
| nemotron-3-ultra-free | 8 | 7 | 0 | 1 (upstream 503, retry hung) |
| big-pickle | 8 | 7 | 1 | 0 |
| mimo-v2.6-flash-free | 8 | 4 | 4 | 0 |

## What we learned

1. **The gap is decision consistency and cost, not raw capability.** Good judgment exists in free models (big-pickle asked "which policy, date, scope?" on Q06 and enumerated four disagreeing lenses on Q03), but it arrives late, after long exploration, and differs sharply between models.
2. **Asking is late or absent.** nemotron asked on Q05 in 12 s with 1 tool call. big-pickle asked only after 27 tool calls and building a script. mimo never asked within 15 minutes on either ASK question.
3. **Run-to-run variance is large.** nemotron on Q02 concluded "risk has increased substantially" in E003 (from a per-crash rate) but called the same rate "an artifact" in E004. One run per cell is not enough; the real baseline needs 3+ repeats.
4. **New failure mode — memory-sourced numbers.** With web access denied, models still used population figures, "DOT's published mode data" and ACS commuter estimates from memory to build per-capita or per-trip rates. Plausible, unsourced, and unverifiable from the data provided.
5. **Even a correct control answer can carry a trap.** big-pickle answered Q01 correctly and then added "each crash is ~2.5× more deadly", a rate on the collapsed crash denominator (TR01).
6. **Answer key needs widening.** Models flagged traps we had not listed for that question (e.g., TR01 on Q02, TR08 on Q04). Scoring should credit valid unlisted traps.

## Implications for Poppy
- An explicit, cheap ask / enumerate / proceed decision **before** exploration (the `decide()` layer) is the lever: it could give big-pickle-level judgment at nemotron-level cost, and stop exploration loops.
- Add metrics: time and tool calls until the decision, timeout rate, unsourced-number rate, run-to-run agreement.
- Next baseline round: 3 repeats per cell, the `policy` prompt arm (B2) on the same models, and a human check of these scores.

Scored by Claude; needs a human check before any number is quoted outside the team.
