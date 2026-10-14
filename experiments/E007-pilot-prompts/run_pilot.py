"""Pilot runner (E007). Arms: A (prompt A.vN), C (C_selfcheck.vN), B (critique + revise on A's output).
Same sandbox/config as E006 agent runs. Usage:
  python3 run_pilot.py A  <A_prompt_version> <repeats>
  python3 run_pilot.py C  <C_prompt_version>
  python3 run_pilot.py B  <B_critique_version> <B_revise_version> <A_run_label>
Outputs go to runs/<label>/<question>/ with meta.json, events, response.md, out/."""
import json, os, shutil, subprocess, sys, time, re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "E006-mimo-screen"))
from common import DATA_DICTIONARY, PARQUET, MODEL  # noqa
from run_screen import call_model  # noqa

SANDBOX = HERE.parents[2] / "poppy-sandbox" / "E007"
STEPS = 15  # formal config chosen from E006 (clear Qs needed <= 11 tool calls; ambiguous Qs use the budget)
CONFIG = {"$schema": "https://opencode.ai/config.json",
          "permission": {"external_directory": "deny", "webfetch": "deny", "edit": "allow",
                         "bash": {"*": "deny", "python3 *": "allow", "python *": "allow", "ls": "allow",
                                  "ls *": "allow", "mkdir *": "allow", "head *": "allow", "cat *": "allow"}},
          "agent": {"build": {"steps": STEPS}}}
QS = {q["id"]: q for q in json.loads((HERE / "pilot_questions.json").read_text())["questions"]}

def prep(sb):
    shutil.rmtree(sb, ignore_errors=True)
    (sb / "data").mkdir(parents=True); (sb / "out").mkdir()
    os.symlink(PARQUET, sb / "data" / "crashes.parquet")
    (sb / "opencode.json").write_text(json.dumps(CONFIG))

def summarize(sb, r, extra):
    steps = sum('"type":"step_start"' in l for l in (sb / "events.jsonl").read_text().splitlines())
    t = r["text"]; pos = t.rfind("ANSWER:"); ans = t[pos + 7:].strip() if pos >= 0 else None
    meta = {"call_ok": r["exit"] == 0 and not r["timed_out"] and not r["errors"], "timed_out": r["timed_out"],
            "secs": r["secs"], "tool_calls": r["tool_calls"], "steps": steps, "hit_step_limit": steps >= STEPS,
            "errors": r["errors"], "answer": ans, "answer_ok": bool(ans and len(ans) >= 15),
            "tokens": r["tokens"], **extra}
    return meta

def final_code(sb):
    """Collect the python the model wrote in the sandbox (files it created), concatenated."""
    parts = []
    for p in sorted(sb.glob("*.py")) + sorted((sb / "out").glob("*.py")):
        parts.append(f"# file: {p.name}\n{p.read_text()}")
    return "\n\n".join(parts) if parts else "(no python file was saved)"

def run_A_or_C(job):
    label, q, rep, tmpl = job
    sb = SANDBOX / label / f"{q}-r{rep}"; prep(sb)
    prompt = tmpl.format(dictionary=DATA_DICTIONARY, question=QS[q]["text"])
    r = call_model(sb, prompt, timeout=600)
    meta = summarize(sb, r, {"q": q, "rep": rep, "label": label,
                             "png": (sb / "out" / "initial.png").exists(), "values": (sb / "out" / "values.csv").exists()})
    (sb / "response.md").write_text(r["text"]); (sb / "meta.json").write_text(json.dumps(meta, indent=1))
    print(f"[{label} {q} r{rep}] ok={meta['call_ok']} ans={meta['answer_ok']} png={meta['png']} {meta['secs']}s tools={meta['tool_calls']} steps={meta['steps']}", flush=True)
    return meta

def run_B(job):
    label, q, rep, a_label, crit_t, rev_t = job
    src = SANDBOX / a_label / f"{q}-r{rep}"
    sb = SANDBOX / label / f"{q}-r{rep}"
    shutil.rmtree(sb, ignore_errors=True); shutil.copytree(src, sb, symlinks=True, ignore=shutil.ignore_patterns(".ocdata", "events.jsonl", "stderr.log", "response.md", "meta.json"))
    (sb / "opencode.json").write_text(json.dumps(CONFIG))
    a_meta = json.loads((src / "meta.json").read_text())
    code, answer = final_code(sb), a_meta.get("answer") or "(none)"
    # call 2: critique (sees chart file, values file, code, answer)
    sbc = sb / "critique"; sbc.mkdir(exist_ok=True)
    r2 = call_model(sb, crit_t.format(question=QS[q]["text"], code=code, answer=answer), timeout=600)
    critique = r2["text"].strip()
    (sb / "critique.md").write_text(critique)
    # call 3: revise (sees code + critique), may execute
    shutil.copy(sb / "events.jsonl", sb / "events_critique.jsonl")
    r3 = call_model(sb, rev_t.format(question=QS[q]["text"], code=code, critique=critique), timeout=600)
    meta = summarize(sb, r3, {"q": q, "rep": rep, "label": label, "a_label": a_label,
                              "png_revised": (sb / "out" / "revised.png").exists(),
                              "values_revised": (sb / "out" / "revised_values.csv").exists(),
                              "critique_ok": r2["exit"] == 0 and not r2["timed_out"] and len(critique) > 20,
                              "critique_secs": r2["secs"], "critique_tool_calls": r2["tool_calls"], "critique_chars": len(critique)})
    (sb / "response.md").write_text(r3["text"]); (sb / "meta.json").write_text(json.dumps(meta, indent=1))
    print(f"[{label} {q} r{rep}] critique_ok={meta['critique_ok']} revised_png={meta['png_revised']} ans={meta['answer_ok']} {meta['secs']}s", flush=True)
    return meta

if __name__ == "__main__":
    mode = sys.argv[1]; qids = list(QS)
    with ThreadPoolExecutor(3) as ex:
        if mode in ("A", "C"):
            ver, reps = sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1
            f = HERE / "prompts" / (f"A.{ver}.md" if mode == "A" else f"C_selfcheck.{ver}.md")
            label = f"{mode}-{ver}"; tmpl = f.read_text()
            res = list(ex.map(run_A_or_C, [(label, q, r, tmpl) for q in qids for r in range(1, reps + 1)]))
        else:
            cv, rv, a_label = sys.argv[2], sys.argv[3], sys.argv[4]
            crit = (HERE / "prompts" / f"B_critique.{cv}.md").read_text(); rev = (HERE / "prompts" / f"B_revise.{rv}.md").read_text()
            label = f"B-{cv}-{rv}"
            res = list(ex.map(run_B, [(label, q, 1, a_label, crit, rev) for q in qids]))
    out = HERE / "runs"; out.mkdir(exist_ok=True)
    (out / f"{label}.json").write_text(json.dumps(res, indent=1)); print("saved", label)
