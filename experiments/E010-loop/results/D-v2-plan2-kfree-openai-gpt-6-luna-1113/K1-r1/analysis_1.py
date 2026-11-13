import duckdb
import matplotlib.pyplot as plt
import pandas as pd


con = duckdb.connect()
values = con.execute(
    """SELECT year(crash_date) AS year,
              sum(number_of_pedestrians_killed)::BIGINT AS pedestrians_killed
       FROM read_parquet('./data/crashes.parquet')
       WHERE crash_date >= DATE '2013-01-01'
         AND crash_date < DATE '2026-01-01'
       GROUP BY year(crash_date)
       ORDER BY year"""
).df()
values["year"] = values["year"].astype(int)
values["pedestrians_killed"] = values["pedestrians_killed"].astype(int)
values.to_csv("./out/values_1.csv", index=False)

fig, ax = plt.subplots(figsize=(12, 6.8))
bars = ax.bar(values["year"].astype(str), values["pedestrians_killed"], color="#3274A1")
ax.bar_label(bars, fmt="{:,.0f}", padding=3, fontsize=9)
ax.set_title("Pedestrians killed in NYC motor-vehicle crashes each year, 2013–2025", pad=34, fontsize=15)
ax.text(
    0.5, 1.015,
    "Annual sum of pedestrian deaths recorded per police-reported crash; counts are not exposure-adjusted",
    transform=ax.transAxes, ha="center", va="bottom", fontsize=9,
)
ax.set_xlabel("Crash year")
ax.set_ylabel("Pedestrians killed (recorded count)")
ax.set_ylim(0, values["pedestrians_killed"].max() * 1.13)
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig("./out/option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)
