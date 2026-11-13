import json
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import StrMethodFormatter


OUT = Path("out")
DATA = 'read_parquet("data/crashes.parquet")'
con = duckdb.connect()

specs = {
    1: {
        "column": "number_of_pedestrians_injured",
        "metric_column": "pedestrians_injured",
        "title": "Pedestrians injured in Brooklyn crashes, 2013–2025",
        "ylabel": "Pedestrians reported injured",
        "color": "#176B87",
        "query": "sum(number_of_pedestrians_injured)::BIGINT",
    },
    2: {
        "column": "number_of_pedestrians_killed",
        "metric_column": "pedestrians_killed",
        "title": "Pedestrians killed in Brooklyn crashes, 2013–2025",
        "ylabel": "Pedestrians reported killed",
        "color": "#B33A3A",
        "query": "sum(number_of_pedestrians_killed)::BIGINT",
    },
    3: {
        "column": "pedestrian_casualty_crashes",
        "metric_column": "crashes_with_pedestrian_casualty",
        "title": "Brooklyn crashes with a pedestrian injured or killed, 2013–2025",
        "ylabel": "Crashes with a pedestrian injured or killed",
        "color": "#6A5A9A",
        "query": "count(*) FILTER (WHERE number_of_pedestrians_injured > 0 OR number_of_pedestrians_killed > 0)::BIGINT",
    },
}

for option_id, spec in specs.items():
    frame = con.execute(
        f"""
        SELECT year(crash_date)::INT AS year,
               {spec['query']} AS {spec['metric_column']}
        FROM {DATA}
        WHERE upper(trim(borough)) = 'BROOKLYN'
          AND crash_date >= DATE '2013-01-01'
          AND crash_date < DATE '2026-01-01'
          AND {spec['column'] if option_id != 3 else 'number_of_pedestrians_injured'} IS NOT NULL
          {"AND number_of_pedestrians_killed IS NOT NULL" if option_id == 3 else ""}
        GROUP BY year
        ORDER BY year
        """
    ).df()
    frame["year"] = frame["year"].astype(int)
    frame = (
        frame.set_index("year")
        .reindex(range(2013, 2026), fill_value=0)
        .rename_axis("year")
        .reset_index()
    )
    frame.to_csv(OUT / f"values_{option_id}.csv", index=False)

    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    fig.patch.set_facecolor("#FAF9F6")
    ax.set_facecolor("#FAF9F6")
    ax.plot(
        frame["year"],
        frame[spec["metric_column"]],
        color=spec["color"],
        linewidth=3,
        marker="o",
        markersize=6,
    )
    ax.set_title(spec["title"], loc="left", fontsize=17, fontweight="bold", pad=20)
    ax.text(
        0,
        1.015,
        "Annual count from police-reported motor vehicle crashes · Brooklyn borough label",
        transform=ax.transAxes,
        fontsize=10,
        color="#555555",
        va="bottom",
    )
    ax.set_xlabel("Crash year", fontsize=11)
    ax.set_ylabel(spec["ylabel"], fontsize=11)
    ax.set_xticks(range(2013, 2026, 2))
    ax.set_xlim(2012.7, 2025.3)
    ax.set_ylim(bottom=0)
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    ax.grid(axis="y", color="#D9D6D0", linewidth=0.8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#999999")
    ax.tick_params(axis="y", length=0, pad=7)
    ax.tick_params(axis="x", length=0, pad=7)
    ax.text(
        0,
        -0.22,
        "Counts are not adjusted for pedestrian exposure; 2026 is partial and excluded. "
        "Crashes with missing borough cannot be assigned to Brooklyn.",
        transform=ax.transAxes,
        fontsize=9,
        color="#555555",
        va="top",
    )
    fig.subplots_adjust(left=0.11, right=0.98, top=0.82, bottom=0.25)
    fig.savefig(OUT / f"option_{option_id}.png", dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)

print("Saved annual value tables and charts for options 1–3")
