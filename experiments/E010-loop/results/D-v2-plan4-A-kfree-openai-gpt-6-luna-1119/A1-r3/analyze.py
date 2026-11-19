from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


DATA = Path(__file__).resolve().parents[1] / "data" / "crashes.parquet"
OUT = Path(__file__).resolve().parent

con = duckdb.connect()
con.from_parquet(str(DATA)).create_view("crashes")

annual = con.execute(
    """
    SELECT YEAR(crash_date) AS year,
           SUM(number_of_pedestrians_injured)::BIGINT AS pedestrian_injuries,
           SUM(number_of_pedestrians_killed)::BIGINT AS pedestrian_deaths
    FROM crashes
    WHERE LOWER(TRIM(COALESCE(borough, ''))) = 'brooklyn'
      AND crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY YEAR(crash_date)
    ORDER BY year
    """
).fetchdf()
annual["pedestrian_casualties"] = (
    annual["pedestrian_injuries"] + annual["pedestrian_deaths"]
)
annual.to_csv(OUT / "values_1.csv", index=False)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titleweight": "bold",
})

fig, ax = plt.subplots(figsize=(10, 5.8))
ax.plot(
    annual["year"], annual["pedestrian_casualties"],
    color="#176B87", linewidth=2.8, marker="o", markersize=5.5,
)
ax.fill_between(
    annual["year"], annual["pedestrian_casualties"],
    color="#176B87", alpha=0.10,
)
ax.set_title("Brooklyn: reported pedestrian casualties in crashes", loc="left", fontsize=17, pad=24)
ax.text(
    0, 1.025, "Annual count of pedestrian injuries plus deaths | full years 2013–2025",
    transform=ax.transAxes, ha="left", va="bottom", fontsize=10.5, color="#4b5563",
)
ax.set_ylabel("Pedestrian injury and death outcomes (count)")
ax.set_xlabel("Year of crash")
ax.set_xticks(annual["year"])
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", color="#d9e0e5", linewidth=0.8)
ax.set_axisbelow(True)
fig.text(
    0.01, 0.01,
    "Police-reported crash counts; not adjusted for walking exposure. 2026 is omitted as partial.",
    fontsize=9, color="#4b5563",
)
fig.tight_layout(rect=(0, 0.045, 1, 1))
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

deaths = annual[["year", "pedestrian_deaths"]].copy()
deaths.to_csv(OUT / "values_2.csv", index=False)

fig, ax = plt.subplots(figsize=(10, 5.8))
ax.bar(deaths["year"], deaths["pedestrian_deaths"], color="#B2473E", width=0.72)
ax.set_title("Brooklyn: pedestrians killed in reported crashes", loc="left", fontsize=17, pad=24)
ax.text(
    0, 1.025, "Annual pedestrian death count | full years 2013–2025",
    transform=ax.transAxes, ha="left", va="bottom", fontsize=10.5, color="#4b5563",
)
ax.set_ylabel("Pedestrians killed (count)")
ax.set_xlabel("Year of crash")
ax.set_xticks(deaths["year"])
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", color="#d9e0e5", linewidth=0.8)
ax.set_axisbelow(True)
fig.text(
    0.01, 0.01,
    "Police-reported deaths; not adjusted for walking exposure. 2026 is omitted as partial.",
    fontsize=9, color="#4b5563",
)
fig.tight_layout(rect=(0, 0.045, 1, 1))
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)

print(f"Wrote annual results for {len(annual)} full years.")
