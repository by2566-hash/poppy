import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

con = duckdb.connect()

# Brooklyn pedestrian counts by year, as reported by borough field.
# 2026 is excluded (data ends 2026-06-11, partial year).
df = con.sql("""
SELECT
  YEAR(crash_date)                       AS year,
  SUM(number_of_pedestrians_injured)     AS ped_injured,
  SUM(number_of_pedestrians_killed)      AS ped_killed,
  COUNT(*) FILTER (
    WHERE number_of_pedestrians_injured + number_of_pedrians_killed > 0
  )                                      AS ped_crashes,
  COUNT(*)                               AS all_crashes
FROM 'data/crashes.parquet'
WHERE borough = 'BROOKLYN'
  AND YEAR(crash_date) BETWEEN 2013 AND 2025
GROUP BY 1 ORDER BY 1
""").df()

# Sensitivity check: add back crashes with NULL borough whose coordinates
# fall inside a Brooklyn bounding box (validated: 96% of known-Brooklyn
# pedestrian-injury rows with coordinates fall inside this box).
df_bbox = con.sql("""
SELECT
  YEAR(crash_date) AS year,
  SUM(number_of_pedestrians_injured) AS ped_injured_bbox,
  SUM(number_of_pedestrians_killed)  AS ped_killed_bbox
FROM 'data/crashes.parquet'
WHERE YEAR(crash_date) BETWEEN 2013 AND 2025
  AND (
    borough = 'BROOKLYN'
    OR (
      borough IS NULL
      AND latitude BETWEEN 40.5776 AND 40.7395
      AND longitude BETWEEN -74.0431 AND -73.8300
    )
  )
GROUP BY 1 ORDER BY 1
""").df()

df = df.merge(df_bbox, on="year")
df["ped_injured_per_1000_crashes"] = (
    df["ped_injured"] / df["all_crashes"] * 1000
).round(1)

df.to_csv("out/values.csv", index=False)
print(df.to_string(index=False))

# --- Key figures for the written answer ---
def y(year, col):
    return int(df.loc[df.year == year, col].iloc[0])

print("\n2013 vs 2025 injured:", y(2025, "ped_injured") - y(2013, "ped_injured"),
      round(100 * (y(2025, "ped_injured") / y(2013, "ped_injured") - 1), 1), "%")
print("2020 vs 2025 injured change:",
      round(100 * (y(2025, "ped_injured") / y(2020, "ped_injured") - 1), 1), "%")
print("2013 vs 2025 killed:", y(2013, "ped_killed"), "->", y(2025, "ped_killed"))
w1 = df[df.year.between(2013, 2015)]
w2 = df[df.year.between(2023, 2025)]
print("3yr avg injured 2013-15 vs 2023-25:",
      round(w1.ped_injured.mean(), 1), round(w2.ped_injured.mean(), 1),
      round(100 * (w2.ped_injured.mean() / w1.ped_injured.mean() - 1), 1), "%")
print("3yr avg killed 2013-15 vs 2023-25:",
      round(w1.ped_killed.mean(), 1), round(w2.ped_killed.mean(), 1),
      round(100 * (w2.ped_killed.mean() / w1.ped_killed.mean() - 1), 1), "%")
print("bbox sensitivity injured 2025:", y(2025, "ped_injured_bbox"),
      "2013:", y(2013, "ped_injured_bbox"),
      "2020:", y(2020, "ped_injured_bbox"))

# --- Chart ---
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

fig, ax = plt.subplots(figsize=(11, 6.5), dpi=150)

years = df["year"].astype(int)
colors = ["#7fa8c9"] * len(years)
colors[list(years).index(2020)] = "#c9d8e4"  # de-emphasize pandemic year

bars = ax.bar(years, df["ped_injured"], color=colors, width=0.72, zorder=3)
ax.set_ylabel("Pedestrians injured", fontsize=12, color="#1a3a52")
ax.set_ylim(0, 4100)
ax.yaxis.grid(True, color="#e3e8ee", zorder=0)
ax.set_axisbelow(True)
ax.tick_params(axis="y", labelsize=10, colors="#445566")
ax.tick_params(axis="x", labelsize=10, rotation=0)

# Fatalities on secondary axis (dots + line, thin, clearly labeled)
ax2 = ax.twinx()
ax2.spines["top"].set_visible(False)
ax2.plot(years, df["ped_killed"], color="#c0392b", marker="o", markersize=5,
         linewidth=2, zorder=4, label="Pedestrians killed")
ax2.set_ylabel("Pedestrians killed", fontsize=12, color="#c0392b")
ax2.set_ylim(0, 78)
ax2.tick_params(axis="y", labelsize=10, colors="#c0392b")

# Annotate key points on bars
for yr, label in [(2013, "3,641"), (2020, "1,781"), (2025, "2,835")]:
    v = y(yr, "ped_injured")
    ax.text(yr, v + 90, label, ha="center", fontsize=11, fontweight="bold",
            color="#1a3a52")

ax.text(2020, 900, "pandemic\nyear", ha="center", fontsize=9, color="#667788",
        style="italic")

ax.set_title(
    "Brooklyn pedestrians: fewer injuries than 2013,\n"
    "but injuries have risen four years in a row",
    fontsize=15, fontweight="bold", color="#12293d", loc="left", pad=14)

ax.text(0, 1.02,
        "Police-reported crashes in Brooklyn, by year, 2013–2025",
        transform=ax.transAxes, fontsize=11, color="#556677")

# Legend
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
handles = [
    Patch(facecolor="#7fa8c9", label="Pedestrians injured (left axis)"),
    Line2D([0], [0], color="#c0392b", marker="o", markersize=5, lw=2,
           label="Pedestrians killed (right axis)"),
]
ax.legend(handles=handles, loc="upper right", frameon=False, fontsize=10)

fig.text(0.01, 0.01,
         "Source: NYPD motor vehicle collisions (crashes.parquet). 2026 excluded (partial year). "
         "Counts cover crashes with borough = Brooklyn.",
         fontsize=8.5, color="#778899")

fig.tight_layout(rect=[0, 0.03, 1, 1])
fig.savefig("out/initial.png", bbox_inches="tight")
print("\nSaved out/initial.png and out/values.csv")
