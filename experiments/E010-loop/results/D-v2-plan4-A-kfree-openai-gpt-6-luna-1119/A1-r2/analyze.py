import json
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
PARQUET = ROOT / "data" / "crashes.parquet"

con = duckdb.connect()
parquet_literal = str(PARQUET).replace("'", "''")
con.execute(
    "CREATE VIEW crashes AS SELECT crash_date, borough, number_of_pedestrians_injured, number_of_pedestrians_killed FROM read_parquet('"
    + parquet_literal
    + "')"
)

for plan_id in (1, 2):
    plan = json.loads((OUT / f"plan_{plan_id}.json").read_text())["final_plan"]
    year_start, year_end = 2013, 2025
    year_clause = f"year(crash_date) BETWEEN {year_start} AND {year_end}"
    borough_clause = "upper(trim(borough)) = 'BROOKLYN'"

    if plan_id == 1:
        query = f"""
        SELECT year(crash_date) AS year,
               sum(number_of_pedestrians_injured) AS pedestrian_injuries,
               sum(number_of_pedestrians_killed) AS pedestrian_deaths,
               sum(number_of_pedestrians_injured + number_of_pedestrians_killed) AS pedestrian_casualties
        FROM crashes
        WHERE {borough_clause} AND {year_clause}
          AND number_of_pedestrians_injured IS NOT NULL
          AND number_of_pedestrians_killed IS NOT NULL
        GROUP BY year ORDER BY year
        """
        title = "Recorded pedestrian casualties in Brooklyn, 2013–2025"
        y_label = "Recorded pedestrian injuries + deaths"
        chart_type = "line chart"
        value_column = "pedestrian_casualties"
        color = "#176B87"
        chart_file = OUT / "option_1.png"
    else:
        query = f"""
        SELECT year(crash_date) AS year,
               sum(number_of_pedestrians_killed) AS pedestrian_deaths
        FROM crashes
        WHERE {borough_clause} AND {year_clause}
          AND number_of_pedestrians_killed IS NOT NULL
        GROUP BY year ORDER BY year
        """
        title = "Recorded pedestrian deaths in Brooklyn, 2013–2025"
        y_label = "Recorded pedestrian deaths"
        chart_type = "bar chart"
        value_column = "pedestrian_deaths"
        color = "#B24C3D"
        chart_file = OUT / "option_2.png"

    frame = con.execute(query).fetchdf()
    expected_years = list(range(year_start, year_end + 1))
    if frame["year"].astype(int).tolist() != expected_years:
        raise ValueError(f"Plan {plan_id} does not have exactly one result for every retained year")
    frame["year"] = frame["year"].astype(int)
    frame.to_csv(OUT / f"values_{plan_id}.csv", index=False)

    fig, ax = plt.subplots(figsize=(10.4, 5.8), layout="constrained")
    if plan_id == 1:
        ax.plot(frame["year"], frame[value_column], color=color, linewidth=2.8, marker="o", markersize=5.5)
        ax.fill_between(frame["year"], frame[value_column], color=color, alpha=0.10)
    else:
        bars = ax.bar(frame["year"], frame[value_column], color=color, width=0.68)
        ax.bar_label(bars, padding=3, fontsize=8, color="#4b5563")

    ax.set_title(title, loc="left", fontsize=17, weight="bold", pad=22)
    ax.text(
        0,
        1.035,
        "Source: NYC police-reported crash records | Not adjusted for pedestrian exposure; partial 2026 omitted.",
        transform=ax.transAxes,
        fontsize=9.5,
        color="#555555",
    )
    ax.set_xlabel("Crash year", fontsize=10)
    ax.set_ylabel(y_label, fontsize=10)
    ax.set_xticks(expected_years)
    ax.tick_params(axis="x", rotation=45, labelsize=8.5)
    ax.tick_params(axis="y", labelsize=9)
    ax.grid(axis="y", color="#d9dfe3", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#aab2b7")
    ax.spines["bottom"].set_color("#aab2b7")
    fig.savefig(chart_file, dpi=180, facecolor="white")
    plt.close(fig)

con.close()
