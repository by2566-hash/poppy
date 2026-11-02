#!/usr/bin/env python3
"""Phase-2 v0 scorer (docs/v2-plan.md, section v0): one script, one sheet.

  POPPY_MODEL=openai/gpt-6-luna ~/.poppy/venv/bin/python scripts/score_runs.py E009-enumerate D-v1-k3-openai-gpt-6-luna
  ... --no-grader                    machine checks only (no model call)
  ... --only A1-r1 K1-r2             restrict to runs
  ... --workers 3                    parallel grader calls
  ~/.poppy/venv/bin/python scripts/score_runs.py --summary E009-enumerate D-v1-k3-... [--baseline <label>]

Row = one option of a D run, or the single output of an A/B run. Columns:
  machine : complete, n_options, n_distinct_analytic, gold_match, gold_detail, n_numbers, unsourced_numbers, framing_flags
  grader  : m_<item> (PASS/FAIL/NA/unparsed) + ev_<item> (quoted evidence), for c1..c8, the question's trap items,
            unsupported_claim, required_statement; grader_model, grader_secs
  human   : h_<item> filled only where the human disagrees (review by exception), first_failure, notes.
            Existing human columns are preserved when the sheet is re-generated.
The grader runs in the review sandbox (read-only, no code, no network) with only the chart attached; values, answer and
code lines are passed inline. It never sees the run folder, the gold or the other options.
"""
import argparse, csv, itertools, json, math, os, re, shutil, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "E006-mimo-screen"))
from common import QUESTIONS, QUESTION_TYPES  # noqa: E402

GOLD = json.loads((ROOT / "experiments" / "E007-pilot-prompts" / "gold_readings.json").read_text())
REVIEW_CONFIG = ROOT / "experiments" / "E007-pilot-prompts" / "config" / "opencode.review.json"
SANDBOX = ROOT.parent / "poppy-sandbox" / "_score"
GRADER_VERSION = "g2"   # bump on any change to grader_prompt / items / standard; recorded in the sheet and in each run's grader/<version>-p<pass>/
CRITERIA = {"c1": "question answered: the output answers the question that was asked (not a neighbouring one)",
            "c2": "appropriate measure: the metric and denominator fit the question",
            "c3": "appropriate chart type for the data and the comparison",
            "c4": "useful comparison: the chart makes the relevant comparison visible",
            "c5": "faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)",
            "c6": "evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated",
            "c7": "clear and readable: titles, axes, legend and text are understandable without the code",
            "c8": "visually well presented"}
WEEKDAYS = {n: i for i, n in enumerate(["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"])}
NUM_RE = re.compile(r"(?<![\w.])(?<!per )(?<!per\s)(?<!every )[-~≈]?\s?(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?\s?(%|k\b|K\b|M\b|million|thousand|×|x\b)?")


# ---------------------------------------------------------------- loading runs
def code_of(events):
    """Every bash command and written/edited file content, in order, with a line index for evidence."""
    out = []
    if not events.exists():
        return ""
    for line in events.read_text().splitlines():
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("type") != "tool_use":
            continue
        p = d["part"]; t = p.get("tool"); inp = p.get("state", {}).get("input", {}) or {}
        if t == "bash":
            out.append(f"# bash\n{inp.get('command', '')}")
        elif t == "write":
            out.append(f"# write {inp.get('filePath', '')}\n{inp.get('content', '')}")
        elif t == "edit":
            out.append(f"# edit {inp.get('filePath', '')}\n{inp.get('newString', '')}")
    return "\n".join(out)


def answer_of(text):
    pos = text.rfind("ANSWER:")
    return text[pos + 7:].strip() if pos >= 0 else text.strip()


