"""Check collected F2 A2-formal runs (no grader): structure, PNGs, CSVs; every values cell recomputed by a direct
DuckDB query under the run's own day window over the full file (what all three runs used); trap-relevant wording."""
import os
from pathlib import Path as _P
os.chdir(_P(__file__).resolve().parents[3])   # repo root: every path below is relative to it

import json, csv, re
from pathlib import Path
import duckdb, matplotlib.image as mpimg
R = Path("experiments/E009-enumerate/results/D-v2-kfree-openai-gpt-6-luna-rephrasing"); PQ = "data/processed/nyc_crashes.parquet"
def q(a, b):   # day = a:00 .. b:59
    t = duckdb.sql(f"""SELECT CASE WHEN hour(crash_time) BETWEEN {a} AND {b} THEN 'day' ELSE 'night' END p, count(*) crashes,
        count(*) FILTER (WHERE number_of_persons_injured > 0) inj, count(*) FILTER (WHERE number_of_persons_injured > 0 OR number_of_persons_killed > 0) harm,
        count(*) FILTER (WHERE number_of_persons_killed > 0) fatal, sum(number_of_persons_injured) pinj, sum(number_of_persons_killed) pkil,
        count(*) FILTER (WHERE number_of_persons_killed IS NULL) null_killed,
        count(*) FILTER (WHERE number_of_persons_killed IS NOT NULL) known_kil, count(*) FILTER (WHERE number_of_persons_killed > 0) fatal_known
        FROM '{PQ}' GROUP BY 1""").df().set_index("p").reindex(["day", "night"]); return t
runs = {"A2-formal-r1": (6, 17), "A2-formal-r2": (6, 17), "A2-formal-r3": (7, 18)}
def ref(col, t, p):
    c = col.lower(); r = t.loc[p]
    if c == "window_hours_per_day": return 12
    if c == "crashes": return r.crashes
    if c == "injury_crashes": return r.inj
    if c == "injury_crash_pct": return 100 * r.inj / r.crashes
    if c == "injury_or_fatal_crashes": return r.harm
    if c in ("injury_or_fatal_pct", "injury_or_fatal_crash_pct"): return 100 * r.harm / r.crashes
    if c == "fatal_crashes": return r.fatal
    if c == "fatal_crash_pct": return 100 * r.fatal / r.crashes
    if c == "fatal_crashes_per_1000": return 1000 * r.fatal / r.crashes
    if c == "persons_injured": return r.pinj
    if c == "persons_killed": return r.pkil
    if c == "casualties": return r.pinj + r.pkil
    if c == "casualties_per_crash": return (r.pinj + r.pkil) / r.crashes
for run, (a, b) in runs.items():
    d = R / run; t = q(a, b); opts = json.load(open(d / "out/options.json"))["options"]
    files = sorted(p.name for p in (d / "out").iterdir() if p.name not in ("options.json",) and not p.name.endswith(".py"))
    expect = sorted(f"{s}_{o['id']}.{e}" for o in opts for s, e in (("option", "png"), ("values", "csv")))
    print(f"{run} (day {a:02d}:00-{b:02d}:59, full file): files match ids {files == expect}; prob sum {sum(o['probability'] for o in opts):.2f}; "
          f"NULL-killed rows day/night {list(t.null_killed)}; complete-case fatal per 1000 day/night {[round(1000*x/y, 3) for x, y in zip(t.fatal_known, t.known_kil)]}")
    src = (d / "events.jsonl").read_text()
    for o in opts:
        miss = [k for k in ("metric", "denominator", "grouping", "chart_type", "reason", "answer", "interpretation", "probability") if o.get(k) in (None, "")]
        img = mpimg.imread(d / "out" / f"option_{o['id']}.png"); rows = list(csv.DictReader(open(d / "out" / f"values_{o['id']}.csv")))
        probs = []
        for i, r in enumerate(rows):
            p = ["day", "night"][i]
            for c, v in r.items():
                if c == "period": continue
                x = ref(c, t, p)
                if x is None or abs(float(v) - x) > 1e-4 * max(1, abs(x)): probs.append((p, c, v, x))
        txt = o["answer"] + " " + o["interpretation"] + " " + o["denominator"]
        print(f"  o{o['id']} p={o['probability']} png {img.shape[1]}x{img.shape[0]} rows={len(rows)} missing={miss} value problems={probs} "
              f"| text mentions 2026/missing/NULL: {bool(re.search(r'2026|missing|null|incomplete|partial', txt, re.I))}")
    print("  chart code mentions 2026/missing/incomplete in a note:", sorted({m.group(0)[:150] for m in re.finditer(r'(?i)(source|note|data)[^"\\]{0,140}', src) if re.search(r"(?i)2026|missing|incomplete|partial", m.group(0))})[:3] or "none")
