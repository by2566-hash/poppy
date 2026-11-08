import duckdb
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
START_YEAR = 2013
END_YEAR = 2025

con = duckdb.connect()
query = f"""
    SELECT year(crash_date) AS year,
           sum(number_of_pedestrians_injured) AS pedestrians_injured,
           sum(number_of_pedestrians_killed) AS pedestrians_killed
    FROM read_parquet('{str(DATA).replace("'", "''")}')
    WHERE upper(trim(borough)) = 'BROOKLYN'
      AND crash_date >= DATE '{START_YEAR}-01-01'
      AND crash_date < DATE '{END_YEAR + 1}-01-01'
    GROUP BY year
    ORDER BY year
"""
annual = con.execute(query).df()
con.close()

expected_years = list(range(START_YEAR, END_YEAR + 1))
annual = annual.set_index("year").reindex(expected_years, fill_value=0).rename_axis("year").reset_index()
annual[["pedestrians_injured", "pedestrians_killed"]] = annual[["pedestrians_injured", "pedestrians_killed"]].astype(int)
annual["pedestrian_casualties"] = annual["pedestrians_injured"] + annual["pedestrians_killed"]

chart_specs = [
    {
        "id": 1,
        "column": "pedestrian_casualties",
        "metric": "Pedestrians injured plus killed per year",
        "short_metric": "Pedestrian casualties",
        "color": "#1769aa",
        "y_label": "Pedestrians injured or killed",
    },
    {
        "id": 2,
        "column": "pedestrians_killed",
        "metric": "Pedestrians killed per year",
        "short_metric": "Pedestrians killed",
        "color": "#b42318",
        "y_label": "Pedestrians killed",
    },
]

for spec in chart_specs:
    values = annual[["year", spec["column"]]].rename(columns={spec["column"]: "count"})
    values.to_csv(OUT / f"values_{spec['id']}.csv", index=False)

    fig, ax = plt.subplots(figsize=(10.5, 5.8), layout="constrained")
    ax.plot(
        values["year"], values["count"],
        color=spec["color"], linewidth=2.8, marker="o", markersize=5.8,
    )
    ax.fill_between(values["year"], values["count"], color=spec["color"], alpha=0.10)
    first = values.iloc[0]
    last = values.iloc[-1]
    ax.annotate(
        f"{int(first['count']):,}", (first["year"], first["count"]),
        xytext=(0, 12), textcoords="offset points", ha="center",
        fontsize=9, fontweight="bold", color=spec["color"],
    )
    ax.annotate(
        f"{int(last['count']):,}", (last["year"], last["count"]),
        xytext=(0, 12), textcoords="offset points", ha="center",
        fontsize=9, fontweight="bold", color=spec["color"],
    )
    ax.set_title(
        f"{spec['short_metric']} in Brooklyn, 2013–2025\n"
        f"{spec['metric']} in police-reported crashes",
        loc="left", fontsize=17, fontweight="bold", pad=15,
    )
    ax.set_xlabel("Crash year")
    ax.set_ylabel(spec["y_label"])
    ax.set_xticks(expected_years)
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", color="#d9dee5", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#8b95a1")
    ax.set_ylim(bottom=0, top=values["count"].max() * 1.18)
    fig.text(
        0.01, -0.015,
        "Source: NYC police-reported crash records. Raw counts, not adjusted for walking exposure; 2026 is partial and excluded.",
        ha="left", va="top", fontsize=8.5, color="#4b5563",
    )
    fig.savefig(OUT / f"option_{spec['id']}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
