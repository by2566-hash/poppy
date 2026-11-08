"""E010-1 diagnosis: did the profile reach the model, and did the agent act on data facts? Reads stored event traces only.

Per run: prompt tokens of the first step (input + cache write + cache read), number of tool calls, number of data
queries, queries that look at NULLs, queries that look at borough NULLs, todo/text mentions of NULL / missing / partial.
Run: ~/.poppy/venv/bin/python experiments/E010-loop/diagnosis/trace_stats.py <results dir> [<results dir> ...]
"""
import json, re, sys, statistics
from pathlib import Path

NULLQ = re.compile(r"is\s+null|is\s+not\s+null|isna|isnull|notna|dropna|count\(\*\)\s*-\s*count\(|null", re.I)
BORO_NULL = re.compile(r"borough[^\n]{0,40}is\s+(not\s+)?null|borough\W+\.isna|borough[^\n]{0,30}null", re.I)
YEARQ = re.compile(r"group by[^\n]{0,30}year|year\(crash_date\)[^\n]{0,40}count|strftime\([^)]*%Y", re.I)
WORDS = re.compile(r"\bnull\b|missing|partial|incomplete|not recorded|no borough|unknown borough", re.I)


def run_stats(run):
    ev = [json.loads(l) for l in (run / "events.jsonl").read_text().splitlines() if l.strip()]
    first = next(e for e in ev if e["type"] == "step_finish")["part"]["tokens"]
    prompt_tok = first["input"] + first["cache"]["write"] + first["cache"]["read"]
    tools = [e["part"] for e in ev if e["type"] == "tool_use"]
    cmds = [json.dumps(t.get("state", {}).get("input", {})) for t in tools]
    queries = [c for c in cmds if re.search(r"select|duckdb|read_parquet|pandas|pd\.", c, re.I)]
    before_first_png = []
    for c in cmds:
        if "savefig" in c or ".png" in c:
            break
        before_first_png.append(c)
    texts = " ".join(e["part"].get("text", "") for e in ev if e["type"] == "text") + " " + \
        " ".join(c for c, t in zip(cmds, tools) if t.get("tool") == "todowrite")
    return {"prompt_tok": prompt_tok, "tools": len(tools), "queries": len(queries),
            "explore_before_chart": sum(bool(re.search(r"select|duckdb", c, re.I)) for c in before_first_png),
            "null_queries": sum(bool(NULLQ.search(c)) for c in queries),
            "borough_null_queries": sum(bool(BORO_NULL.search(c)) for c in queries),
            "year_count_queries": sum(bool(YEARQ.search(c)) for c in queries),
            "null_words_in_text": len(WORDS.findall(texts))}


if __name__ == "__main__":
  for d in map(Path, sys.argv[1:]):
      print(f"\n## {d.name}")
      rows = {}
      for run in sorted(p for p in d.iterdir() if (p / "events.jsonl").exists()):
          rows[run.name] = s = run_stats(run)
          print(f"{run.name:8s} " + " ".join(f"{k}={v}" for k, v in s.items()))
      for q in ["K1", "K2", "K3", "A1", "A2", "I1"]:
          rs = [v for k, v in rows.items() if k.startswith(q + "-")]
          if rs:
              print(f"  {q} mean: " + " ".join(f"{k}={statistics.mean(r[k] for r in rs):.1f}" for k in rs[0]))
      print("  ALL mean: " + " ".join(f"{k}={statistics.mean(r[k] for r in rows.values()):.1f}" for k in next(iter(rows.values()))))
