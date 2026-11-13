import json
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import PercentFormatter


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
SOURCE = (ROOT / "data" / "crashes.parquet").as_posix()
con = duckdb.connect()

data = con.execute(
    "SELECT YEAR(crash_date) AS year, "
    "SUM(number_of_motorist_killed) AS motorist_deaths, "
    "COUNT(*) FILTER (WHERE number_of_motorist_killed > 0) AS fatal_motorist_crashes, "
    "COUNT(*) FILTER (WHERE number_of_motorist_killed IS NOT NULL) AS crashes_with_known_deaths "
    f"FROM read_parquet('{SOURCE}') "
    "WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' "
    "GROUP BY year ORDER BY year"
).df()

data["motorist_deaths"] = data["motorist_deaths"].astype("int64")
data["fatal_motorist_crashes"] = data["fatal_motorist_crashes"].astype("int64")
data["crashes_with_known_deaths"] = data["crashes_with_known_deaths"].astype("int64")

options = [
    {
        "id": 1,
        "column": "motorist_deaths",
        "ylabel": "Motorists reported killed",
        "title": "Motorist deaths in police-reported NYC crashes, 2013–2025",
        "subtitle": "Annual death count; not mileage-adjusted (the crash file has no vehicle-miles-traveled data).",
        "filename": "option_1.png",
        "values": data[["year", "motorist_deaths"]].rename(columns={"motorist_deaths": "motorist_deaths"}),
    },
    {
        "id": 2,
        "column": "fatal_motorist_crashes",
        "ylabel": "Crashes with ≥1 motorist killed",
        "title": "NYC crashes with at least one motorist killed, 2013–2025",
        "subtitle": "Annual fatal-crash count; not a per-mile rate or count of motorists killed.",
        "filename": "option_2.png",
        "values": data[["year", "fatal_motorist_crashes"]].rename(columns={"fatal_motorist_crashes": "fatal_motorist_crashes"}),
    },
]

share = data[["year", "fatal_motorist_crashes", "crashes_with_known_deaths"]].copy()
share["fatal_crashes_share_pct"] = share["fatal_motorist_crashes"] / share["crashes_with_known_deaths"] * 100
options.append(
    {
        "id": 3,
        "column": "fatal_crashes_share_pct",
        "ylabel": "Crashes involving a motorist death (%)",
        "title": "Share of NYC crashes with at least one motorist killed, 2013–2025",
        "subtitle": "Among crashes with a known motorist-deaths field; not mileage-adjusted or person-level risk.",
        "filename": "option_3.png",
        "values": share,
    }
)

for option in options:
    option["values"].to_csv(OUT / f"values_{option['id']}.csv", index=False)
    fig, ax = plt.subplots(figsize=(10, 5.6))
    values = option["values"]
    ax.plot(values["year"], values[option["column"]], marker="o", linewidth=2.2, color="#176B87")
    ax.set_title(option["title"], loc="left", fontsize=14, fontweight="bold", pad=28)
    ax.text(0, 1.015, option["subtitle"], transform=ax.transAxes, fontsize=9, color="#4D5966", va="bottom")
    ax.set_xlabel("Crash year")
    ax.set_ylabel(option["ylabel"])
    ax.set_ylim(bottom=0)
    if option["id"] == 3:
        ax.yaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=2))
    ax.set_xticks(values["year"])
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", color="#D9E1E8", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(OUT / option["filename"], dpi=180, bbox_inches="tight")
    plt.close(fig)

print(data.to_json(orient="records"))
