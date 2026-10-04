import duckdb
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

SRC, OUT = "./data/crashes.parquet", "./out/crashes_covid.png"
con = duckdb.connect()

m = con.execute(
    f"""
    SELECT date_trunc('month', crash_date) AS mth,
           count(*)                                        AS crashes,
           sum(number_of_persons_injured)                  AS injured,
           sum(number_of_persons_killed)                   AS killed,
           sum(number_of_pedestrians_injured
             + number_of_cyclist_injured)                  AS vuln_inj,
           count(*) FILTER (WHERE number_of_motorist_injured > 0
                              OR number_of_motorist_killed  > 0) AS motorist,
           count(*) FILTER (WHERE number_of_pedestrians_injured > 0
                              OR number_of_pedestrians_killed  > 0
                              OR number_of_cyclist_injured    > 0
                              OR number_of_cyclist_killed     > 0) AS vuln_crashes,
           sum(number_of_persons_injured) FILTER (WHERE number_of_motorist_injured > 0
                              OR number_of_motorist_killed  > 0) AS motorist_injured
    FROM read_parquet('{SRC}') GROUP BY 1 ORDER BY 1
    """
).df()
m = m[m.mth < pd.Timestamp("2026-06-01")].reset_index(drop=True)   # drop partial Jun 2026

m["vuln_per1k"] = 1000 * m.vuln_inj / m.crashes
m["pct_vuln"] = 100 * m.vuln_crashes / m.crashes
m["pct_mot"] = 100 * m.motorist / m.crashes
m["mot_per1k"] = 1000 * m.motorist_injured / m.crashes

# Pre-COVID baseline window: 26 months before the March 2020 shutdown.
PRE_END, COVID_START = pd.Timestamp("2020-03-01"), pd.Timestamp("2020-03-01")
pre = m[m.mth < COVID_START]
post = m[m.mth >= pd.Timestamp("2022-01-01")]

def d(a, b):
    return 100 * (a / b - 1)

era = {
    "crashes": (pre.crashes.mean(), post.crashes.mean()),
    "inj":    (pre.injured.mean(),   post.injured.mean()),
    "killed": (pre.killed.mean(),    post.killed.mean()),
    "vuln":   (pre.vuln_inj.mean(), post.vuln_inj.mean()),
}
pre_avg = pre.crashes.mean()
trough = m.loc[m.crashes.idxmin()]

# Trailing 12m baseline = 12 months ending Feb 2020.
r = m.set_index("mth")[["crashes", "injured", "killed", "vuln_inj", "motorist",
                        "vuln_per1k", "pct_vuln", "pct_mot", "mot_per1k"]].rolling(12).mean()
base = r.loc[pd.Timestamp("2020-02-01")]
last = r.iloc[-1]
last_m = m.mth.iloc[-1]
end = {c: d(last[c], base[c]) for c in r.columns}

plt.rcParams.update({
    "font.size": 9, "axes.titlesize": 10.5, "axes.titleweight": "bold",
    "axes.labelsize": 9, "axes.edgecolor": "#8a8f98", "axes.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False,
    "xtick.color": "#5c6370", "ytick.color": "#5c6370",
    "axes.labelcolor": "#22262b", "text.color": "#22262b",
    "figure.facecolor": "white", "axes.facecolor": "white",
})
INK, MUTED = "#22262b", "#7d838d"
BLUE, ORANGE, RED, GREEN, GREY = "#2f6fb3", "#e08a2e", "#c4342b", "#2f8f6b", "#9aa1ab"
BAND = "#f3ddc9"
th = FuncFormatter(lambda v, p: f"{v/1000:.0f}k" if v >= 1000 else f"{v:.0f}")

fig, axes = plt.subplots(2, 2, figsize=(13.2, 8.6))
fig.subplots_adjust(hspace=0.46, wspace=0.26, top=0.855, bottom=0.085,
                    left=0.062, right=0.985)

def band(ax, lab_y=0.98):
    ax.axvspan(COVID_START, pd.Timestamp("2022-01-01"), color=BAND, alpha=0.6, lw=0, zorder=0)
    ax.text(pd.Timestamp("2020-10-15"), ax.get_ylim()[1] * lab_y, " COVID ", ha="center",
            va="top", fontsize=8, color="#a5622a", weight="bold", zorder=6)

# ---------- A: monthly crashes ----------
ax = axes[0, 0]
ax.plot(m.mth, m.crashes, color=BLUE, lw=1.1, zorder=3)
ax.axhline(pre_avg, color=MUTED, ls="--", lw=1.1, zorder=2)
ax.annotate(f"pre-COVID avg  {pre_avg:,.0f}/mo", xy=(pd.Timestamp("2013-06-01"), pre_avg),
            xytext=(0, 6), textcoords="offset points", fontsize=8, color=MUTED)
