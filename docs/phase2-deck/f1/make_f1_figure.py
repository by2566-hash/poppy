"""F1 slide figure: D v1 (k = 3 fixed) vs D v2 (free k + interpretation), per pilot question.
Left: options per run (mean of 3 runs). Right: share of options with a silent error (grader g8, human overrides applied).
Reads the committed score sheets; run from the repo root with the team venv."""
import csv, collections
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = Path("experiments/E009-enumerate/results")
QS = ["K1", "K2", "K3", "A1", "A2", "I1"]
TYPE = {"K1": "clear", "K2": "clear", "K3": "clear", "A1": "ambiguous", "A2": "ambiguous", "I1": "insufficient"}
V1, V2 = "#86b6ef", "#1c5cab"            # one hue, two shades (dumbbell: before -> after)
INK, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#ffffff"

def v(r, k): return r.get("h_" + k) or r.get("m_" + k) or ""
def silent(r):
    traps = [k[2:] for k in r if k.startswith("m_tr_") and v(r, k[2:]) == "FAIL"]
    return bool(r.get("h_gold") == "wrong" or r["unsourced_numbers"] or v(r, "unsupported_claim") == "FAIL" or traps)
def stats(label):
    rows = list(csv.DictReader(open(R / label / "scores.csv")))
    per = collections.defaultdict(list)
    for r in rows: per[r["q"]].append(r)
    out = {}
    for q in QS:
        rs = per[q]; runs = {r["rep"] for r in rs}
        out[q] = (len(rs) / len(runs), sum(map(silent, rs)) / len(rs), sum(map(silent, rs)), len(rs))
    return out, sum(map(silent, rows)), len(rows)

s1, n1, t1 = stats("D-v1-k3-openai-gpt-6-luna")
s2, n2, t2 = stats("D-v2-kfree-openai-gpt-6-luna")
plt.rcParams.update({"font.family": "Helvetica Neue", "font.size": 10, "axes.edgecolor": GRID, "text.color": INK,
                     "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK})
fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.9), dpi=220, sharey=True, gridspec_kw={"wspace": 0.12})
fig.patch.set_facecolor(SURF)
y = list(range(len(QS)))[::-1]
panels = [("Options per run (mean of 3 runs)", 0, (0, 3.6), [0, 1, 2, 3], lambda x: f"{x:.1f}".rstrip("0").rstrip(".")),
          ("Options with a silent error", 1, (-0.04, 1.08), [0, .25, .5, .75, 1], lambda x: f"{x:.0%}")]
for ax, (title, i, lim, ticks, fmt) in zip(axes, panels):
    ax.set_facecolor(SURF)
    for q, yy in zip(QS, y):
        a, b = s1[q][i], s2[q][i]
        ax.plot([a, b], [yy, yy], color=GRID, lw=2, zorder=1, solid_capstyle="round")
        ax.scatter([a], [yy], s=70, color=V1, zorder=2, edgecolor=SURF, linewidth=1.5)
        ax.scatter([b], [yy], s=70, color=V2, zorder=3, edgecolor=SURF, linewidth=1.5)
        if i == 1:   # selective labels: counts on the v2 dot only
            apart = abs(a - b) > 0.08   # far apart: both labels above the dots; overlapping: v2 above, v1 below
            ax.annotate(f"{s2[q][2]}/{s2[q][3]}", (b, yy), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=8, color=MUTED)
            ax.annotate(f"{s1[q][2]}/{s1[q][3]}", (a, yy), xytext=(0, 8 if apart else -13), textcoords="offset points", ha="center", fontsize=8, color=MUTED)
            if q == "K1":
                ax.annotate("wording, not v2: the same v2 prompt failed\n9/10 K1 options in F2 (rephrasing)", (0.45, yy), xytext=(0, -20),
                            textcoords="offset points", ha="center", va="top", fontsize=7.3, color=MUTED, style="italic")
    ax.set_xlim(*lim); ax.set_xticks(ticks); ax.set_xticklabels([fmt(t) for t in ticks])
    ax.set_title(title, loc="left", fontsize=10.5, color=INK, pad=8)
    ax.grid(axis="x", color=GRID, lw=0.8); ax.set_axisbelow(True)
    for sp in ("top", "right", "left"): ax.spines[sp].set_visible(False)
    ax.tick_params(axis="y", length=0); ax.tick_params(axis="x", length=0)
axes[0].set_yticks(y); axes[0].set_yticklabels([f"{q}  ({TYPE[q]})" for q in QS])
h1 = axes[0].scatter([], [], s=70, color=V1, label="D v1: k = 3 fixed")
h2 = axes[0].scatter([], [], s=70, color=V2, label="D v2: free k + interpretation")
fig.legend(handles=[h1, h2], loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.03), fontsize=9.5)
fig.text(0.01, -0.09, f"GPT-6 Luna, 6 pilot questions x 3 runs. Silent error = unsourced number, unsupported claim, wrong gold, or a failed trap item "
         f"(grader g8, two passes, human overrides applied). All: v1 {n1}/{t1}, v2 {n2}/{t2}. 6 questions: a screen, not a test.",
         fontsize=7.2, color=MUTED, wrap=True)
fig.savefig("docs/phase2-deck/f1/f1_v1_vs_v2.png", bbox_inches="tight", facecolor=SURF)
print({q: (round(s1[q][0], 2), round(s2[q][0], 2), f"{s1[q][2]}/{s1[q][3]}", f"{s2[q][2]}/{s2[q][3]}") for q in QS}, n1, t1, n2, t2)
