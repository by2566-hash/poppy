"""Does the pre-hermetic grader context matter? (open caveat on the ruler, 2026-11-19)

Verdicts of the 11-08 arms were produced before `call_model` disabled OpenCode's external skills (the grader context then
held a ~237-token skill description). This re-grades a stratified sample of those options hermetically with the same
grader prompt and compares item by item with the stored pass-1 verdicts. Reference: two hermetic-vs-hermetic Luna passes
agree on 0.97-0.99 of cells, so agreement in that band means no detectable effect.

Units of A1 / I1 are skipped (re-graded hermetically under g8.1 already). The sheet is not modified; records go to
grader/<version>-pherm/ inside each run.

usage: set -a; source .env; set +a; POPPY_MODEL=openai/gpt-6-luna POPPY_EXP=E010-loop python grader_hermetic_check.py [n_per_arm=6]
"""
import csv, json, os, random, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts")); sys.path.insert(0, str(ROOT / "experiments" / "E006-mimo-screen"))
os.environ["GRADER_PASS"] = "herm"
import score_runs as s  # noqa: E402
from run_screen import call_model  # noqa: E402

ARMS = ["D-v2-kfree", "D-v2-kfree-hermetic", "D-v2-kfree-profile", "D-v2-cov-kfree", "D-v2-cov-kfree-profile", "D-v2-kfree-jit",
        "D-v2-cov-kfree-jit", "D-v2-plan-kfree"]
N = int(sys.argv[1]) if len(sys.argv) > 1 else 6
rng = random.Random(1119)
todo = []
for arm in ARMS:
    label = f"{arm}-openai-gpt-6-luna"
    d = ROOT / "experiments" / "E010-loop" / "results" / label
    rows = [r for r in csv.DictReader((d / "scores.csv").open()) if r["q"] not in ("A1", "I1")]
    for r in rng.sample(rows, min(N, len(rows))):
        u = [x for x in s.load_units(d / f"{r['q']}-r{r['rep']}") if str(x["option"]) == r["option"]][0]
        todo.append((label, r, u))
with ThreadPoolExecutor(3) as ex:
    outs = list(ex.map(lambda t: s.run_grader(t[2], t[0], call_model), todo))
cells = diff = 0; changed = []
for (label, r, u), o in zip(todo, outs):
    for k in s.grader_items(u["base"]):
        a, b = r.get(f"m_{k}", ""), o.get(f"m_{k}", "")
        if a and b:
            cells += 1
            if a != b:
                diff += 1; changed.append({"label": label, "q": r["q"], "rep": r["rep"], "option": r["option"], "item": k, "stored": a, "hermetic": b})
out = {"options": len(todo), "cells": cells, "disagreements": diff, "agreement": round(1 - diff / cells, 4) if cells else None, "changed": changed}
(Path(__file__).parent / "grader_hermetic_check.json").write_text(json.dumps(out, indent=1))
print(json.dumps({k: v for k, v in out.items() if k != "changed"})); [print(c) for c in changed]
