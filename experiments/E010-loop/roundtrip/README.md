# roundtrip/: values.csv-only reverse inference (T3)

Design, condition and limits: `DESIGN.md`. Status 2026-11-19: pipeline built and smoke-tested on 4 options; the full run (T5) is **not** done.

## Run

Reverse inference (API calls; key from the git-ignored `.env`):

```bash
set -a; source .env; set +a
POPPY_MODEL=openai/gpt-6-luna ~/.poppy/venv/bin/python experiments/E010-loop/roundtrip/run_reverse.py <label> --n 3
```

Options: `--exp E010-loop` (default), `--only K1-r1 I1-r2`, `--limit K` (first K options), `--workers 3`. Resume-safe: a guess whose record parses and whose prompt is unchanged is not called again.

Embedding distances (local models, offline, separate venv):

```bash
HF_HUB_OFFLINE=1 ~/.poppy/embed-venv/bin/python experiments/E010-loop/roundtrip/distance.py <label> [<label> ...]
```

Writes `results/<label>/guesses.jsonl` (distances filled in) and `distance_summary.json`.

## Smoke test (2026-11-19, N = 2)

```bash
POPPY_MODEL=openai/gpt-6-luna ~/.poppy/venv/bin/python experiments/E010-loop/roundtrip/run_reverse.py D-v2-kfree-openai-gpt-6-luna-1113 --only I1-r1 --limit 2 --n 2
POPPY_MODEL=openai/gpt-6-luna ~/.poppy/venv/bin/python experiments/E010-loop/roundtrip/run_reverse.py D-v2-plan2-kfree-openai-gpt-6-luna-1119 --only A1-r2 --limit 2 --n 2
```

8 / 8 guesses parsed, 0 tool calls.

| Option | Header shown | Guessed question (g1) | mpnet asked→guess (core) | repeat floor |
|---|---|---|---|---|
| baseline 11-13, I1-r1 o1 | `year,motorist_deaths` | How many motorist deaths were recorded each year from 2013 through 2025? | 0.39 | 0.015 |
| baseline 11-13, I1-r1 o2 | `year,reported_crashes,motorist_deaths,motorist_deaths_per_100k_crashes` | How did motorist deaths per 100,000 reported crashes change from 2013 to 2025? | 0.37 | 0.002 |
| v3 11-19, A1-r2 o1 | `year,total,eligible_brooklyn_crash_records` | For each year, what was the total compared with the number of eligible Brooklyn crash records? | 0.53 | 0.022 |
| v3 11-19, A1-r2 o2 | `year,total,eligible_brooklyn_crash_records` | How many records meeting the analysis's unspecified criterion were there each year among eligible Brooklyn crash records? | 0.54 | 0.164 |

Asked: I1 "Did the risk of a motorist being killed per mile driven in NYC decline from 2013 to 2025? …"; A1 "Has road safety for pedestrians in Brooklyn gotten better since 2013? …". Paraphrase reference: mpnet 0.069 (max 0.141).

Reading (4 options, not a result): the I1 guesses name exactly the substitution (deaths, deaths per crash; no "per mile"), which is what the judge needs. The A1 tables have a generic `total` column, so the measure is not recoverable from the table at all.
