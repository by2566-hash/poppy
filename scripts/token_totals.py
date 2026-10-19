#!/usr/bin/env python3
"""Full token totals per run, recomputed from events.jsonl (for runs recorded before 2026-10-19, whose
meta.json only kept input/output).

  python3 scripts/token_totals.py <results dir>     e.g. experiments/E007-pilot-prompts/results/C-v3
"""
import json, sys
from pathlib import Path


def totals(events):
    t = {"input": 0, "output": 0, "reasoning": 0, "cache_read": 0, "cache_write": 0, "total": 0}
    for line in Path(events).read_text().splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("type") != "step_finish":
            continue
        k = e.get("part", {}).get("tokens") or {}
        for f in ("input", "output", "reasoning", "total"):
            t[f] += k.get(f, 0) or 0
        t["cache_read"] += (k.get("cache") or {}).get("read", 0) or 0
        t["cache_write"] += (k.get("cache") or {}).get("write", 0) or 0
    return t


if __name__ == "__main__":
    for d in sorted(Path(sys.argv[1]).glob("*/")):
        for name in ("events.jsonl", "events_review.jsonl"):
            if (d / name).exists():
                print(d.name, name, totals(d / name))
