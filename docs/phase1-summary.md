# Phase 1 summary (2026-10-20)

- **Question:** when an AI agent's chart and answer are not good enough, do you fix it in the prompt (C: self-check instruction) or build a step (B: independent read-only review, then revision)? Added on Ryan's request: D (three framings with verbalized probabilities) and a second model (GPT-6 Luna vs free mimo).
- **Status:** all runs collected; machine-checkable results below. **Not yet done:** the team's blind quality scoring (8 binary criteria, `experiments/E007-pilot-prompts/SCORING.md`), so no claim yet that one arm is *better* than another.
- **Set:** the 6 pilot questions (3 clear K1–K3, 2 ambiguous A1–A2, 1 insufficient-evidence I1). B's prompts were tuned on these questions, so B is favoured on them. P1–P10 are untouched and held out for phase 2.

## 1. What was built (and why it took most of the time)

| Piece | Why it was needed | Where |
|---|---|---|
| Bounded agent runs (15 steps, 600 s), traces, `meta.json` with prompt/config hashes and environment | free tier cannot do a tool-less single call; every run must be reproducible | `experiments/E006-mimo-screen`, `E007-pilot-prompts/run_pilot.py` |
| Sandbox v2: no network, no reading the repo, own data copy, isolated review folder | the agent downloaded mileage data from the web, could read the answer key, and the reviewer inherited the analyst's permissions | `PROTOCOL.md` amendments 2026-10-15; `scripts/check_env.py` |
| B contract and end states; acceptance = "B runs as designed", not "B helps" | tuning on effect with pilot data would favour B | `PROTOCOL.md` 2026-10-15; `check_contract.py` |
| Frozen prompts with SHA-256 | no edits after the comparison starts | `FROZEN.md` (A v1, B critique v4 + revise v3, C v3, D v1) |
| One team environment | a teammate's venv could not start under the sandbox | `scripts/setup_env.sh`, `~/.poppy/venv` |

## 2. Machine-checkable results (one run per cell; Luna D: run 1 of 3)

✓ = complete (chart, values and a written answer, no step-cap narration; B: a defined end state with an answer). Number = share of the gold series found in the plotted values (A2 not computed: arms chose different day/night windows, so there is no single gold series).

| Model | Arm | K1 | K2 | K3 | A1 | A2 | I1 | Complete | Median steps | Median s |
|---|---|---|---|---|---|---|---|---|---|---|
| mimo | A | ✓ 1.00 | ✓ 1.00 | ✓ 1.00 | ✗ | ✓ | ✓ 1.00 | 5/6 | 7 | 100 |
| mimo | B (extra over A) | ✓ 1.00 | ✓ 1.00 | ✓ 1.00 | ✗ (A had no answer) | ✓ | ✓ 1.00 | 5/6 | +5 | +98 |
| mimo | C | ✓ 1.00 | ✗ | ✓ 1.00 | ✗ | ✗ | ✗ | 2/6 | 15 | 143 |
| Luna | A | ✓ 1.00 | ✓ 1.00 | ✓ 1.00 | ✓ 1.00 | ✓ | ✓ 1.00 | 6/6 | 13 | 157 |
| Luna | B (extra over A) | ✓ 1.00 | ✓ 1.00 | ✓ 1.00 | ✓ 1.00 | ✓ | ✓ 1.00 | 6/6 | +1 | +11 |
| Luna | C | ✓ 1.00 | ✓ 1.00 | ✓ 1.00 | ✓ 1.00 | ✓ | ✓ 1.00 | 6/6 | 11 | 51 |
| Luna | D (top option) | ✓ 1.00 | ✓ 1.00 | ✓ 1.00 | ✓ 0.50* | ✓ | ✓ 1.00 | 6/6 (18/18 over 3 runs) | 12.5 | 94 |

\* D's top option on A1 plots pedestrian injuries only; the gold has injuries and deaths. Another option covers deaths.

Gold match says the plotted numbers are right. It does not say the chart or the conclusion is right: the I1 runs plot the correct motorist deaths and can still claim a per-mile trend. That is what the blind scoring and the trap sheet are for.

