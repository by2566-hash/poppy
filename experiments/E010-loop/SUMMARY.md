# E010 summary: every modified experiment and every finding (2026-11-08 → 2026-11-19)

This is the one-page record. Detail, commands and per-run evidence live in `ITERATIONS.md`, boundaries in `C5-design.md`, research in `diagnosis/research-2026-11-08.md`, and hashes in `../E007-pilot-prompts/FROZEN.md`.

Setup common to every arm:
- GPT-6 Luna, D v2 enumerate harness, free k, 6 pilot questions × 3 repeats = 18 runs.
- Graded by g8.1 with two Luna passes = **g8.2** (adds decision 10: calendar and unit numbers exempt, 11-19); human overrides where filled.
- Same-day comparisons only (finding M1).

## 1. Experiments

| Label (results/) | Date | Change vs D v2 | Prompt / harness | Options | g8.2 silent-error | traps + UC only |
|---|---|---|---|---|---|---|
| `D-v2-kfree` | 11-08 | none (same-day baseline) | — | 43 | 49% | 49% |
| `D-v2-kfree-hermetic` | 11-08 | none; OpenCode external skills off (F1 context) | `diagnosis/run_hermetic.py` | 46 | 50% | 50% |
| `D-v2-kfree-profile` (E010-1) | 11-08 | code-generated data profile appended to the dictionary | `POPPY_PROFILE`, `profile.md` | 38 | 50% | 50% |
| `D-v2-cov-kfree` (C1) | 11-08 | `interpretation` must state rows not used, share computed by code | `D_enumerate.v2-cov.md` | 41 | 78% | 32% |
| `D-v2-cov-kfree-profile` (C2) | 11-08 | C1 + profile | as above | 38 | 71% | 26% |
| `D-v2-kfree-jit` (C3) | 11-08 | harness prints NULL / partial-period notes next to the agent's DuckDB output | `POPPY_JIT`, `jit/` | 42 | 48% | 45% |
| `D-v2-cov-kfree-jit` (C4) | 11-08 | C1 + C3 | as above | 44 | 80% | 32% |
| `D-v2-plan-kfree` (C5) | 11-08 | Bo's Plan → Data check → Final plan | `D_enumerate.v2-plan.md`, 50 steps | 39 | 38% | 31% |
| `D-v2-kfree-1113` | 11-13 | none (same-day baseline, hermetic harness) | — | 43 | **42%** | 42% |
| `D-v2-plan2-kfree-1113` (C5 v2) | 11-13 | C5 + outcome columns missing-only + definitions in text | `D_enumerate.v2-plan2.md` | 37 | **22%** | **22%** |

Trap counts (FAIL / applicable) for the arms that matter:

| | baseline 11-08 | E010-1 | C1 | C3 | C4 | C5 | baseline 11-13 | C5 v2 |
|---|---|---|---|---|---|---|---|---|
| TR05 NULL borough | 7/7 | 8/8 | 2/8 | 4/8 | 0/8 | 2/6 | 9/9 | 2/7 |
| TR08 2026 NULL killed | 6/7 | 3/5 | 1/5 | 4/6 | 1/6 | 0/5 | 3/7 | 0/7 |
| TR07 counts as official toll | 4/5 | 3/4 | 1/6 | 3/6 | 3/5 | 0/5 | 3/5 | 0/3 |
| TR01 per-crash across 2020 (control) | 4/4 | 4/4 | 7/7 | 3/3 | 7/7 | 5/5 | 5/5 | 4/4 |
| TR15 small numbers (control) | 3/3 | 3/3 | 3/4 | 3/3 | 3/3 | 2/3 | 3/3 | 3/3 |
| PERMILE I1 | 1/4 | 3/3 | 2/4 | 0/3 | 0/5 | 1/5 | 1/3 | 3/4 |
| NIGHTDEF | 0/9 | 1/8 | 0/7 | 3/9 | 0/9 | 3/7 | 0/10 | 0/7 |

## 2. Findings

### Cause of E010-1

