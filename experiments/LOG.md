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