ax.annotate(f"{trough.crashes:,.0f}  ({d(trough.crashes, pre_avg):.0f}% vs pre-COVID)",
            xy=(trough.mth, trough.crashes), xytext=(30, -8), textcoords="offset points",
            fontsize=8.5, color=RED, weight="bold",
            arrowprops=dict(arrowstyle="->", color=RED, lw=1.1))
ax.annotate("no rebound: 2025 total is\nstill ~60% below 2019",
            xy=(pd.Timestamp("2024-06-01"), 7600), xytext=(-118, 52),
            textcoords="offset points", fontsize=8.5, color=INK,
            arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0))
ax.set_title("A.  Reported crashes per month", loc="left")
ax.set_ylabel("crashes / month")
ax.yaxis.set_major_formatter(th)
band(ax)

# ---------- B: indexed 12-mo mean ----------
ax = axes[0, 1]
ax.axhline(100, color=MUTED, ls="--", lw=1.1, zorder=2)
for col, c, lab in [("crashes", BLUE, "crashes"), ("injured", ORANGE, "persons injured"),
                    ("killed", RED, "persons killed")]:
    ax.plot(r.index, 100 * r[col] / base[col], color=c, lw=1.8, label=lab, zorder=3)
    ax.scatter([last_m], [100 * last[col] / base[col]], s=34, color=c, zorder=5,
               edgecolor="white", lw=1.1)
ax.annotate(f"crashes  {end['crashes']:+.0f}%", xy=(last_m, 100 * last.crashes / base.crashes),
            xytext=(-30, -34), textcoords="offset points", fontsize=8.5, color=BLUE, weight="bold")
ax.annotate(f"injured  {end['injured']:+.0f}%", xy=(last_m, 100 * last.injured / base.injured),
            xytext=(-16, 12), textcoords="offset points", fontsize=8.5, color=ORANGE, weight="bold")
ax.annotate(f"killed  {end['killed']:+.0f}%", xy=(last_m, 100 * last.killed / base.killed),
            xytext=(6, -22), textcoords="offset points", fontsize=8.5, color=RED, weight="bold")
ax.text(pd.Timestamp("2020-04-01"), 8, "trailing 12-mo mean, indexed to the 12 months\nending Feb 2020 = 100",
        fontsize=7.5, color=MUTED, va="bottom")
ax.set_title("B.  Same series, indexed (12-mo mean)", loc="left")
ax.set_ylabel("index, 12 mo to Feb 2020 = 100")
ax.legend(frameon=False, ncol=3, loc="upper right", bbox_to_anchor=(1.0, 0.99))
band(ax, 0.99)

# ---------- C: crash-mix shift ----------
ax = axes[1, 0]
ax.plot(r.index, r.pct_mot, color=BLUE, lw=2.0, label="crashes injuring or killing a motorist", zorder=4)
ax.plot(r.index, r.pct_vuln, color=RED, lw=2.0, label="crashes injuring or killing a pedestrian or cyclist",
        zorder=4)
ax.set_ylabel("% of all reported crashes")
b_lab, e_lab = r.loc[pd.Timestamp("2019-12-01")], r.loc[pd.Timestamp("2025-12-01")]
ax.annotate(f"{b_lab.pct_mot:.1f}%\n{e_lab.pct_mot:.1f}%",
            xy=(pd.Timestamp("2025-12-01"), e_lab.pct_mot), xytext=(-4, 16),
            textcoords="offset points", fontsize=8.5, color=BLUE, weight="bold", ha="center")
ax.annotate(f"{b_lab.pct_vuln:.1f}%\n{e_lab.pct_vuln:.1f}%",
            xy=(pd.Timestamp("2025-12-01"), e_lab.pct_vuln), xytext=(-8, -40),
            textcoords="offset points", fontsize=8.5, color=RED, weight="bold", ha="center")
ax.text(pd.Timestamp("2013-02-01"), 27,
        "Both roughly doubled: most of the vanished crashes were\n"
        "low-speed property-damage fender-benders.",
        fontsize=8, color=MUTED, va="top")
ax.set_title("C.  The mix shifted: each share of crashes now involves real harm", loc="left")
ax.legend(frameon=False, loc="lower left", fontsize=8.2, bbox_to_anchor=(0.0, -0.03))
band(ax)

# ---------- D: exposure check ----------
ax = axes[1, 1]
ax.plot(r.index, 100 * r.crashes / base.crashes, color=BLUE, lw=2.0,
        label="all reported crashes", zorder=4)
