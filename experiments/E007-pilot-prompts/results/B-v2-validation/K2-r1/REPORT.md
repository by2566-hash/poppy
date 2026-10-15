# B v2 validation — K2, single item (provisional)

**Status: provisional, second of six.** Per `PROTOCOL.md` scope v2, acceptance requires all 6 pilot items in one iteration, scored together. K1 + K2 together still do not establish acceptance and do not justify freezing B.

## 1. Outcome and execution status

**Complete.** `review_ok: true`, `n_issues: 2`, `says_none: false`, `revise_ok: true`, `revised_png: true`, `revised_values: true`, `answer_ok: true`. No errors, no rate limiting, no step-cap narration in either the review or revise run.

| | Review | Revise |
|---|---|---|
| Steps | 1 | 4 |
| Tool calls | 0 | 4 |
| Wall time | 58.1 s | 48.1 s |
| Session ID | `ses_ec28b0110ffeoIqxv0DXER8Kgx` | `ses_ec28a1f0bffe0DwLhmwFvjQtiZ` |

Run window: 2026-10-15 02:47:18–02:49:05 UTC (2026-10-14 22:47:18–22:49:05 EDT). Model `opencode/mimo-v2.6-flash-free`, OpenCode `1.18.34`, Python `3.13.13`, repo commit at run time `be48b01` (unchanged since K1; `run_pilot.py`'s own sha is not separately recorded by the runner, but its content is identical to the version inspected for K1 — confirmed by `git log` showing no new commits since `be48b01`).

**No newer repository instructions conflict with this task.** `git log` shows no commits since `be48b01` (the HEAD used for K1); all required files (`AGENTS.md`, `direction-v1.md`, `status-2026-10-14.md`, `PROTOCOL.md`, `ITERATIONS.md`, `run_pilot.py`, `collect_runs.py`, both B prompts) are unchanged from the K1 session.

**Environment, re-verified before this run (not assumed from K1):**
- `check_env.py` → `READY` (OpenCode 1.18.34; duckdb 1.4.4, pandas 2.2.3, pyarrow 19.0.0, matplotlib 3.10.0, exact pins; parquet fingerprint OK; same 1 harmless warning as K1).
- `check_free_models.py mimo-v2.6-flash-free` → `OK`, 4.0 s, checked 2026-10-15 02:46:20 UTC.
- **B prompt hashes match K1 exactly** (confirmed, no drift): `B_critique.v2.md` = `9a15fd17aad323b8a76e2b4f0cd8e4c42a06c439a8bec8a6288df966425c92f5`; `B_revise.v2.md` = `21b29bb2097e08a5c31714323cf3bea78330679e193d6fa616287feba2ac078a`.
- **PATH fix re-verified as per-invocation, not persistent** (as K1 found): a plain subprocess without the prefix still resolves `python3` to `/opt/homebrew/opt/python@3.14/bin/python3.14` with `ModuleNotFoundError: No module named 'duckdb'`; prefixing `PATH="/Users/chloehe/poppy/.venv/bin:$PATH"` resolves correctly (`duckdb 1.4.4 pandas 2.2.3 pyarrow 19.0.0 matplotlib 3.10.0`). The actual run confirms this worked: the revise step's `python3 analyze.py` call (event 9 in `events.jsonl`) ran to completion and printed its full output table with no import error — no install detour was needed, unlike the original A-V1-Test incident.

## 2. Source A identification

Used exactly the team's original, frozen result — no staging copy was made (same finding as K1; re-verified this session, not assumed).

- Path: `experiments/E007-pilot-prompts/results/A-v1/K2-r1/`
- Question (from `pilot_questions.json`, id `K2`, type `clear`): *"How are NYC crashes distributed across the days of the week, 2013 to 2025?"*
- Added to git at commit `6c4f6df` ("E007 scope v2: A+B pilot...")
- `collected_by` (A's `meta.json`): `by2566-hash` (teammate's original submission, not mine)
- A's own `meta.json` predates the `env` field (pre-instrumentation run); `a_git_commit: null` in B's `meta.json` is expected, same as K1.
- Session ID of A's original run: `ses_ec6d73271ffeoxyCAw10zgokZy`

SHA-256 of the A input artifacts actually used by this run:
| File | SHA-256 |
|---|---|
| `meta.json` | `4c2f27f0825516b9c0503431edfbd32f5185302b372ab3e7fcfbb9b7bf877866` |
| `response.md` | `8937a38175cbc276fc9fce45f2ba08ae2366bace5a06e59dfa2386eb4d9687b3` |
| `analyze.py` | `98da29d38d317c4a3b747ee922db6adbc1c6f220c02139fce8adea01b808e678` |
| `opencode.json` | `e121e93ce4f398aa64f4aefd55055be93b6f80c2f79997533b8edf145b5c4a65` |
| `events.jsonl` | `fe6836a44f798b0b99fc703204d8a09003a45d69017cce4fae5a7c094d183775` |
| `out/values.csv` | `895f9b269ba877932a368c156a159097cf05a28ba0b3cff9e3457ac19ce1b15a` |
| `out/initial.png` | `3a387d55ef1f2a73b97b19d8978b892e0d6236c52b406ea79fe5fcc475ff22a2` |

Unlike K1 (which only had reconstructible bash-event code), K2's A result has a committed `analyze.py` — `run_pilot.py`'s `code_of()` prefers saved `.py` files over event reconstruction, so the critique prompt received this exact script verbatim as "Code that produced them," not a reconstruction. Verified present and faithful before the run: chart (1950×825 PNG), `values.csv` (7 rows, Mon–Sun), a written `ANSWER:` line, and `analyze.py`. No essential review material was missing.

**Confirmed: the runner reads A directly from the repo, not a sandbox staging copy** — same as K1's finding, re-checked against the current `run_pilot.py` (`src = RESULTS / a_label / f"{q}-r{rep}"`, `RESULTS = HERE / "results"`). Used `A-v1` as the label directly; no `A-v1-input` staging directory was created, and none was needed.

**Isolation of evaluation material confirmed:** `run_B`'s `shutil.copytree(src, sb, ignore=shutil.ignore_patterns("events*.jsonl", "response.md", "meta.json", "critique.md"))` copies only `analyze.py` and `out/` from A's committed folder into B's working sandbox — this K1 report, `gold_pilot.json`, `ITERATIONS.md`, and all other evaluation material live outside `experiments/E007-pilot-prompts/results/A-v1/K2-r1/` and were never copied into the model's working directory.

## 3. Artifact checklist

| File | Present | Check |
|---|---|---|
| `meta.json` | yes | valid JSON |
| `opencode.json` (revise/analysis config) | yes | valid JSON, matches frozen `config/opencode.analysis.json` (sha `93f72e58...`) |
| `opencode_review.json` (review config, added manually — see §5) | yes | valid JSON, matches frozen `config/opencode.review.json` (sha `5a5a4cb0...`) |
| `events.jsonl` (revise run) | yes | 14 valid JSONL lines |
| `events_review.jsonl` (review run) | yes | 3 valid JSONL lines |
| `critique.md` | yes | parses as `ISSUES:` + 2 numbered items |
| `response.md` (revise output) | yes | contains `CHANGES:` and `ANSWER:` |
| Model-generated `.py` files | yes | `analyze.py` (edited copy of A's script — see §4) |
| `out/initial.png` | yes | opens via PIL, 1950×825 PNG, byte-identical to A's source hash above (carried forward, not regenerated) |
| `out/values.csv` | yes | readable, 7 rows, byte-identical to A's source |
| `out/revised.png` | yes | opens via PIL, 1950×825 PNG |
| `out/revised_values.csv` | yes | readable, 7 rows, identical values to `values.csv` (diff: none) |

All JSON/JSONL files parse; both PNGs decode and load via PIL; both CSVs parse with the expected header and full Mon–Sun coverage. **Successful decoding is not visual correctness** — see §4's separate visual assessment.

## 4. Issue-by-issue evaluation

Independent cross-check: `gold_pilot.json`'s K2 series (not shown to the model) — same 7 day-of-week counts as A's `values.csv`, under a different index convention (gold's index 0 = Sunday vs. A's ISO `%u` where 1 = Monday), noted previously in `ITERATIONS.md` as "not an error." A's underlying counts were correct on this item.

**Issue 1** (`critique.md`): *"the sentence ranks weekdays in descending order, but Tue (313,488) actually exceeds Wed (311,111), so the 3rd/4th place order is wrong... 'steady build to Friday' is also not strictly true."*
- **Classification: demonstrated substantive error**, not a verification limitation or a cosmetic remark. Checked directly against `values.csv`: Tue = 313,488, Wed = 311,111 — Tue is in fact larger. A's original `ANSWER:` listed "...then Wed (311,111), Tue (313,488)..." as a descending sequence, which puts the smaller value first — a real ordering/characterization error, and the critique states exactly what is wrong (which two values), where (the ranking clause), and why it matters (misleads a reader about the actual pattern), per the critique prompt's required format.
- **Repaired, and correctly scoped:** the revised `ANSWER:` reorders to "...then Tue (313,488) slightly ahead of Wed (311,111) — a mild mid-week dip rather than a monotonic rise..." — numerically correct and no longer claims a monotonic rise. `CHANGES:` item 1 states exactly this fix. **Repair effective.** No data, filter, or chart-code changes were made (`analyze.py`'s diff against A's version is two lines, both output filenames — `values.csv`→`revised_values.csv`, `initial.png`→`revised.png` — confirmed below).

**Issue 2** (`critique.md`): *"Nothing else could be verified as wrong: the totals..., shares..., Fri/Sun = 32%, weekday share 74.4%, n_days..., per-day averages, and all chart labels/values match the supplied values.csv. Whether the source data is truly 'police-reported' and whether the parquet actually contains 2013–2025 records cannot be checked from the material given."*
- **Classification: verification limitation / uncertainty, not a demonstrated error and not an invented problem.** The first clause is a positive confirmation (everything else checks out against the supplied CSV), not a flaw. The second clause names a specific, genuine gap — the reviewer has no access to the underlying parquet file (by the review config's own no-exec, no-filesystem-access design) and correctly says so instead of asserting or guessing that the data is wrong. Per this task's framing: missing verification evidence is **not** treated here as proof of incorrect data, and none was found to be incorrect — A's counts are in fact correct against independent gold.
- **Repair: not applicable** — this is not an actionable defect; nothing needed to change. Note, however, a **format-compliance gap**: the revise prompt's template is `CHANGES:\n1. <issue number>: <what you changed, or "not changed" and why>`, implying one line per numbered issue. `response.md`'s `CHANGES:` block contains only one line, for issue 1; issue 2 is not explicitly acknowledged as "not changed, because..." This is a minor auditability gap (a reader of `CHANGES:` alone cannot tell issue 2 was considered and correctly left alone, versus silently dropped), not a correctness problem — flagged as a candidate prompt observation in §7, not scored as a repair failure since no repair was actually required.

**No invented substantive errors; no unsupported claims.** Neither numbered issue misstates what A actually produced.

**Unrelated correct content preserved, confirmed by direct diff:** `analyze.py` in this run differs from A's committed script by exactly two lines, both output filenames (`out/values.csv`→`out/revised_values.csv`, `out/initial.png`→`out/revised.png`); the DuckDB query, date filter, day-name mapping, and chart code are untouched. `values.csv` and `revised_values.csv` are byte-for-byte identical (diff: none). **Zero correct→incorrect flips.**

**New substantive errors:** none found.

**Consistency (chart / CSV / answer):** confirmed both by file diff and by direct visual inspection (§5) — the revised `ANSWER:`'s per-day figures, percentages, and the Fri/Sun and weekday-share claims all match `revised_values.csv`, which is identical to `values.csv`.

**Does the combined chart + CSV + answer satisfy the actual question** ("How are NYC crashes distributed across the days of the week, 2013 to 2025?")? **Yes, both before and after revision.** Unlike K1, this question does not ask for an itemized "each X" breakdown; A's original prose already named all seven days with counts and percentages — the revision fixed a characterization error, not a completeness gap. Per the task's instruction, the prose was not expected to restate every plotted value digit-for-digit, and it does not need to.

## 5. Post-run visual assessment (Claude's own, separate from mimo's critique)

I directly opened both `out/initial.png` and `out/revised.png` without regenerating them.

**Observations:**
- Both charts are two side-by-side bar panels: total crashes by day (left) and crashes-per-occurrence (right), Mon→Sun, with Sat/Sun bars in a different color from the weekdays. Axis labels, titles, and tick labels are all legible and correctly oriented; no clipping or label overlap in either panel.
- Bar-top labels match `values.csv`/`revised_values.csv` exactly: 304,518/14.3%, 313,488/14.7%, 311,111/14.6%, 318,376/14.9%, 338,800/15.9%, 288,381/13.5%, 257,544/12.1% (left panel); 449, 462, 458, 470, 500, 425, 380 (right panel, matching `avg_crashes_per_day` rounded to the nearest integer).
- `out/initial.png` and `out/revised.png` are **visually indistinguishable** — same figure, same data, same style — though not byte-identical (sha256 differs: `3a387d55...` vs `e910286e...`), most likely matplotlib/PNG encoder metadata (e.g., embedded timestamp) rather than a rendering difference, since the underlying script and data are identical apart from the output filename.
- **Limitation of the chart itself, not a defect in this run:** the Tue-vs-Wed bar-height difference that issue 1 is about (313,488 vs. 311,111, a ~0.7% gap) is not visually distinguishable at this chart's scale — the only reliable way to see the correct ordering is the printed numeric labels, not the bar heights. This is worth the team's awareness if the chart alone (without labels) is ever used, but it is not something this run's revision could or should have changed.

**What this establishes about image delivery to mimo, and what it does not:** `run_B` attaches the chart to the review call via `call_model(..., files=[rd / "chart.png"])`, which `run_screen.py`'s `call_model` passes to OpenCode as `-f <path>` on the `opencode run` command line — a real multimodal attachment, not just a path mentioned in text (status doc notes mimo is "the only free model that reads images, which B's review step needs"). However, **nothing in `critique.md`'s text makes a claim that could only come from looking at the image** (e.g., no comment on color, legend, or a visual-only detail not already in the embedded CSV/code) — both issues are fully explainable as csv/text-only reasoning. I therefore cannot confirm from the critique's content alone that the model actually inspected the attached image rather than just the embedded text, and I am not inferring either way: the attachment mechanism is confirmed working, but active visual inspection by the model is **unconfirmed, not disproven**, from this item's evidence.

## 6. Audit details

**Files `collect_runs.py` omits (manually preserved here, same as K1):**
- `review/opencode.json` (the review step's effective, no-execution config) — added here as `opencode_review.json`.
- `review/chart.png` — byte-identical to `out/initial.png` (also confirmed identical to A's source `initial.png` hash), so no information is lost by not separately keeping it.
- `review/stderr.log`, top-level `stderr.log` — machine-specific, excluded per the script's own docstring.
- `.ocdata/` (OpenCode's private per-run session dir and local `opencode.db`) — correctly excluded; not inspected beyond confirming exclusion.

**Hashes of prompt files and effective configs used by this run:**
| File | SHA-256 |
|---|---|
| `prompts/B_critique.v2.md` | `9a15fd17aad323b8a76e2b4f0cd8e4c42a06c439a8bec8a6288df966425c92f5` |
| `prompts/B_revise.v2.md` | `21b29bb2097e08a5c31714323cf3bea78330679e193d6fa616287feba2ac078a` |
| `opencode.json` (analysis/revise config) | `93f72e580602faf04c89387ed184da5563a76bdb71782c7a9c756dddccb40b16` |
| `opencode_review.json` (review config) | `5a5a4cb0705b0689edfe29603a2fa1cd4473910845bd08f5562294e45809137b` |

(Identical to K1's hashes — same frozen files, no drift. 16-character prefixes recorded by the runner itself in `meta.json`'s `prompt_sha`/`config_sha` match.)

**Model/runtime versions:** `opencode/mimo-v2.6-flash-free`; OpenCode `1.18.34`; Python `3.13.13` (the pinned venv, reached via the `PATH` fix); repo commit `be48b01`.

**Revision executed, not skipped** (`says_none: false`, 2 issues reported).

**Carried-forward vs. newly generated:** `out/initial.png` and `out/values.csv` are carried forward from A unchanged (confirmed byte-identical to A's source hashes in §2). `out/revised.png`, `out/revised_values.csv`, `analyze.py` (edited), `critique.md`, and `response.md` are newly generated/modified by this run.

**Cost:** review 1 step / 0 tool calls / 58.1 s; revise 4 steps / 4 tool calls / 48.1 s. Total 5 steps, 4 tool calls, 106.2 s — well inside the 15-step / 600-second per-run budgets (each applies per call). Lower cost than K1 (8 steps / 7 tool calls / 166.7 s), consistent with this revision needing only a two-line filename edit rather than new verification code.

**Tokens:** not captured in `meta.json` for the B arm (unlike the A arm's `run_analysis`, `run_B`'s meta dict does not record a `tokens` field) — marked here as **unavailable by the runner's current design**, not an omission on my part.

**Errors:** none — no `error`-type events in either `events.jsonl` or `events_review.jsonl`; no rate limiting; no step-cap narration.

## 7. Limitations and unresolved scoring questions

- **Two of six items.** K1 + K2 together still cannot show B meets the `PROTOCOL.md` acceptance table (≥5/6 per criterion) or estimate an effect size.
- **Single reviewer.** This issue-by-issue read is mine; `PROTOCOL.md` specifies Bo as scorer with Claude as a second scorer, disagreements resolved by discussion — this report is not a resolved team score.
- **CHANGES: completeness is ambiguous, flagged for team review** (§4, issue 2): should every numbered issue get an explicit `CHANGES:` line, including "not changed, because..." for non-actionable issues? The current prompt wording supports either reading. Not scored as a defect here since no actual repair was skipped, but marked for a team decision rather than resolved unilaterally.
- **Visual inspection by mimo is unconfirmed** (§5) — the attachment mechanism works, but neither this item's critique text nor the available event trace lets me confirm the model looked at the image versus reasoning from the embedded text/CSV alone. This is evaluator-side uncertainty, not a claim that inspection didn't happen.
- **Non-byte-identical initial/revised PNGs** despite identical code and data (§5) — almost certainly PNG/matplotlib metadata, not a rendering difference, but not pixel-diffed to confirm.
- **A was already correct on this item** (confirmed against independent gold), so, as with K1, this item provides no evidence about review quality when A's *numbers* are actually wrong — only when A's *prose characterization* of correct numbers is wrong, which is a different (and in this case, real) failure mode worth keeping in view for the full iteration.

## Proposed Prompt Changes

**No change to `B_critique.v2.md` is supported by this item** — it performed exactly as designed: a parseable `ISSUES:` list, 0 tool calls (no reanalysis), one correctly identified substantive error with specific evidence, and one honest, appropriately-scoped "cannot verify" statement that invented nothing.

**One candidate, generic observation on `B_revise.v2.md`, offered for team review, not applied:**

- **Observed failure:** the revise output's `CHANGES:` block did not include a line for issue 2, which required no change — making it impossible to tell, from `CHANGES:` alone, whether that issue was considered and correctly judged non-actionable, or simply dropped. No actual harm resulted in this item (nothing needed to change), but the gap reduces auditability of the revise step's reasoning.
- **Current wording:** `CHANGES:\n1. <issue number>: <what you changed, or "not changed" and why>`
- **Proposed wording:** `CHANGES:\n(one line per issue number from the review, in order): <issue number>: <what you changed, or "not changed" and why>`
- **Rationale:** makes explicit that every numbered issue from the critique gets an accounting, including issues that required no change — closing the specific gap observed here without adding any domain content, question-type-specific instruction, or formal-question example, and without changing what the revise step is allowed to do.

This is a single-item observation; per protocol, any edit to a frozen-pending B prompt requires Bo to cite it in `ITERATIONS.md` and apply it as one edit per iteration, grounded in failures across the full 6-item set, not applied here.

---

**This report is provisional and requires team review before any protocol or prompt decision is made on its basis. K1 + K2 together are 2 of 6 required items and do not establish acceptance or justify freezing B.**
