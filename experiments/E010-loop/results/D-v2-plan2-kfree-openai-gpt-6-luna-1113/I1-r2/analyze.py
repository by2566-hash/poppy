from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
YEARS = list(range(2013, 2026))

con = duckdb.connect()
yearly = con.execute(
    """
    SELECT
        year(crash_date) AS year,
        count(*) AS reported_crashes,
        sum(number_of_motorist_killed) AS motorists_killed,
        count(*) FILTER (WHERE number_of_motorist_killed IS NOT NULL)
            AS crashes_with_motorist_death_data,
        sum(number_of_motorist_killed)
            FILTER (WHERE number_of_motorist_killed IS NOT NULL)
            AS complete_motorists_killed
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
    """,
    [str(DATA)],
).df()
yearly["year"] = yearly["year"].astype(int)
yearly = yearly.set_index("year").reindex(YEARS).rename_axis("year").reset_index()
yearly["motorists_killed"] = yearly["motorists_killed"].fillna(0).astype(int)
yearly["reported_crashes"] = yearly["reported_crashes"].fillna(0).astype(int)
yearly["crashes_with_motorist_death_data"] = (
    yearly["crashes_with_motorist_death_data"].fillna(0).astype(int)
)
yearly["complete_motorists_killed"] = yearly["complete_motorists_killed"].fillna(0).astype(int)
yearly["motorist_deaths_per_1000_crashes"] = (
    yearly["complete_motorists_killed"] / yearly["crashes_with_motorist_death_data"] * 1000
)

values1 = yearly[["year", "motorists_killed", "reported_crashes"]]
values1.to_csv(OUT / "values_1.csv", index=False)

fig, ax = plt.subplots(figsize=(10, 5.8))
ax.plot(yearly["year"], yearly["motorists_killed"], marker="o", linewidth=2.3, color="#245b8f")
ax.set_title("Motorists killed in NYC police-reported crashes by year (count)", fontsize=14, pad=18)
fig.text(
    0.5,
    0.93,
    "Population: all dated crashes, 2013–2025. Not a per-mile risk measure; mileage exposure is unavailable.",
    ha="center",
    fontsize=9,
    color="#444444",
)
ax.set_xlabel("Crash year")
ax.set_ylabel("Motorists killed (people)")
ax.set_xticks(YEARS)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
fig.tight_layout(rect=(0, 0, 1, 0.9))
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

values2 = yearly[
    [
        "year",
        "complete_motorists_killed",
        "crashes_with_motorist_death_data",
        "motorist_deaths_per_1000_crashes",
    ]
]
values2.to_csv(OUT / "values_2.csv", index=False, float_format="%.6f")

fig, ax = plt.subplots(figsize=(10, 5.8))
ax.plot(
    yearly["year"],
    yearly["motorist_deaths_per_1000_crashes"],
    marker="o",
    linewidth=2.3,
    color="#a2523b",
)
ax.set_title("Motorist deaths per 1,000 NYC police-reported crashes", fontsize=14, pad=18)
fig.text(
    0.5,
    0.93,
    "Population: all dated crashes, 2013–2025. A crash-based rate, not a per-mile risk; mileage exposure is unavailable.",
    ha="center",
    fontsize=9,
    color="#444444",
)
ax.set_xlabel("Crash year")
ax.set_ylabel("Motorists killed per 1,000 crashes")
ax.set_xticks(YEARS)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
fig.tight_layout(rect=(0, 0, 1, 0.9))
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)

print(yearly.to_string(index=False))
