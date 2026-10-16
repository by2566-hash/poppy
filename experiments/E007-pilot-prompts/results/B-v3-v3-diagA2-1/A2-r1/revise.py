import duckdb
from decimal import Decimal, ROUND_HALF_UP

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

con = duckdb.connect()
df = con.execute("""
SELECT hour(crash_time) AS hour, COUNT(*) AS crashes,
       SUM(number_of_persons_injured) AS injured,
       SUM(number_of_persons_killed) AS killed,
       SUM(number_of_persons_injured) + SUM(number_of_persons_killed) AS harmed
FROM './data/crashes.parquet'
GROUP BY 1 ORDER BY 1
""").df()
df["injured_per_crash"] = (df["injured"] / df["crashes"]).round(3)
df["deaths_per_1000_crashes"] = (df["killed"] / df["crashes"] * 1000).round(2)
df.to_csv("./out/revised_values.csv", index=False)

fig, ax1 = plt.subplots(figsize=(11, 6))
colors = ["#1a4d7d" if 7 <= h <= 18 else "#e07b39" for h in df["hour"]]
ax1.bar(df["hour"], df["crashes"] / 1000, color=colors, alpha=0.75, width=0.8,
        label="Crashes (thousands)")
ax1.set_xlabel("Hour of day", fontsize=12)
ax1.set_ylabel("Number of crashes (thousands)", fontsize=12, color="#1a4d7d")
ax1.tick_params(axis="y", labelcolor="#1a4d7d")
ax1.set_xticks(range(0, 24))

ax2 = ax1.twinx()
ax2.plot(df["hour"], df["deaths_per_1000_crashes"], color="crimson", marker="o",
         lw=2.5, label="Fatalities per 1,000 crashes")
ax2.set_ylabel("Fatalities per 1,000 crashes", fontsize=12, color="crimson")
ax2.tick_params(axis="y", labelcolor="crimson")


def r1(x):
    return float(Decimal(str(x)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


peak = df.loc[df["deaths_per_1000_crashes"].idxmax()]
ax2.annotate(
    f"4 am: {r1(peak['deaths_per_1000_crashes'])} deaths\n"
    f"per 1,000 crashes\n(8× the 4 pm rate)",
    xy=(4, peak["deaths_per_1000_crashes"]), xytext=(6.5, 5.5),
    arrowprops=dict(arrowstyle="->", color="crimson"), fontsize=10, color="crimson")

handles = [Patch(facecolor="#1a4d7d", alpha=0.75, label="Crashes (day, 7am–6pm)"),
           Patch(facecolor="#e07b39", alpha=0.75, label="Crashes (night, 7pm–6am)"),
           Line2D([0], [0], color="crimson", marker="o", lw=2.5,
                  label="Fatalities per 1,000 crashes")]
ax1.legend(handles=handles, loc="upper left", fontsize=10, framealpha=0.9)
ax1.set_title(
    "NYC crashes by hour: daytime has the most crashes,\nnight crashes are far more deadly",
    fontsize=14, weight="bold")
ax1.grid(axis="y", alpha=0.3)
fig.text(0.5, -0.02,
         "Source: NYPD motor vehicle collisions, July 2012 – June 2026 (n = 2.27M crashes)",
         ha="center", fontsize=9, color="gray")
fig.tight_layout()
fig.savefig("./out/revised.png", dpi=150, bbox_inches="tight")

print(df.to_string())
print("peak deaths/1000:", peak["deaths_per_1000_crashes"], "displayed as", r1(peak["deaths_per_1000_crashes"]))
print("harmed check hour 0:", df.loc[0, "harmed"], "== ", df.loc[0, "injured"] + df.loc[0, "killed"])
