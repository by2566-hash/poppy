from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
DATA = str(ROOT / "data" / "crashes.parquet")
FIRST_YEAR = 2013
LAST_YEAR = 2025

db = duckdb.connect()
years_filter = f"crash_date >= DATE '{FIRST_YEAR}-01-01' AND crash_date < DATE '{LAST_YEAR + 1}-01-01'"

# Option 1: annual total of reported pedestrians injured or killed.
casualties = db.execute(
    f"""
    SELECT year(crash_date) AS year,
           sum(number_of_pedestrians_injured) AS pedestrians_injured,
           sum(number_of_pedestrians_killed) AS pedestrians_killed,
           sum(number_of_pedestrians_injured + number_of_pedestrians_killed) AS pedestrian_casualties
    FROM read_parquet(?)
    WHERE borough = 'BROOKLYN' AND {years_filter}
    GROUP BY year ORDER BY year
    """,
    [DATA],
).df()
casualties[["year", "pedestrians_injured", "pedestrians_killed", "pedestrian_casualties"]] = casualties[
    ["year", "pedestrians_injured", "pedestrians_killed", "pedestrian_casualties"]
].astype(int)
casualties.to_csv(OUT / "values_1.csv", index=False)

plt.style.use("seaborn-v0_8-whitegrid")
fig, ax = plt.subplots(figsize=(10.5, 5.8))
ax.plot(casualties["year"], casualties["pedestrian_casualties"], color="#c43c39", linewidth=2.8, marker="o", markersize=5)
ax.set_title("Pedestrians injured or killed in Brooklyn crashes, 2013–2025", loc="left", fontsize=16, fontweight="bold", pad=28)
ax.text(0, 1.025, "Annual reported casualty count · counts are not adjusted for walking exposure", transform=ax.transAxes, fontsize=10.5, color="#444444")
ax.set_xlabel("Crash year")
ax.set_ylabel("Pedestrians injured or killed")
ax.set_ylim(bottom=0)
ax.set_xticks(casualties["year"].astype(int))
ax.tick_params(axis="x", rotation=45)
ax.spines[["top", "right"]].set_visible(False)
fig.text(0.01, 0.01, "Source: NYC police-reported motor vehicle crashes. 2026 excluded because the file covers only Jan 1–Jun 11, 2026.", fontsize=8.8, color="#555555")
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Option 2: proportion of Brooklyn crash records in each year with a casualty.
crash_share = db.execute(
    f"""
    SELECT year(crash_date) AS year,
           count(*) AS brooklyn_crash_records,
           count(*) FILTER (WHERE number_of_pedestrians_injured > 0
                             OR number_of_pedestrians_killed > 0) AS crashes_with_pedestrian_casualty
    FROM read_parquet(?)
    WHERE borough = 'BROOKLYN' AND {years_filter}
    GROUP BY year ORDER BY year
    """,
    [DATA],
).df()
crash_share["percent_of_crash_records"] = 100 * crash_share["crashes_with_pedestrian_casualty"] / crash_share["brooklyn_crash_records"]
crash_share["year"] = crash_share["year"].astype(int)
crash_share.to_csv(OUT / "values_2.csv", index=False)

fig, ax = plt.subplots(figsize=(10.5, 5.8))
ax.plot(crash_share["year"], crash_share["percent_of_crash_records"], color="#176b87", linewidth=2.8, marker="o", markersize=5)
ax.set_title("Brooklyn crash records with a pedestrian injury or death, 2013–2025", loc="left", fontsize=15, fontweight="bold", pad=28)
ax.text(0, 1.025, "Annual share of all Brooklyn crash records · one or more pedestrians injured or killed", transform=ax.transAxes, fontsize=10.5, color="#444444")
ax.set_xlabel("Crash year")
ax.set_ylabel("Crash records with pedestrian casualty (%)")
ax.set_ylim(bottom=0)
ax.set_xticks(crash_share["year"].astype(int))
ax.tick_params(axis="x", rotation=45)
ax.spines[["top", "right"]].set_visible(False)
fig.text(0.01, 0.01, "Source: NYC police-reported motor vehicle crashes. Not a rate per pedestrian trip or distance; 2026 is partial and excluded.", fontsize=8.8, color="#555555")
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Option 3: a separate count of the most severe recorded pedestrian outcome.
deaths = db.execute(
    f"""
    SELECT year(crash_date) AS year,
           sum(number_of_pedestrians_killed) AS pedestrians_killed
    FROM read_parquet(?)
    WHERE borough = 'BROOKLYN' AND {years_filter}
    GROUP BY year ORDER BY year
    """,
    [DATA],
).df()
deaths[["year", "pedestrians_killed"]] = deaths[["year", "pedestrians_killed"]].astype(int)
deaths.to_csv(OUT / "values_3.csv", index=False)

fig, ax = plt.subplots(figsize=(10.5, 5.8))
ax.bar(deaths["year"].astype(int), deaths["pedestrians_killed"], color="#593b7a", width=0.72)
ax.set_title("Pedestrians killed in Brooklyn crashes, 2013–2025", loc="left", fontsize=16, fontweight="bold", pad=28)
ax.text(0, 1.025, "Annual count of reported pedestrian deaths", transform=ax.transAxes, fontsize=10.5, color="#444444")
ax.set_xlabel("Crash year")
ax.set_ylabel("Pedestrians killed")
ax.set_xticks(deaths["year"].astype(int))
ax.tick_params(axis="x", rotation=45)
ax.spines[["top", "right"]].set_visible(False)
fig.text(0.01, 0.01, "Source: NYC police-reported motor vehicle crashes. Counts do not account for walking exposure; 2026 is partial and excluded.", fontsize=8.8, color="#555555")
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(OUT / "option_3.png", dpi=180, bbox_inches="tight")
plt.close(fig)

print("Saved plotted values and charts for 2013-2025.")
for option_id, frame in ((1, casualties), (2, crash_share), (3, deaths)):
    print(f"Option {option_id}:\n{frame.to_string(index=False)}")
