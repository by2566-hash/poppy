#!/usr/bin/env python3
"""Copy finished pilot runs from the sandbox into the repo, so they can be committed and reviewed in a PR.

Usage:  python3 scripts/collect_runs.py <label> [qid ...]
        e.g. python3 scripts/collect_runs.py A-v1 K1

Source: ../poppy-sandbox/E007/<label>/<qid>-r<rep>/
Target: experiments/E007-pilot-prompts/results/<label>/<qid>-r<rep>/

Copied: meta.json, response.md, critique.md, opencode.json, the model's .py files, out/*.csv, out/*.png,
the event traces (events.jsonl, review/events.jsonl -> events_review.jsonl).
Not copied: the data link, OpenCode's private data dir, stderr logs (machine-specific paths).
"""
import json, shutil, subprocess, sys
from pathlib import Path

import os
ROOT = Path(__file__).resolve().parents[1]
EXP = os.environ.get("POPPY_EXP", "E007-pilot-prompts")   # same switch as run_pilot.py
SANDBOX = ROOT.parent / "poppy-sandbox" / EXP.split("-")[0]
TARGET = ROOT / "experiments" / EXP / "results"


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    label, qids = sys.argv[1], set(sys.argv[2:])
    src_root = SANDBOX / label
    if not src_root.exists():
        sys.exit(f"no runs found at {src_root}")
    who = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True).stdout.strip() or "unknown"
    n = 0
    for run in sorted(p for p in src_root.iterdir() if p.is_dir()):
        if qids and run.name.split("-r")[0] not in qids:
            continue
        if not (run / "meta.json").exists():
            print(f"skip {run.name}: no meta.json (run not finished)")
            continue
        dst = TARGET / label / run.name
        shutil.rmtree(dst, ignore_errors=True)
        (dst / "out").mkdir(parents=True)
        for name in ("meta.json", "response.md", "critique.md", "opencode.json", "events.jsonl",
                     "review_input.json", "review_prompt.md", "review.json", "revise_prompt.md", "changes.json", "prompt.md"):
            if (run / name).exists():
                shutil.copy(run / name, dst / name)
        if (run / "review" / "events.jsonl").exists():
            shutil.copy(run / "review" / "events.jsonl", dst / "events_review.jsonl")
        if (run / "review" / "opencode.json").exists():
            shutil.copy(run / "review" / "opencode.json", dst / "opencode_review.json")
        for f in list(run.glob("*.py")) + list((run / "out").glob("*.py")):
            shutil.copy(f, dst / f.name)
        for f in list((run / "out").glob("*.csv")) + list((run / "out").glob("*.png")) + list((run / "out").glob("*.json")):
            shutil.copy(f, dst / "out" / f.name)
        meta = json.loads((dst / "meta.json").read_text())
        meta["collected_by"] = who
        (dst / "meta.json").write_text(json.dumps(meta, indent=1))
        n += 1
        print(f"collected {label}/{run.name}")
    print(f"{n} run(s) -> {TARGET / label}")
    if n:
        print(f"next: git checkout -b runs/{label}-{who.split()[0].lower()} && git add {TARGET.relative_to(ROOT) / label} "
              f"&& git commit -m '{EXP} runs {label}' && git push -u origin HEAD   # then open a PR")


if __name__ == "__main__":
    main()
