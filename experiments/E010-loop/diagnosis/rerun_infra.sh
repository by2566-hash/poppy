#!/bin/zsh
# usage: rerun_infra.sh <ver> <label> [<ver> <label> ...]
# Re-runs only the units that ended on a provider error (HTTP 5xx / "overloaded" in meta errors) and are incomplete,
# up to 3 attempts each, same harness and env as the original run. An incomplete run without a provider error is a
# model failure and is kept as it is. Then collects and scores each label (two Luna passes + review).
cd /Users/yubo/Documents/Honda/poppy
set -a; source .env; set +a
export POPPY_MODEL=openai/gpt-6-luna POPPY_EXP=E010-loop PILOT_K=0 PILOT_STEPS=50 PILOT_CONCURRENCY=1 POPPY_LABEL_TAG=1119
PY=~/.poppy/venv/bin/python
infra() {  # prints "Q REP" for incomplete units of label $1 whose meta has a provider error
  $PY - "$1" <<'PYEOF'
import json, sys, pathlib
for d in sorted(pathlib.Path("experiments/E010-loop/results", sys.argv[1]).glob("*-r*")):
    m = json.loads((d / "meta.json").read_text()) if (d / "meta.json").exists() else None
    if m is None: continue
    err = " ".join(map(str, m.get("errors") or []))
    if not m.get("complete") and any(s in err for s in ("overloaded", "'statusCode': 5", "statusCode\": 5")):
        print(m["q"], m["rep"])
PYEOF
}
while [ $# -gt 0 ]; do
  ver=$1; label=$2; shift 2
  $PY scripts/collect_runs.py $label | tail -1
  for attempt in 1 2 3; do
    units=$(infra $label); [ -z "$units" ] && break
    echo "attempt $attempt $label: $units" | tr '\n' ' '; echo
    echo "$units" | while read q r; do
      PILOT_QIDS=$q PILOT_REPS=$r $PY experiments/E007-pilot-prompts/run_pilot.py D $ver 3 2>&1 | grep -E "complete=|Traceback"
      $PY scripts/collect_runs.py $label | tail -1
    done
  done
  echo "left after retries ($label): $(infra $label | tr '\n' ' ')"
  $PY scripts/score_runs.py E010-loop $label --workers 3 | tail -1
  $PY scripts/score_runs.py E010-loop $label --grader2 openai/gpt-6-luna --workers 3 | tail -1
  $PY scripts/score_runs.py E010-loop $label --review --audit 5 | tail -1
  echo "SCORED $label"
done
