# E007 — Pilot round: tune the B critique/revise prompts and the C self-check prompt

**Pre-registered before any pilot run.** Edits to this file after the first pilot call must be logged as amendments at the bottom.

## 1. Purpose

Phase 1 compares A (baseline), B (add a review step) and C (self-check prompt). The B and C prompts are written by us, so the comparison is only fair if both received the same, bounded tuning effort on questions that are **not** scored later. This round produces two frozen prompts: `B_critique` + `B_revise`, and `C_selfcheck`.

## 2. Setup (working assumption, pending team confirmation)

- Step ① is one bounded OpenCode run (≤ 10 steps) in which the model writes and executes its own code (E006). Model: `mimo-v2.6-flash-free`. Same sandbox rules as E006.
- Pilot set: 6 questions in `pilot_questions.json`, **disjoint from the 10 formal questions** in subject and wording; same types (3 clear, 2 ambiguous, 1 insufficient evidence). Gold numbers from independent SQL (`gold_pilot.py`).
- Formal questions (P1–P10) are never run with candidate B/C prompts during the pilot.

## 3. Tuning budget (equal for B and C)

| | B (critique + revise) | C (self-check) |
|---|---|---|
| Iterations | 3 | 3 |
| Pilot questions per iteration | all 6 | all 6 |
| Repeats per question | 1 (A baseline: 2) | 1 |
| Runs per iteration | 12 (critique + revise on 6 A outputs) | 6 |

One iteration = run the candidate prompt on all 6 pilot questions, score, read failures, edit the prompt once. After iteration 3, the prompt of the best-scoring iteration is frozen (ties: the shorter prompt).

## 4. What an edit may and may not change

Allowed: output format and section names; which artifacts the prompt tells the model to look at (plotted values, run log, chart); wording clarity; length; ordering; asking for numbered, specific issues; asking the model to leave correct parts unchanged.

Not allowed: any list of specific data traps or domain facts (denominator choice, partial years, unknown borough, reporting changes, category drift, "per ride needs exposure data"); question-type-specific instructions; examples drawn from the formal questions.

If a trap or domain fact is added to B and C alike, it is a different lever; the run is labelled `domain-notes` and reported separately.

## 5. Pilot objective (what "better" means during tuning)

Scored per pilot item by the person tuning (Bo), with Claude as a second scorer; disagreements resolved by reading the output together:

1. **Gate:** values/units/aggregation/conclusion correct, no important misleading claim (pass/fail).
2. **Format compliance:** chart + values file + `ANSWER:` present; for B, a numbered issue list.
3. **Flips:** items that were gate-pass in A and gate-fail after B or C (lower is better).
4. **Cost:** steps and tool calls.

Selection rule per prompt: maximize (gate passes − 2 × flips); ties broken by fewer steps. This is a pilot objective only; it is not reported as a result.

## 6. Freeze

After iteration 3: save the three prompts in `prompts/frozen/`, compute SHA-256 of each file, record them in `FROZEN.md` and in every formal run's metadata, and make no further edits. A later change requires a new protocol version and a re-run of all arms that use the changed prompt.

## 7. Logging

Every iteration: prompt file (versioned `B_critique.v1.md` …), run outputs, scores, the failures that motivated the edit, and the failures the edit did not fix. Summarized in `ITERATIONS.md`; one entry per iteration in `experiments/LOG.md`.

## 8. Known limits

- 6 pilot items, one repeat: enough to catch format and instruction problems, not to estimate effect sizes.
- Tuning on mimo may overfit to mimo; acceptable, since phase 1 uses one model.
- Claude scoring is a convenience; the formal evaluation uses the team's blind human scoring.

## Amendments

- **2026-10-14 (before iteration 1 was scored):** a run that reaches the step cap ends with a narration produced by the step-limit message ("maximum steps reached… recommended next step"). Such a reply is **not an answer**: the item counts as non-completion (gate fail under intention-to-treat), even if the text contains an `ANSWER:` token. Raw runs are kept.
- **2026-10-14:** unsourced numbers (figures not derivable from the data file, e.g. recalled mileage series) are recorded as a separate flag per item and make the gate fail if they carry the conclusion.
- **2026-10-14:** C is allowed to vary only in the self-check instruction (wording, the generic categories it asks to review, and where it sits). Step-economy or ordering advice outside that instruction is not allowed, because the A prompt does not have it.
- **2026-10-14:** rate limiting ("Rate limit exceeded") is an infrastructure failure. A run that was rate limited before its first step is retried with backoff and is not scored; a rate-limited batch is not an iteration. Batches are started only after a liveness check, with concurrency ≤ 2.

## Amendment 2026-10-14 (scope v2, agreed with Bo before any B v2 run)

**Purpose, narrowed:** make B's two steps work as designed — the critique is an honest review, the revision changes only what was flagged — then freeze the A and B prompts. C is out of the pilot.

| Arm | Plan |
|---|---|
| A | Frozen at `A.v1.md` (12 valid runs). Failures on ambiguous items are part of the baseline and are not tuned away. |
| B | Up to 3 iterations on the 6 pilot items, 1 run each. Prompts edited only by Bo; each edit must cite an observed failure in `ITERATIONS.md`. |
| C | Written by Bo after A and B are frozen, informed by what B's reviews found. One format check (chart + values + answer) on the pilot items; no effect tuning. The report states this asymmetry (B tuned up to 3 rounds, C written once). |

**B design v2.** The review run cannot execute code (`config/opencode.review.json`); A's chart is attached, and its values, written answer and code are embedded in the prompt, so the reviewer judges what was produced instead of redoing the analysis. The review must return `ISSUES:` with a numbered list, or `ISSUES: NONE`. The revise run is made only if issues were reported; it must list how each issue was handled and keep everything not flagged unchanged. If the review says none, A's outputs are carried forward and no third run is made (repair only when a problem was reported).

