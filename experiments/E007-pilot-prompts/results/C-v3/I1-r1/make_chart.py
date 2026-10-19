import os

import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.makedirs("out", exist_ok=True)

con = duckdb.connect()
df = con.sql(
    """
    SELECT year(crash_date) AS year,
           COUNT(*) AS crashes,
           SUM(number_of_motorist_killed)::BIGINT AS motorist_killed
    FROM './data/crashes.parquet'
    WHERE year(crash_date) BETWEEN 2013 AND 2025
    GROUP BY 1
    ORDER BY 1
    """
).df()

df["motorist_killed_per_100k_crashes"] = (
    df["motorist_killed"] / df["crashes"] * 100000
).round(1)
df = df[["year", "crashes", "motorist_killed",
         "motorist_killed_per_100k_crashes"]]
df.to_csv("out/values.csv", index=False)

fig, axes = plt.subplots(2, 1, figsize=(9, 8.5), sharex=True)

ax = axes[0]
colors = ["#1f77b4"] * len(df)
colors[0] = "#d62728"
colors[-1] = "#2ca02c"
ax.bar(df["year"], df["motorist_killed"], color=colors, width=0.75)
for x, v in zip(df["year"], df["motorist_killed"]):
    ax.annotate(str(int(v)), (x, v), textcoords="offset points",
                xytext=(0, 3), ha="center", fontsize=8)
ax.set_title("NYC motorist deaths in police-reported crashes, by year")
ax.set_ylabel("Motorists killed")
ax.set_ylim(0, max(df["motorist_killed"]) * 1.18)
ax.grid(axis="y", alpha=0.3)
d13 = int(df.loc[df.year == 2013, "motorist_killed"].iloc[0])
d25 = int(df.loc[df.year == 2025, "motorist_killed"].iloc[0])
ax.annotate(
    f"2013: {d13}\n2025: {d25}  ({(d25 - d13) / d13 * 100:+.0f}%)",
    xy=(0.98, 0.88), xycoords="axes fraction", ha="right", fontsize=9,
    bbox=dict(boxstyle="round", fc="white", ec="gray", alpha=0.9))

ax = axes[1]
ax.plot(df["year"], df["motorist_killed_per_100k_crashes"], marker="o",
        color="#ff7f0e", lw=2)
for x, v in zip(df["year"], df["motorist_killed_per_100k_crashes"]):
    ax.annotate(f"{v:.1f}", (x, v), textcoords="offset points", xytext=(0, 7),
                ha="center", fontsize=8)
ax.set_title(
    "Same deaths, different denominator: motorist deaths per 100,000\n"
    "reported crashes (crash counts in file fell from "
    f"{int(df.loc[df.year == 2013, 'crashes'].iloc[0]):,} to "
    f"{int(df.loc[df.year == 2025, 'crashes'].iloc[0]):,})")
ax.set_ylabel("Deaths per 100k crashes")
ax.set_xlabel("Year")
ax.set_xticks(df["year"])
ax.set_ylim(0, df["motorist_killed_per_100k_crashes"].max() * 1.25)
ax.grid(alpha=0.3)
p13 = float(df.loc[df.year == 2013, "motorist_killed_per_100k_crashes"].iloc[0])
p25 = float(df.loc[df.year == 2025, "motorist_killed_per_100k_crashes"].iloc[0])
ax.annotate(
    f"2013: {p13:.1f}   2025: {p25:.1f}  ({(p25 - p13) / p13 * 100:+.0f}%)",
    xy=(0.02, 0.85), xycoords="axes fraction", ha="left", fontsize=9,
    bbox=dict(boxstyle="round", fc="white", ec="gray", alpha=0.9))

fig.suptitle(
    'Risk per mile driven cannot be computed: ./data/crashes.parquet has no '
    'miles-driven (exposure) column',
    fontsize=11, style="italic")
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig("out/initial.png", dpi=150)
print(df.to_string(index=False))