ax.plot(r.index, 100 * r.motorist / base.motorist, color=GREY, lw=2.0,
        label="crashes injuring/killing a motorist", zorder=4)
ax.axhline(100, color=MUTED, ls="--", lw=1.1, zorder=2)
ax.annotate(f"all crashes  {end['crashes']:+.0f}%", xy=(last_m, 100 * last.crashes / base.crashes),
            xytext=(-96, -34), textcoords="offset points", fontsize=8.5, color=BLUE, weight="bold")
ax.annotate(f"motorist crashes  {end['motorist']:+.0f}%",
            xy=(last_m, 100 * last.motorist / base.motorist), xytext=(-136, 14),
            textcoords="offset points", fontsize=8.5, color="#5f666f", weight="bold")
ax.text(pd.Timestamp("2021-02-01"), 4,
        "Motorist crashes scale with vehicle-miles driven, so they act as a proxy for exposure.\n"
        "They fell far less than the headline count — the crash mix shifted, it didn't just shrink.",
        fontsize=8, color=MUTED, va="bottom")
ax.set_title("D.  Exposure check: motorist crashes fell much less", loc="left")
ax.set_ylabel("index, 12 mo to Feb 2020 = 100")
ax.legend(frameon=False, loc="lower left", fontsize=8.5, bbox_to_anchor=(0.0, -0.03))
band(ax)

for ax in axes.flat:
    ax.set_xlim(pd.Timestamp("2012-07-01"), pd.Timestamp("2026-06-01"))
    ax.set_ylim(bottom=0)
    ax.set_xticks(pd.to_datetime([f"{y}-01-01" for y in range(2013, 2027, 2)]))
    ax.set_xticklabels([str(y) for y in range(2013, 2027, 2)])
    ax.grid(axis="y", color="#e8eaee", lw=0.7)
    ax.set_axisbelow(True)

# headroom so in-panel notes don't collide with the data or the COVID band label
axes[0, 0].set_ylim(0, 23500)
axes[0, 1].set_ylim(-15, 150)
axes[1, 0].set_ylim(0, 34)
axes[1, 1].set_ylim(-18, 132)

c, i, k = era["crashes"], era["inj"], era["killed"]
fig.suptitle("NYC motor vehicle crashes before, during and after COVID",
             x=0.062, ha="left", fontsize=14.5, weight="bold", y=0.968)
fig.text(0.062, 0.916,
         f"Crashes fell {abs(d(c[1], c[0])):.0f}% versus pre-COVID and stayed down. But injuries fell only "
         f"{abs(d(i[1], i[0])):.0f}% and deaths were unchanged\n({c[0]:,.0f} → {c[1]:,.0f} crashes/mo, "
         f"{i[0]:,.0f} → {i[1]:,.0f} injured/mo, {k[0]:.0f} → {k[1]:.0f} killed/mo). "
         "Fewer crashes, each far more dangerous.",
         ha="left", fontsize=9.8, color="#454b54", linespacing=1.5)
fig.text(0.062, 0.026,
         "Source: NYPD Motor Vehicle Collisions – Crashes (h9gi-nx95), one row per police-reported crash. "
         "Reportable when someone is injured or killed, or damage ≥ $1,000.\n"
         "Pre-COVID = Feb 2018–Feb 2020 (26 mo); post = Jan 2022–May 2026 (53 mo). "
         "Jun 2026 excluded (partial month; data ends 2026-06-11). NYPD data are preliminary and subject to revision.",
         ha="left", fontsize=7.4, color=MUTED, linespacing=1.5)

fig.savefig(OUT, dpi=200)
print("wrote", OUT)
print(f"pre  vs post monthly: crashes {c[0]:,.0f}->{c[1]:,.0f} ({d(c[1],c[0]):+.1f}%) | "
      f"inj {i[0]:,.0f}->{i[1]:,.0f} ({d(i[1],i[0]):+.1f}%) | killed {k[0]:.1f}->{k[1]:.1f} ({d(k[1],k[0]):+.1f}%)")
print("trailing12m endpoint deltas:", {k2: f"{v:+.1f}%" for k2, v in end.items()})
print(f"panel C: motorist share {b_lab.pct_mot:.1f}->{e_lab.pct_mot:.1f}% | vuln share {b_lab.pct_vuln:.1f}->{e_lab.pct_vuln:.1f}%")
print(f"harm per 1k: motorist {b_lab.mot_per1k:.0f}->{e_lab.mot_per1k:.0f} | vuln {b_lab.vuln_per1k:.0f}->{e_lab.vuln_per1k:.0f}")
print(f"trough {trough.mth.date()} {trough.crashes:,} ({d(trough.crashes, pre_avg):+.0f}%)")