| # | Finding | Evidence |
|---|---|---|
| R1 | The profile was **correct and delivered**. | Recomputed independently; +2,901 prompt tokens on every run. |
| R2 | The profile was **partial**: it counts NULL only. | Not covered: "Unspecified" 33% in `contributing_factor_vehicle_1`, 00:00 heaping (~16×), 70% of NULL-borough rows with coordinates, 7,591 zero coordinates. It did contain everything TR05 / TR08 need. |
| R3 | The grader was **consistent with the standard**. | Two-pass agreement 0.97–0.99; K1 / TR05 cells read by hand. |
| R4 | **Root cause is the prompt.** The facts had no action hook and no slot in the output. | 0 / 18 runs mention NULL borough; profile alone leaves TR05 unchanged. |
| R5 | The profile **displaces the agent's own checks**. | NULL-inspecting queries 0.7 → 0.1 per run. |
| R6 | Knowing ≠ doing even without a profile. | F1 agents that found NULL boroughs themselves still did not disclose them. |
| R7 | An action hook is what works. | Slot alone: TR05 7/7 → 2/8 (C1). Profile adds nothing on top (C2 ≈ C1). Just-in-time notes alone help partly (C3). |
| R8 | The effect is specific. | Controls TR01 and TR15 move in no arm. |

### Method

| # | Finding | Consequence |
|---|---|---|
| M1 | Day-to-day noise is large: the same D v2 prompt gave 49% / 50% / 42% under g8.2 (51% / 50% / 42% under g8.1). F1's 33% was a favourable draw. | Keep rule compares with a **same-day baseline** only. |
| M2 | The harness was not hermetic: OpenCode auto-loaded `~/.claude/skills` into the agent context (+237 tokens from 11-07). No measurable effect (50% vs 51%). | Fixed 11-13. `call_model` disables external skills and Claude Code loading; meta records first-step tokens (constant per prompt since). |
| M3 | Coverage numbers collided with the values-only provenance rule. They were true (659,713 / 2,132,218 etc. verified). | g8.1 decision 9: a computed `check_<id>.csv` is a source. |
| M4 | TR01 demanded a cause that neither the data nor the dictionary contains. | g8.1 decision 8: disclose the visible fall and its effect; the cause is not required. |
| M5 | C5 leak: "pile-up" checks on outcome columns (counting zeros) revealed outcome counts. 136 check rows in 7 / 18 runs. | C5 v2: outcome columns are checked for missing values only. Result: 0 such rows. |
| M6 | C5 moved the night definition onto the chart only (NIGHTDEF 3/7). | C5 v2: definitions also go in the text. Result: 0/7. |
| M7 | Provenance false positives: "31" (date), "13 years" (calendar length) and "1,000" (rate scale) counted as unsourced; they caused all 8 of C5 v2's unsourced options. | **Closed 11-19** (Bo): decision 10 / **g8.2**, read from context; exempt numbers listed in `exempt_numbers`. C5 v2 41% → 22%, baseline 11-13 unchanged at 42%. |
| M8 | 2 grader errors on C5 v2 UC: "0 missing death values in 2013–2025" was judged against the 2026 NULLs. | For human review. |
| M9 | Embedding probe: paraphrase < unrelated AUC ≈ 1.0, paraphrase < one-field neighbour 0.73 (mpnet) / 0.85 (MiniLM). | Embedding is diagnostic only; the judge decides substitution; both models reported. A teammate's F3 trial uses the leaky chart condition: method shakedown, not a result. |

## 3. Decisions (Bo)

| Date | Decision |
|---|---|
| 11-08 | E010-1 recorded and **reverted**. Diagnose the cause; run candidates; C5 = Bo's Plan → Data check → Final plan. Embedding is diagnostic only. |
| 11-13 | All four accepted: g8.1, TR01 wording, C5 v2, hermetic harness. |
| 11-19 | **Option (a): C5 v2 becomes E010-v3**, the new base. Next target: I1 (PERMILE, TR01). |
| 11-19 | **Calendar and unit numbers are not unsourced** (decision 10, g8.2; all arms re-scored). With it C5 v2 passes the keep rule on silent-error (22% vs 42% same day); the only remaining exception is UC 5/37 vs 4/43 (M8). |

## 4. Open items

- Human review: 2 UC cells (M8); `review.csv` disagreements per arm.
- 19 neighbour questions: teammate check.
- `values.csv`-only reverse-inference runner for the formal round-trip distance.
- E010-v4: the I1 target (`ITERATIONS.md`, 11-19). It bundles two changes: keep only if both PERMILE and TR01 fall and nothing rises; if mixed, split into two arms.
- After v4 (proposed by Bo's other session, Bo to confirm): held-out P1–P10, E010-v3 vs D v2 same day hermetic; F2 phrasing robustness; `values.csv`-only reverse-inference runner + judge v0 validated on human labels; the four numbers on D v2 vs E010-v3.