def load_units(run_dir):
    """A run folder -> list of units (option rows). D: one per option; A/B: one unit from out/."""
    meta = json.loads((run_dir / "meta.json").read_text())
    q, rep = meta["q"], meta["rep"]
    code = code_of(run_dir / "events.jsonl")
    out = run_dir / "out"
    base = {"q": q, "rep": rep, "type": meta.get("type") or QUESTION_TYPES.get(q, GOLD.get(q, {}).get("type", "")),
            "complete": meta.get("complete", meta.get("n_complete_options") == meta.get("n_options")),
            "n_options": meta.get("n_options", 1), "n_distinct_analytic": meta.get("n_distinct_analytic", ""),
            "steps": meta.get("steps", ""), "code": code, "dir": run_dir}
    units = []
    if "options" in meta:
        for o in meta["options"]:
            i = o["id"]
            text = " ".join(str(o.get(f, "")) for f in ("answer", "interpretation") if o.get(f))
            units.append({**base, "option": i, "png": out / f"option_{i}.png", "values": [out / f"values_{i}.csv"],
                          "text": text, "fields": {k: o.get(k, "") for k in ("metric", "denominator", "grouping", "chart_type", "probability")}})
    else:
        png = out / ("revised.png" if (out / "revised.png").exists() else "initial.png")
        vals = [p for p in (out / "revised_values.csv", out / "values.csv") if p.exists()]
        resp = run_dir / "response.md"
        units.append({**base, "option": 0, "png": png, "values": vals,
                      "text": answer_of(resp.read_text()) if resp.exists() else "", "fields": {}})
    return units


# ---------------------------------------------------------------- machine checks
def read_csv(p):
    try:
        rows = list(csv.DictReader(p.open(encoding="utf-8-sig")))
    except Exception:
        return []
    return rows


def norm_key(v, kind):
    s = str(v).strip().lower()
    if kind == "weekday":
        if s[:3] in {k[:3]: k for k in WEEKDAYS}:
            return WEEKDAYS[{k[:3]: k for k in WEEKDAYS}[s[:3]]]
        try:
            i = int(float(s))
        except ValueError:
            return None
        return i  # resolved later (0–6 Sunday-based or 1–7 ISO)
    if kind == "period":
        return "day" if "day" in s and "night" not in s else "night" if "night" in s else s
    try:
        return int(float(s))
    except ValueError:
        return None


def to_float(v):
    try:
        return float(str(v).replace(",", "").strip())
    except ValueError:
        return None


def gold_match(q, values_files):
    """match:<reading>.<col>[...] | mismatch:<reading> (key set matched, no column equal) | no_reading."""
    readings = GOLD.get(q, {}).get("readings", {})
    matches, mismatches = [], []
    for vf in values_files:
        rows = read_csv(vf)
        if not rows:
            continue
        cols = list(rows[0].keys())
        for rname, r in readings.items():
            kind = r["key_kind"]; gkeys = [row[0] for row in r["rows"]]
            for kc in cols:
                keys = [norm_key(row[kc], kind) for row in rows]
                if kind == "weekday" and all(isinstance(k, int) for k in keys) and keys and min(keys) >= 1 and max(keys) == 7:
                    keys = [k % 7 for k in keys]  # ISO Monday=1..Sunday=7 -> Sunday=0
                if None in keys or len(set(keys)) != len(keys) or not set(gkeys) <= set(keys):
                    continue
                idx = {k: i for i, k in enumerate(keys)}
                hit = False
                for gcol, gvals in gold_columns(r).items():
                    for vc in cols:
                        if vc == kc:
                            continue
                        ok = True
                        for k, gv in gvals.items():
                            x = to_float(rows[idx[k]][vc])
                            if x is None or gv is None or abs(x - gv) > (0.5 if float(gv).is_integer() and "-" not in gcol and "/" not in gcol and "%" not in gcol else max(0.01 * abs(gv), 0.05)):
                                ok = False; break
                        if ok:
                            matches.append(f"{rname}.{gcol}={vf.name}:{vc}"); hit = True
                if not hit:
                    mismatches.append(f"{rname}@{vf.name}:{kc}")
    if matches:
        return "match", ";".join(matches)
    if mismatches:
        # keys matched but no column equals a gold column: wrong numbers OR a reading the gold does not have.
        # The human decides (h_gold = wrong | new_reading); period-type keys are free cuts, hence unverified.
        return "unmatched", ";".join(mismatches)
    return "no_key", ""


def gold_columns(r):
    """Gold columns plus the derived ones a run may legitimately plot: pairwise differences and shares."""
    cols = {gcol: {row[0]: row[ci + 1] for row in r["rows"]} for ci, gcol in enumerate(r["columns"])}
    base = list(cols.items())
    for (a, av), (b, bv) in itertools.permutations(base, 2):
        cols[f"{a}-{b}"] = {k: (av[k] - bv[k]) if av[k] is not None and bv[k] is not None else None for k in av}
        cols[f"{a}/{b}"] = {k: (av[k] / bv[k]) if av[k] is not None and bv[k] else None for k in av}
        cols[f"{a}%of({a}+{b})"] = {k: (av[k] / (av[k] + bv[k]) * 100) if av[k] is not None and bv[k] is not None and (av[k] + bv[k]) else None for k in av}
    return cols


