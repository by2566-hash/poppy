from pathlib import Path

import duckdb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter, PercentFormatter


ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
DATA = str(ROOT / "data" / "crashes.parquet").replace("'", "''")

con = duckdb.connect()
query = f"""
    SELECT
        year(crash_date) AS year,
        sum(number_of_pedestrians_injured) AS pedestrians_injured,
        sum(number_of_pedestrians_killed) AS pedestrians_killed,
        count(*) AS brooklyn_crash_reports,
        count(*) FILTER (
            WHERE number_of_pedestrians_injured > 0
               OR number_of_pedestrians_killed > 0
        ) AS reports_with_pedestrian_casualty
    FROM read_parquet('{DATA}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
      AND upper(trim(borough)) = 'BROOKLYN'
      AND number_of_pedestrians_injured IS NOT NULL
      AND number_of_pedestrians_killed IS NOT NULL
      AND number_of_pedestrians_injured >= 0
      AND number_of_pedestrians_killed >= 0
    GROUP BY year(crash_date)
    ORDER BY year
"""
annual = con.execute(query).fetchdf()
annual["year"] = annual["year"].astype(int)
annual["pedestrian_casualties"] = annual["pedestrians_injured"] + annual["pedestrians_killed"]
annual["share_reports_with_pedestrian_casualty_pct"] = (
    annual["reports_with_pedestrian_casualty"] / annual["brooklyn_crash_reports"] * 100
)

options = {
    1: {
        "value": "pedestrian_casualties",
        "title": "Brooklyn pedestrian casualties in reported crashes, 2013–2025",
        "ylabel": "Pedestrians injured or killed (people)",
        "subtitle": "Police-reported crash totals; not adjusted for walking exposure",
        "percent": False,
    },
    2: {
        "value": "pedestrians_killed",
        "title": "Pedestrian deaths in reported Brooklyn crashes, 2013–2025",
        "ylabel": "Pedestrians killed (people)",
        "subtitle": "Police-reported deaths; not a rate per walking exposure",
        "percent": False,
    },
    3: {
        "value": "share_reports_with_pedestrian_casualty_pct",
        "title": "Brooklyn crash reports with a pedestrian casualty, 2013–2025",
        "ylabel": "Share of Brooklyn crash reports",
        "subtitle": "Records with ≥1 pedestrian injured or killed; not risk per walking exposure",
        "percent": True,
    },
}

for option_id, spec in options.items():
    value_column = spec["value"]
    output_columns = ["year", value_column, "brooklyn_crash_reports"]
    if option_id == 1:
        output_columns = [
            "year", "pedestrians_injured", "pedestrians_killed",
            "pedestrian_casualties", "brooklyn_crash_reports",
        ]
    elif option_id == 3:
        output_columns = [
            "year", "reports_with_pedestrian_casualty", "brooklyn_crash_reports",
            "share_reports_with_pedestrian_casualty_pct",
        ]
    plotted = annual[output_columns].copy()
    plotted.to_csv(OUT / f"values_{option_id}.csv", index=False, float_format="%.4f")

    fig, ax = plt.subplots(figsize=(10.5, 5.8), layout="constrained")
    y = annual[value_column]
    ax.plot(annual["year"], y, color="#176B87", marker="o", linewidth=2.8, markersize=6)
    ax.set_title(spec["title"], loc="left", fontsize=16, fontweight="bold", pad=28)
    ax.text(0, 1.015, spec["subtitle"], transform=ax.transAxes,
            ha="left", va="bottom", fontsize=10, color="#4b5563")
    ax.set_xlabel("Crash year")
    ax.set_ylabel(spec["ylabel"])
    ax.set_xticks(annual["year"])
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", color="#d7dee5", linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if spec["percent"]:
        ax.yaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))
    else:
        ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:,.0f}"))
    fig.savefig(OUT / f"option_{option_id}.png", dpi=180, facecolor="white")
    plt.close(fig)
