from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"


def annual_data(columns):
    con = duckdb.connect()
    sums = ", ".join(f"SUM({column}) AS {column}" for column in columns)
    result = con.execute(
        f"""
        SELECT YEAR(crash_date) AS year, {sums}
        FROM read_parquet('{DATA.as_posix()}')
        WHERE UPPER(TRIM(borough)) = 'BROOKLYN'
          AND crash_date >= DATE '2013-01-01'
          AND crash_date < DATE '2026-01-01'
        GROUP BY YEAR(crash_date)
        ORDER BY year
        """
    ).df()
    con.close()
    return result


def style_axes(ax):
    ax.set_xlabel("Crash year")
    ax.set_xticks(range(2013, 2026))
    ax.set_xticklabels(range(2013, 2026), rotation=45, ha="right")
    ax.grid(axis="y", color="#d9dee5", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#9aa4b2")
    ax.spines["bottom"].set_color("#9aa4b2")
    ax.tick_params(colors="#394150")


# Option 1: annual pedestrian casualties (injured plus killed).
casualties = annual_data([
    "number_of_pedestrians_injured",
    "number_of_pedestrians_killed",
])
casualties["pedestrian_casualties"] = (
    casualties["number_of_pedestrians_injured"]
    + casualties["number_of_pedestrians_killed"]
)
values_1 = casualties.rename(columns={
    "number_of_pedestrians_injured": "pedestrians_injured",
    "number_of_pedestrians_killed": "pedestrians_killed",
})
values_1.to_csv(OUT / "values_1.csv", index=False)

fig, ax = plt.subplots(figsize=(10, 5.8), layout="constrained")
fig.suptitle("Pedestrian casualties in Brooklyn, 2013–2025",
             x=0.08, ha="left", fontsize=18, fontweight="bold", color="#16283f")
ax.set_title("People injured or killed in police-reported crashes · annual counts, not exposure-adjusted rates",
             loc="left", fontsize=10, color="#596579", pad=12)
ax.plot(casualties["year"], casualties["pedestrian_casualties"],
        color="#176b87", linewidth=2.8, marker="o", markersize=5.5)
ax.fill_between(casualties["year"], casualties["pedestrian_casualties"],
                color="#176b87", alpha=0.09)
ax.set_ylabel("Pedestrians injured or killed")
style_axes(ax)
fig.text(0.08, -0.015,
         "Source: NYC police-reported crash records. 2026 is omitted because records end June 11; totals do not account for walking exposure.",
         fontsize=8.5, color="#596579")
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)


# Option 2: annual pedestrian deaths.
deaths = annual_data(["number_of_pedestrians_killed"])
deaths = deaths.rename(columns={"number_of_pedestrians_killed": "pedestrians_killed"})
deaths.to_csv(OUT / "values_2.csv", index=False)

fig, ax = plt.subplots(figsize=(10, 5.8), layout="constrained")
fig.suptitle("Pedestrians killed in Brooklyn, 2013–2025",
             x=0.08, ha="left", fontsize=18, fontweight="bold", color="#16283f")
ax.set_title("Deaths in police-reported crashes · annual counts, not exposure-adjusted rates",
             loc="left", fontsize=10, color="#596579", pad=12)
bars = ax.bar(deaths["year"], deaths["pedestrians_killed"], width=0.72, color="#b5473b")
ax.bar_label(bars, fmt="%.0f", padding=3, fontsize=8, color="#394150")
ax.set_ylabel("Pedestrians killed")
ax.margins(y=0.14)
style_axes(ax)
fig.text(0.08, -0.015,
         "Source: NYC police-reported crash records. 2026 is omitted because records end June 11; totals do not account for walking exposure.",
         fontsize=8.5, color="#596579")
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)
