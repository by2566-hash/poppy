# B v2 validation — K1, single item (provisional)

**Status: provisional, one item only.** Per `PROTOCOL.md` scope v2, acceptance requires all 6 pilot items in one iteration. This is not a freeze decision and does not stand in for the full iteration.

## 1. Outcome and execution status

**Complete.** `review_ok: true`, `n_issues: 2`, `says_none: false`, `revise_ok: true`, `revised_png: true`, `revised_values: true`, `answer_ok: true`. No errors, no rate limiting, no step-cap narration in either the review or revise run.

| | Review | Revise |
|---|---|---|
| Steps | 1 | 7 |
| Tool calls | 0 | 7 |
| Wall time | 64.3 s | 102.4 s |
| Session ID | `ses_ec2a15a5bffe2esOS5TpLLGTpY` | `ses_ec2a254b3ffeNLrQ2MG6CNg4LI` |

Run window: 2026-10-15 02:21:50–02:24:37 UTC (2026-10-14 22:21:50–22:24:37 EDT). Model `opencode/mimo-v2.6-flash-free`, OpenCode `1.18.34`, Python `3.13.13`, repo commit at run time `be48b01`.

**Environment, verified before the run:**
- `check_env.py` → `READY` (OpenCode 1.18.34; duckdb 1.4.4, pandas 2.2.3, pyarrow 19.0.0, matplotlib 3.10.0, all exact pins; parquet fingerprint OK; 1 harmless warning: raw CSV sha differs, expected per the script's own note).
- `check_free_models.py mimo-v2.6-flash-free` → `OK`, 9.0 s, checked 2026-10-15 02:19:18 UTC.
- **Python-interpreter fix re-verified for this session.** The earlier finding (A-V1-Test incident) was that OpenCode's `bash` tool inherits `PATH` from the process that launches `run_pilot.py`, so unless the venv's `bin/` is prepended there, the sandbox's `python3` resolves to the host's bare interpreter (no pinned packages). This fix is **not persistent** — confirmed again this session: a plain subprocess without the prefix still resolves `python3` to `/opt/homebrew/opt/python@3.14/bin/python3.14` with `ModuleNotFoundError: No module named 'duckdb'`, while prefixing `PATH="/Users/chloehe/poppy/.venv/bin:$PATH"` resolves it correctly. The run itself was launched with the prefix, and the fix's effectiveness is now directly confirmed from the run's own log, not just simulated: the revise step's first `bash` call, `python3 -c "import duckdb, pandas, matplotlib; print(...)"`, printed `1.4.4 2.2.3 3.10.0` immediately (`events.jsonl`, event 2) — no `ModuleNotFoundError`, no pip-install detour, unlike the earlier A-V1-Test incident. Residual uncertainty: this is still a per-invocation shell fix, not a system-level change; any future invocation of `run_pilot.py` outside this exact `PATH` prefix will regress.

## 2. Source A identification

Used exactly the team's original, frozen result — no staging copy was made (see §5, infrastructure note).

- Path: `experiments/E007-pilot-prompts/results/A-v1/K1-r1/`
- Added to git at commit `6c4f6df` ("E007 scope v2: A+B pilot...")
- `collected_by` (in A's `meta.json`): `by2566-hash` (teammate's original submission, not mine)
- A's own `meta.json` predates the `env` field (pre-instrumentation run); `a_git_commit: null` in B's `meta.json` is expected and documented in `ITERATIONS.md`, not a defect.
- Session ID of A's original run: `ses_ec6d7326effewoXH7yMjk8lzsg`

SHA-256 of the A input artifacts actually used by this run:
| File | SHA-256 |
|---|---|
| `meta.json` | `a93bb59ae08f22a5ae1305cf41eadf5c5cf724c9803f8309f5d2a8c79dd41445` |
| `response.md` | `24b5190a827c7fe088e63d9b4fe4145ef933f65d44c26f4bcbdb883d7de5f30e` |
| `opencode.json` | `e121e93ce4f398aa64f4aefd55055be93b6f80c2f79997533b8edf145b5c4a65` |
| `events.jsonl` | `5090ac177f6b9d13a73c3a1c35b0ac268f74aed5ed7fb638b18ba91e3626c384` |
| `out/values.csv` | `92dec926d2351cac47e4b1aeecd94f52658c3a4930562dfcaef1bb8cd8231d87` |
| `out/initial.png` | `be2d701e0e80243dee4c0852ea8687aa5218bdac2305522522a8cc792b12c4e2` |

A's answer, code, and chart were verified present and faithful before the run (no missing review material): chart (1430×780 PNG), `values.csv` (13 rows, 2013–2025), a written `ANSWER:` line, and code reconstructed by `run_pilot.py`'s `code_of()` fallback from three `bash` tool-use events in A's `events.jsonl` (events 2, 5, 8 — a package-version check, a `DESCRIBE`/date-range probe, and the actual DuckDB aggregation + matplotlib script, the model having written its script to `/tmp/ped_deaths.py` via heredoc rather than saving a `.py` file in the sandbox). This is the same embedding the critique prompt actually received.

## 3. Artifact checklist

| File | Present | Check |
|---|---|---|
| `meta.json` | yes | valid JSON |
| `opencode.json` (revise/analysis config) | yes | valid JSON, matches frozen `config/opencode.analysis.json` (sha `93f72e58...`) |
| `opencode_review.json` (review config, added manually — see §5) | yes | valid JSON, matches frozen `config/opencode.review.json` (sha `5a5a4cb0...`) |
| `events.jsonl` (revise run) | yes | 24 valid JSONL lines |
| `events_review.jsonl` (review run) | yes | 3 valid JSONL lines |
| `critique.md` | yes | present, parses as `ISSUES:` + 2 numbered items |
| `response.md` (revise output) | yes | contains `CHANGES:` and `ANSWER:` |
| Model-generated `.py` files | none saved | model wrote code via heredoc to `/tmp/...`, not a tracked `.py` file (same pattern as A; see events 16 in the revise trace) |
| `out/initial.png` | yes | opens via PIL, 1430×780 PNG (carried from A, byte-identical to A's source — not regenerated) |
| `out/values.csv` | yes | readable, 13 rows, byte-identical to A's source |
| `out/revised.png` | yes | opens via PIL, 1430×780 PNG |
| `out/revised_values.csv` | yes | readable, 13 rows, identical values to `values.csv` (diff: none) |

All JSON/JSONL files parse; both PNGs decode and load via PIL; both CSVs parse with the expected header (`year,pedestrians_killed`) and full 2013–2025 coverage.

## 4. Issue-by-issue evaluation

Independent cross-check used: `gold_pilot.json`'s K1 series (not shown to the model) — matches A's and B's values exactly for all 13 years. A's original answer was numerically correct on this item.

**Issue 1** (`critique.md`): *"The written answer does not actually answer 'each year' as asked — it only gives a summary... anyone reading the prose alone gets no year-by-year answer."*
- **Valid**, substantive, specific. K1's text literally asks "each year from 2013 to 2025"; A's original `ANSWER:` gave a trend summary (high/low/total/average) rather than a full per-year list, even though the full breakdown existed in `values.csv`. Evidence: A's `response.md` vs. the question text in `pilot_questions.json`.
- **Repaired:** the revised `ANSWER:` lists all 13 years individually, then keeps A's summary stats. No gold numbers were changed (verified identical to gold). **Repair effective.**

**Issue 2** (`critique.md`): *"Nothing in the material verifies the numbers against the source... correctness relative to the data cannot be confirmed from what was provided."*
- **Valid, and correctly framed as a verification gap, not an asserted error** — exactly the behavior the critique prompt asks for ("If the material does not let you verify something, say that instead of guessing"). The embedded "code" only contains the *commands* the model ran (per `code_of()`), not their stdout, so the reviewer genuinely could not see A's `DESCRIBE`/date-range output. This is not an invented substantive error: A's underlying computation was in fact correct (confirmed against gold independently), but the reviewer had no way to see that from the supplied material, and said so rather than guessing either way.
- **Repaired:** the revise step added explicit source-coverage and per-year cross-check queries (with `assert`s) to the script, and folded the verification findings into the final `ANSWER:`. This goes slightly beyond the strict minimum ("produce revised chart + values") but is a direct, bounded response to the specific gap issue 2 named, not an unrelated change. **Repair effective; no scope creep into unrelated parts of the analysis.**

**No invented substantive errors.** No claim in either numbered issue misstates what A actually did.

**Unrelated correct content preserved:** confirmed by direct code diff — the revise script's aggregation query, date filter (`BETWEEN DATE '2013-01-01' AND DATE '2025-12-31'`), group-by, and chart code (color `#c0392b`, bar width, figsize, dpi, labels) are **identical** to A's original script, line for line, aside from the added verification block. `values.csv` and `revised_values.csv` are byte-for-byte identical. **Zero correct→incorrect flips.**

**New substantive errors:** none found.

**Consistency (chart / CSV / answer):** `revised_values.csv` == `values.csv` (diff empty); the revised `ANSWER:`'s per-year list and total (1,690) match the CSV exactly; the chart (same script, same data) is consistent with both.

**Not flagged, noted only as a limitation (not scored as a miss):** A's original (and carried-forward) answer attributes the 2020 dip to "(pandemic)" — a causal claim the crash data alone does not establish. The review did not flag this. The protocol's acceptance bar is "no invented problems," not "catches every stylistic issue," so this is not counted against the review, but it is worth the team's attention if "no unsupported causal claims" is meant to be in scope for B.

## 5. Audit details

**Infrastructure note on the run interface (verify-before-run finding):** the task briefing assumed `run_pilot.py`'s `B` mode reads A's input from a local sandbox path and asked me to stage a copy at `../poppy-sandbox/E007/A-v1-input/K1-r1/`. Inspecting the current `run_pilot.py` (repo commit `be48b01`, changed since the prior session under "run_B reads A's committed results from the repo") showed this is now out of date: `run_B` reads directly from `experiments/E007-pilot-prompts/results/<a_label>/<qid>-r<rep>/` in the repo, not from any sandbox staging path, and errors out with a clear message if that path is missing a `meta.json`. A manually staged sandbox copy would have been silently ignored. I therefore ran `... run_pilot.py B v2 v2 A-v1` (using the already-committed `A-v1` label) instead of the originally planned `A-v1-input`, which satisfies the actual intent ("use exactly `results/A-v1/K1-r1/`, not a copy, not a new A run") more directly than staging would have. No staging directory was created; none was needed.

**Files `collect_runs.py` omits (manually preserved here):**
- `review/opencode.json` (the review step's effective, no-execution config) — not copied by `collect_runs.py`; added here as `opencode_review.json`.
- `review/chart.png` — the attached-chart copy used for review; not copied, but it is byte-identical to `out/initial.png`, which is preserved, so no information is lost.
- `review/stderr.log`, top-level `stderr.log` — machine-specific paths, correctly excluded per the script's own docstring; no audit value.
- `.ocdata/` (OpenCode's private per-run data/session dir, including its local `opencode.db`) — correctly excluded; this is exactly the kind of file the project's `.gitignore` and `AGENTS.md` ("never touch `~/.codex*`", "never print credentials") intend to keep out of commits. Not inspected for contents beyond confirming it was excluded.

**Hashes of prompt files and effective configs used by this run:**
| File | SHA-256 |
|---|---|
| `prompts/B_critique.v2.md` | `9a15fd17aad323b8a76e2b4f0cd8e4c42a06c439a8bec8a6288df966425c92f5` |
| `prompts/B_revise.v2.md` | `21b29bb2097e08a5c31714323cf3bea78330679e193d6fa616287feba2ac078a` |
| `opencode.json` (analysis/revise config) | `93f72e580602faf04c89387ed184da5563a76bdb71782c7a9c756dddccb40b16` |
| `opencode_review.json` (review config) | `5a5a4cb0705b0689edfe29603a2fa1cd4473910845bd08f5562294e45809137b` |

(16-character prefixes of these same hashes are recorded by the runner itself in `meta.json`'s `prompt_sha`/`config_sha`; they match.)

**Model/runtime versions:** `opencode/mimo-v2.6-flash-free`; OpenCode `1.18.34`; Python `3.13.13` (the pinned venv, reached via the `PATH` fix); repo commit `be48b01`.

**Revision executed, not skipped** (`says_none: false`, 2 issues reported) — both numbered issues are addressed in `response.md`'s `CHANGES:` block, matching the revise prompt's required format.

**Carried-forward vs. newly generated:** `out/initial.png` and `out/values.csv` are carried forward from A unchanged (copied by `run_B`'s `shutil.copytree`, confirmed byte-identical to A's source hashes above). `out/revised.png`, `out/revised_values.csv`, `critique.md`, and `response.md` are newly generated by this run.

**Cost:** review 1 step / 0 tool calls / 64.3 s; revise 7 steps / 7 tool calls / 102.4 s. Total 8 steps, 7 tool calls, 166.7 s, well inside the 15-step / 600-second per-run budgets (each run individually, as the budget is per-call, not pooled).

**No errors** in either `events.jsonl` or `events_review.jsonl` (no `error`-type events); no rate limiting; no step-cap narration.

## 6. Limitations

- **Single item.** This is 1 of 6 required pilot items; it cannot show B meets the acceptance table in `PROTOCOL.md` (≥5/6 on each criterion) or estimate an effect size. A clean pass here is consistent with, but not proof of, B working as designed.
- **One reviewer, one point of view.** The issue-by-issue evaluation above is mine; `PROTOCOL.md` specifies Bo as scorer with Claude as a second scorer and disagreements resolved by discussion. This report is the Claude-side read, not a resolved score.
- **Gold-matched baseline.** K1 happens to be a case where A was already numerically correct (confirmed against `gold_pilot.json`). This item provides no evidence about review quality when A is actually wrong — that evidence can only come from items where A has a real error.
- **Unflagged causal claim.** As noted in §4, the "(pandemic)" attribution for 2020 was not flagged by the review and persisted into the revised answer. Not scored as a defect under the current protocol, but worth a team decision on whether it should be in scope.
- **A's env block is pre-instrumentation**, so `a_git_commit` is `null` by design, not a collection failure (documented in `ITERATIONS.md`).

## Proposed Prompt Changes

**No change to `B_critique.v2.md` or `B_revise.v2.md` is supported by this item.** Both prompts performed exactly as designed on K1: the review returned a parseable `ISSUES:` list with 0 tool calls (well inside the ≤2 bar), named two specific, non-invented problems, correctly distinguished "this is wrong" language from "I cannot verify this" language, and the revise step addressed both flagged issues while leaving the data, filters, numbers, and chart code byte-for-byte unchanged apart from the flagged points. There is no observed failure here to motivate an edit, and the protocol requires each edit to cite an observed failure (`PROTOCOL.md` scope v2: "edited only by Bo; each edit must cite an observed failure in `ITERATIONS.md`").

Any prompt-change decision should wait for the full 6-item iteration, which can surface failure modes this single, already-correct item cannot (e.g., behavior when A is actually wrong, or on ambiguous/insufficient-evidence items where the review has less to check against).

---

**This report is provisional and requires team review before any protocol or prompt decision is made on its basis.**
