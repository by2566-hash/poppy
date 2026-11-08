from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd

DATA = "data/crashes.parquet"
OUT = Path("out")
OUT.mkdir(exist_ok=True)

con = duckdb.connect()
annual = con.execute(f"""
    SELECT YEAR(crash_date) AS year,
           SUM(number_of_pedestrians_injured) AS pedestrians_injured,
           SUM(number_of_pedestrians_killed) AS pedestrians_killed,
           COUNT(*) FILTER (
               WHERE number_of_pedestrians_injured > 0
                  OR number_of_pedestrians_killed > 0
           ) AS crashes_with_pedestrian_harm
    FROM read_parquet('{DATA}')
    WHERE UPPER(TRIM(borough)) = 'BROOKLYN'
      AND crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY YEAR(crash_date)
    ORDER BY year
""").df()

expected_years = list(range(2013, 2026))
if annual["year"].astype(int).tolist() != expected_years:
    raise ValueError("The planned complete-year series is missing one or more years")

annual["pedestrians_injured"] = annual["pedestrians_injured"].astype("int64")
annual["pedestrians_killed"] = annual["pedestrians_killed"].astype("int64")
annual["crashes_with_pedestrian_harm"] = annual["crashes_with_pedestrian_harm"].astype("int64")
annual["pedestrian_casualties"] = annual["pedestrians_injured"] + annual["pedestrians_killed"]

# Option 1: annual pedestrian casualty counts, split into injuries and deaths.
values_1 = annual[["year", "pedestrians_injured", "pedestrians_killed", "pedestrian_casualties"]]
values_1.to_csv(OUT / "values_1.csv", index=False)
fig, ax = plt.subplots(figsize=(11, 6.4))
ax.bar(annual.year, annual.pedestrians_injured, color="#277DA1", label="Pedestrians injured")
ax.bar(annual.year, annual.pedestrians_killed, bottom=annual.pedestrians_injured,
       color="#F8961E", label="Pedestrians killed")
ax.set_title("Pedestrians injured and killed in Brooklyn motor-vehicle crashes, 2013–2025",
             loc="left", fontsize=16, fontweight="bold", pad=30)
ax.text(0, 1.015,
        "Annual counts in police-reported crashes; not adjusted for walking exposure. Borough-missing records excluded; 2026 partial.",
        transform=ax.transAxes, fontsize=9, color="#444444", va="bottom")
ax.set_ylabel("Pedestrians recorded injured or killed")
ax.set_xlabel("Crash year")
ax.set_xticks(annual.year)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", color="#D9DEE3", linewidth=0.8)
ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, ncol=2, loc="upper right")
fig.tight_layout()
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Option 2: one count for each Brooklyn crash row with any pedestrian harm.
values_2 = annual[["year", "crashes_with_pedestrian_harm"]].rename(
    columns={"crashes_with_pedestrian_harm": "crashes_with_pedestrian_injury_or_death"}
)
values_2.to_csv(OUT / "values_2.csv", index=False)
fig, ax = plt.subplots(figsize=(11, 6.4))
ax.plot(annual.year, annual.crashes_with_pedestrian_harm,
        color="#277DA1", linewidth=2.8, marker="o", markersize=6)
ax.set_title("Brooklyn crashes involving pedestrian injury or death, 2013–2025",
             loc="left", fontsize=16, fontweight="bold", pad=30)
ax.text(0, 1.015,
        "Annual crash counts (each crash counted once); not adjusted for walking exposure. Borough-missing records excluded; 2026 partial.",
        transform=ax.transAxes, fontsize=9, color="#444444", va="bottom")
ax.set_ylabel("Police-reported crashes with pedestrian injury or death")
ax.set_xlabel("Crash year")
ax.set_xticks(annual.year)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", color="#D9DEE3", linewidth=0.8)
ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)