def numbers_in_text(text):
    """Numbers a reader would check: skips years 2000–2030 and bare integers <= 12 (hours, counts of items)."""
    found = []
    for m in NUM_RE.finditer(text):
        raw = m.group(0).strip()
        n = float(m.group(1).replace(",", "") + (m.group(2) or ""))
        suf = (m.group(3) or "").lower()
        if suf in ("k", "thousand"):
            n *= 1e3
        elif suf in ("m", "million"):
            n *= 1e6
        if 2000 <= n <= 2030 and not m.group(2) and suf == "":
            continue
        if n <= 12 and not m.group(2) and suf == "":
            continue
        found.append((raw, n, suf))
    return found


def provenance(text, values_files):
    cells = []
    cols = []
    for vf in values_files:
        rows = read_csv(vf)
        if not rows:
            continue
        for c in rows[0].keys():
            col = [to_float(r[c]) for r in rows]
            col = [x for x in col if x is not None]
            if col:
                cols.append(col); cells += col
    cand = set(round(x, 6) for x in cells)
    # sums of numeric columns within groups of any other column (e.g. monthly rows -> annual totals)
    for vf in values_files:
        rows = read_csv(vf)
        if not rows:
            continue
        names = list(rows[0].keys())
        for g in names:
            if len({r[g] for r in rows}) in (1, len(rows)):
                continue
            for c in names:
                if c == g:
                    continue
                sums = {}
                for r in rows:
                    x = to_float(r[c])
                    if x is not None:
                        sums[r[g]] = sums.get(r[g], 0) + x
                cand.update(round(x, 6) for x in sums.values())
    for col in cols:
        cand.update(round(x, 6) for x in (sum(col), sum(col) / len(col), max(col), min(col)))
        for a, b in itertools.combinations(col, 2):
            cand.add(round(a - b, 6)); cand.add(round(b - a, 6))
            if b:
                cand.add(round(a / b, 6)); cand.add(round((a - b) / b * 100, 6))
            if a:
                cand.add(round(b / a, 6)); cand.add(round((b - a) / a * 100, 6))
    # same-row ratios across columns (rates like per-100-crashes)
    for vf in values_files:
        rows = read_csv(vf)
        for r in rows:
            xs = [to_float(v) for v in r.values()]
            xs = [x for x in xs if x is not None]
            for a, b in itertools.permutations(xs, 2):
                if b:
                    cand.add(round(a / b, 6)); cand.add(round(a / b * 100, 6)); cand.add(round(a / b * 1000, 6)); cand.add(round(a / b * 100000, 6))
    cand_list = sorted(cand)
    nums = numbers_in_text(text)
    unsourced = []
    for raw, n, suf in nums:
        tol = max(0.01 * abs(n), 0.05 if suf == "%" or "." in raw else 0.5)
        if not any(abs(n - abs(c)) <= tol or (suf == "x" or suf == "×") and abs(n - abs(c)) <= 0.1 * n for c in cand_list):
            unsourced.append(raw)
    return len(nums), unsourced


FRAMING = [
    # TR05: a borough *filter* (= / == / in / like ... brooklyn), not a grouping by borough
    ("TR05", re.compile(r"borough[\w.()'\"\]\s]{0,30}?(?:==|=|like|in|eq\()\s*[(\['\"]*\s*brooklyn", re.I)),
    # TR01: a per-crash denominator: a division by a crash count, or a per_..._crashes column (not the parquet path)
    ("TR01", re.compile(r"per_?\d*k?_?crash|crash\w*_per_|/\s*[\w.\[\]'\"()]{0,30}crash(?!es\.parquet)|/\s*(?:nullif\()?count\(\*\)", re.I)),
    # TR08: 2026 inside the window (an exclusive upper bound `< '2026-01-01'` is fine), or a NULL-unsafe sum(a + b)
    ("TR08", re.compile(r"(?<![<]\s)(?<![<]\s')(?<![<]\sdate\s')(?<![<]\sDATE\s')\b2026\b|sum\([^)]*\+[^)]*\)", re.I)),
]


