"""Embedding distances for the round trip (diagnostic only; Bo 2026-11-08: the judge decides substitution).

Reads roundtrip/results/<label>/guesses.jsonl, fills `distances` per row for both local models, and prints per label:
  asked->guess   mean cosine distance between the asked question and each guessed question
  repeat floor   mean pairwise distance among the N guesses of the same option (noise of the reverse step itself)
  core           the same with the asked question cut to its question sentence (the task sentence "Make a chart ..." removed)
  between-option mean distance among guesses of different options of the same asked question (options are meant to differ)
  ratio          asked->guess / repeat floor
  reference      paraphrase scale: distance among the 3 phrasings (original, casual, formal; F2) of each pilot question
Run: HF_HUB_OFFLINE=1 ~/.poppy/embed-venv/bin/python experiments/E010-loop/roundtrip/distance.py <label> [<label> ...]
"""
import itertools, json, sys
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MODELS = {"mpnet": "sentence-transformers/all-mpnet-base-v2", "minilm": "sentence-transformers/all-MiniLM-L6-v2"}

pilot = {q["id"]: q["text"] for q in json.loads((ROOT / "experiments/E007-pilot-prompts/pilot_questions.json").read_text())["questions"]}
phr = {b: [t] for b, t in pilot.items()}
for q in json.loads((ROOT / "experiments/E009-enumerate/questions.rephrasing.json").read_text())["questions"]:
    phr[q["base"]].append(q["text"])


def core(q):
    """The question sentence only: text up to the first '?' (pilot prompts append a task sentence such as 'Make a chart ...')."""
    return q[:q.index("?") + 1] if "?" in q else q


def main(labels):
    data = {}
    for lab in labels:
        f = HERE / "results" / lab / "guesses.jsonl"
        data[lab] = [json.loads(l) for l in f.read_text().splitlines()]
    texts = {t for v in phr.values() for t in v}
    for rows in data.values():
        for r in rows:
            texts.add(r["asked_question"]); texts.add(core(r["asked_question"]))
            if r["parsed"]:
                texts.add(r["guess"]["guessed_question"])
    texts = sorted(texts)
    mean = lambda xs: float(np.mean(xs)) if len(xs) else None
    summary = {lab: {} for lab in labels}
    for short, name in MODELS.items():
        m = SentenceTransformer(name, device="cpu")
        E = dict(zip(texts, m.encode(texts, normalize_embeddings=True)))
        d = lambda a, b: float(1 - E[a] @ E[b])
        para = [d(x, y) for v in phr.values() for x, y in itertools.combinations(v, 2)]
        for lab, rows in data.items():
            ok = [r for r in rows if r["parsed"]]
            by_opt, by_q = {}, {}
            for r in ok:
                r["distances"][f"asked_guess_{short}"] = round(d(r["asked_question"], r["guess"]["guessed_question"]), 4)
                r["distances"][f"core_guess_{short}"] = round(d(core(r["asked_question"]), r["guess"]["guessed_question"]), 4)
                by_opt.setdefault((r["q"], r["rep"], r["option"]), []).append(r)
                by_q.setdefault(r["q"], []).append(r)
            floor = []
            for rs in by_opt.values():
                pair = [d(a["guess"]["guessed_question"], b["guess"]["guessed_question"]) for a, b in itertools.combinations(rs, 2)]
                for r in rs:
                    r["distances"][f"repeat_floor_{short}"] = round(mean(pair), 4) if pair else None
                floor += pair
            between = [d(a["guess"]["guessed_question"], b["guess"]["guessed_question"]) for rs in by_q.values()
                       for a, b in itertools.combinations(rs, 2) if (a["rep"], a["option"]) != (b["rep"], b["option"])]
            ag = [r["distances"][f"asked_guess_{short}"] for r in ok]
            cg = [r["distances"][f"core_guess_{short}"] for r in ok]
            summary[lab][short] = {"options": len(by_opt), "guesses": len(ok), "asked_guess_mean": mean(ag), "core_guess_mean": mean(cg), "repeat_floor_mean": mean(floor),
                                   "ratio": (mean(ag) / mean(floor)) if floor and mean(floor) else None, "between_option_mean": mean(between),
                                   "paraphrase_reference_mean": mean(para), "paraphrase_reference_max": float(max(para)),
                                   "per_question_asked_guess": {q: round(mean([r["distances"][f"asked_guess_{short}"] for r in rs]), 4) for q, rs in sorted(by_q.items())}}
    for lab, rows in data.items():
        with (HERE / "results" / lab / "guesses.jsonl").open("w") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        (HERE / "results" / lab / "distance_summary.json").write_text(json.dumps(summary[lab], indent=1))
        print(f"== {lab}")
        for short, s in summary[lab].items():
            fmt = lambda x: "n/a" if x is None else f"{x:.3f}"
            print(f"  {short:7} options={s['options']} guesses={s['guesses']}  asked->guess {fmt(s['asked_guess_mean'])} (core {fmt(s['core_guess_mean'])})  repeat floor {fmt(s['repeat_floor_mean'])}  "
                  f"ratio {fmt(s['ratio'])}  between-option {fmt(s['between_option_mean'])}  paraphrase ref {fmt(s['paraphrase_reference_mean'])} (max {fmt(s['paraphrase_reference_max'])})")


if __name__ == "__main__":
    main(sys.argv[1:])
