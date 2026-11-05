"""Read-only audit of E009-F2 (label D-v2-kfree-openai-gpt-6-luna-rephrasing): 12 phrasings x r1-r3.

Counts three levels separately:
  repetition      the planned unit (36); a restart is counted under its original repetition
  attempt         one run folder: the original, plus restarts stored as <q>-r<rep>-attempt<n> (label suffix -attempt<n> in the sandbox)
  internal retry  the runner's own zero-output / rate-limit retry inside one attempt (meta.json `attempts` > 1)

Reads the collected results (always) and the sandbox (if present, to confirm the copies are byte-identical), the runs/
summaries and the ITERATIONS.md headings. Prints a per-attempt table and the totals. Changes nothing.

Usage (from anywhere):  python experiments/E009-enumerate/f2_checks/audit_f2.py
"""
import filecmp, json, re, subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
E = ROOT / "experiments" / "E009-enumerate"
LABEL = "D-v2-kfree-openai-gpt-6-luna-rephrasing"
RES = E / "results" / LABEL
SB = ROOT.parent / "poppy-sandbox" / "E009"          # same location run_pilot.py uses; optional here
QS = [f"{b}-{p}" for b in ("K1", "K2", "K3", "A1", "A2", "I1") for p in ("casual", "formal")]

it = (E / "ITERATIONS.md").read_text()
heads = re.findall(r"^## E009-F2 trial: (\S+) r1–r3", it, re.M)
try:
    running = subprocess.run(["pgrep", "-fl", "opencode run"], capture_output=True, text=True).stdout
except FileNotFoundError:
    running = ""


def attempts(q, r):
    """[(n, result_dir, sandbox_dir)] for every attempt of q-r<r> that exists in results or sandbox."""
    out = [(1, RES / f"{q}-r{r}", SB / LABEL / f"{q}-r{r}")]
    for d in sorted(RES.glob(f"{q}-r{r}-attempt*")) + sorted(p / f"{q}-r{r}" for p in SB.glob(f"{LABEL}-attempt*")):
        n = int(re.search(r"attempt(\d+)", str(d)).group(1))
        if n not in [a[0] for a in out]:
            out.append((n, RES / f"{q}-r{r}-attempt{n}", SB / f"{LABEL}-attempt{n}" / f"{q}-r{r}"))
    return [a for a in out if a[1].exists() or a[2].exists()]


def outcome(m, n, summary_entry):
    if m is None:
        return "no record"
    if m.get("complete"):
        return "completed"
    if m.get("timed_out"):
        return "timed out"
    end = (summary_entry or {}).get("process_end", "")
    if "stopped manually" in end:
        return "stopped manually"
    return "failed"


rows, att_out, rep_final, rep_art, gaps, retries, timeout_answer = [], Counter(), Counter(), Counter(), [], [], {}
for q in QS:
    sp = E / "runs" / f"{LABEL}-{q}.json"
    summ = json.loads(sp.read_text()) if sp.exists() else []
    reps_seen = 0
    for r in (1, 2, 3):
        atts = attempts(q, r)
        if not atts:
            rows.append((q, r, "-", "not started", "-", "-", "-", "-", "-")); rep_final["not started"] += 1; continue
        reps_seen += 1
        rep_outcomes, rep_complete_art = [], False
        for n, rd, sd in atts:
            src = rd if (rd / "meta.json").exists() else sd
            m = json.loads((src / "meta.json").read_text()) if (src / "meta.json").exists() else None
            entry = next((e for e in summ if e.get("rep") == r and e.get("attempt", 1) == n), None)
            if n > 1 and entry is None:
                ap = E / "runs" / f"{LABEL}-attempt{n}-{q}-r{r}.json"
                entry = json.loads(ap.read_text())[0] if ap.exists() else None
            st = outcome(m, n, entry) if m else ("running" if str(sd) in running else "no record")
            out = src / "out"
            opts = json.loads((out / "options.json").read_text())["options"] if (out / "options.json").exists() else []
            art = bool(opts) and all((out / f"option_{o['id']}.png").exists() and (out / f"values_{o['id']}.csv").exists() for o in opts)
            collected = (rd / "meta.json").exists()
            if collected and sd.exists():
                files = [f for f in ("events.jsonl", "prompt.md", "response.md", "opencode.json") if (sd / f).exists()]
                files += [f"out/{p.name}" for p in (sd / "out").iterdir() if not p.name.endswith(".py")] if (sd / "out").exists() else []
                copy = "identical" if all(filecmp.cmp(sd / f, rd / f, shallow=False) for f in files) else "DIFFERS"
            else:
                copy = "sandbox absent" if collected else "-"
            in_summary = entry is not None
            logged = q in heads
            ir = (m or {}).get("attempts", 1) - 1
            if ir:
                retries.append(f"{q}-r{r} attempt {n}: {ir} internal retry (zero-output {m.get('zero_output_retries', 0)})")
            if st == "timed out":
                timeout_answer[f"{q}-r{r}"] = bool(m.get("answer_ok"))
            att_out[st] += 1; rep_outcomes.append(st); rep_complete_art |= art
            label = f"{n}" + (f" (restart of r{r})" if n > 1 else "") + (f", +{ir} internal retry" if ir else "")
            rows.append((q, r, label, st, f"{'complete' if art else 'none' if not opts else 'INCOMPLETE'} ({len(opts)})",
                         "yes" if collected else "NO", copy, "yes" if in_summary else "NO", "yes" if logged else "NO"))
            if not collected or copy == "DIFFERS" or not in_summary or not logged:
                gaps.append(f"{q}-r{r} attempt {n}")
        rep_final[rep_outcomes[-1] + (" (on a restart)" if len(atts) > 1 and rep_outcomes[-1] == "completed" else "")] += 1
        rep_art["complete" if rep_complete_art else "none"] += 1

print("| question | rep | attempt | process outcome | artifacts (options) | collected | copy vs sandbox | in summary | logged |")
print("|---|---|---|---|---|---|---|---|---|")
for x in rows:
    print("| " + " | ".join(map(str, x)) + " |")
n_att = sum(att_out.values())
print(f"\nrepetitions: {sum(rep_final.values())} planned; final process outcome per repetition: {dict(rep_final)}")
print(f"repetitions with a complete artifact set (in any attempt): {rep_art['complete']} / {sum(rep_art.values())}")
print(f"attempts: {n_att} ({n_att - sum(rep_final.values())} restart); outcome per attempt: {dict(att_out)}")
print(f"attempts with a complete artifact set: {sum(1 for x in rows if x[4].startswith('complete'))} / {n_att}")
print(f"internal retries (inside an attempt, not restarts): {retries or 'none'}")
print(f"timed-out repetitions with a final ANSWER in the reply: {timeout_answer}")
print(f"log headings: {len(heads)}; duplicates: {[h for h in set(heads) if heads.count(h) > 1]}; missing: {[q for q in QS if q not in heads]}")
print(f"summaries present: {sum((E / 'runs' / f'{LABEL}-{q}.json').exists() for q in QS)} / 12")
print(f"active opencode processes: {len([l for l in running.splitlines() if l.strip()])}")
print(f"bookkeeping gaps: {gaps or 'none'}")
