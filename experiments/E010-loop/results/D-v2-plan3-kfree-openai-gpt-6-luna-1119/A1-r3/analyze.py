from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
PARQUET = ROOT / "data" / "crashes.parquet"
con = duckdb.connect()

casualties = con.execute(
    """
    SELECT year(crash_date) AS year,
           count(*) AS brooklyn_crash_rows,
           sum(number_of_pedestrians_injured) AS pedestrians_injured,
           sum(number_of_pedestrians_killed) AS pedestrians_killed,
           sum(number_of_pedestrians_injured + number_of_pedestrians_killed) AS pedestrian_casualties
    FROM read_parquet(?)
    WHERE upper(trim(borough)) = 'BROOKLYN'
      AND crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
      AND number_of_pedestrians_injured IS NOT NULL
      AND number_of_pedestrians_killed IS NOT NULL
    GROUP BY year(crash_date)
    ORDER BY year
    """,
    [str(PARQUET)],
).df()

deaths = con.execute(
    """
    SELECT year(crash_date) AS year,
           count(*) AS brooklyn_crash_rows,
           sum(number_of_pedestrians_killed) AS pedestrian_deaths
    FROM read_parquet(?)
    WHERE upper(trim(borough)) = 'BROOKLYN'
      AND crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
      AND number_of_pedestrians_killed IS NOT NULL
    GROUP BY year(crash_date)
    ORDER BY year
    """,
    [str(PARQUET)],
).df()
con.close()

expected_years = list(range(2013, 2026))
if casualties["year"].tolist() != expected_years or deaths["year"].tolist() != expected_years:
    raise ValueError("Analysis did not return every complete year from 2013 through 2025")

casualties.to_csv(OUT / "values_1.csv", index=False)
deaths.to_csv(OUT / "values_2.csv", index=False)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titleweight": "bold",
})

fig, ax = plt.subplots(figsize=(10.5, 6.1), constrained_layout=True)
ax.plot(
    casualties["year"], casualties["pedestrian_casualties"],
    color="#176B87", linewidth=2.8, marker="o", markersize=6,
)
ax.set_title("Pedestrians injured or killed in Brooklyn crashes, 2013–2025", loc="left", fontsize=15, pad=32)
ax.text(
    0, 1.025,
    "Annual count in police-reported crashes · Counts are not adjusted for walking exposure",
    transform=ax.transAxes, fontsize=9.5, color="#444444", va="bottom",
)
ax.set_ylabel("Pedestrians injured or killed")
ax.set_xlabel("Crash year")
ax.set_xticks(expected_years)
ax.tick_params(axis="x", rotation=0)
ax.grid(axis="y", color="#D9E0E3", linewidth=0.8)
ax.set_axisbelow(True)
for year, value in ((casualties.iloc[0]["year"], casualties.iloc[0]["pedestrian_casualties"]),
                    (casualties.iloc[-1]["year"], casualties.iloc[-1]["pedestrian_casualties"])):
    ax.annotate(f"{int(value):,}", (year, value), xytext=(0, 10), textcoords="offset points",
                ha="center", fontsize=9, color="#123F50", fontweight="bold")
fig.savefig(OUT / "option_1.png", dpi=180, facecolor="white")
plt.close(fig)

fig, ax = plt.subplots(figsize=(10.5, 6.1), constrained_layout=True)
bars = ax.bar(deaths["year"], deaths["pedestrian_deaths"], color="#C6553D", width=0.72)
ax.set_title("Pedestrians killed in Brooklyn crashes, 2013–2025", loc="left", fontsize=15, pad=32)
ax.text(
    0, 1.025,
    "Annual death count in police-reported crashes · Counts are not adjusted for walking exposure",
    transform=ax.transAxes, fontsize=9.5, color="#444444", va="bottom",
)
ax.set_ylabel("Pedestrians killed")
ax.set_xlabel("Crash year")
ax.set_xticks(expected_years)
ax.grid(axis="y", color="#D9E0E3", linewidth=0.8)
ax.set_axisbelow(True)
ax.bar_label(bars, fmt="{:,.0f}", padding=3, fontsize=8)
fig.savefig(OUT / "option_2.png", dpi=180, facecolor="white")
plt.close(fig)
