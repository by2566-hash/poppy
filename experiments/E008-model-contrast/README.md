# E008 (lite) — A/B/C with GPT-6 Luna, compared with mimo (phase-1 add-on)

Run by the teammates (Chloe: A and B, 2026-10-19, moved here from `E009-enumerate/` on 2026-10-20; folder `B-v1-…` renamed to `B-v4-v3-…`, the prompt versions it actually used). Design and analysis are theirs; this README fixes the harness side so runs are comparable and reproducible.

- Prompts: the frozen phase-1 prompts (`E007-pilot-prompts/FROZEN.md`): A `A.v1.md`; B critique `B_critique.v4.md` + revise `B_revise.v3.md`; C `C_selfcheck.v3.md`. Not re-tuned for Luna (transfer condition). Every `meta.json` carries the prompt and config hashes; all 12 runs so far match the frozen hashes.
- Environment: team venv `~/.poppy/venv` (`sh scripts/setup_env.sh`), `check_env.py` READY with `POPPY_MODEL=openai/gpt-6-luna`, `check_model_vision.py` PASS. Key in the git-ignored `.env`.
- Runner: `~/.poppy/venv/bin/python experiments/E008-model-contrast/run_ab_luna.py A|B <qid>` (Chloe's launcher around `run_pilot`), `PILOT_REP=2` / `3` for repeats; or `run_pilot.py` directly with `POPPY_MODEL=openai/gpt-6-luna POPPY_EXP=E008-model-contrast`. C: `POPPY_MODEL=openai/gpt-6-luna POPPY_EXP=E008-model-contrast python3 experiments/E007-pilot-prompts/run_pilot.py C v3 1` (then `PILOT_REPS=2,3 … C v3 3`).
- Results: `results/<label>/<qid>-r<rep>/`, summaries in `runs/`, collected with `POPPY_EXP=E008-model-contrast python3 scripts/collect_runs.py <label>`, submitted by PR.
- Comparison: the mimo runs of the same prompts on the same 6 pilot questions (`E007-pilot-prompts/results/A-v1`, `B-v4-v3`, `C-v3`). Scoring rules and the per-question trap sheet: `E007-pilot-prompts/SCORING.md`.
