"""Part 2 of the mimo screen: can it read values off a chart? 5 charts x 3 questions with known answers."""
import json, os, re, subprocess, shutil, time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import HERE, MODEL
from run_screen import SANDBOX
CONFIG = {"$schema": "https://opencode.ai/config.json"}  # default agent; images need no step limit

gold = json.loads((HERE / "gold.json").read_text())
OUT = HERE / "vision"; OUT.mkdir(exist_ok=True)

def line(q, fname, title, ylabel, col=1):
    xs = [int(r[0]) for r in gold[q]]; ys = [r[col] for r in gold[q]]
    fig, ax = plt.subplots(figsize=(8, 4.5)); ax.plot(xs, ys, marker="o"); ax.set_title(title)
    ax.set_xlabel("Year"); ax.set_ylabel(ylabel); ax.set_xticks(xs); ax.tick_params(axis="x", labelrotation=45)
    fig.tight_layout(); fig.savefig(OUT / fname, dpi=110); top = ax.get_yticks()
    plt.close(fig); return dict(zip(xs, ys)), float(max(t for t in top if t <= ax.get_ylim()[1]))

def bar(q, fname, title, xlabel, ylabel, labels=None):
    ks = [r[0] if isinstance(r[0], str) else int(r[0]) for r in gold[q]]; ys = [r[1] for r in gold[q]]
    fig, ax = plt.subplots(figsize=(8, 4.5)); ax.bar([str(k) for k in ks], ys); ax.set_title(title)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.tick_params(axis="x", labelrotation=45)
    fig.tight_layout(); fig.savefig(OUT / fname, dpi=110); top = ax.get_yticks()
    plt.close(fig); return dict(zip([str(k) for k in ks], ys)), float(max(t for t in top if t <= ax.get_ylim()[1]))

charts = []
d, t = line("P1", "c1.png", "Persons killed per year", "Persons killed"); charts.append(("c1.png", d, t, "2019", "persons killed per year (line chart)"))
d, t = line("P2", "c2.png", "Cyclists injured per year", "Cyclists injured"); charts.append(("c2.png", d, t, "2022", "cyclists injured per year (line chart)"))
d, t = bar("P4", "c3.png", "Crashes by hour of day", "Hour", "Crashes"); charts.append(("c3.png", d, t, "17", "crashes by hour of day (bar chart)"))
d, t = bar("P3", "c4.png", "Pedestrians injured by borough", "Borough", "Pedestrians injured"); charts.append(("c4.png", d, t, "QUEENS", "pedestrians injured by borough (bar chart)"))
d, t = line("P6", "c5.png", "Pedestrians injured per year", "Pedestrians injured", col=2); charts.append(("c5.png", d, t, "2020", "pedestrians injured per year (line chart)"))

Q = """The attached image chart.png is a {desc}. Answer from the image only, as JSON with exactly these keys:
{{"highest_category": "<the x-axis label of the tallest point or bar>", "value_at_{key}": <your best estimate of the value at {key}>, "top_y_tick": <the largest numeric label printed on the y-axis>}}
Reply with the JSON only."""

res = []
for fname, d, top, key, desc in charts:
    sb = SANDBOX / f"vision-{fname[:-4]}"; shutil.rmtree(sb, ignore_errors=True); sb.mkdir(parents=True)
    shutil.copy(OUT / fname, sb / "chart.png"); (sb / "opencode.json").write_text(json.dumps(CONFIG))
    env = dict(os.environ, XDG_DATA_HOME=str(sb / ".ocdata")); t0 = time.time()
    p = subprocess.run(["opencode", "run", "--pure", "--format", "json", "-m", f"opencode/{MODEL}", "--dir", str(sb),
                        "-f", str(sb / "chart.png"), "--", Q.format(desc=desc, key=key)],
                       capture_output=True, text=True, env=env, cwd=sb, stdin=subprocess.DEVNULL, timeout=300)
    text = "".join(json.loads(l).get("part", {}).get("text", "") for l in p.stdout.splitlines()
                   if l.startswith("{") and json.loads(l).get("type") == "text")
    m = re.search(r"\{.*\}", text, re.S); ans = None
    try: ans = json.loads(m.group(0)) if m else None
    except json.JSONDecodeError: pass
    true_max = max(d, key=d.get); true_val = d[key] if key in d else d[int(key)] if key.isdigit() and int(key) in d else None
    rec = {"chart": fname, "gold_max": true_max, "gold_value": true_val, "gold_top_tick": top, "answer": ans, "raw": text[:200],
           "secs": round(time.time() - t0, 1)}
    if ans:
        rec["max_ok"] = str(ans.get("highest_category")).strip().upper() == str(true_max).upper()
        v = ans.get(f"value_at_{key}")
        try: rec["value_rel_err"] = round(abs(float(v) - true_val) / true_val, 3); rec["value_ok"] = rec["value_rel_err"] <= 0.10
        except (TypeError, ValueError): rec["value_ok"] = False
        try: rec["tick_ok"] = abs(float(ans.get("top_y_tick")) - top) < 1e-6
        except (TypeError, ValueError): rec["tick_ok"] = False
    res.append(rec); print(fname, {k: rec.get(k) for k in ("max_ok", "value_ok", "value_rel_err", "tick_ok", "secs")}, flush=True)
(HERE / "vision_runs.json").write_text(json.dumps(res, indent=1))