def framing_flags(code):
    flags = []
    for tid, rx in FRAMING:
        for i, line in enumerate(code.splitlines()):
            m = rx.search(line)
            if m and not (tid == "TR08" and "2026" in m.group(0) and re.search(r"<\s*(?:date|DATE|make_date\()?[\s\\'\"(]*2026|range\(\s*\d{4}\s*,\s*2026|2026[^\n]{0,12}exclu|exclud\w*[^\n]{0,20}2026", line)):
                flags.append(f"{tid}@L{i + 1}: {line.strip()[max(0, m.start() - 50):m.end() + 40][:140]}")
                break
    return flags


# ---------------------------------------------------------------- grader
def grader_items(q):
    items = dict(CRITERIA)
    for t in GOLD.get(q, {}).get("traps", []):
        items[f"tr_{t['id']}"] = t["item"]
    items["unsupported_claim"] = ("PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, "
                                  "or uses a number from outside the data; FAIL otherwise, quoting the sentence")
    if GOLD.get(q, {}).get("required_statement"):
        items["required_statement"] = "PASS if the output states, in its own words: " + GOLD[q]["required_statement"]
    return items


def grader_prompt(unit, values_text, code_text):
    q = unit["q"]
    items = grader_items(q)
    lines = "\n".join(f"- {k}: {v}" for k, v in items.items())
    fields = "\n".join(f"{k}: {v}" for k, v in unit["fields"].items() if v != "")
    return f"""You are grading ONE output of a data-analysis agent against a written standard. The chart is attached as an image.
Judge from the materials below only. Do not fix anything, do not redo the analysis. For each item answer PASS or FAIL
(NA if the item does not apply to this output) and quote the sentence, number or chart element that decides it.
Be strict: a limitation that matters but is not stated is a FAIL on the item that asks for it.
If the QUESTION TYPE is "insufficient", the data cannot answer the question as asked; the appropriate output states that
(required_statement) and shows a measure the data does support. Do not FAIL c1 or c2 merely because the measure is not the
one the question named (e.g. not per mile); FAIL them only if the output pretends to answer the unanswerable question.

QUESTION ASKED: {QUESTIONS.get(q, q)}
QUESTION TYPE: {unit['type']}
{('DECLARED FRAMING:' + chr(10) + fields) if fields else ''}
WRITTEN ANSWER:
{unit['text'] or '(none)'}

VALUES TABLE(S) BEHIND THE CHART:
{values_text}

CODE LINES THE AGENT RAN (for filters, windows, denominators):
{code_text or '(none captured)'}

ITEMS:
{lines}

Reply with exactly one JSON object and nothing else:
{{"<item>": {{"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}}, ...}} with one entry per item above."""


def parse_json(text):
    """The first complete JSON object in the reply; trailing text (or an extra brace) is ignored."""
    start = text.find("{")
    if start < 0:
        return {}
    try:
        obj, _ = json.JSONDecoder().raw_decode(text[start:])
        return obj if isinstance(obj, dict) else {}
    except json.JSONDecodeError:
        return {}


def code_for_grader(code, limit=12000):
    """Full code when short; otherwise only the lines that decide filters, windows and denominators."""
    if len(code) <= limit:
        return code
    keep = re.compile(r"where|date|year|20\d\d|borough|per_|/|sum\(|coalesce|fillna|dropna|between|filter|query\(|hour|night|day", re.I)
    lines = [l for l in code.splitlines() if l.startswith("#") or keep.search(l)]
    out = "\n".join(lines)
    note = "\n... (code lines filtered to those about filters, windows and denominators" + ("; truncated)" if len(out) > limit else ")")
    return out[:limit] + note


