#!/usr/bin/env python3
"""Pilot runner (E007). One OpenCode run per item, in its own sandbox folder.

  python3 run_pilot.py A <A_version> [repeats]                 e.g. A v1 1
  python3 run_pilot.py C <C_version>                           e.g. C v1
  python3 run_pilot.py B <critique_version> <revise_version> <A_label>   e.g. B v2 v2 A-v1
  python3 run_pilot.py D <D_version> [repeats]                 e.g. D v1 1   (PILOT_K=3 framings per run)

Environment:
  POPPY_MODEL         model id (default mimo-v2.6-flash-free; "openai/gpt-6-luna" needs OPENAI_API_KEY in poppy/.env)
  POPPY_EXP           experiment folder for sandbox + results (default E007-pilot-prompts; e.g. E008-model-contrast)
  POPPY_QSET          pilot (6 pilot questions, default) or formal (P1-P10)
  PILOT_K             arm D: framings per run (default 3)
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
        If A produced no `ANSWER:` (step cap, timeout, format), B is not run: the item fails in both
        arms and meta.json records `b_skipped` (PROTOCOL amendment 2026-10-15).

The model's `python` runs this interpreter under macOS sandbox-exec with no network
(run_screen.sandbox_shims): no network, no reading the repo or other runs, writing only in its own folder.
`websearch` and `webfetch` are denied in both configs. The review runs in its own folder tree
(_review/...) so it cannot inherit the analysis config. Every B item ends in one of B_STATES.

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
from common import DATA_DICTIONARY, PARQUET, MODEL, MODEL_TAG, QUESTIONS, QUESTION_TYPES  # noqa: E402
from run_screen import call_model  # noqa: E402

# Which experiment folder the runs belong to (sandbox + committed results), and which question set.
#   POPPY_EXP=E007-pilot-prompts (default)  POPPY_QSET=pilot (default: the 6 pilot questions)
#   POPPY_EXP=E008-model-contrast POPPY_QSET=formal  -> P1-P10 from E006/common.py, results under experiments/E008-model-contrast/results
EXP = os.environ.get("POPPY_EXP", HERE.name)
QSET = os.environ.get("POPPY_QSET", "pilot")
SANDBOX = ROOT.parent / "poppy-sandbox" / EXP.split("-")[0]
RESULTS = ROOT / "experiments" / EXP / "results"   # committed runs (scripts/collect_runs.py)
CONFIG_ANALYSIS = HERE / "config" / "opencode.analysis.json"
CONFIG_REVIEW = HERE / "config" / "opencode.review.json"
CONFIG_ENUMERATE = HERE / "config" / "opencode.enumerate.json"   # arm D: k charts in one run, larger step cap
STEPS = json.loads(CONFIG_ANALYSIS.read_text())["agent"]["build"]["steps"]
TIMEOUT = 600
REVIEW_TIMEOUT = 420   # every finished review took < 400 s; the review has no code to run
CONCURRENCY = int(os.environ.get("PILOT_CONCURRENCY", "1"))
SUFFIX = "" if MODEL == "mimo-v2.6-flash-free" else f"-{MODEL_TAG}"   # keep other models' runs separate
if QSET == "formal":
    QS = {k: {"id": k, "type": QUESTION_TYPES[k], "text": v} for k, v in QUESTIONS.items()}
else:
    QS = {q["id"]: q for q in json.loads((HERE / "pilot_questions.json").read_text())["questions"]}
MAX_EMBED = 6000  # characters of values / code embedded in a prompt
ATTACH_CHART = os.environ.get("PILOT_NO_IMAGE") != "1"   # control run only


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


def link_data(sb):
    """Own copy of the data file (APFS clone: no extra disk). A symlink would point into the repo, which the
    sandbox does not let the model read."""
    dst = sb / "data" / "crashes.parquet"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if subprocess.run(["cp", "-c", str(PARQUET), str(dst)], capture_output=True).returncode != 0:
        shutil.copy(PARQUET, dst)


def prep(sb, config):
    shutil.rmtree(sb, ignore_errors=True)
    (sb / "out").mkdir(parents=True)
    link_data(sb)
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


NET = re.compile(r"urlopen|urllib|requests\.(get|post)|http\.client|socket\.|curl |wget ")


def net_calls(path):
    """Completed tool calls that tried to reach the internet (audit; the sandbox should block them all)."""
    n = 0
    for line in (Path(path).read_text().splitlines() if Path(path).exists() else []):
        try:
            p = json.loads(line).get("part", {})
        except json.JSONDecodeError:
            continue
        st = p.get("state", {}) if p.get("type") == "tool" else {}
        if st.get("status") == "completed" and (p.get("tool") in ("websearch", "webfetch")
                                                or NET.search(json.dumps(st.get("input", {})))):
            n += 1
    return n


CHANGE_STATUS = ("fixed", "kept", "cannot address")
SECTION = re.compile(r"(?im)^\W*(CHART CHECK|ISSUES|UNVERIFIED)\W*:")
WRITE_TOOLS = ("edit", "write", "patch", "task", "webfetch", "websearch")


def parse_review(text):
    """Review reply -> sections. v2 replies (ISSUES only) parse too. `parsed` = an ISSUES section exists and it is
    either NONE or a numbered list; numbered lines under UNVERIFIED are never counted as issues."""
    parts, marks = {}, list(SECTION.finditer(text))
    for i, m in enumerate(marks):
        body = text[m.end(): marks[i + 1].start() if i + 1 < len(marks) else len(text)]
        parts.setdefault(m.group(1).upper(), re.sub(r"^[\s*_`]+", "", body).strip())
    body = parts.get("ISSUES")
    issues = [(int(n), t.strip()) for n, t in re.findall(r"(?m)^\s*(\d+)[.)]\s+(.+)", body or "")]
    none = body is not None and bool(re.match(r"\W*NONE\b", body, re.I)) and not issues
    unverified = [l.strip(" -*") for l in (parts.get("UNVERIFIED") or "").splitlines()
                  if l.strip(" -*") and l.strip(" -*").lower() not in ("none", "none.")]
    return {"parsed": body is not None and (none or bool(issues)), "issues": issues, "none": none,
            "chart_check": parts.get("CHART CHECK"), "unverified": unverified}


def parse_changes(text):
    """CHANGES block -> {issue number: status}; status is one of CHANGE_STATUS or 'other'."""
    block = text.split("CHANGES:", 1)[1].split("ANSWER:", 1)[0] if "CHANGES:" in text else ""
    out = {}
    for n, rest in re.findall(r"(?m)^\s*(\d+)[.)]\s+(.+)", block):
        word = rest.strip(" *`<").lower()
        out[int(n)] = next((st for st in CHANGE_STATUS if word.startswith(st)), "other")
    return out


def side_effects(path):
    """Tool calls in the review run that could change files, execute or fetch (should be none)."""
    hits = []
    for line in (Path(path).read_text().splitlines() if Path(path).exists() else []):
        try:
            p = json.loads(line).get("part", {})
        except json.JSONDecodeError:
            continue
        if p.get("type") != "tool" or p.get("state", {}).get("status") != "completed":
            continue
        cmd = (p["state"].get("input") or {}).get("command", "")
        if p.get("tool") in WRITE_TOOLS or (p.get("tool") == "bash" and cmd.strip() != "true"):
            hits.append(p.get("tool"))
    return hits


def changed_columns(before, after):
    """Columns of values.csv whose values differ after revision (audit for "nothing unflagged changed")."""
    if not (Path(before).exists() and Path(after).exists()):
        return None
    import csv
    a, b = list(csv.DictReader(open(before))), list(csv.DictReader(open(after)))
    cols = set(a[0] if a else {}) | set(b[0] if b else {})
    if len(a) != len(b):
        return sorted(cols) + ["<row count>"]
    return sorted(c for c in cols if any(r.get(c) != t.get(c) for r, t in zip(a, b)))


B_STATES = {   # every B item ends in exactly one of these
    "skipped_no_A_answer": "A has no answer: B not run; both arms fail the item",
    "review_infra_failure": "review call failed before a step, or its stream stalled twice (rate limit, crash, stall): not scored",
    "review_failure": "review ran but gave no parseable ISSUES block: B fails the item, no revise",
    "none_carried_forward": "review said NONE: A's outputs are B's outputs",
    "revise_infra_failure": "revise call failed before a step, or its stream stalled twice: not scored",
    "revise_incomplete": "revise ran but no ANSWER or no revised files (step cap, timeout): B fails the item",
    "revised": "review listed issues and revise finished",
}


def b_state(m, r2, review_steps):
    if not m.get("review_ok"):
        infra = (review_steps == 0 and not r2["text"].strip()) or r2.get("stalled")
        return "review_infra_failure" if infra else "review_failure"
    if m.get("says_none"):
        return "none_carried_forward"
    if (m.get("revise_rate_limited") and not m.get("revise_steps")) or m.get("revise_stalled"):
        return "revise_infra_failure"
    done = m.get("answer_ok") and m.get("revised_png") and m.get("revised_values")
    return "revised" if done else "revise_incomplete"


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
            "rate_limited": r["rate_limited"], "stalled": r["stalled"], "attempts": r["attempts"], "secs": r["secs"],
            "zero_output_retries": r["zero_output_retries"], "secs_total": r["secs_total"],
            "steps": steps, "hit_step_limit": steps >= STEPS, "tool_calls": r["tool_calls"], "tokens": r["tokens"],
            "net_calls": net_calls(sb / "events.jsonl"),
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
    link_data(sb)   # results in the repo carry no data file
    shutil.copy(CONFIG_ANALYSIS, sb / "opencode.json")
    question = QS[q]["text"]
    values_path = sb / "out" / "values.csv"
    values = clip(values_path.read_text()) if values_path.exists() else "(no values file was produced)"
    a_text = (src / "response.md").read_text() if (src / "response.md").exists() else ""
    a_answer = answer_of(a_text) if a_text else a_meta.get("answer")   # re-judge with current rules
    a_complete = bool(a_answer) and (src / "out" / "initial.png").exists() and values_path.exists()
    chart = sb / "out" / "initial.png"
    if not a_answer:
        # Rule (PROTOCOL amendment 2026-10-15): B needs a "before". With no answer from A there is nothing to
        # review, and a revise run would just be a second analysis with 15 more steps. Both arms fail the item.
        meta = {"q": q, "rep": rep, "label": label, "a_label": a_label, "type": QS[q]["type"],
                "a_source": str(src.relative_to(ROOT)), "a_git_commit": (a_meta.get("env") or {}).get("git_commit"),
                "a_complete": False, "b_skipped": "A produced no answer (step cap, timeout or format); B not applicable",
                "b_state": "skipped_no_A_answer",
                "review_ok": False, "n_issues": 0, "says_none": False, "revise_skipped": True,
                "revised_png": False, "revised_values": False, "answer": None, "answer_ok": False,
                "env": environment([crit_file, rev_file])}
        (sb / "meta.json").write_text(json.dumps(meta, indent=1))
        print(f"[{label} {q} r{rep}] skipped: A has no answer", flush=True)
        return meta
    answer = a_answer
    code = clip(code_of(src))

    # Run 2: review only. Read-only by config (no edits, no execution, no network); its output is text.
    # OpenCode also loads opencode.json from parent folders, so a review folder inside A's sandbox would inherit
    # the analysis config (python allowed). The review runs in its own tree and is copied into sb/review afterwards.
    rd = SANDBOX / "_review" / label / f"{q}-r{rep}"
    shutil.rmtree(rd, ignore_errors=True)
    rd.mkdir(parents=True)
    shutil.copy(CONFIG_REVIEW, rd / "opencode.json")
    inherited = [str(d) for d in rd.parents for n in ("opencode.json", "opencode.jsonc", ".opencode") if (d / n).exists()]
    if inherited:
        raise SystemExit(f"review folder would inherit OpenCode config from: {inherited}")
    files = []
    if chart.exists() and ATTACH_CHART:   # PILOT_NO_IMAGE=1: same prompt, image withheld and not on disk (control)
        shutil.copy(chart, rd / "chart.png")
        files = [rd / "chart.png"]
    chart_note = "attached as an image" if chart.exists() else "no chart was produced"
    crit_prompt = Path(crit_file).read_text().format(question=question, dictionary=DATA_DICTIONARY, chart_note=chart_note,
                                                      values=values, answer=answer, code=code)
    # Typed record of exactly what the reviewer received, so the review can be evaluated on its own.
    # Review records are written next to the review run (outside the revise sandbox) and copied into the item
    # folder after revise: the reviser must only see the ISSUES list, not critique.md / UNVERIFIED (E007 iteration 2:
    # K2's reviser read critique.md from its folder).
    (rd / "review_prompt.md").write_text(crit_prompt)
    (rd / "review_input.json").write_text(json.dumps({
        "item": f"{q}-r{rep}", "a_source": str(src.relative_to(ROOT)), "question": question,
        "chart": {"attached": bool(files), "sha": sha(chart) if chart.exists() else None},
        "values_sha": sha(values_path) if values_path.exists() else None, "answer": answer,
        "code_sha": hashlib.sha256(code.encode()).hexdigest()[:16],
        "dictionary_sha": hashlib.sha256(DATA_DICTIONARY.encode()).hexdigest()[:16],
        "prompt_file": Path(crit_file).name, "prompt_sha": sha(crit_file),
        "rendered_prompt_sha": hashlib.sha256(crit_prompt.encode()).hexdigest()[:16]}, indent=1))
    r2 = call_model(rd, crit_prompt, timeout=REVIEW_TIMEOUT, files=files)
    critique = r2["text"].strip()
    (rd / "critique.md").write_text(critique)
    parsed = parse_review(critique)
    (rd / "review.json").write_text(json.dumps({
        "verdict": "none" if parsed["none"] else "issues" if parsed["issues"] else "unparseable",
        "chart_check": parsed["chart_check"],
        "issues": [{"n": n, "text": t} for n, t in parsed["issues"]],   # routed to revise
        "unverified": parsed["unverified"]}, indent=1))                 # recorded only
    call_ok = r2["exit"] == 0 and not r2["timed_out"] and not r2["errors"]
    review = {"review_ok": call_ok and parsed["parsed"], "review_call_ok": call_ok, "review_parsed": parsed["parsed"],
              "review_rate_limited": r2["rate_limited"], "review_stalled": r2["stalled"], "review_attempts": r2["attempts"],
              "review_zero_output_retries": r2["zero_output_retries"], "review_secs_total": r2["secs_total"],
              "review_secs": r2["secs"], "review_tokens": r2["tokens"],
              "review_steps": steps_in(rd / "events.jsonl"), "review_tool_calls": r2["tool_calls"],
              "review_side_effects": side_effects(rd / "events.jsonl"), "review_dir": str(rd), "chart_attached": bool(files),
              "n_issues": len(parsed["issues"]), "says_none": parsed["none"],
              "chart_check": parsed["chart_check"], "n_unverified": len(parsed["unverified"])}

    # Run 3: revise, only if the review is usable and listed issues. Only the ISSUES list is passed on:
    # CHART CHECK and UNVERIFIED are records for us, not instructions for the reviser.
    if not review["review_ok"]:
        # Unusable review (format failure, or a call failure left after retries): no revise; B fails the item.
        r3_text, final_answer = "", None
        rev = {"revise_skipped": True, "b_failure": "review call failed" if not call_ok else "review format failure"}
    elif parsed["none"]:
        if chart.exists():
            shutil.copy(chart, sb / "out" / "revised.png")
        if values_path.exists():
            shutil.copy(values_path, sb / "out" / "revised_values.csv")
        r3_text, rev = "", {"revise_skipped": True, "revise_secs": 0, "revise_steps": 0, "revise_tool_calls": 0,
                            "revise_rate_limited": False}
        final_answer = a_answer
    else:
        issues_text = "\n".join(f"{n}. {t}" for n, t in parsed["issues"])
        rev_prompt = Path(rev_file).read_text().format(question=question, dictionary=DATA_DICTIONARY, code=code,
                                                       values=values, answer=answer, critique=issues_text)
        (rd / "revise_prompt.md").write_text(rev_prompt)
        r3 = call_model(sb, rev_prompt, timeout=TIMEOUT,
                        protect=[sb / "out" / "initial.png", sb / "out" / "values.csv"])   # A's "before" stays intact
        r3_text = r3["text"]
        changes = parse_changes(r3_text)
        (sb / "changes.json").write_text(json.dumps({"issues_sent": [n for n, _ in parsed["issues"]],
                                                     "changes": changes}, indent=1))
        rev = {"revise_skipped": False, "revise_ok": r3["exit"] == 0 and not r3["timed_out"] and not r3["errors"],
               "revise_rate_limited": r3["rate_limited"], "revise_stalled": r3["stalled"], "revise_attempts": r3["attempts"],
               "revise_zero_output_retries": r3["zero_output_retries"], "revise_secs_total": r3["secs_total"],
               "revise_secs": r3["secs"], "revise_tokens": r3["tokens"],
               "revise_steps": steps_in(sb / "events.jsonl"), "revise_tool_calls": r3["tool_calls"],
               "revise_net_calls": net_calls(sb / "events.jsonl"),
               "changes_listed": "CHANGES:" in r3_text, "changes": changes,
               "changes_match_issues": sorted(changes) == sorted(n for n, _ in parsed["issues"]) and
                                       all(v in CHANGE_STATUS for v in changes.values())}
        final_answer = answer_of(r3_text)
    (sb / "response.md").write_text(r3_text)
    for name in ("critique.md", "review_prompt.md", "review_input.json", "review.json", "revise_prompt.md"):
        if (rd / name).exists():
            shutil.copy(rd / name, sb / name)
    shutil.copytree(rd, sb / "review", ignore=shutil.ignore_patterns(".ocdata", ".bin", "critique.md", "review_*", "revise_prompt.md"), dirs_exist_ok=True)
    meta = {"q": q, "rep": rep, "label": label, "a_label": a_label, "type": QS[q]["type"],
            "a_source": str(src.relative_to(ROOT)),
            "a_git_commit": (a_meta.get("env") or {}).get("git_commit"),   # None for runs made before env logging
            "a_complete": a_complete, **review, **rev,
            "revised_png": (sb / "out" / "revised.png").exists(),
            "revised_values": (sb / "out" / "revised_values.csv").exists(),
            "values_changed_cols": changed_columns(src / "out" / "values.csv", sb / "out" / "revised_values.csv"),
            "a_outputs_intact": all(not (src / "out" / n).exists() or sha(src / "out" / n) == sha(sb / "out" / n)
                                    for n in ("initial.png", "values.csv")),
            "answer": final_answer, "answer_ok": final_answer is not None,
            "env": environment([crit_file, rev_file])}
    meta["b_state"] = b_state(meta, r2, steps_in(rd / "events.jsonl"))
    (sb / "meta.json").write_text(json.dumps(meta, indent=1))
    print(f"[{label} {q} r{rep}] {meta['b_state']} review_ok={meta['review_ok']} issues={meta['n_issues']} none={meta['says_none']} "
          f"chart_check={bool(meta['chart_check'])} revised_png={meta['revised_png']} answer={meta['answer_ok']}", flush=True)
    return meta


OPTION_FIELDS = ("id", "metric", "denominator", "grouping", "chart_type", "reason", "probability", "answer")


def parse_options(sb):
    """out/options.json -> list of options with the files they point to. Distinctness is judged on the
    framing fields only (metric, denominator, grouping, chart_type), never on wording."""
    f = sb / "out" / "options.json"
    if not f.exists():
        return {"parsed": False, "options": [], "reason": "no options.json"}
    try:
        raw = json.loads(f.read_text())
    except json.JSONDecodeError as e:
        return {"parsed": False, "options": [], "reason": f"invalid JSON: {e}"}
    opts = raw.get("options") if isinstance(raw, dict) else raw
    if not isinstance(opts, list) or not opts:
        return {"parsed": False, "options": [], "reason": "no options list"}
    out, framings = [], set()
    for i, o in enumerate(opts, 1):
        o = o if isinstance(o, dict) else {}
        oid = o.get("id", i)
        framing = tuple(str(o.get(k, "")).strip().lower() for k in ("metric", "denominator", "grouping", "chart_type"))
        out.append({**{k: o.get(k) for k in OPTION_FIELDS}, "id": oid,
                    "png": (sb / "out" / f"option_{oid}.png").exists(),
                    "values": (sb / "out" / f"values_{oid}.csv").exists(),
                    "fields_ok": all(o.get(k) not in (None, "") for k in OPTION_FIELDS if k != "id"),
                    "duplicate_framing": framing in framings})
        framings.add(framing)
    rec = raw.get("recommended") if isinstance(raw, dict) else None
    return {"parsed": True, "options": out, "recommended": rec, "n_distinct": len(framings),
            "reason": None}


def run_enumerate(job):
    """Arm D: one run, k framings of the same question, each with its own chart and values (E009, simplified)."""
    label, q, rep, prompt_file, k = job
    sb = SANDBOX / label / f"{q}-r{rep}"
    prep(sb, CONFIG_ENUMERATE)
    prompt = Path(prompt_file).read_text().format(dictionary=DATA_DICTIONARY, question=QS[q]["text"], k=k)
    (sb / "prompt.md").write_text(prompt)
    r = call_model(sb, prompt, timeout=TIMEOUT)
    steps = steps_in(sb / "events.jsonl")
    ans = answer_of(r["text"])
    po = parse_options(sb)
    opts = po["options"]
    meta = {"q": q, "rep": rep, "label": label, "type": QS[q]["type"], "k": k,
            "call_ok": r["exit"] == 0 and not r["timed_out"] and not r["errors"], "timed_out": r["timed_out"],
            "rate_limited": r["rate_limited"], "stalled": r["stalled"], "attempts": r["attempts"], "secs": r["secs"],
            "zero_output_retries": r["zero_output_retries"], "secs_total": r["secs_total"],
            "steps": steps, "hit_step_limit": steps >= json.loads(CONFIG_ENUMERATE.read_text())["agent"]["build"]["steps"],
            "tool_calls": r["tool_calls"], "tokens": r["tokens"], "net_calls": net_calls(sb / "events.jsonl"),
            "options_parsed": po["parsed"], "options_reason": po["reason"], "n_options": len(opts),
            "n_complete_options": sum(o["png"] and o["values"] and o["fields_ok"] for o in opts),
            "n_distinct_framings": po.get("n_distinct", 0), "recommended": po.get("recommended"),
            "options": opts, "answer": ans, "answer_ok": ans is not None, "errors": r["errors"],
            "env": environment([prompt_file])}
    meta["complete"] = (meta["call_ok"] and po["parsed"] and meta["n_complete_options"] == k
                        and meta["n_distinct_framings"] == k and meta["answer_ok"])
    (sb / "response.md").write_text(r["text"])
    (sb / "meta.json").write_text(json.dumps(meta, indent=1))
    print(f"[{label} {q} r{rep}] complete={meta['complete']} options={meta['n_complete_options']}/{k} "
          f"distinct={meta['n_distinct_framings']} {meta['secs']}s steps={steps}", flush=True)
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
        elif mode == "D":
            ver, reps = sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1
            k = int(os.environ.get("PILOT_K", "3"))
            pf = HERE / "prompts" / f"D_enumerate.{ver}.md"
            label = f"D-{ver}-k{k}{SUFFIX}"
            res = list(ex.map(run_enumerate, [(label, q, r, pf, k) for q in qids for r in range(1, reps + 1)]))
        else:
            sys.exit("mode must be A, B, C or D")
    out = HERE / "runs"
    out.mkdir(exist_ok=True)
    name = label if not os.environ.get("PILOT_QIDS") else f"{label}-{'-'.join(qids)}"   # a subset never overwrites the full summary
    (out / f"{name}.json").write_text(json.dumps(res, indent=1))
    print("saved", label)
