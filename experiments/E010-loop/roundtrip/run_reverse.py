"""Reverse inference, cleared context, values.csv only (docs/v2-design-2026-11-07.md §4 step 1; T3).

For each option of a results label: a fresh sandbox, a fresh OpenCode session, and a prompt that contains only the
option's values table (header + rows). The model returns a structured guess of the question. N guesses per option
give the repeat floor. Nothing else from the run is shown: no question, chart, title, answer, interpretation, code,
plan or check file, and no file name (the table is inlined; the sandbox holds only the permission config).

Run (from the repo root):
  set -a; source .env; set +a
  POPPY_MODEL=openai/gpt-6-luna ~/.poppy/venv/bin/python experiments/E010-loop/roundtrip/run_reverse.py <label> [--n 3] [--limit K] [--only K1-r1 ...] [--exp E010-loop]
Output: roundtrip/results/<label>/guesses.jsonl  (+ records/<q>-r<rep>-o<opt>-g<n>/{prompt.md,response.md,meta.json})
Resume-safe: a guess whose record already parses is not called again. The API key is read from .env by the harness
and never written anywhere.
"""
import argparse, csv, hashlib, json, os, re, shutil, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

os.environ.setdefault("POPPY_MODEL", "openai/gpt-6-luna")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "scripts")); sys.path.insert(0, str(ROOT / "experiments" / "E006-mimo-screen"))
import score_runs as S          # noqa: E402  (load_units, parse_json, REVIEW_CONFIG)
from run_screen import call_model  # noqa: E402

PROMPT_FILE = HERE / "reverse_prompt.md"
PROMPT = PROMPT_FILE.read_text()
PROMPT_SHA = hashlib.sha256(PROMPT.encode()).hexdigest()
SANDBOX = ROOT.parent / "poppy-sandbox" / "_roundtrip"
MAX_ROWS = 200
FIELDS = ["guessed_question", "metric", "denominator", "population", "filters", "grouping", "time_window", "confidence", "not_recoverable"]
STOP = set("a an and are as at be by did do does each for from has have how in is it many more most much nyc of on or over per than that the there to was were what when where which who with year years".split())


def table_text(vf):
    lines = vf.read_text(encoding="utf-8", errors="replace").strip().splitlines()
    rows = lines[1:]
    shown = lines[:1] + rows[:MAX_ROWS]
    return "\n".join(shown), len(rows), (f", first {MAX_ROWS} shown" if len(rows) > MAX_ROWS else "")


def leak_tokens(question, vf):
    """Content words of the asked question that also appear in the table's header or text cells. Recorded, not removed:
    column names are part of what the option shows (DESIGN.md, limits)."""
    qw = {w for w in re.findall(r"[a-z]+", question.lower()) if w not in STOP and len(w) > 2}
    rows = list(csv.reader(vf.open(encoding="utf-8", errors="replace")))
    cells = " ".join(rows[0]) + " " + " ".join(c for r in rows[1:] for c in r if not re.fullmatch(r"[-\d.,eE+%]*", c))
    tw = set(re.findall(r"[a-z]+", cells.lower().replace("_", " ")))
    stem = lambda w: re.sub(r"(ies|es|s|ed|ing)$", "", w)
    ts = {stem(w) for w in tw}
    return sorted(w for w in qw if stem(w) in ts)