def run_grader(unit, label, call_model):
    q, rep, opt = unit["q"], unit["rep"], unit["option"]
    sb = SANDBOX / label / f"{q}-r{rep}-o{opt}"
    shutil.rmtree(sb, ignore_errors=True); sb.mkdir(parents=True)
    shutil.copy(REVIEW_CONFIG, sb / "opencode.json")
    files = []
    if unit["png"].exists():
        shutil.copy(unit["png"], sb / "chart.png"); files = [sb / "chart.png"]
    vt = []
    for vf in unit["values"]:
        if vf.exists():
            txt = vf.read_text(encoding="utf-8", errors="replace").splitlines()
            vt.append(f"[{vf.name}]\n" + "\n".join(txt[:61]) + ("\n... (truncated)" if len(txt) > 61 else ""))
    prompt = grader_prompt(unit, "\n".join(vt) or "(none)", code_for_grader(unit["code"]))
    (sb / "grader_prompt.md").write_text(prompt)
    t0 = time.time(); got, text, r, attempt = {}, "", {}, 0
    for attempt in (1, 2):   # one retry when nothing parses
        r = call_model(sb, prompt, timeout=300, files=files)
        text = r.get("text", "")
        got = parse_json(text)
        if got:
            break
    (sb / "grader_response.md").write_text(text)
    keep = unit["dir"] / "grader" / f"{GRADER_VERSION}-p{os.environ.get('GRADER_PASS', '1')}" / f"o{opt}"   # record stays with the run
    keep.mkdir(parents=True, exist_ok=True)
    shutil.copy(sb / "grader_prompt.md", keep / "prompt.md"); shutil.copy(sb / "grader_response.md", keep / "response.md")
    (keep / "meta.json").write_text(json.dumps({"grader_model": os.environ.get("POPPY_MODEL", ""), "grader_version": GRADER_VERSION, "attempts": attempt,
                                                "secs": round(time.time() - t0, 1), "tool_calls": r.get("tool_calls"), "errors": r.get("errors")}, indent=1))
    res = {"grader_secs": round(time.time() - t0, 1), "grader_tools": r.get("tool_calls", "")}
    for k in grader_items(q):
        v = got.get(k) if isinstance(got, dict) else None
        if isinstance(v, dict):
            res[f"m_{k}"] = str(v.get("verdict", "unparsed")).upper()[:6]; res[f"ev_{k}"] = str(v.get("evidence", ""))[:300]
        else:
            res[f"m_{k}"] = "unparsed"; res[f"ev_{k}"] = ""
    if not got:
        res["ev_raw"] = text[:500]
    return res


# ---------------------------------------------------------------- sheet
ALL_ITEMS = list(CRITERIA) + sorted({f"tr_{t['id']}" for g in GOLD.values() for t in g.get("traps", [])}) + ["unsupported_claim", "required_statement"]
HUMAN = ["h_gold"] + [f"h_{k}" for k in ALL_ITEMS] + ["first_failure", "notes"]   # h_gold: wrong | new_reading | ok
MACHINE = ["exp", "label", "q", "type", "rep", "option", "complete", "n_options", "n_distinct_analytic", "steps", "gold_match", "gold_detail",
           "n_numbers", "unsourced_numbers", "framing_flags"]
GRADER = ["grader_model", "grader_secs", "grader_tools"] + [c for k in ALL_ITEMS for c in (f"m_{k}", f"ev_{k}")] + ["ev_raw"]
COLUMNS = MACHINE + GRADER + HUMAN


def score(exp, label, only, use_grader, workers):
    res_dir = ROOT / "experiments" / exp / "results" / label
    sheet = res_dir / "scores.csv"
    old = {}
    if sheet.exists():
        for r in csv.DictReader(sheet.open()):
            old[(r["q"], r["rep"], r["option"])] = r
    runs = sorted(p for p in res_dir.iterdir() if p.is_dir() and (p / "meta.json").exists())
    if only:
        runs = [p for p in runs if p.name in only]
    units = [u for p in runs for u in load_units(p)]
    rows = []
    for u in units:
        gm, gd = gold_match(u["q"], [v for v in u["values"] if v.exists()])
        nn, uns = provenance(u["text"], [v for v in u["values"] if v.exists()])
        rows.append({"exp": exp, "label": label, "q": u["q"], "type": u["type"], "rep": u["rep"], "option": u["option"],
                     "complete": u["complete"], "n_options": u["n_options"], "n_distinct_analytic": u["n_distinct_analytic"], "steps": u["steps"],
                     "gold_match": gm, "gold_detail": gd, "n_numbers": nn, "unsourced_numbers": " | ".join(uns), "framing_flags": " | ".join(framing_flags(u["code"]))})
    if use_grader:
        from common import MODEL  # noqa: E402
        from run_screen import call_model  # noqa: E402
        print(f"grader: {MODEL}, {len(units)} units, {workers} workers", flush=True)
        with ThreadPoolExecutor(workers) as ex:
            outs = list(ex.map(lambda u: run_grader(u, label, call_model), units))
        for r, o in zip(rows, outs):
            r.update(o); r["grader_model"] = f"{MODEL}@{GRADER_VERSION}"
    for r in rows:
        prev = old.get((r["q"], str(r["rep"]), str(r["option"])), {})
        for c in HUMAN:
            r[c] = prev.get(c, "")
        if not use_grader:
            for c in GRADER:
                r.setdefault(c, prev.get(c, ""))
    if only:  # keep the rows of runs not re-scored
        done = {(r["q"], str(r["rep"]), str(r["option"])) for r in rows}
        rows += [r for k, r in old.items() if k not in done]
        rows.sort(key=lambda r: (r["q"], int(r["rep"]), int(r["option"])))
    with sheet.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    print(f"wrote {sheet} ({len(rows)} rows)")
    for r in rows:
        flags = [k for k in ALL_ITEMS if r.get(f"m_{k}") == "FAIL"]
        print(f"{r['q']}-r{r['rep']} o{r['option']}: gold={r['gold_match']} unsourced={r['unsourced_numbers'] or '-'} "
              f"flags={r['framing_flags'][:60] or '-'} FAIL={','.join(flags) or '-'}")


