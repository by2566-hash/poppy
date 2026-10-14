# Scope Freeze v0 (Poppy Capstone)

- **Date:** 2026-10-12
- **Status:** FROZEN (Boundary lock for Proposal v1)
- **Role Alignment:** Applied AI Engineer + Forward Deployed Engineer (FDE)

---

## 1. Project Mission & Deliverable
- **Core Deliverable:** A step-wise evaluation harness and playbook for LLM analytical pipelines.
- **Agent Stance:** The agent pipeline is deliberately simple and serves solely as the testbed for the evaluation methodology.

---

## 2. In-Scope Boundaries (Strict)

### 2.1 Dataset (Single Table Gate)
- **Included:** NYC Motor Vehicle Collisions — Crashes (`h9gi-nx95`), snapshot pinned at 2026-10-03 (`nyc_crashes.parquet`, 2,269,187 rows).
- **License Status:** `LICENSE_STATUS=UNKNOWN`. Restricted strictly to internal academic capstone prototyping until official NYC Open Data terms evidence is recorded.

### 2.2 Question Scope (Literal 3 Questions — Trend Family)
Only 3 literal questions forming the Trend Family (`[Entity/Mode] safety over [Time/Event]`):
1. **T1 (Control):** "How many people were killed in motor vehicle crashes in NYC each year from 2016 through 2025? Show the trend." (`PROCEED`)
2. **T2 (Ambiguous):** "Are cyclists safer in NYC than they used to be?" (`ENUMERATE` / `PROCEED_WITH_STATED_ASSUMPTIONS`)
3. **T3 (Must-Ask):** "Has the new policy made things better for pedestrians?" (`ASK` -> single slot clarification)

### 2.3 Evaluation Subject Models
3 Free OpenCode Zen models evaluated in baseline and iteration:
- `big-pickle`
- `nemotron-3-ultra-free`
- `mimo-v2.6-flash-free`

### 2.4 Visualizations (Only 2 Types)
- **T1: Time-series Line Chart** (single or segmented line with vertical event markers and confidence/partial annotations).
- **T2: Indexed Multi-series Chart** (base year = 100, comparing divergent series like crashes, injuries, deaths).

### 2.5 Pipeline Architecture
- 4 steps: `S1 Clarify Intent` -> `S2 Analysis Plan` -> `TC Trap Check (Code)` -> `S3 Render (SQL + Spec)` -> `S4 Narrative`.
- Execution: Single structured JSON call per step. **No autonomous agentic looping.**

---

## 3. Out-of-Scope (Explicitly Cut / Deferred)
- ❌ Datasets: `persons`, `vehicles`, `bike_monthly` (East River bridges), Chicago, FARS, Ohio/ODOT.
- ❌ Questions: Borough ranking (Q03), street-level search (Q05), crash factors/cause ranking (Q07).
- ❌ Chart Types: Geospatial maps, scatter plots, dashboards, multi-page reports.
- ❌ Modeling: Unconstrained Python agents, multi-agent debates, closed frontier models as mandatory runtime.
- ❌ UI/UX: Interactive web apps, complex frontends (Output is static rendered HTML/markdown View).

---

## 4. Enforcement Rule
Any feature or experiment proposed outside these boundaries is rejected unless a formal Scope Defrost amendment is approved by the team and mentor.
