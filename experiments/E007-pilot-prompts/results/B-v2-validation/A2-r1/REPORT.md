# B v2 validation — A2, fifth scheduled item (provisional)

**Status: provisional, completed, fifth of six scheduled.** A1 was the fourth scheduled item but remains **blocked** (preflight diagnostic only, documented in `experiments/E007-pilot-prompts/results/B-v2-validation/A1-r1/REPORT.md`) — that blocker is preserved unchanged and **not resolved by this task**. A2 is the first completed, evaluable B v2 run on an ambiguous-type item in this iteration — A1, the other scheduled ambiguous-type item, was never completed (its input was ineligible before any model call), so there is no prior completed ambiguous-type item for A2 to follow. Together, K1, K2, K3, A1 (blocked), A2 still do not establish the six-item acceptance decision in `PROTOCOL.md` scope v2, and this item alone does not justify freezing B.

**No newer repository instructions conflict with this task.** `git log` shows no commits since `be48b01` (the HEAD used for all prior validation items); all required files are unchanged.

## 1. Environment verification

- `check_env.py` → `READY` (OpenCode 1.18.34; duckdb 1.4.4, pandas 2.2.3, pyarrow 19.0.0, matplotlib 3.10.0, exact pins; parquet fingerprint OK; same 1 harmless warning as all prior items).
- B prompt hashes match all prior items exactly (no drift): `B_critique.v2.md` = `9a15fd17aad323b8a76e2b4f0cd8e4c42a06c439a8bec8a6288df966425c92f5`; `B_revise.v2.md` = `21b29bb2097e08a5c31714323cf3bea78330679e193d6fa616287feba2ac078a`.
- PATH fix re-verified as per-invocation, not persistent: plain `python3` resolves to `/opt/homebrew/opt/python@3.14/bin/python3.14` (`ModuleNotFoundError: No module named 'duckdb'`); `PATH="/Users/chloehe/poppy/.venv/bin:$PATH"` resolves correctly to the pinned venv — confirmed, as before, by the run's own clean execution with no import errors.
- `check_free_models.py mimo-v2.6-flash-free` → `OK`, 24.1 s (slower than K1–K3's 4–9 s but not rate-limited), checked 2026-10-15 03:32:37 UTC.

## 2. Source A identification and input eligibility

- Path: `experiments/E007-pilot-prompts/results/A-v1/A2-r1/`
- Question (from `pilot_questions.json`, id `A2`, type `ambiguous`, read directly from the file, not paraphrased): *"Are NYC's streets more dangerous at night? Make a chart and give a conclusion for a news report."*
- Repo commit at execution: `be48b01`. Runner file `experiments/E007-pilot-prompts/run_pilot.py`, sha256 `6497d593891a2b9ccf73213d833889832fe0937e6b32832020a834dbc1ee8c05`.
- A2-r1 added to git at commit `6c4f6df`. `collected_by` (A's `meta.json`): `by2566-hash`.
- **A-v1 is a fixed source outcome, not a stated-frozen prompt.** `PROTOCOL.md` scope v2 records "A frozen at `A.v1.md` (12 valid runs)" — that refers to the *prompt* `A.v1.md`. A2-r1 is simply one of those 12 committed runs, used as-is; I make no separate claim that the *run itself* carries any special "frozen" status beyond being the team's committed, unmodified artifact at this path.
- Original A session ID: `ses_ec6d3a7dfffeZRk7vh7PJSbVnG`.

**Input eligibility — verified, not assumed, learning directly from A1's lesson:** unlike A1-r1, I did not trust `meta.json`'s `answer_ok: true` at face value. I re-applied the current `run_pilot.py` `answer_of()` logic directly to A2-r1's `response.md` text and the result **matches** the stored `meta.json["answer"]` field exactly (confirmed by direct string equality, not just inspection) — A2-r1's `meta.json` is accurate under current code, unlike A1-r1's stale one. `out/initial.png` (1637×928 PNG) and `out/values.csv` (24 rows, one per hour) both exist and were inspected directly (not assumed complete from the directory listing alone). **A2 was eligible for B; no protocol gap applied here.**

SHA-256 of the A input artifacts used:
| File | SHA-256 |
|---|---|
| `meta.json` | `776f7acdd8b0c3a201ccf107ed28d9e25e5dfdc432433c87baaec7cffc34f59d` |
| `response.md` | `64205ee4941144e2800bb7f21a6ded93c9dd65aaaa517500842f1715ef73bf52` |
| `opencode.json` | `e121e93ce4f398aa64f4aefd55055be93b6f80c2f79997533b8edf145b5c4a65` |
| `events.jsonl` | `367927d8d86e1d1472731d1ae3cd29592f93b765780997781b0567e7619d42a2` |
| `out/values.csv` | `37398d73b8cb03dafbc9e360323d486cc11458d6d763252c238f60b1520fccf8` |
| `out/initial.png` | `2247ebbcca9be544193b7d44f39306d2c5f8a4563df3c24ccee2ce101dfcf9ca` |

A2's A result has no committed `.py` file; `code_of()` reconstructed "Code that produced them" from five matching `bash` tool-use events in `events.jsonl` (events 2, 5, 8, 11, 14 — package check, schema probe, three successive DuckDB/matplotlib scripts culminating in the actual chart/CSV-producing script). This is the same text the critique prompt received.

**Confirmed: the runner still reads A directly from the repo, not a sandbox staging copy** — re-checked against the current `run_pilot.py`. Used `A-v1` directly; no `A-v1-input` staging directory was created or needed. **Isolation of evaluation material confirmed:** `run_B`'s `shutil.copytree` excludes `events*.jsonl`, `response.md`, `meta.json`, `critique.md` from A's folder. This report, all prior validation reports, `gold_pilot.json`, and `ITERATIONS.md` remain outside the path B reads from.

## 3. Artifact checklist

| File | Present | Check |
|---|---|---|
| `meta.json` | yes | valid JSON |
| `opencode.json` (revise/analysis config) | yes | valid JSON, matches frozen `config/opencode.analysis.json` (sha `93f72e58...`) |
| `opencode_review.json` (review config, added manually — see §6) | yes | valid JSON, matches frozen `config/opencode.review.json` (sha `5a5a4cb0...`) |
| `events.jsonl` (revise run) | yes | 26 valid JSONL lines |
| `events_review.jsonl` (review run) | yes | 3 valid JSONL lines |
| `critique.md` | yes | parses as `ISSUES:` + 5 numbered items |
| `response.md` (revise output) | yes | contains `CHANGES:` (5 items) and `ANSWER:` |
| Model-generated `.py` files | none saved this run either | revise step edited inline via heredoc, same reconstruction pattern as A's source |
| `out/initial.png` | yes | opens via PIL, 1637×928 PNG, byte-identical to A's source hash above (carried forward, not regenerated) |
| `out/values.csv` | yes | readable, 24 rows, byte-identical to A's source |
| `out/revised.png` | yes | opens via PIL, 1629×928 PNG (width differs slightly from `initial.png` — see §5) |
| `out/revised_values.csv` | yes | readable, 24 rows — 23 of 24 columns identical to `values.csv`; only `harmed` differs (correctly — see §4) |

All JSON/JSONL parse; both PNGs decode via PIL; both CSVs parse with the expected header and full 0–23 hour coverage.

## 4. Issue-by-issue evaluation

Five issues were reported (`n_issues: 5`), each independently checked against `values.csv` and the embedded code, not taken on faith:

**Issue 1 — `harmed` column internally inconsistent with `injured`+`killed`.**
- **Classification: provisionally substantive error (pending team review).** Verified directly: hour 0, `injured`=29,417 + `killed`=189 = 29,606, but `harmed`=29,342 (less than `injured` alone — mathematically impossible if `harmed` is meant to be their sum); hour 16: 50,359+133=50,492 vs. published 50,105. The critique's specific numbers check out, though the classification below remains mine pending the team's own scoring pass, per `PROTOCOL.md`'s two-scorer process.
- **Repair:** root cause correctly diagnosed in `response.md` — the original query computed `SUM(injured + killed)`, which drops a row from the sum entirely whenever `killed` is `NULL` for that row (SQL: `NULL` + anything = `NULL`), silently undercounting; fixed to `SUM(injured) + SUM(killed)`. Confirmed by diff: **only** the `harmed` column changed across all 24 rows in `revised_values.csv`; spot-checked hour 0 (29,606) and hour 16 (50,492) now equal `injured+killed` exactly. **Repair effective**, and precisely scoped — `crashes`, `injured`, `killed`, `injured_per_crash`, `deaths_per_1000_crashes` are **byte-identical** before and after.

**Issue 2 — written answer says "8× the midday rate"; the chart annotation (and the actual numbers) say otherwise.**
- **Classification: provisionally substantive error (pending team review) — specifically the baseline mislabel, not the rounding.** The embedded code (`code_of()` reconstruction) contains the literal annotation string `"(8× the 4 pm rate)"` — the chart was never about "midday"; the written answer named the wrong baseline hour. Independently recomputed from `values.csv`: noon (hour 12) rate is 0.97 deaths/1,000 → 6.35/0.97 ≈ 6.5× (a materially different ratio if "midday" were really meant); 4 pm (hour 16) is 0.82 → 6.35/0.82 ≈ 7.7×. **Rounding 7.7× to "8×" is, on its own, a defensible, ordinary rounding (7.7 rounds to 8) — not an error.** The clear, unambiguous problem is the baseline label itself: "midday" (noon, rate 0.97) and "4 pm" (the chart's actual reference, rate 0.82) are different hours with different rates, so a reader taking "midday" literally gets a different, wrong ratio (≈6.5×) than the one the chart and numbers actually support.
- **Repair:** `response.md` recomputes from unrounded values (4 am = 6.3536, 4 pm = 0.8241 → 7.7×) and updates both the chart annotation and the `ANSWER:` text to "7.7× the 4 pm rate" consistently. Confirmed visually (§5) — the revised chart's annotation now reads "(7.7× the 4 pm rate)". **Repair effective.**

**Issue 3 — chart says "6.3 deaths per 1,000 crashes" at 4 am; the written answer says "~6.4".**
- **Classification: optional presentation improvement** (the critique itself calls it "Minor"). Both are defensible roundings of the true value, 6.3536 (CSV `deaths_per_1000_crashes` for hour 4, rounded to 2dp = 6.35; "6.3" truncates, "~6.4" rounds up) — not a substantive error, just an inconsistency between two restatements of the same number.
- **Repair:** both now say "6.4," computed from the unrounded rate rather than the 2-decimal CSV value. **Repair effective**, though this was a cosmetic fix, not a correctness fix — recorded as such, not overstated.

**Issue 4 — legend labels ("7am–6pm" / "7pm–6am") don't match the actual hour buckets used (7–18 / 19–6), which include hour 18 as "day" and hour 6 as "night".**
- **Classification: provisionally substantive error (pending team review)** — a real mismatch between the chart's stated methodology (the legend text) and its actual implementation (the bucketing code: `'#1a4d7d' if 7 <= h <= 18 else '#e07b39'`), confirmed directly from the embedded code. Hours 7–18 span 7:00am–7:00pm (12 one-hour buckets), not 7am–6pm (which would only be 11 hours, 7–17); the legend's stated boundary undercounts by one hour on each side.
- **Repair:** relabeled to match the existing bucket code ("day, hours 7am–7pm" / "night, hours 7pm–7am") rather than moving the hour boundaries to match the old label — the correct fix, since changing the boundaries would have altered every other already-correct number. Confirmed both by text diff and by directly viewing the chart (§5): the bar colors for hour 18 (blue) and hour 6 (orange) are unchanged; only the legend text changed. **Repair effective, correctly scoped** (data unchanged, only the mislabeling fixed).

**Issue 5 — cannot verify the claimed date range "July 2012 – June 2026" from the supplied material (the query that would show it isn't included); separately confirms `n = 2.27M` does check out against the CSV.**
- **Classification: verification limitation, not a demonstrated error** — appropriately hedged, exactly per the critique prompt's "say that instead of guessing" instruction, and it does the extra work of cross-checking what *can* be checked (the row count) rather than flagging everything as unverifiable.
- **Repair:** the revise step actually ran the previously-missing query (`MIN(crash_date) = 2012-07-01`, `MAX = 2026-06-11`, `COUNT(*) = 2,269,187`) and confirmed the original claim was correct, so it is explicitly left unchanged in `CHANGES:` item 5. **Repair effectiveness: not applicable in the correctness sense (nothing was wrong) — but the revise step went beyond "no change needed" to actually resolve the uncertainty with real verification, which is a meaningful improvement in confidence, not merely a no-op.**

**No invented substantive errors; no unsupported claims in the critique itself.** All five issues are specific, evidenced, and independently checked here.

**Preservation of unrelated correct content, and zero flips:** confirmed by full-file diff — `crashes`, `injured`, `killed`, `injured_per_crash`, and `deaths_per_1000_crashes` are **byte-identical** across all 24 rows between `values.csv` and `revised_values.csv`; only `harmed` differs (correctly). **Zero correct→incorrect flips.**

**A notable, positive counter-observation on the open "`CHANGES:` completeness" question raised in the K2 report:** this item had **5** numbered issues, including one (issue 5) that required no substantive data/chart change — and `CHANGES:` lists **all five**, explicitly, including "...so it is unchanged" for issue 5. This is evidence *against* a systematic gap in the revise prompt's format compliance (K2's single miss may have been an isolated inconsistency rather than a pattern) — noted here as a new data point for team synthesis, not treated as resolving the open question on its own.

### On interpretation, metrics, and causal vs. descriptive claims (A2 is an ambiguous-type question)

Per the task's instruction not to impose a preferred interpretation merely because the question is ambiguous: A's chosen framing — comparing **per-crash injury rate** and **per-1,000-crash fatality rate** between day and night, rather than raw crash counts — is a reasonable, defensible interpretation of "more dangerous" (risk per incident, not incident volume), and the `ANSWER:` line is transparent about using rates rather than raw counts (it states both: "daytime... has the most crashes... but night crashes are far deadlier"). I do not treat an alternative framing (e.g., absolute death counts by hour) as more correct; the chosen metric directly answers "more dangerous," which is about severity, not frequency.

**A precision worth stating explicitly:** "fatalities per reported crash" measures the severity of a crash once one has already occurred — it is not a measure of risk per mile driven or per trip taken. A true per-mile or per-trip risk comparison would require an exposure/denominator measure (how many miles were driven, or trips taken, at each hour), which is not present in this dataset — the same kind of missing-exposure gap documented for I1's VMT denominator. A's chosen metric is a defensible proxy for "more dangerous" under a severity-given-a-crash reading, but on its own it does not establish that night driving carries higher risk per mile or per trip. This is a scope limitation of the metric A chose, not something B's review was asked to catch (the critique prompt does not ask the reviewer to question A's choice of metric), and B did not claim otherwise — noted here as an evaluator-side clarification, not a finding against either A or B.

**Descriptive vs. causal:** the embedded `ANSWER:` line (what B's review actually received) is purely descriptive/correlational — it states rates and a ranking, with no causal language. A's full original `response.md` narrative (the text *before* the `ANSWER:` line, which is **not** embedded in B's critique prompt — `run_pilot.py`'s `answer_of()` extracts only the text after the last `ANSWER:`) contains one unsupported causal aside: "...when lighter traffic lulls drivers into higher speeds — the deadliest hour on NYC streets." This speculates a mechanism (traffic volume → speed → fatality) that the available crash-count/rate data alone does not establish (no speed or traffic-volume data in the dataset). **This was never exposed to B's review** — not because the review failed to catch it, but because the critique prompt only embeds the extracted `answer`, `values`, and `code`, by the scope-v2 amendment's explicit design ("the reviewer judges what was produced instead of redoing the analysis... values, written answer and code are embedded"). This is a genuine scope boundary worth the team's awareness (§7), not a defect in mimo's review — mimo could not have flagged a sentence it was never shown.

**Does the combined chart + CSV + answer satisfy A2's actual question** ("are streets more dangerous at night... chart... conclusion for a news report")? **Yes, both before and after revision**, under the interpretation A itself chose and stated. The revision did not change the underlying conclusion ("yes, night is more dangerous") — it corrected one data bug, one baseline mislabel, one rounding inconsistency, and one legend mismatch, all without altering the substance of the finding.

## 5. Post-run visual assessment (Claude's own, separate from mimo's critique)

I directly opened both `out/initial.png` and `out/revised.png` without regenerating them.

**Observations:**
- Dual-axis chart: left axis "Number of crashes (thousands)" (bar heights, colored by day/night bucket), right axis "Fatalities per 1,000 crashes" (red line with markers), bold title, annotated peak at hour 4, legend, and a source caption at the bottom matching A's claimed date range.
- **Axes/scales/baselines:** both y-axes start at 0, linear scale, gridlines present on the left axis only; appropriate for a dual-axis chart.
- **Titles/labels/units/legend:** title correctly states the finding ("daytime has the most crashes, night crashes are far more deadly"); axis labels correctly colored to match their series (blue left axis/bars, crimson right axis/line); x-axis shows all 24 hours (0–23), fully legible, no rotation needed.
- **Clipping/overlap/readability:** none — the annotation arrow and text box do not overlap any bars or the legend in either image.
- **Displayed categories/series vs. CSV:** all 24 hours present in both; bar heights and the fatality-rate line visually track the CSV values I already verified by hand (e.g., the fatality line peaks sharply at hour 4, consistent with `deaths_per_1000_crashes`=6.35 being far above its neighbors).
- **What actually changed between `initial.png` and `revised.png` (confirmed by direct visual comparison, matching the text diff exactly):**
  1. Legend: "Crashes (day, 7am–6pm)" / "Crashes (night, 7pm–6am)" → "Crashes (day, hours 7am–7pm)" / "Crashes (night, hours 7pm–7am)" (issue 4's fix).
  2. Annotation: "4 am: 6.3 deaths\nper 1,000 crashes\n(8× the 4 pm rate)" → "4 am: 6.4 deaths\nper 1,000 crashes\n(7.7× the 4 pm rate)" (issues 2+3's fix).
  3. **Nothing else changed** — bar heights, bar colors (hour 18 still blue/"day", hour 6 still orange/"night" in both images — confirming the underlying hour-bucketing was *not* altered, only its label), the fatality line, title, and axis labels are identical. This directly confirms the repair was scoped exactly to what the three content-level issues required.
- `out/revised.png` is 8px narrower than `out/initial.png` (1629×928 vs. 1637×928) — consistent with the shorter annotation/legend text after editing, not a rendering defect.
- **Visual completeness vs. underlying data completeness:** the chart showing all 24 hours confirms the chart itself is complete; it says nothing about whether the underlying `crash_time` field has any nulls or quality issues in the source data — that is a separate question the chart cannot answer, and I make no claim about it.

**What this establishes about image delivery to mimo, and what it does not — with specific evidence this time, not just a general statement:** as in K1–K3, `run_B` attaches the chart as a real `-f <path>` argument to `opencode run`. **For this item specifically, I can show precisely why the critique provides no evidence either way about actual visual inspection:** the matplotlib code embedded in the critique prompt (via `code_of()`) contains the annotation and legend text as **literal Python string constants** — `"(8× the 4 pm rate)"`, `'Crashes (day, 7am–6pm)'`, `'Crashes (night, 7pm–6am)'` are all directly readable in the code text, not something that requires looking at the rendered image. Every one of the five issues is fully derivable from the embedded CSV, the embedded answer text, and these literal strings in the embedded code — none of them requires information only visible in pixels (e.g., no comment on color choice, marker style, or anything not already present as text). I am not concluding mimo *didn't* look at the image — only that this item's evidence, like K1–K3's, does not establish that it did. Per the task's instruction, I do not infer either way from the attachment, the 0 tool calls, or the absence of a purely-visual remark.

**Revision was not skipped** (`says_none: false`), so the "carried-forward chart, no new chart generated" case does not apply here.

## 6. Audit details

**Files `collect_runs.py` omits (manually preserved here, same pattern as prior items):**
- `review/opencode.json` — added here as `opencode_review.json`.
- `review/chart.png` — confirmed byte-identical to `out/initial.png` (and to A's source hash), so no information is lost.
- `review/stderr.log`, top-level `stderr.log` — machine-specific, excluded per the script's own docstring.
- `.ocdata/` — correctly excluded; not inspected beyond confirming exclusion.

**Hashes of prompt files and effective configs used by this run:**
| File | SHA-256 |
|---|---|
| `prompts/B_critique.v2.md` | `9a15fd17aad323b8a76e2b4f0cd8e4c42a06c439a8bec8a6288df966425c92f5` |
| `prompts/B_revise.v2.md` | `21b29bb2097e08a5c31714323cf3bea78330679e193d6fa616287feba2ac078a` |
| `opencode.json` (analysis/revise config) | `93f72e580602faf04c89387ed184da5563a76bdb71782c7a9c756dddccb40b16` |
| `opencode_review.json` (review config) | `5a5a4cb0705b0689edfe29603a2fa1cd4473910845bd08f5562294e45809137b` |

(Identical to all prior items — no drift.)

**Model/runtime versions:** `opencode/mimo-v2.6-flash-free`; OpenCode `1.18.34`; Python `3.13.13` (pinned venv); repo commit `be48b01`.

**Session IDs:** review `ses_ec26107cdffemn6GkvuuVMj4TD`; revise `ses_ec25dc201ffekz9pobVb6l8Jiq`.

**Execution times:** 2026-10-15 03:33:10–03:40:43 UTC (2026-10-14 23:33:10–23:40:43 EDT).

**Revision executed, not skipped** (`says_none: false`, 5 issues reported).

**Carried-forward vs. newly generated:** `out/initial.png` and `out/values.csv` carried forward from A unchanged (confirmed byte-identical to A's source hashes in §2). `out/revised.png`, `out/revised_values.csv`, `critique.md`, and `response.md` are newly generated.

**Cost:** review 1 step / 0 tool calls / 214.4 s; revise 7 steps / 10 tool calls / 238.5 s. Total 8 steps, 10 tool calls, 452.9 s — the highest cost of the four executed B items so far (K1, K2, K3, A2 — A1 was blocked, not executed), consistent with this A input having genuinely more to find and fix (5 issues vs. 1–2 for K1–K3) and the question being an ambiguous type with a more involved analysis. Still within the 15-step / 600-second per-run budgets (each applies per call).

**Tokens:** not captured in `meta.json` for the B arm (same limitation noted for K1–K3 — `run_B`'s meta dict does not record a `tokens` field). Marked **unavailable by the runner's current design**.

**Errors:** none — no `error`-type events in either `events.jsonl` or `events_review.jsonl`; no rate limiting; no step-cap narration (`revise_steps: 7` is well under the 15-step cap).

## 7. Limitations and unresolved protocol/scoring questions

- **Five of six scheduled items attempted; A1 remains blocked, not resolved here.** The six-item acceptance table in `PROTOCOL.md` scope v2 cannot be evaluated until the team decides how to handle A1 (or substitutes a resolution) — that decision is explicitly out of scope for this task, per instruction, and A1's preflight record is untouched.
- **Single reviewer.** This issue-by-issue read is mine; `PROTOCOL.md` specifies Bo as scorer with Claude as a second scorer, disagreements resolved by discussion — this report is not a resolved team score.
- **Genuine scope boundary identified, not a defect:** B's critique prompt embeds only the `answer_of()`-extracted `ANSWER:` text, not A's full narrative — so any claim A makes *before* its `ANSWER:` line (here, an unsupported causal aside about traffic volume and speed) is architecturally invisible to the review. This is consistent with the scope-v2 amendment's explicit design (review judges "values, written answer and code," not the full transcript), so it is not a prompt wording problem — but the team may want to decide whether that scope boundary is intended to extend to causal claims made outside the formal answer line.
- **Positive counter-observation for the K2 "`CHANGES:` completeness" question:** this item's 5-issue `CHANGES:` block addressed all 5 explicitly, including a no-op one — new evidence, not a resolution, since only 2 of 5 items so far have had multi-issue reviews with a non-actionable entry (K2 and A2), with opposite outcomes.
- **Visual inspection by mimo remains unconfirmed, not disconfirmed**, for the same reason as K1–K3 — and for this item specifically, I can show *why*: every issue is derivable from literal text (CSV, embedded code's string constants, written answer) without needing the rendered image.

## Proposed Prompt Changes

**No change to `B_critique.v2.md` or `B_revise.v2.md` is supported by this item.** Both performed strongly. Of the five reported issues: three are provisionally substantive, pending team review (issue 1, a real data bug; issue 2, a mislabeled ratio baseline — the "~8×" rounding itself is defensible, the baseline mislabel is the clearer problem; issue 4, a legend/code mismatch); one is a minor presentation inconsistency (issue 3); and one is a well-scoped "cannot verify" (issue 5) that the revise step proactively resolved rather than leaving unaddressed. Nothing was invented, and the revise step repaired every flagged issue with surgical precision — one column changed for the data bug, text/annotation strings changed for the labeling issues, and everything else held byte-identical. This is, if anything, evidence of the B design working as intended on a harder, messier input than K1–K3 — though the issue classifications above (3 substantive / 1 presentation / 1 verification limitation) remain mine, pending the team's own scoring pass.

Two standing observations from prior reports are **not** re-raised here with new "Observed failure" blocks, consistent with this item either providing counter-evidence or being silent on them (see §7): the K2 `CHANGES:`-completeness question, and the ongoing uncertainty about whether mimo visually inspects the attached chart. Both remain candidate directions for the team's synthesis across all scheduled items, not established failures requiring an edit now.

---

**This report documents a completed, evaluated item. Together with K1, K2, K3 (completed) and A1 (blocked, unresolved), this is 5 of 6 scheduled items attempted, 4 of 6 completed and evaluated. This does not establish full acceptance and does not justify freezing B.**