What the reviewer (B) did:

| | K1 | K2 | K3 | A1 | A2 | I1 |
|---|---|---|---|---|---|---|
| mimo | 1 issue, fixed ("pandemic" cause) | 1, fixed (ranking) | none | not run | 2, fixed (NULL-sum bug, wrong baseline) | 4, fixed (shading, unsupported mileage, misnamed column, contradicted caveat) |
| Luna | none | 2, fixed | none | none | 2, fixed | none |

## 3. Findings so far (each with its evidence)

1. **The agent fixes errors that crash, not errors that run silently.** mimo A fixed 6 crash-type errors across 10 runs inside its own run; the NULL-dropping sum (A2), a wrong ranking (K2), a "gap" that was only a ratio (K3) and an unsupported per-mile claim (I1) survived. (`ITERATIONS.md`, iteration 2/3; `LOG.md` 2026-10-15)
2. **An independent read-only reviewer catches silent errors the agent does not**, with zero invented issues and zero unflagged changes in the contract check (mimo, iteration 3). One known miss (K3 "gap"). (`ITERATIONS.md`)
3. **A self-check in the prompt mostly costs steps on the small model.** C completes 2/6 on mimo (15-step cap reached on extra verification passes) and 6/6 on Luna with the same prompt and budget, in fewer steps than Luna A. The failure on mimo is model capability, not prompt wording. (`ITERATIONS.md` C v3; `LOG.md` 2026-10-20 Jamie)
4. **On Luna, the reviewer finds less.** Luna B flagged issues on 2/6 items vs 5/5 for mimo B. Either Luna A makes fewer reviewer-visible errors or the reviewer is more lenient; the blind scoring decides. A teammate noted one Luna issue the reviewer missed (I1 y-axis starting at 70).
5. **Asking for three framings gives real alternatives, but the first choice is still the typical one.** D: 18/18 complete, three analytically distinct framings in 17/18 runs; the top-probability option is the plain count on 5 of 6 questions in all three runs. (`E009-enumerate/ITERATIONS.md`)
6. **Numbers can be right while the framing misleads, and no check in phase 1 catches it.** D on A1 dropped the 19.9–38.1% of Brooklyn-era crashes with no borough in 3/3 runs; A1 and I1 options divided by reported crashes across the 2020 recording change without a caveat (3/3 and 2/3). Every number was correct. (`E009-enumerate/ITERATIONS.md`; trap sheet in `SCORING.md`)
7. **Engineering findings that shaped the harness:** the agent reached the internet through a search tool and Python; Python could read the answer key; OpenCode merges parent-folder configs (the reviewer inherited the analyst's permissions); the free gateway stalls silently and a client cannot tell a stall from a long thought; Luna reports ~99% of input as cache. (`PROTOCOL.md` amendments; `LOG.md`)

## 4. What is left for phase 1

| Item | Owner | Blocking the midterm? |
|---|---|---|
| Blind scoring (8 criteria) of mimo A/B/C and Luna A/B/C/D, D read as D-top / D-best / D-all | team | the headline comparison needs it; without it the midterm reports the machine-checkable table and findings above |
| Repeats r2/r3 for Luna A/B/C | teammates | no (stated as single runs) |
| Second review of B's records | teammates | no |
| Slides | in progress (`docs/midterm/`) | yes |

## 5. What phase 1 hands to phase 2

- A reviewer that works when the error is visible in the material, and evidence that it misses framing errors (finding 6) → the fourth silent-error component and the framing check in `docs/v2-eval-layer-architecture.md`.
- A per-question trap sheet and gold series → the first ground truth for the evaluation layer.
- 60+ traced runs across two models and four arms with hashes and environment records → the open-coding corpus for the failure taxonomy.
- A model contrast where the same prompt fails or succeeds by model (C) → the generator × reviewer design of E008-full.
- A held-out question set (P1–P10, gold ready) never used for tuning → the test split of the regression suite.