# ---------------------------------------------------------------- summary
def verdict(r, k):
    return r.get(f"h_{k}") or r.get(f"m_{k}") or ""


def silent_error(r):
    traps = [k for k in ALL_ITEMS if k.startswith("tr_") and verdict(r, k) == "FAIL"]
    return bool(r.get("h_gold") == "wrong" or r["unsourced_numbers"] or verdict(r, "unsupported_claim") == "FAIL" or traps)


def summary(exp, labels, baseline):
    sheets = {}
    for lab in labels:
        p = ROOT / "experiments" / exp / "results" / lab / "scores.csv"
        sheets[lab] = list(csv.DictReader(p.open())) if p.exists() else []
    items = ["silent_error", "gold_wrong", "gold_unverified", "unsourced", "complete_fail"] + ALL_ITEMS
    def fails(r, k):
        if k == "silent_error": return silent_error(r)
        if k == "gold_wrong": return r.get("h_gold") == "wrong"
        if k == "gold_unverified": return r["gold_match"] != "match" and r.get("h_gold", "") == ""
        if k == "unsourced": return bool(r["unsourced_numbers"])
        if k == "complete_fail": return r["complete"] not in ("True", "true", "1")
        return verdict(r, k) == "FAIL"
    def applicable(r, k):
        if k in ("silent_error", "gold_wrong", "gold_unverified", "unsourced", "complete_fail"): return True
        return verdict(r, k) in ("PASS", "FAIL")
    print(f"{'item':22s}" + "".join(f"{lab[:28]:>30s}" for lab in labels))
    for k in items:
        cells = []
        for lab in labels:
            rs = [r for r in sheets[lab] if applicable(r, k)]
            n = len(rs); f = sum(fails(r, k) for r in rs)
            cells.append(f"{f}/{n}" if n else "-")
        if any(c != "-" for c in cells):
            print(f"{k:22s}" + "".join(f"{c:>30s}" for c in cells))
    if baseline and baseline in sheets:
        print(f"\npaired per-question differences vs {baseline} (fail rate, treatment - baseline), silent_error:")
        for lab in labels:
            if lab == baseline: continue
            diffs = []
            for q in sorted({r["q"] for r in sheets[baseline]}):
                b = [r for r in sheets[baseline] if r["q"] == q]; t = [r for r in sheets[lab] if r["q"] == q]
                if b and t:
                    d = sum(map(silent_error, t)) / len(t) - sum(map(silent_error, b)) / len(b); diffs.append((q, d))
            print(f"  {lab}: " + ", ".join(f"{q} {d:+.2f}" for q, d in diffs) + (f"  mean {sum(d for _, d in diffs) / len(diffs):+.2f}" if diffs else ""))
    print("\n6 dev questions: screening only. MDE ≈ 48 points at K = 5 (Miller 2024); treat differences below that as unresolved.")
    print("human columns override grader columns where filled; grader columns are shadow until promoted (plan §3a).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("exp"); ap.add_argument("labels", nargs="+")
    ap.add_argument("--summary", action="store_true"); ap.add_argument("--baseline")
    ap.add_argument("--no-grader", action="store_true"); ap.add_argument("--only", nargs="*", default=[])
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    if a.summary:
        summary(a.exp, a.labels, a.baseline)
    else:
        for lab in a.labels:
            score(a.exp, lab, set(a.only), not a.no_grader, a.workers)


if __name__ == "__main__":
    main()
