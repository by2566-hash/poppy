import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

con = duckdb.connect()
SRC = "./data/crashes.parquet"

monthly = con.sql(f"""
    SELECT date_trunc('month', crash_date)::DATE AS month,
           count(*) AS crashes,
           sum(number_of_persons_injured) AS injured,
           sum(number_of_persons_killed) AS killed
    FROM '{SRC}'
    WHERE crash_date >= '2015-01-01'
    GROUP BY 1 ORDER BY 1
""").df()

yearly = con.sql(f"""
    SELECT year(crash_date) AS yr, count(*) AS crashes,
           sum(number_of_persons_injured) AS injured,
           sum(number_of_persons_killed) AS killed
    FROM '{SRC}'
    WHERE crash_date >= '2013-01-01'
    GROUP BY 1 ORDER BY 1
""").df()

# ---------- period comparison (full years only) ----------
def period(y0, y1, label):
    d = yearly[(yearly.yr >= y0) & (yearly.yr <= y1)]
    n = len(d)
    return dict(label=label, years=f"{y0}-{y1}", n_years=n,
                crashes=d.crashes.mean(), injured=d.injured.mean(), killed=d.killed.mean())

periods = [period(2017, 2019, "Pre-COVID"),
           period(2020, 2021, "COVID onset"),
           period(2022, 2025, "Post-COVID")]
pre = periods[0]
print("=== Annual averages ===")
for p in periods:
    print(f"{p['label']:14s} {p['years']:9s} crashes={p['crashes']:>10,.0f} "
          f"injured={p['injured']:>8,.0f} killed={p['killed']:>7,.1f}")
print("\nPost (2022-25) vs Pre (2017-19):")
for k in ("crashes", "injured", "killed"):
    ch = 100 * (periods[2][k] / pre[k] - 1)
    print(f"  {k:8s} {ch:+.1f}%")

# ---------- COVID trough ----------
covid = monthly[(monthly.month >= "2020-01-01") & (monthly.month <= "2020-12-31")]
apr = covid[covid.month == "2020-04-01"].iloc[0]
feb = covid[covid.month == "2020-02-01"].iloc[0]
print(f"\nApril 2020 crashes: {apr.crashes:,.0f} vs Feb 2020 {feb.crashes:,.0f} "
      f"({100*(apr.crashes/feb.crashes-1):+.1f}%)")

# ---------- recency: last 12 complete months ----------
last12 = monthly[monthly.month <= "2025-06-01"].tail(12)
pre_monthly = pre["crashes"] / 12
print(f"Latest 12 full months (Jul 2024-Jun 2025) avg: {last12.crashes.mean():,.0f} crashes/month "
      f"vs pre-COVID {pre_monthly:,.0f} ({100*(last12.crashes.mean()/pre_monthly-1):+.1f}%)")

# 2026 YTD vs same period 2025
ytd = con.sql(f"""
    SELECT year(crash_date) AS yr, count(*) AS crashes
    FROM '{SRC}'
    WHERE month(crash_date) < 6 OR (month(crash_date) = 6 AND day(crash_date) <= 11)
    GROUP BY 1 ORDER BY 1
""").df()
print("\nJan-1..Jun-11 crashes by year:")
print(ytd.to_string(index=False))
latest = ytd[ytd.yr == 2026].crashes.iloc[0]
prev = ytd[ytd.yr == 2025].crashes.iloc[0]
print(f"2026 YTD vs 2025 same period: {latest:,.0f} vs {prev:,.0f} ({100*(latest/prev-1):+.1f}%)")

# severity per crash
yearly["inj_per_crash"] = yearly.injured / yearly.crashes
yearly["killed_per_crash"] = yearly.killed / yearly.crashes

# ================= charts =================
plt.rcParams.update({"figure.dpi": 130, "font.size": 9,
                     "axes.grid": True, "grid.alpha": 0.3})

