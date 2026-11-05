"""Check collected F2 A1 runs (no grader): structure, PNGs, CSVs, values vs A1 gold (+ one direct DuckDB query for
crashes with a pedestrian casualty, which the gold file does not hold), quoted figures recomputed, trap-relevant wording."""
import os
from pathlib import Path as _P
os.chdir(_P(__file__).resolve().parents[3])   # repo root: every path below is relative to it

import json, csv, sys, re
from pathlib import Path
import duckdb, matplotlib.image as mpimg
R = Path("experiments/E009-enumerate/results/D-v2-kfree-openai-gpt-6-luna-rephrasing")
G = json.load(open("experiments/E007-pilot-prompts/gold_readings.json"))["A1"]["readings"]
inj = {int(y): i for y, i, k in G["brooklyn_ped_injured_killed_by_year"]["rows"]}
kil = {int(y): k for y, i, k in G["brooklyn_ped_injured_killed_by_year"]["rows"]}
cr = {int(y): c for y, c in G["brooklyn_crashes_by_year"]["rows"]}
PQ = "data/processed/nyc_crashes.parquet"
q = f"""SELECT year(crash_date) y, count(*) FILTER (WHERE coalesce(number_of_pedestrians_injured,0)+coalesce(number_of_pedestrians_killed,0) > 0) pc
        FROM '{PQ}' WHERE year(crash_date) BETWEEN 2013 AND 2025 AND upper(borough)='BROOKLYN' GROUP BY 1 ORDER BY 1"""
pc = {int(y): v for y, v in duckdb.sql(q).fetchall()}
nb = duckdb.sql(f"""SELECT year(crash_date) y, round(100*avg(CASE WHEN borough IS NULL OR trim(borough)='' THEN 1 ELSE 0 END),1)
                    FROM '{PQ}' WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY 1 ORDER BY 1""").fetchall()
print("query: crashes with pedestrian casualty", pc)
print("query: % crashes with no borough, by year", dict(nb))
cas = {y: inj[y] + kil[y] for y in inj}; share = {y: 100 * pc[y] / cr[y] for y in cr}
ref = {"cas": cas, "kil": kil, "inj": inj, "cr": cr, "pc": pc, "share": share, "per1000": {y: 10 * share[y] for y in share}}
def role(col, opt):
    c = col.lower()
    if c in ("value", "count"):   # generic column: infer from the option's metric
        m = opt["metric"].lower()
        return "pc" if "crashes with" in m else "cas" if "injured + killed" in m or "casualt" in m else "kil" if "death" in m or "killed" in m else "inj"
    if "per_1000" in c: return "per1000"
    if "pct" in c or "share" in c: return "share"
    if "crashes_with" in c or "involved_crashes" in c: return "pc"
    if "crash" in c: return "cr"
    if "casualt" in c: return "cas"
    if "killed" in c: return "kil"
    if "injured" in c: return "inj"
pct = lambda a, b: round(100 * (b - a) / a, 1)
for run in sys.argv[1:]:
    d = R / run; f = d / "out" / "options.json"
    if not f.exists(): print(f"{run}: no options.json; out/ holds {sorted(p.name for p in (d / 'out').iterdir())}"); continue
    opts = json.load(open(f))["options"]
    files = sorted(p.name for p in (d / "out").iterdir() if p.name != "options.json")
    expect = sorted(f"{s}_{o['id']}.{e}" for o in opts for s, e in (("option", "png"), ("values", "csv")))
    print(f"{run}: files match ids {files == expect}; prob sum {sum(o['probability'] for o in opts):.2f}")
    for o in opts:
        miss = [k for k in ("metric", "denominator", "grouping", "chart_type", "reason", "answer", "interpretation", "probability") if o.get(k) in (None, "")]
        img = mpimg.imread(d / "out" / f"option_{o['id']}.png")
        rows = list(csv.DictReader(open(d / "out" / f"values_{o['id']}.csv"))); probs = []; roles = set()
        for r in rows:
            y = int(r["year"])
            for c, v in r.items():
                if c == "year": continue
                k = role(c, o); roles.add(f"{c}->{k}")
                if abs(float(v) - ref[k][y]) > 1e-3 * max(1, abs(ref[k][y])): probs.append((y, c, v, round(ref[k][y], 3)))
        text = o["answer"] + " " + o["interpretation"]
        flags = {"borough/missing disclosed": bool(re.search(r"borough|missing|unassigned|no location|not recorded", text, re.I)),
                 "exposure caveat": bool(re.search(r"exposure|walking|per trip|per pedestrian|walked", text, re.I)),
                 "2020 recording caveat": bool(re.search(r"2020.*(report|record|threshold|policy)|(report|record).*(change|threshold)", text, re.I)),
                 "small-count caveat": bool(re.search(r"small|few|volatil|fluctuat|swing", text, re.I))}
        print(f"  o{o['id']} p={o['probability']} png {img.shape[1]}x{img.shape[0]} rows={len(rows)} missing={miss} roles={sorted(roles)} value problems={probs}")
        print(f"     wording: {flags}")
print("recomputed:", {"casualties 2013->2025": pct(cas[2013], cas[2025]), "injured": pct(inj[2013], inj[2025]), "killed": pct(kil[2013], kil[2025]),
      "pc crashes": pct(pc[2013], pc[2025]), "share 2013": round(share[2013], 2), "share 2025": round(share[2025], 2),
      "share rel": pct(share[2013], share[2025]), "cas 2020-2025 rising each year": all(cas[y] > cas[y - 1] for y in range(2021, 2026)),
      "inj 2020-2025 rising each year": all(inj[y] > inj[y - 1] for y in range(2021, 2026)), "pc 2020": pc[2020],
      "cas 2020 low -> 2025": pct(cas[2020], cas[2025]), "share 2025 - 2013 (pp)": round(share[2025] - share[2013], 2)})
