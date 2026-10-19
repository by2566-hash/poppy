# E008 (lite) — A/B/C with GPT-6 Luna, compared with mimo (phase-1 add-on)

Run by the teammates; design and analysis are theirs and will be recorded here with their results. This README only fixes the harness side so runs are comparable and reproducible.

- Prompts: the frozen phase-1 prompts (`E007-pilot-prompts/FROZEN.md`), unchanged, not re-tuned for Luna (transfer condition).
- Model: `POPPY_MODEL=openai/gpt-6-luna` (key in `poppy/.env`, see `docs/status-2026-10-18.md` §4). Pre-checks before scored runs: `check_env.py` READY, one image-reading check, one K1 run for the step/time profile.
- Folder: `POPPY_EXP=E008-model-contrast` (sandbox `poppy-sandbox/E008/`, results here); question set `POPPY_QSET=pilot` or `formal` as the team decides.
- Example: `POPPY_MODEL=openai/gpt-6-luna POPPY_EXP=E008-model-contrast python3 experiments/E007-pilot-prompts/run_pilot.py A v1 1`, then `POPPY_EXP=E008-model-contrast python3 scripts/collect_runs.py A-v1-openai-gpt-6-luna`, PR.
- Comparison target: the mimo runs of the same prompts on the same question set.
