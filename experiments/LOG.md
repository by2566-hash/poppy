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
