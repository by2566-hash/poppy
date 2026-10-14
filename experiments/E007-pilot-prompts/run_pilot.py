#!/usr/bin/env python3
"""Pilot runner (E007). One OpenCode run per item, in its own sandbox folder.

  python3 run_pilot.py A <A_version> [repeats]                 e.g. A v1 1
  python3 run_pilot.py C <C_version>                           e.g. C v1
  python3 run_pilot.py B <critique_version> <revise_version> <A_label>   e.g. B v2 v2 A-v1

Environment:
  POPPY_MODEL         model id (default mimo-v2.6-flash-free)
  PILOT_QIDS          comma-separated pilot question ids (default: all six)
  PILOT_CONCURRENCY   parallel runs (default 1; the free tier rate-limits)

Arms
  A, C  one analysis run: the model writes and executes its own code (config/opencode.analysis.json).
  B     reads A's output from the repo: experiments/E007-pilot-prompts/results/<A_label>/<qid>-r<rep>/.
        A's results must be collected and committed first (scripts/collect_runs.py <A_label>), so
        anyone who clones the repo runs B on the same A outputs. Then a review run on A's output (config/opencode.review.json: no code execution; the chart is
        attached, values/answer/code are embedded in the prompt), then a revise run with the analysis
        config. If the review says `ISSUES: NONE`, A's outputs are carried forward unchanged and no
        revise run is made (repair only when a problem was reported).

Sandboxes: ../../../poppy-sandbox/E007/<label>/<qid>-r<rep>/ ; collect them into the repo with
scripts/collect_runs.py. Every meta.json records model, OpenCode/Python versions, git commit,
and SHA-256 of the prompt and config files used.
"""
import hashlib, json, os, platform, re, shutil, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / "E006-mimo-screen"))
from common import DATA_DICTIONARY, PARQUET, MODEL  # noqa: E402
from run_screen import call_model  # noqa: E402

SANDBOX = ROOT.parent / "poppy-sandbox" / "E007"
RESULTS = HERE / "results"   # committed runs (scripts/collect_runs.py)
CONFIG_ANALYSIS = HERE / "config" / "opencode.analysis.json"
CONFIG_REVIEW = HERE / "config" / "opencode.review.json"
STEPS = json.loads(CONFIG_ANALYSIS.read_text())["agent"]["build"]["steps"]
TIMEOUT = 600
CONCURRENCY = int(os.environ.get("PILOT_CONCURRENCY", "1"))
SUFFIX = "" if MODEL == "mimo-v2.6-flash-free" else f"-{MODEL}"   # keep other models' runs separate
QS = {q["id"]: q for q in json.loads((HERE / "pilot_questions.json").read_text())["questions"]}
MAX_EMBED = 6000  # characters of values / code embedded in a prompt


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def environment(prompt_files):
    def run(cmd):
        try:
            return subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout.strip()
        except Exception:  # noqa: BLE001
            return "?"
    return {"model": MODEL, "opencode": run(["opencode", "--version"]), "python": platform.python_version(),
            "git_commit": run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"]),
            "prompt_sha": {Path(p).name: sha(p) for p in prompt_files},
            "config_sha": {CONFIG_ANALYSIS.name: sha(CONFIG_ANALYSIS), CONFIG_REVIEW.name: sha(CONFIG_REVIEW)}}


def prep(sb, config):
    shutil.rmtree(sb, ignore_errors=True)
    (sb / "data").mkdir(parents=True)
    (sb / "out").mkdir()
    os.symlink(PARQUET, sb / "data" / "crashes.parquet")
    shutil.copy(config, sb / "opencode.json")


def answer_of(text):
    """The text after the last ANSWER:, unless the reply is a step-cap narration (not an answer)."""
    if "maximum steps" in text.lower():
        return None
    pos = text.rfind("ANSWER:")
    ans = text[pos + 7:].strip() if pos >= 0 else None
    return ans if ans and len(ans) >= 15 else None


def steps_in(path):
    return sum('"type":"step_start"' in l for l in Path(path).read_text().splitlines()) if Path(path).exists() else 0


def clip(s, n=MAX_EMBED):
    return s if len(s) <= n else s[:n] + f"\n... [truncated, {len(s) - n} more characters]"


