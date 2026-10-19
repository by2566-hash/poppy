# Experiments Log

Format (from the 99P Labs capstone instructions): date — experiment id and name. What we attempted and how it was set up. Result, including failures and partial successes. What we will try next. Keep entries brief.

Copy entries into the team's Google Sheet when ready.

---

## 2026-10-03 — E000: Can Codex be used as a clean baseline subject?

- **Setup:** ran `codex exec` (CLI 0.159.2, ChatGPT login, gpt-6-luna) with `-c project_doc_max_bytes=0` and asked whether any user/AGENTS.md instructions were in context.
- **Result:** the user's global `~/.codex/AGENTS.md` was still loaded, and the default profile also starts MCP servers (e.g., Figma). The global instructions include "separate verified facts from assumptions" and "consider data quality", which would inflate exactly the behaviors we measure (stating assumptions, flagging traps).
- **Next:** run baseline subjects from a separate `CODEX_HOME` with its own login and a minimal config. Never symlink or copy the main `auth.json` (token refresh could invalidate the main login).

## 2026-10-03 — E001: NYC crashes data card and trap verification

- **Setup:** typed the NYC crashes CSV to Parquet with DuckDB; profiled all columns and ran saved T1–T8 queries.
- **Result:** 2,269,187 source rows = 2,269,187 Parquet rows; 2019–2020 declines include PDO and injury crashes; missing borough/location and unspecified causes are material; one literal e-bike spelling misses most regex-matched labels. An initial regex escape returned no T6 matches; corrected and reran.
- **Next:** use this catalog to define E002 expected trap flags and interpretation coverage; keep outcome counts distinct from exposure-adjusted safety.

## 2026-10-03 — E001-review: independent verification of the Codex data card

