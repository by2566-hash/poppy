"""Part 3 of the mimo screen: step ① as ONE bounded OpenCode agent run in which the model writes AND
executes its own code (the way OpenCode is meant to be used, as in E004), then harness collects artifacts.
6 clear questions x 3 repeats. Measures completion, artifacts, tool calls, time, value agreement, consistency."""
import csv, json, os, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from common import HERE, MODEL, PARQUET, QUESTIONS, DATA_DICTIONARY
from run_screen import call_model, numbers_in, gold_cover, SANDBOX

STEPS = int(os.environ.get("E006_STEPS", 10))
TIMEOUT = int(os.environ.get("E006_TIMEOUT", 420))
LABEL = os.environ.get("E006_LABEL", "agent")
CONFIG = {"$schema": "https://opencode.ai/config.json",
          "permission": {"external_directory": "deny", "webfetch": "deny", "edit": "allow",
                         "bash": {"*": "deny", "python3 *": "allow", "python *": "allow", "ls": "allow",
                                  "ls *": "allow", "mkdir *": "allow", "head *": "allow", "cat *": "allow"}},
          "agent": {"build": {"steps": STEPS}}}
PROMPT = """You are a data analyst. Answer the user's question about the data described below.

{dictionary}

Write and run code yourself. Save the chart to ./out/initial.png and the plotted data to ./out/values.csv
(create ./out if needed). When finished, reply with a line `ANSWER:` followed by a short written answer
for a reader of the chart, based on the numbers you computed.

Question: {question}"""

def one(job):
    q, rep = job
    sb = SANDBOX / f"{LABEL}-{q}-r{rep}"
    shutil.rmtree(sb, ignore_errors=True)
    (sb / "data").mkdir(parents=True); (sb / "out").mkdir()
    os.symlink(PARQUET, sb / "data" / "crashes.parquet")
    (sb / "opencode.json").write_text(json.dumps(CONFIG))
    r = call_model(sb, PROMPT.format(dictionary=DATA_DICTIONARY, question=QUESTIONS[q]), timeout=TIMEOUT)
    steps = sum('"type":"step_start"' in l for l in (sb / "events.jsonl").read_text().splitlines())
    ans_pos = r["text"].rfind("ANSWER:")
    answer = r["text"][ans_pos + 7:].strip() if ans_pos >= 0 else None
    v = sb / "out" / "values.csv"
    rec = {"q": q, "rep": rep, "call_ok": r["exit"] == 0 and not r["timed_out"] and not r["errors"],
           "timed_out": r["timed_out"], "secs": r["secs"], "tool_calls": r["tool_calls"], "steps": steps,
           "hit_step_limit": steps >= STEPS, "errors": r["errors"],
           "answer_ok": bool(answer and len(answer) >= 15), "png": (sb / "out" / "initial.png").exists(),
           "values": v.exists(), "tokens": r["tokens"], "gold_cover": None}
    if v.exists():
        ns = numbers_in(v); rec["plotted_numbers"] = sorted(round(n, 2) for n in ns); rec["gold_cover"] = gold_cover(q, ns)
    (sb / "response.md").write_text(r["text"])
    print(f"[{q} r{rep}] ok={rec['call_ok']} timeout={rec['timed_out']} answer={rec['answer_ok']} png={rec['png']} "
          f"values={rec['values']} gold={rec['gold_cover']} {rec['secs']}s tools={rec['tool_calls']} steps={steps}", flush=True)
    return rec

if __name__ == "__main__":
    qids = sys.argv[1].split(",") if len(sys.argv) > 1 else list(QUESTIONS)
    out_name = sys.argv[2] if len(sys.argv) > 2 else "screen_agent_runs.json"
    jobs = [(q, r) for q in qids for r in (1, 2, 3)]
    with ThreadPoolExecutor(max_workers=3) as ex:
        recs = list(ex.map(one, jobs))
    (HERE / out_name).write_text(json.dumps(recs, indent=1))
    print("done", len(recs))
