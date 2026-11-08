"""One table across labels: silent-error (g8, human overrides applied), trap FAIL counts, per-question silent-error,
and two behaviour counts from the traces (NULL-inspecting queries per run, options whose interpretation states rows left out).
Run: ~/.poppy/venv/bin/python experiments/E010-loop/diagnosis/compare.py <results dir> [...]
"""
import csv, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import score_runs as s  # noqa: E402
from trace_stats import run_stats  # noqa: E402

TRAPS = ["tr_TR05", "tr_TR01", "tr_TR08", "tr_TR07", "tr_TR15", "tr_PERMILE", "tr_TR11", "tr_NIGHTDEF", "unsupported_claim"]
COVER = re.compile(r"\bnull\b|missing|no (recorded )?borough|without a borough|unknown borough|partial|only in part|left out|excluded|exclud", re.I)
QS = ["K1", "K2", "K3", "A1", "A2", "I1"]

cols = {}
for d in map(Path, sys.argv[1:]):
    rows = list(csv.DictReader(open(d / "scores.csv")))
    c = {"options": str(len(rows)), "silent-error": f"{sum(map(s.silent_error, rows))} ({100 * sum(map(s.silent_error, rows)) / len(rows):.0f}%)"}
    se2 = sum(bool(s.verdict(r, "unsupported_claim") == "FAIL" or any(k.startswith("tr_") and s.verdict(r, k) == "FAIL" for k in s.ALL_ITEMS)) for r in rows)
    c["SENSITIVITY traps+UC only (no provenance)"] = f"{se2} ({100 * se2 / len(rows):.0f}%)"
    c["unsourced numbers"] = f"{sum(bool(r['unsourced_numbers']) for r in rows)}/{len(rows)}"
    for t in TRAPS:
        app = [r for r in rows if s.verdict(r, t) in ("PASS", "FAIL")]
        c[t] = f"{sum(s.verdict(r, t) == 'FAIL' for r in app)}/{len(app)}"
    for q in QS:
        qr = [r for r in rows if r["q"] == q]
        c["SE " + q] = f"{sum(map(s.silent_error, qr))}/{len(qr)}"
    runs = sorted(p for p in d.iterdir() if (p / "events.jsonl").exists())
    st = [run_stats(p) for p in runs]
    c["NULL queries / run"] = f"{sum(x['null_queries'] for x in st) / len(st):.1f}"
    cov = tot = 0
    for p in runs:
        for o in json.loads((p / "out" / "options.json").read_text())["options"]:
            tot += 1; cov += bool(COVER.search(str(o.get("interpretation", "")) + " " + str(o.get("answer", ""))))
    c["options stating rows left out"] = f"{cov}/{tot}"
    a1 = [r for r in rows if r["q"] == "A1"]
    cols[f"{d.parent.parent.name.split('-')[0]} {d.name.replace('-openai-gpt-6-luna', '')}"] = c

keys = list(next(iter(cols.values())))
print("| item | " + " | ".join(cols) + " |")
print("|---|" + "---|" * len(cols))
for k in keys:
    print(f"| {k} | " + " | ".join(cols[c].get(k, "") for c in cols) + " |")