# 1) monthly series (complete months only; data ends 2026-06-11)
plot_m = monthly[monthly.month < "2026-06-01"]
fig, ax = plt.subplots(figsize=(11, 4.4))
ax.plot(plot_m.month, plot_m.crashes, lw=1.1, color="#1f4e9c")
ax.axvspan(pd.Timestamp("2020-03-01"), pd.Timestamp("2020-06-01"),
           color="red", alpha=0.12, label="COVID onset (Mar-Jun 2020)")
ax.axhline(pre_monthly, color="gray", ls="--", lw=1,
           label=f"Pre-COVID avg ({pre_monthly:,.0f}/mo)")
ax.axvline(pd.Timestamp("2020-03-01"), color="red", ls=":", lw=1)
ax.set_title("NYC police-reported motor vehicle collisions per month, 2015-May 2026")
ax.set_ylabel("Crashes")
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.legend(loc="upper right", frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig("out/monthly_crashes.png")
plt.close(fig)

# 2) annual counts, three panels
y = yearly[yearly.yr <= 2025]
fig, axes = plt.subplots(3, 1, figsize=(8.5, 8), sharex=True)
cols = ["#1f4e9c", "#c8641e", "#a83232"]
names = ["Crashes", "People injured", "People killed"]
keys = ["crashes", "injured", "killed"]
for ax, k, nm, c in zip(axes, keys, names, cols):
    ax.bar(y.yr, y[k], color=c, width=0.75)
    ax.set_ylabel(nm)
    ax.set_title(nm, loc="left", fontsize=10, fontweight="bold")
axes[0].set_title("Annual totals: crashes, injuries, deaths (2013-2025)",
                  loc="left", fontsize=11, fontweight="bold")
axes[-1].set_xticks(range(2013, 2026))
axes[-1].set_xticklabels(range(2013, 2026), rotation=45)
fig.tight_layout()
fig.savefig("out/annual_totals.png")
plt.close(fig)

# 3) severity mix
fig, ax1 = plt.subplots(figsize=(9, 4.2))
ax1.bar(y.yr - 0.18, y.inj_per_crash, width=0.36, color="#2e8b57", label="Injuries per crash")
ax1.set_ylabel("Injuries per crash", color="#2e8b57")
ax1.tick_params(axis="y", colors="#2e8b57")
ax1.set_ylim(0, 0.7)
ax2 = ax1.twinx()
ax2.bar(y.yr + 0.18, y.killed_per_crash * 1000, width=0.36, color="#a83232",
        label="Fatalities per crash (x1000)")
ax2.set_ylabel("Fatalities per crash (x1000)", color="#a83232")
ax2.tick_params(axis="y", colors="#a83232")
ax2.grid(False)
ax1.set_xticks(range(2013, 2026))
ax1.set_xticklabels(range(2013, 2026), rotation=45)
ax1.set_title("Crash severity mix: injuries and deaths per reported crash")
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, loc="upper left", frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig("out/severity_per_crash.png")
plt.close(fig)

# 4) indexed trend vs pre-COVID baseline
base = yearly[(yearly.yr >= 2017) & (yearly.yr <= 2019)][["crashes", "injured", "killed"]].mean()
idx = yearly[(yearly.yr >= 2017) & (yearly.yr <= 2025)].copy()
for k in keys:
    idx[k] = 100 * idx[k] / base[k]
fig, ax = plt.subplots(figsize=(9, 4.2))
for k, c, nm in zip(keys, cols, names):
    ax.plot(idx.yr, idx[k], marker="o", ms=4, lw=1.6, color=c, label=nm)
ax.axhline(100, color="gray", ls="--", lw=1)
ax.set_ylabel("Index (2017-2019 average = 100)")
ax.set_xticks(range(2017, 2026))
ax.set_title("Change since pre-COVID: crashes fell far more than injuries or deaths")
ax.legend(frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig("out/indexed_vs_precovid.png")
plt.close(fig)

print("\nSaved: out/monthly_crashes.png, out/annual_totals.png, "
      "out/severity_per_crash.png, out/indexed_vs_precovid.png")
