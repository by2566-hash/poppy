from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


OUT = Path("out")
SOURCE = "data/crashes.parquet"
YEARS = list(range(2013, 2026))

con = duckdb.connect()

# Option 1: an outcome count, not an exposure-adjusted risk.
counts = con.execute(
    f"""
    SELECT year(crash_date) AS year,
           sum(number_of_motorist_killed) AS motorist_deaths
    FROM read_parquet('{SOURCE}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
      AND number_of_motorist_killed IS NOT NULL
    GROUP BY year
    ORDER BY year
    """
).df()
counts["year"] = counts["year"].astype(int)
counts.to_csv(OUT / "values_1.csv", index=False)

fig, ax = plt.subplots(figsize=(10, 5.5))
ax.bar(counts["year"], counts["motorist_deaths"], color="#2878a5", width=0.72)
ax.set_title("Annual motorist deaths in police-reported NYC crashes", loc="left", weight="bold", pad=28)
ax.text(
    0,
    1.015,
    "Count of persons classified as motorists killed; this is not a per-mile risk (miles driven unavailable).",
    transform=ax.transAxes,
    ha="left",
    va="bottom",
    fontsize=9,
    color="#4b5563",
)
ax.set_xlabel("Crash year")
ax.set_ylabel("Motorist deaths")
ax.set_xticks(YEARS)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", color="#d8dee6", linewidth=0.7)
ax.set_axisbelow(True)
fig.text(0.01, 0.01, "Date endpoints span each calendar year; daily reporting completeness is not established.", fontsize=8, color="#4b5563")
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Option 2: motorist deaths' share of all reported deaths, using a matched
# complete-case set of crash records for numerator and denominator.
shares = con.execute(
    f"""
    SELECT year(crash_date) AS year,
           sum(number_of_motorist_killed) AS motorist_deaths,
           sum(number_of_persons_killed) AS all_deaths
    FROM read_parquet('{SOURCE}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
      AND number_of_motorist_killed IS NOT NULL
      AND number_of_persons_killed IS NOT NULL
    GROUP BY year
    ORDER BY year
    """
).df()
shares["year"] = shares["year"].astype(int)
shares["motorist_death_share"] = shares["motorist_deaths"] / shares["all_deaths"]
shares.to_csv(OUT / "values_2.csv", index=False)

fig, ax = plt.subplots(figsize=(10, 5.5))
ax.plot(
    shares["year"],
    shares["motorist_death_share"] * 100,
    color="#a84e30",
    marker="o",
    linewidth=2.4,
    markersize=5,
)
ax.set_title("Motorist deaths as a share of all deaths in police-reported NYC crashes", loc="left", weight="bold", pad=28)
ax.text(
    0,
    1.015,
    "Annual motorist deaths ÷ all reported deaths; not a per-mile risk (miles driven unavailable).",
    transform=ax.transAxes,
    ha="left",
    va="bottom",
    fontsize=9,
    color="#4b5563",
)
ax.set_xlabel("Crash year")
ax.set_ylabel("Motorist deaths (% of all deaths)")
ax.set_xticks(YEARS)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", color="#d8dee6", linewidth=0.7)
ax.set_axisbelow(True)
fig.text(0.01, 0.01, "Same-year complete-case crashes; date endpoints span each year but daily reporting completeness is unknown.", fontsize=8, color="#4b5563")
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)

con.close()
