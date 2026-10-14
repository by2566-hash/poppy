import duckdb
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SRC = "./data/crashes.parquet"
con = duckdb.connect()

counts = con.execute(
    """
    SELECT strftime(crash_date, '%u')::INT AS dow, COUNT(*) AS crashes
    FROM read_parquet(?)
    WHERE crash_date BETWEEN DATE '2013-01-01' AND DATE '2025-12-31'
      AND crash_date IS NOT NULL
    GROUP BY 1
    """,
    [SRC],
).df()

dates = con.execute(
    """
    WITH d AS (SELECT unnest(generate_series(DATE '2013-01-01', DATE '2025-12-31', INTERVAL '1 day')) AS dt)
    SELECT strftime(dt, '%u')::INT AS dow, COUNT(*) AS n_days
    FROM d GROUP BY 1
    """
).df()

df = dates.merge(counts, on="dow", how="left").fillna({"crashes": 0})
df["crashes"] = df["crashes"].astype(int)

names = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}
df["day"] = df["dow"].map(names)
df["share_pct"] = 100 * df["crashes"] / df["crashes"].sum()
df["avg_per_day"] = df["crashes"] / df["n_days"]
df = df.sort_values("dow").reset_index(drop=True)

total = df["crashes"].sum()
weekend = df.loc[df["dow"].isin([6, 7]), "crashes"].sum()
weekday = total - weekend
fri = df.loc[df["dow"] == 5, "crashes"].iloc[0]
sun = df.loc[df["dow"] == 7, "crashes"].iloc[0]
peak = df.loc[df["crashes"].idxmax()]
low = df.loc[df["crashes"].idxmin()]

out = df[["dow", "day", "crashes", "share_pct", "n_days", "avg_per_day"]].copy()
out.columns = ["dow", "day_of_week", "crashes", "share_pct", "n_days", "avg_crashes_per_day"]
out.to_csv("./out/values.csv", index=False)

print(out.to_string(index=False))
print(f"total={total} weekend={weekend} ({100*weekend/total:.1f}%) weekday={weekday} ({100*weekday/total:.1f}%)")
print(f"peak={peak['day']} {peak['crashes']} ({peak['share_pct']:.1f}%) low={low['day']} {low['crashes']} ({low['share_pct']:.1f}%)")
print(f"Fri/Sun ratio = {fri/sun:.3f}")

fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

colors = ["#4C72B0"] * 5 + ["#C44E52", "#C44E52"]
ax = axes[0]
bars = ax.bar(df["day"], df["crashes"], color=colors, edgecolor="black", linewidth=0.5)
for b, v, p in zip(bars, df["crashes"], df["share_pct"]):
    ax.text(b.get_x() + b.get_width() / 2, v + 4000, f"{v:,.0f}\n{p:.1f}%",
            ha="center", va="bottom", fontsize=9)
ax.set_title("NYC police-reported crashes by day of week\n(2013–2025, n = %s)" % f"{total:,}")
ax.set_ylabel("Total crashes")
ax.set_ylim(0, df["crashes"].max() * 1.18)
ax.grid(axis="y", alpha=0.3)
ax.set_axisbelow(True)

ax = axes[1]
bars = ax.bar(df["day"], df["avg_per_day"], color=colors, edgecolor="black", linewidth=0.5)
for b, v in zip(bars, df["avg_per_day"]):
    ax.text(b.get_x() + b.get_width() / 2, v + 30, f"{v:,.0f}", ha="center", va="bottom", fontsize=9)
ax.set_title("Average crashes per occurrence of each weekday\n(normalised for uneven weekday counts)")
ax.set_ylabel("Crashes per day")
ax.set_ylim(0, df["avg_per_day"].max() * 1.15)
ax.grid(axis="y", alpha=0.3)
ax.set_axisbelow(True)

for ax in axes:
    ax.set_xlabel("Day of week")

fig.tight_layout()
fig.savefig("./out/initial.png", dpi=150)
print("saved ./out/initial.png and ./out/values.csv")
