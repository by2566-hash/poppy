"""C5 process checks from the stored traces (no model call).
Per run: plan / check files written; whether an outcome aggregate (SUM/AVG/... of an injured or killed column) was run
before the analysis stage started (first chart or values file written) = a breach of "no results in Plan / Data check /
Final plan"; whether the first data query came after the first plan file (Plan made before looking at data).
Run: ~/.poppy/venv/bin/python experiments/E010-loop/diagnosis/c5_process.py <results dir>
"""
import json, re, sys
from pathlib import Path

OUTCOME = re.compile(r"(sum|avg|mean|max|min)\s*\(\s*\"?number_of_\w*(injured|killed)"
                     r"|number_of_\w*(injured|killed)\"?\s*(=|>|<>|!=|>=)\s*\d", re.I)   # sums, or counts by outcome value (zeros reveal the rest)
QUERY = re.compile(r"select|read_parquet|duckdb", re.I)
d = Path(sys.argv[1])
tot = {"runs": 0, "plan_files": 0, "check_files": 0, "options": 0, "outcome_before_analysis": 0, "check_rows_by_outcome_value": 0, "query_before_plan": 0}
for run in sorted(p for p in d.iterdir() if (p / "events.jsonl").exists()):
    ev = [json.loads(l) for l in (run / "events.jsonl").read_text().splitlines() if l.strip()]
    calls = [json.dumps(e["part"].get("state", {}).get("input", {})) for e in ev if e["type"] == "tool_use"]
    first_plan = next((i for i, c in enumerate(calls) if "plan_" in c and ".json" in c), None)
    first_query = next((i for i, c in enumerate(calls) if QUERY.search(c) and "crashes" in c), None)
    first_analysis = next((i for i, c in enumerate(calls) if "savefig" in c or re.search(r"values_\d+\.csv", c)), len(calls))
    outcome_early = any(OUTCOME.search(c) for c in calls[:first_analysis])
    opts = json.loads((run / "out" / "options.json").read_text())["options"]
    chk_outcome = sum(bool(re.search(r"(injur|kill|fatal|death)", l, re.I) and re.search(r"\bzero\b|= ?0|nonzero|non-zero|> ?0", l, re.I))
                      for f in (run / "out").glob("check_*.csv") for l in f.read_text().splitlines())
    n_plan = len(list((run / "out").glob("plan_*.json"))); n_chk = len(list((run / "out").glob("check_*.csv")))
    qbp = first_plan is None or (first_query is not None and first_query < first_plan)
    print(f"{run.name:7s} options={len(opts)} plan_files={n_plan} check_files={n_chk} outcome_before_analysis={outcome_early} outcome_value_rows_in_check={chk_outcome} query_before_first_plan={qbp}")
    tot["runs"] += 1; tot["plan_files"] += n_plan; tot["check_files"] += n_chk; tot["options"] += len(opts)
    tot["outcome_before_analysis"] += outcome_early; tot["check_rows_by_outcome_value"] += chk_outcome; tot["query_before_plan"] += qbp
print(tot)