def code_of(run_dir):
    """Python the model wrote: .py files in its folder, else python commands from its tool calls."""
    files = sorted(run_dir.glob("*.py")) + sorted((run_dir / "out").glob("*.py"))
    if files:
        return "\n\n".join(f"# file: {p.name}\n{p.read_text()}" for p in files)
    cmds = []
    ev = run_dir / "events.jsonl"
    for line in (ev.read_text().splitlines() if ev.exists() else []):
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("type") == "tool_use":
            inp = e.get("part", {}).get("state", {}).get("input", {}) or {}
            c = inp.get("command") or inp.get("content") or ""
            if "python" in c or "import " in c:
                cmds.append(c)
    return "\n\n".join(cmds) or "(no code was saved)"


def run_analysis(job):
    label, q, rep, prompt_file = job
    sb = SANDBOX / label / f"{q}-r{rep}"
    prep(sb, CONFIG_ANALYSIS)
    prompt = Path(prompt_file).read_text().format(dictionary=DATA_DICTIONARY, question=QS[q]["text"])
    r = call_model(sb, prompt, timeout=TIMEOUT)
    steps = steps_in(sb / "events.jsonl")
    ans = answer_of(r["text"])
    meta = {"q": q, "rep": rep, "label": label, "type": QS[q]["type"],
            "call_ok": r["exit"] == 0 and not r["timed_out"] and not r["errors"], "timed_out": r["timed_out"],
            "rate_limited": r["rate_limited"], "attempts": r["attempts"], "secs": r["secs"],
            "steps": steps, "hit_step_limit": steps >= STEPS, "tool_calls": r["tool_calls"], "tokens": r["tokens"],
            "png": (sb / "out" / "initial.png").exists(), "values": (sb / "out" / "values.csv").exists(),
            "answer": ans, "answer_ok": ans is not None, "errors": r["errors"],
            "env": environment([prompt_file])}
    meta["complete"] = meta["call_ok"] and meta["png"] and meta["values"] and meta["answer_ok"]
    (sb / "response.md").write_text(r["text"])
    (sb / "meta.json").write_text(json.dumps(meta, indent=1))
    print(f"[{label} {q} r{rep}] complete={meta['complete']} rate_limited={meta['rate_limited']} "
          f"{meta['secs']}s steps={steps} tools={meta['tool_calls']}", flush=True)
    return meta


