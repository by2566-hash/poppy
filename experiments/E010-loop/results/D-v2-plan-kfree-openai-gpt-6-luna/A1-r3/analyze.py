import csv
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
YEARS = list(range(2013, 2026))


def annual_sums(columns):
    con = duckdb.connect()
    source = str(DATA).replace("'", "''")
    aggregation = ",\n".join(f"sum({column}) AS {column}" for column in columns)
    result = con.execute(
        f"""
        SELECT year(crash_date) AS year, {aggregation}
        FROM read_parquet('{source}')
        WHERE lower(trim(coalesce(borough, ''))) = 'brooklyn'
          AND crash_date >= DATE '2013-01-01'
          AND crash_date < DATE '2026-01-01'
        GROUP BY year(crash_date)
        ORDER BY year
        """
    ).df()
    con.close()
    return result.set_index("year").reindex(YEARS, fill_value=0).reset_index()


casualties = annual_sums([
    "number_of_pedestrians_injured",
    "number_of_pedestrians_killed",
])
casualties["pedestrians_injured_or_killed"] = (
    casualties["number_of_pedestrians_injured"] + casualties["number_of_pedestrians_killed"]
)
casualties[["year", "number_of_pedestrians_injured", "number_of_pedestrians_killed", "pedestrians_injured_or_killed"]].to_csv(
    OUT / "values_1.csv", index=False
)

deaths = casualties[["year", "number_of_pedestrians_killed"]].rename(
    columns={"number_of_pedestrians_killed": "pedestrians_killed"}
)
deaths.to_csv(OUT / "values_2.csv", index=False)


def line_chart():
    fig, ax = plt.subplots(figsize=(10.8, 6.4))
    x = casualties["year"].astype(int)
    y = casualties["pedestrians_injured_or_killed"]
    ax.plot(x, y, color="#155E75", linewidth=2.7, marker="o", markersize=5.2)
    ax.fill_between(x, y, color="#155E75", alpha=0.10)
    ax.annotate(f"{int(y.iloc[0]):,}", (x.iloc[0], y.iloc[0]), xytext=(7, 9), textcoords="offset points", fontsize=9)
    ax.annotate(f"{int(y.iloc[-1]):,}", (x.iloc[-1], y.iloc[-1]), xytext=(-34, 9), textcoords="offset points", fontsize=9)
    ax.set_title("Pedestrians injured or killed in Brooklyn crashes, 2013–2025", loc="left", fontsize=15, weight="bold", pad=28)
    ax.text(0, 1.015, "Annual reported casualty count  •  Not adjusted for walking exposure", transform=ax.transAxes, fontsize=9.5, color="#4B5563")
    ax.set_ylabel("Pedestrians injured or killed")
    ax.set_xlabel("Crash year")
    ax.set_ylim(bottom=0)
    ax.set_xticks(YEARS)
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", color="#D1D5DB", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def death_chart():
    fig, ax = plt.subplots(figsize=(10.8, 6.4))
    x = deaths["year"].astype(int)
    y = deaths["pedestrians_killed"]
    ax.bar(x, y, color="#B45309", width=0.68)
    ax.bar_label(ax.containers[0], padding=3, fontsize=8)
    ax.set_title("Pedestrians killed in Brooklyn crashes, 2013–2025", loc="left", fontsize=15, weight="bold", pad=28)
    ax.text(0, 1.015, "Annual reported deaths  •  Not adjusted for walking exposure", transform=ax.transAxes, fontsize=9.5, color="#4B5563")
    ax.set_ylabel("Pedestrians killed")
    ax.set_xlabel("Crash year")
    ax.set_xticks(YEARS)
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", color="#D1D5DB", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


line_chart()
death_chart()
