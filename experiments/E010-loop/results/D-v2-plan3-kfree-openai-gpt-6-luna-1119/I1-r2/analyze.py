from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
source = str(ROOT / "data" / "crashes.parquet").replace("'", "''")
con = duckdb.connect()
annual = con.execute(
    f"""
    SELECT
      year(crash_date)::INTEGER AS year,
      count(*)::BIGINT AS reported_crashes,
      sum(number_of_motorist_killed)::BIGINT AS motorist_deaths
    FROM read_parquet('{source}')
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
    """
).df()

if annual["motorist_deaths"].isna().any():
    raise ValueError("A planned motorist-death value is missing; see the data check.")

annual["deaths_per_1000_reported_crashes"] = (
    annual["motorist_deaths"] / annual["reported_crashes"] * 1000
)

annual[["year", "motorist_deaths"]].to_csv(OUT / "values_1.csv", index=False)
annual[
    ["year", "motorist_deaths", "reported_crashes", "deaths_per_1000_reported_crashes"]
].to_csv(OUT / "values_2.csv", index=False)


def save_chart(y, ylabel, title, path, ylim_bottom=0):
    fig, ax = plt.subplots(figsize=(10, 5.7))
    ax.plot(annual["year"], y, color="#176B87", marker="o", linewidth=2.2, markersize=5)
    ax.set_title(title, loc="left", fontsize=14, weight="bold", pad=28)
    ax.text(
        0,
        1.025,
        "NYC police-reported crashes, 2013–2025 | Not per-mile risk; miles driven unavailable",
        transform=ax.transAxes,
        fontsize=9,
        color="#4B5563",
        va="bottom",
    )
    ax.set_xlabel("Crash year")
    ax.set_ylabel(ylabel)
    ax.set_xticks(annual["year"])
    ax.tick_params(axis="x", rotation=45)
    ax.set_ylim(bottom=ylim_bottom)
    ax.grid(axis="y", color="#D9E1E8", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / path, dpi=180, bbox_inches="tight")
    plt.close(fig)


save_chart(
    annual["motorist_deaths"],
    "Recorded motorist deaths (count)",
    "Annual motorist deaths in NYC police-reported crashes",
    "option_1.png",
)
save_chart(
    annual["deaths_per_1000_reported_crashes"],
    "Recorded motorist deaths per 1,000 reported crashes",
    "Annual motorist deaths per 1,000 NYC reported crashes",
    "option_2.png",
)