def run_B(job):
    label, q, rep, a_label, crit_file, rev_file = job
    src = RESULTS / a_label / f"{q}-r{rep}"   # A's committed result in the repo, not the local sandbox
    if not (src / "meta.json").exists():
        raise SystemExit(f"A result not found in the repo: {src.relative_to(ROOT)}\n"
                         f"Collect A's results first: python3 scripts/collect_runs.py {a_label}")
    a_meta = json.loads((src / "meta.json").read_text())
    sb = SANDBOX / label / f"{q}-r{rep}"
    shutil.rmtree(sb, ignore_errors=True)
    shutil.copytree(src, sb, ignore=shutil.ignore_patterns("events*.jsonl", "response.md", "meta.json", "critique.md"))
    (sb / "data").mkdir(exist_ok=True)
    (sb / "out").mkdir(exist_ok=True)
    os.symlink(PARQUET, sb / "data" / "crashes.parquet")   # results in the repo carry no data link
    shutil.copy(CONFIG_ANALYSIS, sb / "opencode.json")
    question = QS[q]["text"]
    values_path = sb / "out" / "values.csv"
    values = clip(values_path.read_text()) if values_path.exists() else "(no values file was produced)"
    a_text = (src / "response.md").read_text() if (src / "response.md").exists() else ""
    a_answer = answer_of(a_text) if a_text else a_meta.get("answer")   # re-judge with current rules
    a_complete = bool(a_answer) and (src / "out" / "initial.png").exists() and values_path.exists()
    answer = a_answer or "(no written answer was produced)"
    code = clip(code_of(src))
    chart = sb / "out" / "initial.png"

    # Run 2: review only (no execution). Chart attached; everything else embedded.
    rd = sb / "review"
    rd.mkdir()
    shutil.copy(CONFIG_REVIEW, rd / "opencode.json")
    files = []
    if chart.exists():
        shutil.copy(chart, rd / "chart.png")
        files = [rd / "chart.png"]
    chart_note = "attached as an image" if files else "no chart was produced"
    crit_prompt = Path(crit_file).read_text().format(question=question, chart_note=chart_note,
                                                      values=values, answer=answer, code=code)
    r2 = call_model(rd, crit_prompt, timeout=TIMEOUT, files=files)
    critique = r2["text"].strip()
    (sb / "critique.md").write_text(critique)
    body = critique.split("ISSUES:", 1)[1] if "ISSUES:" in critique else critique
    issues = re.findall(r"(?m)^\s*(\d+)[.)]\s+(.+)", body)
    says_none = bool(re.search(r"ISSUES:\s*NONE", critique, re.I)) and not issues
    review = {"review_ok": r2["exit"] == 0 and not r2["timed_out"] and not r2["errors"] and (bool(issues) or says_none),
              "review_rate_limited": r2["rate_limited"], "review_secs": r2["secs"],
              "review_steps": steps_in(rd / "events.jsonl"), "review_tool_calls": r2["tool_calls"],
              "n_issues": len(issues), "says_none": says_none}

    # Run 3: revise, only if problems were reported.
    if says_none:
        if chart.exists():
            shutil.copy(chart, sb / "out" / "revised.png")
        if values_path.exists():
            shutil.copy(values_path, sb / "out" / "revised_values.csv")
        r3_text, rev = "", {"revise_skipped": True, "revise_secs": 0, "revise_steps": 0, "revise_tool_calls": 0,
                            "revise_rate_limited": False}
        final_answer = a_answer
    else:
        rev_prompt = Path(rev_file).read_text().format(question=question, code=code, values=values,
                                                       answer=answer, critique=critique)
        r3 = call_model(sb, rev_prompt, timeout=TIMEOUT)
        r3_text = r3["text"]
        rev = {"revise_skipped": False, "revise_ok": r3["exit"] == 0 and not r3["timed_out"] and not r3["errors"],
               "revise_rate_limited": r3["rate_limited"], "revise_secs": r3["secs"],
               "revise_steps": steps_in(sb / "events.jsonl"), "revise_tool_calls": r3["tool_calls"],
               "changes_listed": "CHANGES:" in r3_text}
        final_answer = answer_of(r3_text)
    (sb / "response.md").write_text(r3_text)
    meta = {"q": q, "rep": rep, "label": label, "a_label": a_label, "type": QS[q]["type"],
            "a_source": str(src.relative_to(ROOT)),
            "a_git_commit": (a_meta.get("env") or {}).get("git_commit"),   # None for runs made before env logging
            "a_complete": a_complete, **review, **rev,
            "revised_png": (sb / "out" / "revised.png").exists(),
            "revised_values": (sb / "out" / "revised_values.csv").exists(),
            "answer": final_answer, "answer_ok": final_answer is not None,
            "env": environment([crit_file, rev_file])}
    (sb / "meta.json").write_text(json.dumps(meta, indent=1))
    print(f"[{label} {q} r{rep}] review_ok={meta['review_ok']} issues={meta['n_issues']} none={says_none} "
          f"review_tools={meta['review_tool_calls']} revised_png={meta['revised_png']} answer={meta['answer_ok']}", flush=True)
    return meta


if __name__ == "__main__":
    mode = sys.argv[1]
    qids = [q for q in os.environ.get("PILOT_QIDS", "").split(",") if q] or list(QS)
    with ThreadPoolExecutor(CONCURRENCY) as ex:
        if mode in ("A", "C"):
            ver, reps = sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1
            pf = HERE / "prompts" / (f"A.{ver}.md" if mode == "A" else f"C_selfcheck.{ver}.md")
            label = f"{mode}-{ver}{SUFFIX}"
            res = list(ex.map(run_analysis, [(label, q, r, pf) for q in qids for r in range(1, reps + 1)]))
        elif mode == "B":
            cv, rv, a_label = sys.argv[2], sys.argv[3], sys.argv[4]
            cf, rf = HERE / "prompts" / f"B_critique.{cv}.md", HERE / "prompts" / f"B_revise.{rv}.md"
            label = f"B-{cv}-{rv}{SUFFIX}"
            res = list(ex.map(run_B, [(label, q, 1, a_label, cf, rf) for q in qids]))
        else:
            sys.exit("mode must be A, B or C")
    out = HERE / "runs"
    out.mkdir(exist_ok=True)
    (out / f"{label}.json").write_text(json.dumps(res, indent=1))
    print("saved", label)
