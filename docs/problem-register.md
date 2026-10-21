# Problem register (phase 1, as of 2026-10-21)

Every problem found so far, where it was found, what was done, where the fix lives, and what remains. Three kinds: **H** harness and environment, **P** model behaviour (measured, not "fixed": the arms exist to measure it), **R** protocol and process. Status: fixed / mitigated / open / recorded (a finding, not a defect). File anchors are `path:line` at commit `85d2a56`.

## H — harness and environment

| ID | Problem | Found | Fix | Where | Status / residual |
|---|---|---|---|---|---|
| H1 | Background runs hung (stdin left open) | E006 | `stdin=DEVNULL` | `E006-mimo-screen/run_screen.py` `call_model` | fixed |
| H2 | Parallel runs → "database is locked" | E003 | per-run `XDG_DATA_HOME` | `run_screen.py` `call_model` | fixed |
| H3 | Free tier: no tool-less single call (403 without bash/read; `steps=1` → narration) | E006 | ① = bounded agent run; bash restricted by patterns | `E007-pilot-prompts/config/opencode.analysis.json` | fixed; design doc §10 |
| H4 | Rate limiting looked like a hang | E007 iter 1 | stderr detection, backoff, `rate_limited` flag | `run_screen.py` `call_model` | fixed |
| H5 | Step-cap narration parsed as an answer | E007 | `answer_of` rejects "maximum steps" | `run_pilot.py:104` | fixed |
| H6 | Model reached the internet (`websearch` tool; `urllib` in python) | A-v1 I1, E004 big-pickle | `websearch: deny`; python under `sandbox-exec` no-net; `net_calls` audit | `config/*.json:6`, `run_screen.py:23`, `run_pilot.py:120` | fixed; I1 runs voided and re-run; E004 report corrected |
| H7 | Model could read the repo (gold, docs) and write into it | C-v1 I1 listed the repo; red-team | sandbox denies repo reads, writes only in the run folder; data as APFS clone, not a symlink into the repo | `run_screen.py:23`, `run_pilot.py:88` | fixed; red-team tested on both configs |
| H8 | Review run inherited the analysis permissions (OpenCode merges parent-folder configs) | contract verification | review runs in `_review/` tree; refuses if an ancestor has a config; `check_env` fails on a global config with permissions | `run_pilot.py:306–310`, `scripts/check_env.py` | fixed; re-tested |
| H9 | Reviser could read `critique.md` (UNVERIFIED, CHART CHECK) from its folder | iteration 2 (K2) | review records written next to the review run, copied after revise | `run_pilot.py:324` | fixed |
| H10 | Revise could overwrite A's `initial.png` / `values.csv` | design review | files read-only during revise; `a_outputs_intact` check | `run_pilot.py:372`, `check_contract.py:32` | fixed |
| H11 | UNVERIFIED items counted as issues; unparseable review passed to revise | iteration 1→2 | sectioned `parse_review`; gate → `review_failure`, no revise; `B_STATES` | `run_pilot.py:140, 194, 205` | fixed |
| H12 | B ran on an A with no answer (placeholders) | A1/I1 | rule: skip, both arms fail; `b_skipped` | `run_pilot.py:287–292`; PROTOCOL 2026-10-15 | fixed |
| H13 | Provider stream stalls silently (A2 review 401 s; K2 revise 300 s) | iteration 2 | stall detector built and measured: **cannot work** (no client-side signal during reasoning), left off; zero-output timeout retried once; review timeout 420 s | `run_screen.py:58, 118`, `run_pilot.py:60`; PROTOCOL 2026-10-15/16 | mitigated; a stall still shows as a timeout |
| H14 | Review `steps=1` as a stall guard | validation | narration contamination, no benefit → rejected | PROTOCOL 2026-10-15 | closed |
| H15 | Token accounting ignored cache (Luna ≈ 40× understated) | D measurement | six token fields; `token_totals.py` for old runs | `run_screen.py:91`, `scripts/token_totals.py` | fixed; cost not scored in phase 1 anyway |
| H16 | Venv inside the repo could not start under the sandbox (teammate) | E008 (Chloe) | metadata allowed on the interpreter's ancestors; team venv outside the repo; `check_env` starts the sandboxed python and checks location, Python 3.13 | `run_screen.py:35`, `scripts/setup_env.sh`, `check_env.py:62, 88` | mitigated (not reproduced on Bo's machine); interpreter recorded in every `meta.json` |
| H17 | Results and summaries landed in the wrong experiment folder (own D copy; Chloe's runs under E009); subset runs overwrote full summaries; repeats overwrote r1 | 10-19/20 | `POPPY_EXP`, `POPPY_QSET`; summaries next to results; `PILOT_REPS`; Chloe's runs moved with `git mv`, B folder renamed to its prompt versions | `run_pilot.py:480`, `scripts/collect_runs.py` | fixed |
| H18 | Framing distinctness over-counts (free-text fields) | D | `n_distinct_analytic`; hand coding for scoring | `run_pilot.py:440` | mitigated; phase 2: controlled vocabulary in the plan declaration |
| H19 | CHART CHECK is a record, not proof that the image was used | v3 draft | image-withheld control (`PILOT_NO_IMAGE`); token delta | `run_pilot.py` `ATTACH_CHART` | mitigated (1 control item) |
| H20 | Two draft docs committed by mistake (10-14) | — | untracked + excluded; still in history | `.git/info/exclude` | open: purge needs a force push, decision pending |

## P — model behaviour (what the arms measure)

| ID | Problem | Evidence | What exists today | Status |
|---|---|---|---|---|
| P1 | **Silent errors**: NULL-dropping sum (A2), wrong ranking (K2), "gap" that is a ratio (K3), unsupported causal aside (K1), invented or downloaded exposure (I1) | `ITERATIONS.md` iterations 2–3; `phase1-summary.md` finding 1 | detection: B's reviewer (model; mimo flagged real issues on 5/5 runnable items, Luna on 2/6); `gold_cover` for plotted numbers only; humans with the trap sheet. **No automated check of numbers in the prose or of claims** | open → phase 2: recompute oracle, claim judge |
| P2 | **Misleading framing**: undisclosed borough filter (A1, 3/3 D runs, all options; A/C too), per-reported-crash denominators across the 2020 change (A1 3/3, I1 2/3) | `E009-enumerate/ITERATIONS.md`; `SCORING.md` §4 | nothing automated; not caught by C's self-check nor by D's per-option review; humans with the trap sheet | open → phase 2: framing check (plan vs gold plan + trap catalog), the fourth silent-error component |
| P3 | Exploration drift on ambiguous questions: A1 builds a borough classifier and hits the cap (mimo A 0/2, C 0/1) | `ITERATIONS.md` | baseline behaviour; Luna completes A1 | recorded → phase 2: plan declaration with answerability |
| P4 | Review listed "cannot verify" as issues → false revise trigger (K1) | iteration 1 | `UNVERIFIED` section (v3) | fixed (prompt) |
| P5 | "No problems is normal" sentence lowered review sensitivity (K1, K3 misses) | iteration 2 | removed (v4); K1 caught again; K3 "gap" still missed | fixed / one known miss |
| P6 | Review did pixel-geometry reasoning on "cut-off / overlapping" → 14k reasoning tokens, second request, stall | iteration 2 A2 | descriptive CHART CHECK (v4) | fixed |
| P7 | Self-check instruction (C) burns the step budget on the small model (2/6) and not on Luna (6/6) | C v3 format check | none (C is frozen, not tuned) | recorded: capability, not wording |
| P8 | Reviser re-runs the full analysis for text-only fixes | iteration 2 K2 | none; architecture decision deferred | parked → phase 2 candidate (design §7) |
| P9 | Luna reviewer flags issues on 2/6 items vs 5/5 on mimo; unknown whether leniency or fewer errors; missed I1 y-axis starting at 70 (Chloe) and K3 "gap" | E008, `phase1-summary.md` finding 4 | none | open → blind scoring now; phase 2: calibrated judge + code chart checks |
| P10 | D's top-probability option is the typical answer (5/6 questions, 3/3 runs) | `E009 ITERATIONS.md` | — | recorded (finding, matches VS) |

## R — protocol and process

| ID | Problem | Fix / decision | Status |
|---|---|---|---|
| R1 | B was tuned on the 6 pilot questions that are now the comparison set | caveat stated in `SCORING.md` and `phase1-summary.md`; P1–P10 held out | open limitation |
| R2 | Single runs per cell (mimo all arms; Luna A/B/C); D shows run-to-run variance | repeats when time allows; cells stated as single runs | open |
| R3 | Acceptance was effect-based (would favour B) | contract-based acceptance | fixed (PROTOCOL 2026-10-15) |
| R4 | Two prompt edits in one iteration (v4) | attribution limit stated | recorded |
| R5 | Rules found missing after the fact (A2 timeout class; stall) | amendments, never retroactive | fixed |
| R6 | Results pushed straight to main instead of PR (Chloe, Jamie) | reminder; harness prints the PR command | open (process) |
| R7 | Rubric inconsistency (8 binary vs 0–12) | 8 binary adopted | fixed |
| R8 | Blind human scoring not done; slow and unstable | this discussion (automated primary + human freeze review) | open |
| R9 | Two Claude sessions editing the same docs | pull/rebase before push | process |
| R10 | Gold encodes interpretive choices (A1 borough filter, A2 window, P5 "Unspecified") | documented in `ground-truth-audit-2026-10-21.md`; scorer must accept disclosed alternatives | fixed (documented) → phase 2: gold plans |
| R11–R13 | Three wrong statements in our own records (E004 "network disabled"; "I1 recalled numbers"; K2 revise cost) | corrected in place with dated notes | fixed |
