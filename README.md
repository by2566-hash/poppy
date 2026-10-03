# Poppy — agentic data visualization for vague questions

NYU Center for Data Science × Honda Research Institute (99P Labs) capstone, Fall 2026.

Poppy is an agent that receives a **vague analytical question** over public data, decides whether to **ask** a clarifying question, **enumerate** legitimate interpretations, or **proceed**, then produces visualizations with rationale and flags data traps that would mislead the answer. About 80% of the work is evaluation.

**Status:** early exploration. Direction and scenario are proposals pending team agreement.

## Start here

| Document | What it holds |
|---|---|
| [`docs/direction-v1.md`](docs/direction-v1.md) | Core research question, agent behavior, evaluation layers, baselines |
| [`docs/scenario-data-v1.md`](docs/scenario-data-v1.md) | Scenario (NYC traffic safety, journalist / fact-checker persona), data bundle, trap catalog TR01–TR17 |
| [`docs/decide-layer-v1.md`](docs/decide-layer-v1.md) | Decision layer (`decide()`) backends: local LLM logprobs, Jev, Clef-flash |
| [`experiments/LOG.md`](experiments/LOG.md) | Experiments log |
| [`docs/FIELD_GUIDE.md`](docs/FIELD_GUIDE.md) | Learnings field guide |
| [`AGENTS.md`](AGENTS.md) | Rules for coding agents working in this repo |

## Layout

```
docs/            direction, scenario, design notes, field guide
experiments/     one folder per experiment (TASK.md, scripts, results, REPORT.md) + LOG.md
data/raw/        downloaded source files (git-ignored)
data/processed/  derived Parquet (git-ignored)
```

## Reproduce the data

```bash
curl -L -o data/raw/nyc_crashes_h9gi-nx95.csv "https://data.cityofnewyork.us/api/views/h9gi-nx95/rows.csv?accessType=DOWNLOAD"
python3 experiments/E001-data-card/run_experiment.py   # needs duckdb (pip install duckdb)
```

The NYC source froze updates at 2026-06-15; results here use the snapshot downloaded on 2026-10-03.

## Team

Mentors: Ryan Lingo, Rajeev Chhajer (Honda Research Institute, 99P Labs).
