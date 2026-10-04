#!/usr/bin/env python3
"""Run OpenCode free models as baseline subjects on the E002 vague-question set.

Each (model, question) run gets its own sandbox outside the repo with:
- ./data/crashes.parquet (symlink) + ./data/README.md (neutral dictionary)
- ./opencode.json restricting tools (OpenCode has no OS sandbox)
- its own XDG_DATA_HOME, so runs can go in parallel without SQLite lock clashes
  and do not pollute the user's OpenCode history.
Outputs (events.jsonl, final text, charts, meta.json) are copied to runs/<model>/<qid>/.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
E002 = PROJECT / "experiments" / "E002-baseline"

PERMISSIONS = {
    "$schema": "https://opencode.ai/config.json",
    "permission": {
        "edit": "allow",
        "webfetch": "deny",
        "external_directory": "deny",
        "bash": {
            "*": "deny", "python3 *": "allow", "python *": "allow", "ls": "allow",
            "ls *": "allow", "mkdir *": "allow", "head *": "allow", "cat *": "allow",
        },
    },
}


def summarize(events_path: Path) -> dict:
    tokens = {"input": 0, "output": 0, "reasoning": 0}
    texts, tools, errors = [], 0, []
    for line in events_path.read_text().splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        part = e.get("part", {})
        if e.get("type") == "step_finish":
            for k in tokens:
                tokens[k] += (part.get("tokens") or {}).get(k, 0)
        elif e.get("type") == "tool_use":
            tools += 1
        elif e.get("type") == "text":
            texts.append(part.get("text", ""))
        elif e.get("type") == "error":
            errors.append(str(e)[:500])
    return {"tokens": tokens, "tool_calls": tools, "errors": errors, "final_text": "\n\n".join(texts)}


def run_one(model: str, q: dict, args: argparse.Namespace) -> dict:
    sandbox = Path(args.sandbox_root) / "E004" / model / q["id"]
    if sandbox.exists():
        shutil.rmtree(sandbox)
    (sandbox / "data").mkdir(parents=True)
    (sandbox / "out").mkdir()
    os.symlink(Path(args.data).resolve(), sandbox / "data" / "crashes.parquet")
    shutil.copy(E002 / "sandbox_README.md", sandbox / "data" / "README.md")
    (sandbox / "opencode.json").write_text(json.dumps(PERMISSIONS, indent=2))

    prompt = (E002 / "prompts" / f"{args.arm}.md").read_text().replace("{question}", q["text"])
    cmd = ["opencode", "run", "--pure", "--format", "json", "-m", f"opencode/{model}",
           "--dir", str(sandbox), prompt]
    env = dict(os.environ, XDG_DATA_HOME=str(sandbox / ".ocdata"))
    t0 = time.time()
    timed_out = False
    with open(sandbox / "events.jsonl", "w") as out, open(sandbox / "stderr.log", "w") as err:
        try:
            proc = subprocess.run(cmd, stdout=out, stderr=err, env=env, cwd=sandbox, timeout=args.timeout)
            code = proc.returncode
        except subprocess.TimeoutExpired:
            code, timed_out = None, True
    elapsed = round(time.time() - t0, 1)

    summary = summarize(sandbox / "events.jsonl")
    dest = HERE / "runs" / args.arm / model / q["id"]
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(sandbox, dest, ignore=shutil.ignore_patterns("data", ".ocdata", "stderr.log"))
    (dest / "final.md").write_text(summary.pop("final_text"))
    meta = {"model": model, "qid": q["id"], "arm": args.arm, "question": q["text"],
            "elapsed_s": elapsed, "exit_code": code, "timed_out": timed_out, **summary}
    (dest / "meta.json").write_text(json.dumps(meta, indent=2))
    print(f"[{model} {q['id']}] exit={code} timeout={timed_out} {elapsed}s tools={meta['tool_calls']}", flush=True)
    return meta


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--models", default="nemotron-3-ultra-free,big-pickle,mimo-v2.6-flash-free")
    p.add_argument("--qids", default="")
    p.add_argument("--arm", choices=["plain", "policy"], default="plain")
    p.add_argument("--concurrency", type=int, default=3)
    p.add_argument("--timeout", type=int, default=900)
    p.add_argument("--sandbox-root", default=str(PROJECT.parent / "poppy-sandbox"))
    p.add_argument("--data", default=str(PROJECT / "data" / "processed" / "nyc_crashes.parquet"))
    args = p.parse_args()

    questions = json.loads((E002 / "questions.json").read_text())["questions"]
    wanted = {s.strip() for s in args.qids.split(",") if s.strip()}
    if wanted:
        questions = [q for q in questions if q["id"] in wanted]
    jobs = [(m.strip(), q) for m in args.models.split(",") for q in questions]

    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        metas = list(pool.map(lambda job: run_one(job[0], job[1], args), jobs))
    out = HERE / "runs" / args.arm / "_batch_summary.json"
    out.write_text(json.dumps(metas, indent=2))
    print(f"done: {len(metas)} runs -> {out}")


if __name__ == "__main__":
    main()
