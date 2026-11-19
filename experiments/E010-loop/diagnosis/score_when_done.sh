#!/bin/zsh
# usage: score_when_done.sh <run log | -> <label>   (waits for "saved", collects, current GRADER_VERSION, two Luna passes, review sheet)
cd /Users/yubo/Documents/Honda/poppy
set -a; source .env; set +a
export POPPY_MODEL=openai/gpt-6-luna POPPY_EXP=E010-loop
if [ "$1" != "-" ]; then
  until grep -q "^saved " "$1" || grep -q "Traceback" "$1"; do sleep 20; done
  grep -q Traceback "$1" && { echo "RUN FAILED $2"; exit 1; }
  ~/.poppy/venv/bin/python scripts/collect_runs.py "$2" | tail -1
fi
~/.poppy/venv/bin/python scripts/score_runs.py E010-loop "$2" --workers 3 | tail -1
~/.poppy/venv/bin/python scripts/score_runs.py E010-loop "$2" --grader2 openai/gpt-6-luna --workers 3 | tail -1
~/.poppy/venv/bin/python scripts/score_runs.py E010-loop "$2" --review --audit 5 | tail -1
echo "SCORED $2"