def one(job):
    label, u, g, model, out_dir = job
    key = f"{u['q']}-r{u['rep']}-o{u['option']}-g{g}"
    rec = out_dir / "records" / key
    vf = u["values"][0]
    table, n_rows, trunc = table_text(vf)
    prompt = PROMPT.replace("{n_rows}", str(n_rows)).replace("{trunc}", trunc).replace("{table}", table)
    got, meta = {}, {}
    if (rec / "response.md").exists() and (rec / "prompt.md").exists() and (rec / "prompt.md").read_text() == prompt:
        got = S.parse_json((rec / "response.md").read_text())
        meta = json.loads((rec / "meta.json").read_text()) if (rec / "meta.json").exists() else {}
    if not got.get("guessed_question"):
        sb = SANDBOX / label / key
        t0 = time.time(); text, r, attempt = "", {}, 0
        for attempt in (1, 2):   # one retry when nothing parses
            shutil.rmtree(sb, ignore_errors=True); sb.mkdir(parents=True)   # fresh sandbox and session store per attempt
            shutil.copy(S.REVIEW_CONFIG, sb / "opencode.json")              # read-only permissions; no data, no run files
            r = call_model(sb, prompt, timeout=240, model=model)
            text = r.get("text", ""); got = S.parse_json(text)
            if got.get("guessed_question"):
                break
        rec.mkdir(parents=True, exist_ok=True)
        (rec / "prompt.md").write_text(prompt); (rec / "response.md").write_text(text)
        meta = {"model": model, "prompt_sha": PROMPT_SHA, "attempts": attempt, "secs": round(time.time() - t0, 1),
                "tool_calls": r.get("tool_calls"), "tokens": r.get("tokens"), "errors": [e[:200] for e in (r.get("errors") or [])],
                "opencode_env": {"OPENCODE_DISABLE_EXTERNAL_SKILLS": "1", "OPENCODE_DISABLE_CLAUDE_CODE": "1"}}
        (rec / "meta.json").write_text(json.dumps(meta, indent=1))
    row = {"label": label, "q": u["q"], "base": u["base"], "type": u["type"], "rep": u["rep"], "option": u["option"], "guess_n": g,
           "asked_question": u["question"], "values_file": vf.name, "values_sha": hashlib.sha256(vf.read_bytes()).hexdigest()[:16],
           "n_rows": n_rows, "header": table.splitlines()[0] if table else "", "leak_tokens": leak_tokens(u["question"], vf),
           "guess": {k: got.get(k, "") for k in FIELDS} if got else {}, "parsed": bool(got.get("guessed_question")),
           "model": meta.get("model", model), "prompt_sha": meta.get("prompt_sha", PROMPT_SHA),
           "tool_calls": meta.get("tool_calls"), "errors": meta.get("errors", []), "distances": {}}
    print(f"[{label} {key}] parsed={row['parsed']} tools={row['tool_calls']} :: {row['guess'].get('guessed_question', '')[:110]}", flush=True)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("label"); ap.add_argument("--exp", default="E010-loop")
    ap.add_argument("--n", type=int, default=3, help="reverse guesses per option (repeat floor needs >= 2)")
    ap.add_argument("--limit", type=int, default=0, help="smoke test: only the first K options")
    ap.add_argument("--only", nargs="*", default=[], help="run folders, e.g. K1-r1 I1-r2")
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    model = os.environ["POPPY_MODEL"]
    res = ROOT / "experiments" / a.exp / "results" / a.label
    runs = sorted(p for p in res.iterdir() if p.is_dir() and (p / "meta.json").exists() and (not a.only or p.name in a.only))
    units = [u for p in runs for u in S.load_units(p) if u["values"] and u["values"][0].exists()]
    if a.limit:
        units = units[:a.limit]
    out_dir = HERE / "results" / a.label
    out_dir.mkdir(parents=True, exist_ok=True)
    jobs = [(a.label, u, g, model, out_dir) for u in units for g in range(1, a.n + 1)]
    print(f"{a.label}: {len(units)} options x {a.n} guesses, model {model}, prompt {PROMPT_SHA[:12]}", flush=True)
    with ThreadPoolExecutor(a.workers) as ex:
        rows = list(ex.map(one, jobs))
    old = {}
    gj = out_dir / "guesses.jsonl"
    if gj.exists():   # keep rows of options not in this call (--only / --limit)
        for l in gj.read_text().splitlines():
            r = json.loads(l); old[(r["q"], str(r["rep"]), str(r["option"]), r["guess_n"])] = r
    for r in rows:
        old[(r["q"], str(r["rep"]), str(r["option"]), r["guess_n"])] = r
    with gj.open("w") as f:
        for k in sorted(old, key=lambda k: (k[0], int(k[1]), int(k[2]), k[3])):
            f.write(json.dumps(old[k], ensure_ascii=False) + "\n")
    print(f"wrote {gj} ({len(old)} rows; {sum(not r['parsed'] for r in old.values())} unparsed; "
          f"{sum(bool(r['tool_calls']) for r in old.values())} with tool calls)")


if __name__ == "__main__":
    main()
