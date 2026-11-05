"""Check collected F2 I1 runs (no grader): structure, PNGs, CSVs vs I1 gold, per-crash rates recomputed, quoted
changes recomputed, and a scan of text, chart notes and code for VMT figures, 2020 caveats and proxy wording."""
import os
from pathlib import Path as _P
os.chdir(_P(__file__).resolve().parents[3])   # repo root: every path below is relative to it

import json, csv, re, sys
from pathlib import Path
import matplotlib.image as mpimg
R = Path("experiments/E009-enumerate/results/D-v2-kfree-openai-gpt-6-luna-rephrasing")
G = json.load(open("experiments/E007-pilot-prompts/gold_readings.json"))["I1"]["readings"]
mk = {int(y): v for y, v in G["motorist_killed_by_year"]["rows"]}
cr = {int(y): c for y, c, k in G["crashes_and_all_killed_by_year"]["rows"]}
pk = {int(y): k for y, c, k in G["crashes_and_all_killed_by_year"]["rows"]}
import duckdb
_PQ = "data/processed/nyc_crashes.parquet"
FC = {m: dict(duckdb.sql(f"SELECT year(crash_date), count(*) FILTER (WHERE {col} > 0) FROM '{_PQ}' WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY 1").fetchall())
      for m, col in (("motorist", "number_of_motorist_killed"), ("any", "number_of_persons_killed"))}
FC_MODE = None
def ref(c, y):
    c = c.lower()
    if c == "fatal_crashes": return FC[FC_MODE or "motorist"][y]
    if re.search(r"per_(100000|100k)(_|$)", c): return 1e5 * mk[y] / cr[y]
    if re.search(r"per_(1000|1k)(_|$)", c): return 1e3 * mk[y] / cr[y]
    if "crash" in c: return cr[y]
    if "motorist" in c: return mk[y]
    if "persons_killed" in c or "all_killed" in c: return pk[y]
print("recomputed: motorist deaths 2013->2025", round(100 * (mk[2025] - mk[2013]) / mk[2013], 1), "% ; per-100k", round(1e5 * mk[2013] / cr[2013], 1), "->",
      round(1e5 * mk[2025] / cr[2025], 1), "(", round(100 * (mk[2025] / cr[2025] / (mk[2013] / cr[2013]) - 1), 1), "% ); peak", max(mk, key=mk.get), max(mk.values()),
      "; per-100k 2019 -> 2020", round(1e5 * mk[2019] / cr[2019], 1), "->", round(1e5 * mk[2020] / cr[2020], 1))
print("query: crashes with a motorist killed 2013/2025", FC["motorist"][2013], FC["motorist"][2025], "| with anyone killed", FC["any"][2013], FC["any"][2025])
for run in sys.argv[1:]:
    d = R / run; opts = json.load(open(d / "out/options.json"))["options"]
    files = sorted(p.name for p in (d / "out").iterdir() if p.name != "options.json" and not p.name.endswith(".py"))
    expect = sorted(f"{s}_{o['id']}.{e}" for o in opts for s, e in (("option", "png"), ("values", "csv")))
    print(f"{run}: files match ids {files == expect}; prob sum {sum(o['probability'] for o in opts):.2f}")
    src = (d / "events.jsonl").read_text()
    for o in opts:
        miss = [k for k in ("metric", "denominator", "grouping", "chart_type", "reason", "answer", "interpretation", "probability") if o.get(k) in (None, "")]
        img = mpimg.imread(d / "out" / f"option_{o['id']}.png"); rows = list(csv.DictReader(open(d / "out" / f"values_{o['id']}.csv")))
        probs = [(r["year"], c, v) for r in rows for c, v in r.items() if c != "year" and (ref(c, int(r["year"])) is None or abs(float(v) - ref(c, int(r["year"]))) > 1e-4 * max(1, ref(c, int(r["year"]))))]
        t = o["answer"] + " " + o["interpretation"]
        print(f"  o{o['id']} p={o['probability']} png {img.shape[1]}x{img.shape[0]} rows={len(rows)} missing={miss} value problems={probs}")
        print(f"     says per-mile not answerable: {bool(re.search(r'cannot|can.t|not (a )?per-mile|no (miles|vehicle-miles)|unanswered', t, re.I))}; "
              f"2020 recording caveat: {bool(re.search(r'threshold|reporting (change|rule|policy)|recording|fewer minor|change in (crash )?report', t, re.I))}; "
              f"'proxy' wording: {re.findall(r'[^.;]*proxy[^.;]*', t, re.I)}")
    vmt = sorted({m.group(0)[:120] for m in re.finditer(r"(?i)[^\"\\]{0,60}(vmt|vehicle[- ]miles?|miles (driven|traveled))[^\"\\]{0,60}", src) if re.search(r"\d{2,}", m.group(0))})
    notes = sorted({m.group(0)[:150] for m in re.finditer(r'(?i)(source|note)[^"\\]{0,140}', src) if re.search(r"(?i)2020|report|mile", m.group(0))})
    print(f"  mileage-with-number strings in trace: {vmt[:3] or 'none'}"); print(f"  chart notes: {notes[:3] or 'none'}")
