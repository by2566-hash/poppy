import duckdb
import matplotlib.pyplot as plt
import pandas as pd

con = duckdb.connect()
data = con.execute(
    """SELECT YEAR(crash_date) AS year,
              SUM(number_of_pedestrians_killed) AS pedestrians_killed
       FROM read_parquet('data/crashes.parquet')
       WHERE crash_date >= DATE '2013-01-01'
         AND crash_date < DATE '2026-01-01'
       GROUP BY year
       ORDER BY year"""
).df()
con.close()
data["pedestrians_killed"] = data["pedestrians_killed"].astype("int64")
data.to_csv("out/values_1.csv", index=False)

fig, ax = plt.subplots(figsize=(10, 5.7))
ax.bar(data["year"].astype(str), data["pedestrians_killed"], color="#176B87")
ax.set_title("Pedestrians killed per year in NYC police-reported motor vehicle crashes", fontsize=13, pad=20)
ax.text(
    0.5,
    1.015,
    "Annual sum of reported pedestrian deaths; full calendar years 2013–2025",
    transform=ax.transAxes,
    ha="center",
    va="bottom",
    fontsize=9,
    color="#444444",
)
ax.set_xlabel("Crash year")
ax.set_ylabel("Pedestrians killed (count)")
ax.grid(axis="y", alpha=0.22)
ax.set_axisbelow(True)
fig.text(
    0.5,
    0.01,
    "Limitation: counts reflect police-reported crashes and are not adjusted for annual crash-report volume.",
    ha="center",
    fontsize=8.5,
    color="#444444",
)
fig.tight_layout(rect=(0, 0.04, 1, 0.95))
fig.savefig("out/option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)
