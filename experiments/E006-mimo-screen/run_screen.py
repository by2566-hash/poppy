"""Part 1 of the mimo screen: step ① exactly as in arm A (one tool-less call), then ② execute.
6 questions x 3 repeats. Records call success, format compliance, code execution, gold agreement,
and consistency of plotted values across repeats."""
import csv, json, os, re, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from common import HERE, MODEL, PARQUET, QUESTIONS, DATA_DICTIONARY, PROMPT_A

REPEATS = 3
SANDBOX = HERE.parents[2] / "poppy-sandbox" / "E006"
# Free-tier gateway returns 403 unless both the bash and read tools are present in the request,
# so tools cannot be removed. steps=1 forces a single text-only step (verified: 0 tool calls vs 13 without).
CONFIG = {"$schema": "https://opencode.ai/config.json",
          "permission": {"external_directory": "deny"},
          "agent": {"build": {"steps": 1}}}
gold = json.loads((HERE / "gold.json").read_text())

def call_model(sb, prompt, timeout=300):
    env = dict(os.environ, XDG_DATA_HOME=str(sb / ".ocdata"))
    t0 = time.time(); code = None; timed_out = False
    with open(sb / "events.jsonl", "w") as out, open(sb / "stderr.log", "w") as err:
        try:
            code = subprocess.run(["opencode", "run", "--pure", "--format", "json", "-m", f"opencode/{MODEL}",
                                   "--dir", str(sb), "--", prompt], stdout=out, stderr=err, env=env, cwd=sb,
                                  stdin=subprocess.DEVNULL, timeout=timeout).returncode
        except subprocess.TimeoutExpired:
            timed_out = True
    text, tools, tok, errors = [], 0, {"input": 0, "output": 0}, []
    for l in (sb / "events.jsonl").read_text().splitlines():
        try: e = json.loads(l)
        except json.JSONDecodeError: continue
        p = e.get("part", {})
        if e.get("type") == "text": text.append(p.get("text", ""))
        elif e.get("type") == "tool_use": tools += 1
        elif e.get("type") == "step_finish":
            for k in tok: tok[k] += (p.get("tokens") or {}).get(k, 0)
        elif e.get("type") == "error": errors.append(str(e)[:300])
    return {"text": "\n".join(text), "exit": code, "timed_out": timed_out, "secs": round(time.time() - t0, 1),
            "tool_calls": tools, "tokens": tok, "errors": errors}

def parse(text):
    """Strict: exactly the requested format. Returns (code, answer). The answer must come after the
    code block, start with an `ANSWER:` line and contain at least 15 characters of text."""
    m = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.S)
    if not m:
        return None, None
    tail = text[m.end():]
    a = re.search(r"(?m)^\s*\**ANSWER:?\**:?\s*(.+)", tail, re.S)
    ans = a.group(1).strip() if a else None
    return m.group(1), (ans if ans and len(ans) >= 15 else None)

def numbers_in(path):
    nums = []
    for row in csv.reader(open(path, errors="ignore")):
        for c in row:
            try: nums.append(float(c.replace(",", "")))
            except ValueError: pass
    return nums

def gold_numbers(q):
    return [x for r in gold[q] for x in r if isinstance(x, float)]

def gold_cover(q, nums):
    g = gold_numbers(q)
    have = {round(n) for n in nums}
    return round(sum(round(x) in have for x in g) / len(g), 3)

def one(job):
    q, rep = job
    sb = SANDBOX / f"{q}-r{rep}"
    shutil.rmtree(sb, ignore_errors=True)
    (sb / "data").mkdir(parents=True); (sb / "out").mkdir()
    os.symlink(PARQUET, sb / "data" / "crashes.parquet")
    (sb / "opencode.json").write_text(json.dumps(CONFIG))
    prompt = PROMPT_A.format(dictionary=DATA_DICTIONARY, question=QUESTIONS[q])
    r = call_model(sb, prompt)
    code, answer = parse(r["text"])
    rec = {"q": q, "rep": rep, "call_ok": r["exit"] == 0 and not r["timed_out"] and not r["errors"] and bool(r["text"]),
           "timed_out": r["timed_out"], "secs": r["secs"], "tool_calls": r["tool_calls"], "tokens": r["tokens"],
           "errors": r["errors"], "format_ok": code is not None and answer is not None,
           "max_steps_artifact": "maximum steps" in r["text"].lower(), "has_code_block": code is not None,
           "exec_ok": False, "png": False, "values": False, "gold_cover": None, "exec_error": None}
    (sb / "response.md").write_text(r["text"])
    if code:
        (sb / "chart.py").write_text(code)
        try:
            p = subprocess.run([sys.executable, "chart.py"], cwd=sb, capture_output=True, text=True, timeout=180)
            rec["exec_ok"] = p.returncode == 0
            if p.returncode: rec["exec_error"] = p.stderr.strip().splitlines()[-1][:200] if p.stderr.strip() else "nonzero exit"
        except subprocess.TimeoutExpired:
            rec["exec_error"] = "timeout"
        rec["png"] = (sb / "out" / "initial.png").exists()
        v = sb / "out" / "values.csv"
        if v.exists():
            rec["values"] = True
            rec["plotted_numbers"] = sorted(round(n, 2) for n in numbers_in(v))
            rec["gold_cover"] = gold_cover(q, numbers_in(v))
    print(f"[{q} r{rep}] call_ok={rec['call_ok']} format={rec['format_ok']} exec={rec['exec_ok']} png={rec['png']} "
          f"gold={rec['gold_cover']} {rec['secs']}s tools={rec['tool_calls']}", flush=True)
    return rec

if __name__ == "__main__":
    jobs = [(q, r) for q in QUESTIONS for r in range(1, REPEATS + 1)]
    with ThreadPoolExecutor(max_workers=3) as ex:
        recs = list(ex.map(one, jobs))
    (HERE / "screen_runs.json").write_text(json.dumps(recs, indent=1))
    n = len(recs)
    print("calls ok", sum(r["call_ok"] for r in recs), "/", n, "| format ok", sum(r["format_ok"] for r in recs),
          "| exec ok", sum(r["exec_ok"] for r in recs), "| png", sum(r["png"] for r in recs))
