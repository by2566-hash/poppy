"""Check collected F2 K1 runs: files match option ids, required fields present, values vs K1 gold."""
import os
from pathlib import Path as _P
os.chdir(_P(__file__).resolve().parents[3])   # repo root: every path below is relative to it

import json, csv, sys
from pathlib import Path
R = Path("experiments/E009-enumerate/results/D-v2-kfree-openai-gpt-6-luna-rephrasing")
gold = {int(k): v for k, v in json.load(open("experiments/E007-pilot-prompts/gold_readings.json"))["K1"]["readings"]["ped_killed_by_year"]["rows"]}
for q in sys.argv[1:]:
    for r in (1, 2, 3):
        d = R / f"{q}-r{r}"
        opts = json.load(open(d / "out/options.json"))["options"]
        files = sorted(p.name for p in (d / "out").iterdir() if p.name != "options.json")
        expect = sorted(f"{s}_{o['id']}.{e}" for o in opts for s, e in (("option", "png"), ("values", "csv")))
        print(f"{q}-r{r}: files match ids {files == expect}; prob sum {sum(o['probability'] for o in opts):.2f}")
        for o in opts:
            miss = [k for k in ("metric", "denominator", "grouping", "chart_type", "reason", "answer", "interpretation", "probability") if o.get(k) in (None, "")]
            rows = list(csv.DictReader(open(d / f"out/values_{o['id']}.csv")))
            vals = {int(x["year"]): float(list(x.values())[1]) for x in rows}
            diff = {y: (vals.get(y), gold.get(y)) for y in set(gold) | set(vals) if vals.get(y) != gold.get(y)}
            print(f"  o{o['id']} p={o['probability']} cols={list(rows[0])} missing={miss} years={len(vals)} diffs_vs_gold={diff}")
            print(f"     chart={o['chart_type']} | metric={o['metric']} | denom={o['denominator']}")
            print(f"     answer: {o['answer']}")
            print(f"     interp: {o['interpretation']}")
