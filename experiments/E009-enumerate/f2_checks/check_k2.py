"""Check collected F2 K2 runs: files vs ids, fields, counts vs K2 gold, derived shares / per-date averages recomputed."""
import os
from pathlib import Path as _P
os.chdir(_P(__file__).resolve().parents[3])   # repo root: every path below is relative to it

import json, csv, sys, datetime as dt
from pathlib import Path
R = Path("experiments/E009-enumerate/results/D-v2-kfree-openai-gpt-6-luna-rephrasing")
names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]   # DuckDB dayofweek: 0 = Sunday
gold = {names[int(k)]: v for k, v in json.load(open("experiments/E007-pilot-prompts/gold_readings.json"))["K2"]["readings"]["crashes_by_weekday"]["rows"]}
total = sum(gold.values())
days = {n: 0 for n in names}
d = dt.date(2013, 1, 1)
while d <= dt.date(2025, 12, 31):
    days[names[(d.weekday() + 1) % 7]] += 1; d += dt.timedelta(1)
print("gold total", total, "| weekday dates", days)
for q in sys.argv[1:]:
    for r in (1, 2, 3):
        rd = R / f"{q}-r{r}"
        opts = json.load(open(rd / "out/options.json"))["options"]
        files = sorted(p.name for p in (rd / "out").iterdir() if p.name != "options.json")
        expect = sorted(f"{s}_{o['id']}.{e}" for o in opts for s, e in (("option", "png"), ("values", "csv")))
        print(f"{q}-r{r}: files match ids {files == expect}; prob sum {sum(o['probability'] for o in opts):.2f}")
        for o in opts:
            miss = [k for k in ("metric", "denominator", "grouping", "chart_type", "reason", "answer", "interpretation", "probability") if o.get(k) in (None, "")]
            probs = []
            rows = list(csv.DictReader(open(rd / f"out/values_{o['id']}.csv")))
            key = list(rows[0])[0]   # first column holds the weekday name
            for row in rows:
                w = row[key]
                for c, v in row.items():
                    if c == key or c.endswith("_num"): continue
                    v = float(v)
                    if "share" in c: ok = abs(v - 100 * gold[w] / total) < 0.001
                    elif any(t in c for t in ("mean", "avg", "average", "per_")): ok = abs(v - gold[w] / days[w]) < 0.001
                    elif "date" in c or "days" in c: ok = v == days[w]
                    else: ok = v == gold[w]   # crash count
                    if not ok: probs.append((w, c, v))
            print(f"     columns {list(rows[0])}")
            if False:
                    if not ok: probs.append((w, c, v))
            print(f"  o{o['id']}: missing={miss} value problems={probs}")
