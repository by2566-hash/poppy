import os
import duckdb
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

os.makedirs("./out", exist_ok=True)

con = duckdb.connect()
df = con.execute("""
    SELECT (dayofweek(crash_date) + 6) % 7 AS dow_index,
           strftime(crash_date, '%A')       AS day_of_week,
           count(*)                         AS total_crashes,
           count(DISTINCT crash_date)       AS num_days
    FROM './data/crashes.parquet'
    WHERE crash_date BETWEEN DATE '2013-01-01' AND DATE '2025-12-31'
      AND crash_date IS NOT NULL
    GROUP BY 1, 2
    ORDER BY 1
""").df()

df["avg_crashes_per_day"] = df["total_crashes"] / df["num_days"]
grand_total = int(df["total_crashes"].sum())
df["share_pct"] = 100 * df["total_crashes"] / grand_total
df["share_of_expected_pct"] = 100 * df["avg_crashes_per_day"] / df["avg_crashes_per_day"].mean()

df = df[["dow_index", "day_of_week", "total_crashes", "num_days",
         "avg_crashes_per_day", "share_pct", "share_of_expected_pct"]]
df.to_csv("./out/values.csv", index=False)
print(df.to_string(index=False))
print("grand_total", grand_total, "| date coverage days", df["num_days"].sum(),
      "expected", (pd.Timestamp("2025-12-31") - pd.Timestamp("2013-01-01")).days + 1)

# robustness: does the pattern hold in every single year?
yr = con.execute("""
    SELECT year(crash_date) AS y,
           (dayofweek(crash_date) + 6) % 7 AS dow_index,
           count(*) AS n
    FROM './data/crashes.parquet'
    WHERE crash_date BETWEEN DATE '2013-01-01' AND DATE '2025-12-31'
    GROUP BY 1, 2
""").df()
yr["share"] = yr.groupby("y")["n"].transform(lambda s: s / s.sum())
piv = yr.pivot(index="y", columns="dow_index", values="share")
print("share of crashes by weekday, per year (0=Mon .. 6=Sun):")
print((piv * 100).round(1).to_string())
print("Fri is top day in", int((piv[4] == piv.max(axis=1)).sum()), "of", len(piv), "years;",
      "Sun is bottom day in", int((piv[6] == piv.min(axis=1)).sum()), "of", len(piv), "years")

days = df["day_of_week"].tolist()
x = list(range(len(df)))
mean_total = df["total_crashes"].mean()
mean_avg = df["avg_crashes_per_day"].mean()

fig, axes = plt.subplots(1, 2, figsize=(12, 5.2))
colors = ["#4C78A8"] * 7
colors[days.index("Friday")] = "#E45756"
colors[days.index("Sunday")] = "#72B7B2"

def style(ax, mean_val, mean_label_y):
    ax.axhline(mean_val, color="#555", ls="--", lw=1.2)
    ax.text(6.55, mean_label_y, f"mean {mean_val:,.0f}", ha="left", va="center",
            fontsize=9, color="#555")
    ax.set_xticks(x)
    ax.set_xticklabels([d[:3] for d in days])
    ax.set_xlim(-0.6, 7.35)
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)

ax = axes[0]
bars = ax.bar(x, df["total_crashes"], color=colors, edgecolor="white")
style(ax, mean_total, mean_total)
ax.set_ylabel("Crashes")
ax.set_title("A. Total crashes by weekday, 2013–2025\n(all {:,} crashes)".format(grand_total),
             fontsize=11)
ax.set_ylim(0, df["total_crashes"].max() * 1.20)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{v/1000:,.0f}k"))
for b, v, s in zip(bars, df["total_crashes"], df["share_pct"]):
    ax.text(b.get_x() + b.get_width() / 2, b.get_height(),
            f"{v/1000:,.1f}k\n{s:.1f}%", ha="center", va="bottom", fontsize=9)

ax = axes[1]
bars = ax.bar(x, df["avg_crashes_per_day"], color=colors, edgecolor="white")
style(ax, mean_avg, mean_avg)
ax.set_ylabel("Crashes per calendar day")
ax.set_title("B. Average crashes per weekday\n(same pattern after normalizing\nfor how many of each weekday)",
             fontsize=11)
ax.set_ylim(0, df["avg_crashes_per_day"].max() * 1.20)
for b, v in zip(bars, df["avg_crashes_per_day"]):
    ax.text(b.get_x() + b.get_width() / 2, b.get_height(),
            f"{v:,.0f}", ha="center", va="bottom", fontsize=9)

fig.suptitle("NYC police-reported crashes by day of week, 2013–2025", fontsize=13, y=0.99)
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig("./out/initial.png", dpi=150)
print("saved ./out/initial.png")
