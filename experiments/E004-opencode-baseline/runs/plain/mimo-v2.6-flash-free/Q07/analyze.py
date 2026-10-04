import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PARQUET = "./data/crashes.parquet"
OUT = "./out"

con = duckdb.connect()

total, specified, unspecified = con.execute(f"""
    SELECT COUNT(*),
           COUNT(*) FILTER (WHERE contributing_factor_vehicle_1 <> 'Unspecified'),
           COUNT(*) FILTER (WHERE contributing_factor_vehicle_1 = 'Unspecified'
                             OR contributing_factor_vehicle_1 IS NULL)
    FROM '{PARQUET}'
""").fetchone()

print(f"total={total:,}  specified={specified:,} ({specified/total:.1%})  "
      f"unspecified={unspecified:,} ({unspecified/total:.1%})")

top = con.execute(f"""
    SELECT contributing_factor_vehicle_1 AS factor, COUNT(*) AS n
    FROM '{PARQUET}'
    WHERE contributing_factor_vehicle_1 <> 'Unspecified'
    GROUP BY 1 ORDER BY n DESC LIMIT 15
""").df()
top["pct"] = 100.0 * top["n"] / specified
print("\nTop 15 primary contributing factors (% of the "
      f"{specified:,} crashes with a recorded factor):")
for _, r in top.iterrows():
    print(f"  {r['factor']:<58} {r['n']:>9,}  {r['pct']:5.1f}%")

# ---- Chart 1: top contributing factors -------------------------------------
plt.rcParams.update({"font.size": 11})
fig, ax = plt.subplots(figsize=(10, 7))
labels = top["factor"][::-1]
vals = top["pct"][::-1]
colors = ["#d62728" if i == len(vals) - 1 else "#4C72B0" for i in range(len(vals))]
ax.barh(labels, vals, color=colors)
for i, v in enumerate(vals):
    ax.text(v + 0.4, i, f"{v:.1f}%", va="center", fontsize=10)
ax.set_xlabel(f"% of crashes with a recorded contributing factor (n = {specified:,})")
ax.set_title("Top 15 primary contributing factors in NYC crashes, 2012–2026\n"
             f"({total:,} crashes total; {unspecified/total:.0%} list the factor as 'Unspecified')",
             fontsize=13, loc="left")
ax.set_xlim(0, max(vals) * 1.15)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(f"{OUT}/top_contributing_factors.png", dpi=150)
plt.close(fig)

# ---- Chart 2: all crashes vs fatal crashes ---------------------------------
allc = con.execute(f"""
    SELECT contributing_factor_vehicle_1 AS factor, COUNT(*) AS n
    FROM '{PARQUET}'
    WHERE contributing_factor_vehicle_1 <> 'Unspecified'
    GROUP BY 1 ORDER BY n DESC LIMIT 8
""").df()
allc["pct"] = 100.0 * allc["n"] / specified

fatal_tot = con.execute(f"""
    SELECT COUNT(*) FROM '{PARQUET}'
    WHERE number_of_persons_killed > 0 AND contributing_factor_vehicle_1 <> 'Unspecified'
""").fetchone()[0]
fatal = con.execute(f"""
    SELECT contributing_factor_vehicle_1 AS factor, COUNT(*) AS n
    FROM '{PARQUET}'
    WHERE number_of_persons_killed > 0 AND contributing_factor_vehicle_1 <> 'Unspecified'
    GROUP BY 1
""").df()
fatal = allc[["factor"]].merge(fatal, on="factor", how="left").fillna(0)
fatal["pct"] = 100.0 * fatal["n"] / fatal_tot

import numpy as np
x = np.arange(len(allc))
w = 0.38
fig, ax = plt.subplots(figsize=(11, 6.5))
ax.bar(x - w / 2, allc["pct"], w, label="All crashes with a recorded factor", color="#4C72B0")
ax.bar(x + w / 2, fatal["pct"], w, label=f"Fatal crashes (n = {fatal_tot:,})", color="#d62728")
ax.set_xticks(x)
ax.set_xticklabels(allc["factor"], rotation=35, ha="right")
ax.set_ylabel("% of crashes in group")
ax.set_title("What causes crashes vs. what causes fatal crashes in NYC", fontsize=13, loc="left")
ax.legend(frameon=False)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(f"{OUT}/all_vs_fatal.png", dpi=150)
plt.close(fig)

# ---- Chart 3: yearly trend --------------------------------------------------
trend = con.execute(f"""
    SELECT year(crash_date) AS yr, COUNT(*) AS n,
           100.0 * AVG(CASE WHEN contributing_factor_vehicle_1 =
                'Driver Inattention/Distraction' THEN 1.0 ELSE 0.0 END) AS inatt,
           100.0 * AVG(CASE WHEN contributing_factor_vehicle_1 = 'Unspecified'
                THEN 1.0 ELSE 0.0 END) AS unspec
    FROM '{PARQUET}'
    GROUP BY 1 ORDER BY 1
""").df()

fig, ax = plt.subplots(figsize=(10, 5.5))
ax.plot(trend["yr"], trend["inatt"], marker="o", lw=2.5, color="#d62728",
        label="Driver Inattention/Distraction")
ax.plot(trend["yr"], trend["unspec"], marker="o", lw=2.5, color="#888888",
        label="'Unspecified'")
ax.set_ylabel("% of crashes that year")
ax.set_xlabel("Year (2026 = through June)")
ax.set_title("Recorded cause of NYC crashes over time", fontsize=13, loc="left")
ax.legend(frameon=False)
ax.grid(alpha=0.3)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(f"{OUT}/yearly_trend.png", dpi=150)
plt.close(fig)

print("\nCharts written: top_contributing_factors.png, all_vs_fatal.png, yearly_trend.png")
