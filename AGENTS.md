# Poppy — instructions for coding agents

Poppy is an NYU × Honda Research Institute (99P Labs) capstone: an agent that handles vague analytical questions over public road-safety data, decides whether to ask / enumerate interpretations / proceed, and produces visualizations with rationale. About 80% of the work is evaluation. Read `docs/direction-v1.md` before non-trivial work.

These project rules override any global or user-level defaults for this repository.

## Language and style
- Write all code, comments, docs, and reports in **English** (mentors read them).
- Keep reports short: lead with the result and its numbers.

## Layout
- `docs/` — direction and design notes.
- `experiments/LOG.md` — experiment log (date, setup, result incl. failures, next). Append; never rewrite past entries.
- `experiments/EXXX-name/` — one folder per experiment: `TASK.md` (the spec), scripts, `results/`, `REPORT.md`.
- `data/raw/` — downloaded files, never modified in place. `data/processed/` — derived Parquet/DuckDB. Both are git-ignored.

## Environment
- Python: `python3` (Anaconda, 3.13) with duckdb, pandas, pyarrow, matplotlib, altair available. `vl_convert` is NOT installed; save Altair/Vega-Lite specs as JSON or HTML, render PNGs with matplotlib.
- Do not install new packages or create virtualenvs without saying so in the report.
- Prefer DuckDB SQL over pandas for aggregation. Use Parquet for derived data.

## Rules
- Data engineering must stay light: no geospatial joins, no free-text parsing beyond simple normalization, unless a task says otherwise.
- Every number in a report must come from a query or script saved in the experiment folder.
- Separate verified facts (backed by a query) from interpretation.
- Never commit or print credentials. Never touch `~/.codex*` directories.
- Do not delete or overwrite files outside the experiment folder you were assigned.