- **Setup:** re-ran T1, T3, T5, T6 and T8 with independent DuckDB queries (not Codex's SQL). Also profiled the Codex run from its JSONL trace.
- **Result:** T1, T3 (30.47% missing borough), T5 (33.34% "Unspecified") and T8 match exactly. **T6 was misleading:** Codex's "one spelling misses 59.44%" mixes e-bikes with e-scooters and mopeds. For e-bikes alone, the exact spelling `E-Bike` covers 12,246 of 12,621 crashes (97%). The real micromobility trap is **category drift over time**: e-bike crashes 23 (2018) → 2,688 (2021) → 1,411 (2025) while moped crashes 193 → 693 → 1,859 and scooter crashes fell 1,725 → 591 in 2024 → 2025. A single-category trend can look like improving safety when the cause may be reclassification (cause unverified). Codex run cost: 12.2 min wall clock, 24 shell commands (3 failed, including a regex-escape bug it caught and fixed), 2.31M input tokens (96% cached), 36.7K output tokens; actual data processing took 7 s.
- **Next:** replace T6 in the answer key with T6b "category drift" for Q08; keep independent verification as a standing rule for agent-produced numbers (this is itself an example of the judgment failure Poppy targets).

## 2026-10-03 — R001: Scenario and data due diligence (research, with spot checks)

- **Setup:** compared NYC, Chicago, Ohio/Columbus, FARS and Montgomery County with server-side SoQL/ArcGIS aggregation and FARS header reads; collected real public vague questions; built a unified trap catalog (`docs/scenario-data-v1.md`). Re-checked the two most consequential new traps on our snapshot.
- **Result:** NYC wins on trap richness and relatability; MVP bundle = crashes + injured/killed persons + East River bridge bike counts (~4–6 DE hours). Ohio has no scriptable public bulk download. Two earlier claims were wrong: Person/Vehicles start 2012-07-01 (sparse before Apr 2016), and the freeze is worse than "pending". Verified: killed count NULL in 87.8% of May-2026 and 100% of June-2026 rows (TR08); hidden e-rider injuries outside all mode columns since 2021, 2,132 → 1,405 per year (TR03). E001 (Codex) missed both.
- **Next:** team decision on Monday; fetch persons + bike_monthly once the bundle is agreed; run E002 when the clean Codex profile exists.

## 2026-10-03 — E003-smoke: Can OpenCode free models serve as the baseline subject?

- **Setup:** OpenCode 1.18.34, no account or API key. `opencode models` lists 8 free Zen models (big-pickle, nemotron-3-ultra-free, mimo-v2.6-flash-free, …; `jev-1.13-free` is not listed without a Zen key). Hello test with `opencode run --pure --format json`. Then Q02 with the plain prompt in a sandbox outside the repo, with a project `opencode.json` that allows only python/ls/cat/head/mkdir and denies web fetch and external directories (OpenCode has no OS-level sandbox, unlike Codex).
- **Result:** hello test passed on big-pickle (25 s) and nemotron-3-ultra-free (4 s), cost $0, token counts present in `step_finish` events, so JSON events work as traces. Running two `opencode run` processes in parallel failed: one died with "database is locked" (shared SQLite state in `~/.local/share/opencode`) and the other hung with no events for 10 min. Sequential runs work.
- **Next:** run subjects sequentially (or give each run its own `XDG_DATA_HOME`); finish the Q02 comparison and write an OpenCode subject runner.

## 2026-10-03 — E003-smoke result: two free OpenCode models on Q02

- **Setup:** sequential runs of nemotron-3-ultra-free and big-pickle on Q02 ("Are cyclists safer in NYC than they used to be?"), plain prompt, restricted sandbox. Details in `experiments/E003-opencode-smoke/REPORT.md`.
- **Result:** both PROCEEDed with one reading, never asked or enumerated, flagged 0 of 4 answer-key traps, and made misleading claims. nemotron "proved" cyclists are less safe by dividing by total crashes, whose count collapsed after the 2020 NYPD recording change (TR01). big-pickle compared against half-year 2012 (TR09). ~2 min and $0 per run.
- **Next:** make OpenCode free models the main baseline (B1-open); Codex stays as a frontier reference. Write an OpenCode subject runner (sequential, per-run data dir), then run all 8 questions × 2–3 free models.

## 2026-10-04 — E004: OpenCode free-model baseline, 8 questions × 3 models

- **Setup:** nemotron-3-ultra-free, big-pickle, mimo-v2.6-flash-free; plain prompt; per-run sandbox and `XDG_DATA_HOME` (parallel works), 900 s timeout. 24 runs + 1 retry, ~50 min, $0.
- **Result:** 18 answered, 5 timeouts (mimo 4, big-pickle 1), 1 infra failure (NVIDIA upstream 503, retry hung). Acceptable decision: big-pickle 7/7, mimo 4/4, nemotron 4/7. big-pickle asked on both ASK questions but only after long exploration; mimo timed out on both without asking. nemotron's Q02 conclusion flipped between E003 and E004 runs. New failure mode: unsourced numbers from model memory (population, DOT mode data). Scores in `experiments/E004-opencode-baseline/SCORES.md` (Claude-scored, needs human check).
- **Next:** 3 repeats per cell; run the B2 policy prompt on the same models; add decision-latency, timeout, unsourced-number and consistency metrics; credit valid unlisted traps.

## 2026-10-13 — E005-smoke: Can the free OpenCode models read a chart image?

- **Setup:** one existing 4-panel matplotlib chart, renamed to a neutral `chart.png`, attached with `opencode run -f chart.png -- "<question>"`. Asked three details only visible in the pixels (top-right panel title, bottom-right line color, highest y-axis tick bottom-left), with an explicit `NO_IMAGE` escape. Note: `-f` is an array option, so the message must follow `--`.
- **Result:** big-pickle → `NO_IMAGE`; nemotron-3-ultra-free → `NO_IMAGE`; mimo-v2.6-flash-free → all three correct. In E004 every model's `read` tool reported "Image read successfully" on PNGs, which only means the file loaded, not that the model saw it. n = 1 image: a capability check, not an accuracy estimate.
- **Next:** with big-pickle as the single model, any critique step must work on text (analysis plan, chart spec, computed result table), not pixels. Pixel critique is only possible as a separate mimo variant, which would change the model and confound comparisons.

## 2026-10-14 — E006-setup: Can a free OpenCode model be run as a single tool-less call?

- **Setup:** wanted step ① of phase 1 as one call, no tools. Tried `opencode run` with permission and tool configs on mimo-v2.6-flash-free (trivial and real prompts, 2 repeats each).
- **Result:**
  1. **With the default config mimo is an agent even when told to reply in a fixed format**: 13 tool calls in 99 s, including `find` outside its sandbox and reading other runs' logs. "Single call" cannot be enforced by the prompt.
  2. **Free-tier gateway rejects requests with HTTP 403 ("free tier can only be used from within OpenCode") when `bash` or `read` is disabled** (`permission.bash: "deny"` or `tools.bash/read: false`). Disabling any other tool, or restricting bash with command patterns (as in E004), is fine. So tools cannot be removed.
  3. **`agent.build.steps: 1` works**: one step, 0 tool calls, 14 s, code block and `ANSWER:` present. (`maxSteps: 1` behaved the same in this version.)
  4. A first screening batch ran with the all-deny config and every call stalled to the 300 s timeout or returned 403; it was invalid and discarded.
- **Next:** rerun the mimo stability screen with `steps: 1` (call success, format compliance, code execution, repeat consistency) and the image-reading test.

## 2026-10-14 — E006: mimo-v2.6-flash-free as the single phase-1 model

- **Setup:** step ① on 6 clear questions × 3 repeats as a bounded agent run (steps ≤ 10, python-only bash, sandboxed); chart-reading test on 5 charts × 3 questions. Details: `experiments/E006-mimo-screen/REPORT.md`.
- **Result:** 18/18 completed, 0 timeouts, chart + values + answer every time, gold numbers matched on all 18 (16 at 100%, 2 at 90%: P5 repeats disagree on whether "Unspecified" counts), median 65 s and 6 tool calls. Chart reading 5/5. Two earlier screens were invalid and discarded: `steps=1` made every reply a "maximum steps reached" narration; the first batch hung because background `opencode run` waits on an open stdin.
- **Next:** team decides whether step ① is a bounded agent run (recommended) or a direct API call; run the same screen on the ambiguous and insufficient-evidence questions; pilot round for B and C prompts.

## 2026-10-14 — E006-b: ambiguous and insufficient-evidence questions (P7–P10) on mimo

- **Setup:** same bounded-agent screen, 4 questions × 3 repeats at cap 10 / 420 s, then at the proposed formal config cap 15 / 600 s.
- **Result:** completion 9/12 (cap 10) and 10/12 (cap 15), vs 18/18 on clear questions; median 198 → 263 s; 8/12 used the full step cap in both. Failures: one client crash (infrastructure), two timeouts, two missing charts. Every borough table dropped the unknown-borough group without comment (TR05); P9 runs consistently stated that per-ride risk cannot be computed.
- **Next:** formal config fixed at steps 15 / timeout 600 s for all arms; pilot round E007 (pre-registered protocol) started.

## 2026-10-14 — E007 iteration 1, and the rate limit

- **Setup:** pilot round per `experiments/E007-pilot-prompts/PROTOCOL.md` (pre-registered, commit a1f89a9): 6 pilot questions disjoint from the 10 formal ones, mimo, bounded agent run (15 steps, 600 s). Iteration 1: A baseline (2 repeats) and C v1.
- **Result:** A 7/12 gate pass (clear 6/6; ambiguous 1/4; insufficient 0/2), C v1 4/6 with no flips; C used ~60% more steps on clear questions with no gate change. On the insufficient-evidence item both arms imported recalled mileage numbers (unsourced), and runs that reached the step cap ended in "maximum steps reached" narration (counted as non-completion).
- **Failure:** B v1 and C v2 produced empty critiques and 6/6 timeouts. Cause: free-tier rate limiting (`Rate limit exceeded`), invisible in the event stream because OpenCode retries silently; mimo and big-pickle limited for ≥ 45 min, nemotron still served. Batch discarded, harness fixed to detect it.
- **Next:** wait for mimo's quota or switch the single model after a stability screen (decision for the team); then re-run B v1 and C v2.

## 2026-10-14 — E007 scope v2, B v2 and team setup

- **Setup:** pilot narrowed to A and B (C written after the freeze); A frozen at v1. B v2: the review run cannot execute code and gets A's chart attached plus values, answer and code embedded; it returns a numbered `ISSUES:` list or `ISSUES: NONE`; the revise run happens only if issues were reported and must keep unflagged parts unchanged. Team tooling: `requirements.txt`, `scripts/check_env.py` (OpenCode 1.18.34, data content fingerprint), config templates in `experiments/E007-pilot-prompts/config/`, `scripts/collect_runs.py` (runs into the repo via PR), concurrency default 1.
- **Result:** pipeline test on one item with nemotron (mimo rate-limited): review used 1 step and 0 tool calls and raised 2 specific, verifiable wording issues; revise kept every number and listed each change. Not a pilot result. A-v1 and C-v1 runs collected into `results/`.
- **Next:** B v2 iteration on mimo when quota allows; one teammate checks whether the rate limit is per machine.

## 2026-10-15 — E007: B v2 iteration 1 on mimo; the model could reach the internet

- **Setup:** Chloe ran B v2 (review + revise) on A-v1 r1 for the 6 pilot items on her machine, mimo, OpenCode 1.18.34 (`results/B-v2-validation/`). Claude re-checked each item against `values.csv`, gold and DuckDB, and scanned every committed event trace for external calls.
- **Result:** 4 items ran (K1, K2, K3, A2), review used 0 tools, 0 correct numbers changed. Real errors found and fixed on K2, K3 and A2 (A2: `SUM(injured + killed)` silently dropped rows with NULL killed; corrected values match DuckDB). Weaknesses: "cannot verify" remarks are numbered as issues, so the review never says NONE and a revise run is triggered on a correct item (K1, 7 steps); no critique records what it saw in the chart. A1, I1 not run: A had no answer. The sandbox leaked: A-v1 I1 r1/r2 downloaded vehicle-mile data (`websearch` tool, `urllib` in python), and E004 big-pickle Q02/Q03 used `websearch`; `webfetch: deny` covers neither.
- **Next:** `websearch: deny` plus python under `sandbox-exec` without network (checked by `check_env.py`); I1 r1/r2 void and re-run; B runs only when A produced an answer; B v3 prompts (Bo) against agreed acceptance criteria.

## 2026-10-15 — E007: B contract, sandbox v2, B v3 draft end-to-end

- **Setup:** acceptance redefined as the B contract (inputs, outputs, boundaries, end states), checked by `check_contract.py`. Audited every committed trace for out-of-folder access; red-teamed OpenCode tools and the OS sandbox with nemotron; ran B v3 draft end-to-end on mimo (A-v1 K1-r2, K2-r2) and re-ran the void A-v1 I1 under the new sandbox.
- **Result:** boundary gaps found and closed: python could read gold answers and write into the repo, the review folder inherited the analysis permissions, C-v1 I1 listed the repo root. Sandbox v2 (all commands under sandbox-exec, own data copy, isolated review folder) blocks every tested escape. B v3 draft: 2/2 items pass the contract; unsupported causal claims now routed to ISSUES and removed by revise without touching numbers. I1 re-runs complete in 8 and 11 steps without network but still claim a per-mile decline from crash data alone.
- **Next:** Bo finalizes v3 prompts; B iteration 2 on the six pilot items (A-v1 r1 inputs) under the contract.

## 2026-10-15 — E007: B v3 iteration 2 on mimo

- **Setup:** B v3 prompts (Bo approved), A-v1 r1 inputs (I1 re-run under sandbox v2), six items, contract check plus Claude's human checks; team second review pending.
- **Result:** K1, K3 NONE (A carried forward); K2 one real issue fixed; I1 three real issues fixed, one visible only in the chart; A1 skipped (no A answer); A2 review timed out after one step with no output (B fails the item). No boundary violation, no invented issue, no unflagged change, values.csv unchanged everywhere. Whether A2's non-completion counts as the one allowed slip is a team decision.
- **Next:** team second review (`check_contract.py results/B-v3-v3 --show`); decide on A2; freeze B v3 or run iteration 3.

## 2026-10-16 — E007: B v4 iteration 3; prompts frozen

- **Setup:** Bo's decisions after iteration 2: two critique edits (removed "finding no problems is a normal result…"; CHART CHECK asks what is seen, not overlap checks), zero-output timeout retried once, iteration 3 is the last. Prompts committed before the run (281692d). Six pilot items, A-v1 r1 inputs.
- **Result:** contract passes on all 5 runnable items (A1 skipped): no boundary violation, no invented issue, no unflagged change, no stall, no retry, every review one step. K1, K2, A2, I1 revised with real issues; K3 NONE. A2's review finished in 164 s. B frozen: critique v4 + revise v3 (`FROZEN.md` with SHA-256).
- **Next:** team second review of the records; Bo writes C; formal run plan (10 questions × 3 repeats, split across three machines).

## 2026-10-19 — E007: C fixed (v3) and format-checked; phase-1 comparison set decided; harness for Luna and arm D

- **Setup:** team decided the phase-1 comparison set is the 6 pilot questions (P1–P10 held out for phase 2). Bo fixed C at v3 (A + one self-check sentence mirroring the review's categories); one format-check run on mimo, no tuning. Harness: provider-qualified model ids, `.env` key loading, `POPPY_EXP`/`POPPY_QSET` switches, arm D (`run_pilot.py D`), `check_model_vision.py`.
- **Result:** C-v3 on mimo: 2/6 complete under the strict rule (K1, K3); K2, A2, I1 produced chart and values but hit the 15-step cap on extra verification passes; A1 drifted like A. The self-check sentence roughly doubles steps on clear questions. No boundary violation. The step cost is C's result on this model, not a format defect.
- **Next:** teammates run A/B/C on GPT-6 Luna (E008-lite); Bo measures D's step need on K1 and A2 with Luna, sets the cap, then tunes the D prompt on the 6 pilot questions (E009-lite); slides updated to frozen-version outputs.

## 2026-10-19 — E009-lite: arm D measurement runs on GPT-6 Luna; token accounting fixed

- **Setup:** Luna pre-checks passed (key from git-ignored `.env`, model listed, reads an attached chart). Arm D draft prompt (C v3 + "give 3 framings", options.json + 3 charts and value files) on K1 and A2, step cap 30 only to measure.
- **Result:** both complete in 11–12 steps, 76–108 s. K1: three chart types of the same correct series (only encoding varies, as expected for a clear count question). A2: three different analytic framings (counts, share of harmful crashes, people harmed per 100 crashes), each stating that exposure data is missing; the harm rate matches DuckDB and avoids the NULL-sum error mimo's A made in iteration 1. Found a harness defect: only input/output tokens were summed; Luna reports ~99% of input as cache, so costs were understated ~40×. Fixed; older runs recomputable from events.
- **Next:** Bo sets D's step cap; acceptance round on the 6 pilot questions; distinctness reported with and without chart type; framings coded by hand for scoring.