**Acceptance (all on the 6 pilot items, one iteration):**

| Step | Pass if |
|---|---|
| Review | ≥ 5/6 return a parseable `ISSUES:` block; ≥ 5/6 use ≤ 2 tool calls; on items where A was wrong (gold available), at least half name the real error; on items where A was right, no invented substantive error (one cosmetic remark allowed) |
| Revise | ≥ 5/6 produce `revised.png` and `revised_values.csv` (or are correctly skipped); every number A had right is unchanged; zero correct → incorrect flips |

**Freeze when:** an iteration meets acceptance; or 3 iterations are used; or an iteration's edit removed none of the failures it targeted.

**Not acceptance items (recorded automatically):** steps, requests, time per run.

**Mechanics test (not a result):** B v2 was run once on A-v1 K1 with `nemotron-3-ultra-free` (mimo was rate-limited) to check the pipeline: review 1 step, 0 tool calls, 2 specific wording issues, no invented numbers; revise kept every number and changed only the text, listing each change. Stored under `results/B-v2-v2-nemotron-3-ultra-free/`.

## Amendments 2026-10-15 (after B v2 iteration 1 on mimo, run by Chloe)

- **B runs only when A produced an `ANSWER:`.** If A's reply is a step-cap narration or has no answer, B is not run; the item fails in both arms (ITT) and is recorded as `b_skipped`. An A run with an answer but no chart still goes to B. Rationale in `docs/phase1-abc-design.md` §9. Agreed by Bo.
- **Environment: no internet for the model.** A-v1 I1 r1 and r2 fetched vehicle-mile data from the web (`websearch` tool and `urllib` inside `python`; `webfetch: deny` covers neither). The design requires the model to answer from the data file only; "insufficient evidence" questions test exactly that. Fix (harness, not prompt): `websearch: deny` in both configs, and the model's `python`/`python3` run the runner's interpreter under macOS `sandbox-exec` with outbound network denied (`run_screen.python_shims`). Verified on mimo: no 403, `websearch` absent, `urllib` → "Operation not permitted", duckdb works. **A-v1 I1 r1/r2 are void** (environment violated the protocol) and are moved to `results/A-v1/_void/` and re-run under the fixed sandbox with the unchanged A.v1 prompt; the other 10 A-v1 runs made no external call (checked every committed `events.jsonl`) and stand. The fix also pins the sandbox interpreter to the pinned environment, which the PATH problem on Chloe's machine showed was not guaranteed.
- **Pilot pairing.** B's input is A's r1, as before. The void I1 runs are moved to `results/A-v1/_void/` and the re-runs take their place, so I1's r1 is a clean run. A1 has no answer in r1 (nor r2), so B has no pilot evidence on A1; this is reported, not patched by re-running A until it completes.

## Amendment 2026-10-15 (B contract, sandbox v2; agreed with Bo before B iteration 2)

**Acceptance is the B contract, not B's effect.** The pilot checks that B runs as designed: right inputs, right outputs, inside its boundaries, every item in a defined end state. How many real errors the review finds is the formal experiment's question; tuning prompts on it with pilot data would favour B. This replaces the scope-v2 acceptance table.

| Part | Contract | Checked by |
|---|---|---|
| ③ review: input | question, data dictionary, A's chart attached, A's values / answer / code embedded; recorded in `review_input.json` and `review_prompt.md` | harness |
| ③ review: output | text only, three sections: `CHART CHECK:` (what it saw in the image), `ISSUES:` (numbered, or `NONE`: problems shown from the material, including statements the data cannot support), `UNVERIFIED:` (checks that would need the data file or code); parsed into `review.json` | parser |
| ③ review: boundary | no code execution, no file writes, no reading outside its folder, no network; runs in its own folder so it cannot inherit the analysis config | config + folder guard; `review_side_effects` |
| Gate 2 | `NONE` → A's outputs are B's; numbered list → ④ gets the ISSUES list only; no parseable ISSUES block → B fails the item, no ④ | harness |
| ④ revise: output | `revised.png`, `revised_values.csv`, `ANSWER:`, `CHANGES:` one line per issue number with fixed / kept / cannot address; recorded in `changes.json` | parser |
| ④ revise: boundary | sandbox as ①; A's `initial.png` / `values.csv` read-only; values compared with the repo copy | sandbox; `a_outputs_intact`, `values_changed_cols` |
| End state | one of `B_STATES` (`run_pilot.py`) | harness |
| Human (yes/no per item) | ③ invented an issue? ④ changed something not flagged? | scorer |

**Pass:** on every item B can run (A has an answer), all boundary checks and both human checks hold; format checks may fail on at most one item. `check_contract.py` prints the machine part. **Freeze** when an iteration passes, or after 3 iterations.

**Sandbox v2 (all arms, before any formal run).** Every command the model may run (`python`, `python3`, `ls`, `cat`, `head`, `mkdir`) runs under macOS `sandbox-exec`: no network; no reading the repo (gold answers, docs, other results) or other runs; writing only inside its own folder. Each run gets its own APFS clone of the data file instead of a symlink into the repo. `check_env.py` fails if the sandbox does not block network or if a global OpenCode config sets permissions. Red-team test (nemotron, permissions are enforced by OpenCode and the OS, not the model): read / glob / grep on the repo, `ls` of the repo, python reading the gold file or writing into the repo, a `task` subagent, websearch: all blocked in the analysis folder and in the review folder; DuckDB on the data file works. Evidence that this was needed: C-v1 I1 listed the repo root through `ls` and tried to read `AGENTS.md` and `docs/`.
