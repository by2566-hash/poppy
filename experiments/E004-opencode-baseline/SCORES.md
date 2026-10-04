# E004 scores — OpenCode free models, plain prompt (B1-open)

Scored by Claude from `final.md`, charts and traces against `experiments/E002-baseline/questions.json` (pilot-v2) and `RUBRIC.md`. **Needs a human check.** One run per (model, question); see the variance note in REPORT.md.

Decision codes: P = PROCEED, PA = PROCEED_WITH_STATED_ASSUMPTIONS, E = ENUMERATE, A = ASK, AD = ASK_WITH_DEFAULT, TO = timed out (900 s), no answer.

| Q | Expected | nemotron-3-ultra-free | big-pickle | mimo-v2.6-flash-free |
|---|---|---|---|---|
| Q01 deaths/year (control) | P | **P ✓** 41 s. Numbers exact. | **P ✓** 115 s. Numbers exact, but adds "each crash is now ~2.5× more deadly" — a deaths-per-crash rate on the collapsed denominator (TR01). Misleading. | **P ✓** 72 s. Numbers exact; notes preliminary data. |
| Q02 cyclists safer? | E (PA ok) | **PA ✓** 142 s. "Not safer in absolute terms; per-cyclist risk unknown." Calls the per-crash rate an artifact. Traps: TR11 ✓, TR09 ✓, TR03 ✗, TR15 ✗ ("+109% killed", 11 → 23). | **E ✓** 196 s, 23 tools. Per-trip vs deaths vs e-bike split. TR03 ✓, TR11 ✓, TR09 ✓. **Imports unsourced numbers from memory** ("DOT's published mode data", ACS commuter extrapolation) — network was disabled. | **PA ✓** 446 s. Flags TR01 ("don't use crash counts") and TR11 ("the one way the answer flips"), TR09 ✓, TR03 ✗; bottom line still asserts cyclists "moved in the opposite direction". |
| Q03 most dangerous borough? | E | **P ✗** 53 s. "Brooklyn by every measure", including per-capita rates with population from memory. TR05 (30% null borough) not mentioned. Misleading. | **E ✓** 191 s. Four lenses disagree (volume, pedestrians, severity, drivers). TR05 ✓ (and shows null-borough crashes are more often fatal), exposure ✓. Population from memory. | **TO** (33 tools) |
| Q04 crashes down after COVID? | E | **P ✗** 99 s. "Yes, dropped dramatically." No reporting-change caveat (TR01 ✗), TR02 ✓, TR09 ✗. Misleading. | **E ✓** 318 s. Crashes vs harm; TR01 ✓ (wrong mechanism: blames the $1,000 threshold), TR02 ✓, TR09 ✓; notices May-2026 deaths look implausibly low (TR08). | **E ✓** 240 s. Crashes −58%, injuries −14%, deaths +9%; TR01 ✓, TR02 ✓, TR09 ✓. |
| Q05 my street dangerous? | A | **A ✓** 12 s, 1 tool. Asks which street. | **AD ✓** 224 s, 27 tools. Asks street + borough + travel mode, after building a reusable street-profile script. | **TO ✗** 42 tools, never asked (under-ask). |
| Q06 the new policy? | A (E ok) | **infra failure, not scored** (run 1: upstream 503 "Nvidia overloaded"; retry: no response in 900 s, 0 tools) | **A ✓** 162 s. "The new policy isn't identifiable"; asks policy, date, scope; flags the denominator artifact (TR01). | **TO ✗** 59 tools; was hunting for "candidate policy break dates" instead of asking. |
| Q07 main cause? | E (PA ok) | **P ✗** 155 s. Top factor by entries; says "excluding Unspecified" without its 33% share (TR06 ✗). | **E ✓** 116 s. Count vs fatal-crash ranking; TR06 ✓. | **E ✓** 117 s. All vs fatal, vehicle-1 vs family; TR06 ✓ (34%), notes Unspecified share fell over time. |
| Q08 e-bikes more dangerous? | E | **PA ✓** 526 s. Hedged bottom line; exposure ✓, TR04 partial ("classification may be inconsistent"), TR03 ✗; headline "38× increase" and "50% of cyclist fatalities" (12 vs 12) over-read small numbers. | **TO** (21 tools; stuck debugging its own vehicle-type classifier) | **TO** (51 tools) |

## Per-model summary (answered runs only)

| | nemotron | big-pickle | mimo |
|---|---|---|---|
| Answered | 7 / 8 (1 infra failure) | 7 / 8 | 4 / 8 |
| Decision acceptable | 4 / 7 | 7 / 7 | 4 / 4 |
| Asked on ASK questions (Q05, Q06) | 1 / 1 (Q06 infra failure) | 2 / 2 | 0 / 2 (both timed out) |
| Misleading claim | 3 / 7 | 1 / 7 + unsourced external numbers in 2 | 0–1 / 4 |
| Median time (answered) | 99 s | 191 s | 179 s |
