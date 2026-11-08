from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


OUT = Path("out")
source = "data/crashes.parquet"
annual = duckdb.connect().execute(
    f"""
    SELECT YEAR(crash_date) AS year,
           SUM(number_of_pedestrians_killed) AS pedestrians_killed
    FROM read_parquet('{source}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY YEAR(crash_date)
    ORDER BY year
    """
).fetchdf()
annual["year"] = annual["year"].astype(int)
annual["pedestrians_killed"] = annual["pedestrians_killed"].astype(int)

title = "Pedestrians killed in NYC police-reported motor vehicle crashes"
subtitle = (
    "By crash year, 2013–2025 · Recorded counts; year endpoints are present, "
    "but within-year completeness and reporting accuracy are not independently verified"
)

for option_id, chart_type in [(1, "bar"), (2, "line")]:
    values = annual.copy()
    values.to_csv(OUT / f"values_{option_id}.csv", index=False)

    fig, ax = plt.subplots(figsize=(12, 6.5))
    if chart_type == "bar":
        bars = ax.bar(values["year"], values["pedestrians_killed"], color="#176B87", width=0.72)
        ax.bar_label(bars, fmt="{:,.0f}", padding=3, fontsize=8)
    else:
        ax.plot(
            values["year"], values["pedestrians_killed"],
            color="#176B87", marker="o", linewidth=2.5, markersize=6,
        )
        for year, count in zip(values["year"], values["pedestrians_killed"]):
            ax.annotate(f"{count:,}", (year, count), xytext=(0, 8),
                        textcoords="offset points", ha="center", fontsize=8)
    ax.set_title(title, loc="left", fontsize=15, weight="bold", pad=30)
    ax.text(0, 1.015, subtitle, transform=ax.transAxes, fontsize=9, color="#555555", va="bottom")
    ax.set_xlabel("Crash year")
    ax.set_ylabel("Pedestrians killed (people)")
    ax.set_xticks(values["year"])
    ax.set_xlim(2012.4, 2025.6)
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", color="#D9E0E3", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / f"option_{option_id}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
