import csv
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
PARQUET = ROOT / "data" / "crashes.parquet"
con = duckdb.connect()
con.execute("SET threads TO 2")

queries = {
    1: """
        SELECT YEAR(crash_date) AS year,
               SUM(number_of_pedestrians_injured + number_of_pedestrians_killed)::BIGINT AS value
        FROM read_parquet(?)
        WHERE UPPER(TRIM(borough)) = 'BROOKLYN'
          AND crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
          AND number_of_pedestrians_injured IS NOT NULL
          AND number_of_pedestrians_killed IS NOT NULL
        GROUP BY 1 ORDER BY 1
    """,
    2: """
        SELECT YEAR(crash_date) AS year, COUNT(*)::BIGINT AS value
        FROM read_parquet(?)
        WHERE UPPER(TRIM(borough)) = 'BROOKLYN'
          AND crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
          AND number_of_pedestrians_injured IS NOT NULL
          AND number_of_pedestrians_killed IS NOT NULL
          AND number_of_pedestrians_injured + number_of_pedestrians_killed > 0
        GROUP BY 1 ORDER BY 1
    """,
}

palette = {1: "#b5392f", 2: "#176b87"}
for option_id, query in queries.items():
    df = con.execute(query, [str(PARQUET)]).df()
    df["year"] = df["year"].astype(int)
    df["value"] = df["value"].astype(int)
    df.to_csv(OUT / f"values_{option_id}.csv", index=False, quoting=csv.QUOTE_MINIMAL)

    fig, ax = plt.subplots(figsize=(11, 6.5))
    fig.subplots_adjust(left=0.12, right=0.98, top=0.82, bottom=0.16)
    color = palette[option_id]
    if option_id == 1:
        ax.plot(df["year"], df["value"], color=color, linewidth=2.7,
                marker="o", markersize=7)
        ax.fill_between(df["year"], df["value"], color=color, alpha=0.09)
        title = "Annual pedestrian casualty count in reported Brooklyn crashes"
        ax.set_ylabel("Pedestrian casualties (annual count)")
        subtitle = "Pedestrian injured + killed · Complete years 2013–2025 · No walking-exposure denominator"
        ax.annotate(f"{df.iloc[0]['value']:,}", (df.iloc[0]["year"], df.iloc[0]["value"]),
                    xytext=(0, 12), textcoords="offset points", ha="center",
                    color=color, fontweight="bold")
        ax.annotate(f"{df.iloc[-1]['value']:,}", (df.iloc[-1]["year"], df.iloc[-1]["value"]),
                    xytext=(0, 12), textcoords="offset points", ha="center",
                    color=color, fontweight="bold")
    else:
        bars = ax.bar(df["year"], df["value"], color=color, width=0.68)
        ax.bar_label(bars, labels=[f"{v:,}" for v in df["value"]],
                     padding=3, fontsize=8, color="#333333")
        title = "Annual Brooklyn crashes with pedestrian injury or death"
        ax.set_ylabel("Qualifying crashes (annual count)")
        subtitle = "A crash qualifies if at least one pedestrian was injured or killed · Complete years 2013–2025 · No walking-exposure denominator"

    fig.text(0.12, 0.965, title, ha="left", va="top", fontsize=16.5,
             fontweight="bold", color="#111111")
    fig.text(0.12, 0.91, subtitle, ha="left", va="top", fontsize=9.5,
             color="#555555")
    ax.set_xlabel("Crash year")
    ax.set_xticks(df["year"])
    ax.set_xticklabels([str(y) for y in df["year"]], rotation=0)
    ax.grid(axis="y", color="#dddddd", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#888888")
    ax.tick_params(axis="y", length=0, pad=7)
    ax.tick_params(axis="x", length=0, pad=7)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    fig.text(0.125, 0.008,
             "Source: NYC police-reported motor vehicle crashes. Crashes without a usable borough label are excluded.",
             fontsize=9, color="#555555")
    fig.savefig(OUT / f"option_{option_id}.png", dpi=180, facecolor="white")
    plt.close(fig)

con.close()
