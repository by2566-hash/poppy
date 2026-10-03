#!/usr/bin/env python3
"""Run Codex as the *subject* on vague questions, one isolated sandbox per question.

Isolation rules (see experiments/LOG.md, E000):
- Use a dedicated CODEX_HOME (default ~/.codex-poppy) with its own login and a minimal
  config.toml, so the user's global AGENTS.md, MCP servers and plugins are not loaded.
- Sandboxes live outside the project tree, so no project AGENTS.md is discovered.
- Each sandbox only contains ./data (parquet symlink + neutral README) and ./out.

Outputs per run are copied to experiments/E002-baseline/runs/<arm>/<qid>/.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

CODEX = "/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex"
HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]


def build_prompt(arm: str, question: str) -> str:
    template = (HERE / "prompts" / f"{arm}.md").read_text()
    return template.replace("{question}", question)


def run_one(q: dict, args: argparse.Namespace) -> dict:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    sandbox = Path(args.sandbox_root) / "E002" / args.arm / f"{q['id']}-{stamp}"
    (sandbox / "data").mkdir(parents=True)
    (sandbox / "out").mkdir()
    os.symlink(Path(args.data).resolve(), sandbox / "data" / "crashes.parquet")
    shutil.copy(args.readme, sandbox / "data" / "README.md")

    final_path = sandbox / "final.md"
    cmd = [
        CODEX, "exec", "--json", "--skip-git-repo-check", "--ephemeral",
        "-s", "workspace-write", "-C", str(sandbox),
        "-c", f"model_reasoning_effort={json.dumps(args.effort)}",
        "-o", str(final_path),
    ]
    if args.model:
        cmd += ["-m", args.model]
    for kv in args.extra_config:
        cmd += ["-c", kv]
    cmd.append(build_prompt(args.arm, q["text"]))

    env = dict(os.environ, CODEX_HOME=str(Path(args.codex_home).expanduser()))
    t0 = time.time()
    with open(sandbox / "events.jsonl", "w") as out, open(sandbox / "stderr.log", "w") as err:
        proc = subprocess.run(cmd, stdout=out, stderr=err, env=env, cwd=sandbox)
    elapsed = round(time.time() - t0, 1)

    dest = HERE / "runs" / args.arm / q["id"]
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(sandbox, dest, ignore=shutil.ignore_patterns("data"), symlinks=False)
    meta = {
        "qid": q["id"], "arm": args.arm, "question": q["text"],
        "model": args.model or "(profile default)", "reasoning_effort": args.effort,
        "extra_config": args.extra_config, "codex_home": args.codex_home,
        "sandbox": str(sandbox), "started_utc": stamp, "elapsed_s": elapsed,
        "exit_code": proc.returncode,
    }
    (dest / "meta.json").write_text(json.dumps(meta, indent=2))
    print(f"[{q['id']}] arm={args.arm} exit={proc.returncode} {elapsed}s -> {dest}", flush=True)
    return meta


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--arm", choices=["plain", "policy"], required=True)
    p.add_argument("--qids", default="", help="comma-separated, default all")
    p.add_argument("--codex-home", default="~/.codex-poppy")
    p.add_argument("--model", default="")
    p.add_argument("--effort", default="high")
    p.add_argument("--extra-config", action="append", default=[])
    p.add_argument("--concurrency", type=int, default=4)
    p.add_argument("--sandbox-root", default=str(PROJECT.parent / "poppy-sandbox"))
    p.add_argument("--data", default=str(PROJECT / "data" / "processed" / "nyc_crashes.parquet"))
    p.add_argument("--readme", default=str(HERE / "sandbox_README.md"))
    args = p.parse_args()

    questions = json.loads((HERE / "questions.json").read_text())["questions"]
    wanted = {s.strip() for s in args.qids.split(",") if s.strip()}
    if wanted:
        questions = [q for q in questions if q["id"] in wanted]

    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        metas = list(pool.map(lambda q: run_one(q, args), questions))
    summary = HERE / "runs" / args.arm / "_batch_summary.json"
    summary.write_text(json.dumps(metas, indent=2))
    print(f"done: {len(metas)} runs, summary at {summary}")


if __name__ == "__main__":
    main()
