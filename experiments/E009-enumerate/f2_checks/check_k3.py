"""Check collected F2 K3 runs: files vs ids, fields, values vs K3 gold (wide or long format), derived gap/ratio recomputed,
and the extremes quoted in answers recomputed from gold."""
import os
from pathlib import Path as _P
os.chdir(_P(__file__).resolve().parents[3])   # repo root: every path below is relative to it

import json, csv, sys
from pathlib import Path
R = Path("experiments/E009-enumerate/results/D-v2-kfree-openai-gpt-6-luna-rephrasing")
rows = json.load(open("experiments/E007-pilot-prompts/gold_readings.json"))["K3"]["readings"]["motorist_cyclist_killed_by_year"]["rows"]
mot = {int(y): m for y, m, c in rows}; cyc = {int(y): c for y, m, c in rows}
gap = {y: mot[y] - cyc[y] for y in mot}; ratio = {y: mot[y] / cyc[y] for y in mot}
ext = lambda d: (min(d, key=d.get), min(d.values()), max(d, key=d.get), max(d.values()))
print("gold motorist min/max", ext(mot), "cyclist", ext(cyc), "gap", ext(gap), "ratio", tuple(round(x, 3) if isinstance(x, float) else x for x in ext(ratio)))
for q in sys.argv[1:]:
    for r in (1, 2, 3):
        rd = R / f"{q}-r{r}"
        opts = json.load(open(rd / "out/options.json"))["options"]
        files = sorted(p.name for p in (rd / "out").iterdir() if p.name != "options.json")
        expect = sorted(f"{s}_{o['id']}.{e}" for o in opts for s, e in (("option", "png"), ("values", "csv")))
        print(f"{q}-r{r}: files match ids {files == expect}; prob sum {sum(o['probability'] for o in opts):.2f}")
        for o in opts:
            miss = [k for k in ("metric", "denominator", "grouping", "chart_type", "reason", "answer", "interpretation", "probability") if o.get(k) in (None, "")]
            data = list(csv.DictReader(open(rd / f"out/values_{o['id']}.csv"))); probs = []; checked = set()
            for row in data:
                y = int(row["year"])
                if "road_user" in row or "group" in row:   # long format
                    g = (row.get("road_user") or row.get("group")).lower()
                    ref = mot if g.startswith("motor") else cyc
                    col = [c for c in row if c not in ("year", "road_user", "group")][0]
                    checked.add(f"long:{g}")
                    if float(row[col]) != ref[y]: probs.append((y, g, row[col]))
                    continue
                for c, v in row.items():
                    if c == "year": continue
                    v = float(v); cl = c.lower()
                    if "ratio" in cl: ok = abs(v - ratio[y]) < 1e-6 or abs(v - round(ratio[y], 2)) < 1e-9
                    elif "minus" in cl or "gap" in cl or "diff" in cl: ok = v == gap[y]
                    elif "motor" in cl: ok = v == mot[y]
                    elif "cycl" in cl: ok = v == cyc[y]
                    else: ok = None
                    checked.add(c)
                    if ok is not True: probs.append((y, c, v, ok))
            print(f"  o{o['id']}: missing={miss} rows={len(data)} checked={sorted(checked)} value problems={probs}")
