"""Embedding probe (docs/v2-design-2026-11-07.md §4, 'Validation before use'): can a local sentence-embedding model
order  paraphrase < neighbour < unrelated  by cosine distance?

Pairs
- paraphrase: the three phrasings of each pilot question (original, casual, formal; F2): 3 pairs x 6 bases = 18
- neighbour (hard negative): each drafted neighbour (neighbours.draft.json, one field changed) x the 3 phrasings of its base
- unrelated (easy negative): phrasings of different bases
- reading pairs (two legitimate readings of an ambiguous question): reported, not counted as negatives

AUC(a < b) = P(distance of a random b-pair > distance of a random a-pair), ties count 1/2.
Local models only (HF_HUB_OFFLINE=1); no API. Separate venv: ~/.poppy/embed-venv (requirements-embed.txt).
Run: HF_HUB_OFFLINE=1 ~/.poppy/embed-venv/bin/python experiments/E010-loop/probe/probe_embedding.py
"""
import itertools, json, sys
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MODELS = sys.argv[1:] or ["sentence-transformers/all-mpnet-base-v2", "sentence-transformers/all-MiniLM-L6-v2"]

pilot = {q["id"]: q["text"] for q in json.loads((ROOT / "experiments/E007-pilot-prompts/pilot_questions.json").read_text())["questions"]}
reph = json.loads((ROOT / "experiments/E009-enumerate/questions.rephrasing.json").read_text())["questions"]
phr = {b: {"original": t} for b, t in pilot.items()}
for q in reph:
    phr[q["base"]][q["id"].split("-")[1]] = q["text"]
nb = json.loads((HERE / "neighbours.draft.json").read_text())


def auc(pos, neg):
    pos, neg = np.asarray(pos), np.asarray(neg)
    return float(((neg[None, :] > pos[:, None]).sum() + 0.5 * (neg[None, :] == pos[:, None]).sum()) / (len(pos) * len(neg)))


def run(model_name):
    m = SentenceTransformer(model_name, device="cpu")
    texts = sorted({t for v in phr.values() for t in v.values()} | {n["text"] for n in nb["neighbours"]}
                   | {t for p in nb["reading_pairs"]["pairs"] for t in p})
    E = dict(zip(texts, m.encode(texts, normalize_embeddings=True)))
    d = lambda a, b: float(1 - E[a] @ E[b])
    para = {b: [d(x, y) for x, y in itertools.combinations(v.values(), 2)] for b, v in phr.items()}
    neigh = {b: [] for b in phr}
    neigh_by_field = {}
    for n in nb["neighbours"]:
        ds = [d(n["text"], t) for t in phr[n["base"]].values()]
        neigh[n["base"]] += ds
        neigh_by_field.setdefault(n["field"], []).extend(ds)
    unrel = [d(x, y) for b1, b2 in itertools.combinations(phr, 2) for x in phr[b1].values() for y in phr[b2].values()]
    reading = [d(a, b) for a, b in nb["reading_pairs"]["pairs"]]
    P, N = sum(para.values(), []), sum(neigh.values(), [])
    rng = np.random.default_rng(0)
    bases = list(phr)
    boot = []
    for _ in range(2000):   # cluster bootstrap over the 6 bases (pairs inside a base are not independent)
        bs = rng.choice(bases, size=len(bases))
        boot.append(auc(sum((para[b] for b in bs), []), sum((neigh[b] for b in bs), [])))
    out = {"model": model_name,
           "auc_paraphrase<neighbour_ci95_cluster_bootstrap": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))], "n": {"paraphrase": len(P), "neighbour": len(N), "unrelated": len(unrel)},
           "mean_distance": {"paraphrase": np.mean(P), "neighbour": np.mean(N), "unrelated": np.mean(unrel), "reading_pair": np.mean(reading)},
           "auc": {"paraphrase<neighbour": auc(P, N), "neighbour<unrelated": auc(N, unrel), "paraphrase<unrelated": auc(P, unrel)},
           "auc_per_base_paraphrase<neighbour": {b: auc(para[b], neigh[b]) for b in phr},
           "max_paraphrase_vs_min_neighbour_per_base": {b: (round(max(para[b]), 3), round(min(neigh[b]), 3)) for b in phr},
           "mean_neighbour_distance_by_field": {f: round(float(np.mean(v)), 3) for f, v in neigh_by_field.items()},
           "closest_neighbours": sorted(((round(min(d(n["text"], t) for t in phr[n["base"]].values()), 3), n["id"], n["field"]) for n in nb["neighbours"]))[:6]}
    return out


if __name__ == "__main__":
    res = [run(mn) for mn in MODELS]
    for r in res:
        print(f"\n## {r['model']}  n={r['n']}")
        print("mean distance:", {k: round(float(v), 3) for k, v in r["mean_distance"].items()})
        print("AUC:", {k: round(v, 3) for k, v in r["auc"].items()})
        print("AUC paraphrase<neighbour 95% CI (bootstrap over bases):", [round(x, 3) for x in r["auc_paraphrase<neighbour_ci95_cluster_bootstrap"]])
        print("AUC paraphrase<neighbour per base:", {k: round(v, 3) for k, v in r["auc_per_base_paraphrase<neighbour"].items()})
        print("max paraphrase vs min neighbour per base:", r["max_paraphrase_vs_min_neighbour_per_base"])
        print("neighbour distance by field:", r["mean_neighbour_distance_by_field"])
        print("closest neighbours:", r["closest_neighbours"])
    (HERE / "probe_results.json").write_text(json.dumps(res, indent=1, default=float))
