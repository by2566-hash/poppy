from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


OUT = Path("out")
DATA = "data/crashes.parquet"

annual = duckdb.connect().execute(
    """
    SELECT
        year(crash_date) AS year,
        sum(number_of_motorist_killed)::BIGINT AS motorist_deaths,
        sum(number_of_cyclist_killed)::BIGINT AS cyclist_deaths
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
    """,
    [DATA],
).df()

annual.to_csv(OUT / "values_1.csv", index=False)

fig, ax = plt.subplots(figsize=(12, 6.5))
x = annual["year"].astype(int).to_numpy()
width = 0.38
bars_m = ax.bar(x - width / 2, annual["motorist_deaths"], width, label="Motorists", color="#3569a8")
bars_c = ax.bar(x + width / 2, annual["cyclist_deaths"], width, label="Cyclists", color="#e58b3a")
ax.bar_label(bars_m, padding=2, fontsize=8)
ax.bar_label(bars_c, padding=2, fontsize=8)
ax.set_title(
    "Annual motorist and cyclist deaths in police-reported NYC motor-vehicle crashes\n"
    "All crashes dated 2013–2025; deaths summed by road-user category",
    fontsize=13,
)
ax.set_xlabel("Calendar year")
ax.set_ylabel("People killed (annual count)")
ax.set_xticks(x)
ax.legend(frameon=False)
ax.grid(axis="y", alpha=0.25)
fig.text(
    0.5,
    0.01,
    "Full calendar years. Counts are not adjusted for travel exposure and are not per-trip or per-mile risk rates.",
    ha="center",
    fontsize=9,
)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(OUT / "option_1.png", dpi=180)
plt.close(fig)

shares = annual.copy()
shares["combined_motorist_cyclist_deaths"] = (
    shares["motorist_deaths"] + shares["cyclist_deaths"]
)
shares["motorist_share_pct"] = (
    100 * shares["motorist_deaths"] / shares["combined_motorist_cyclist_deaths"]
)
shares["cyclist_share_pct"] = (
    100 * shares["cyclist_deaths"] / shares["combined_motorist_cyclist_deaths"]
)
shares.to_csv(OUT / "values_2.csv", index=False)

fig, ax = plt.subplots(figsize=(12, 6.5))
ax.plot(
    shares["year"], shares["motorist_share_pct"], marker="o", linewidth=2,
    label="Motorist share", color="#3569a8"
)
ax.plot(
    shares["year"], shares["cyclist_share_pct"], marker="o", linewidth=2,
    label="Cyclist share", color="#e58b3a"
)
ax.set_title(
    "Annual share of motorist and cyclist deaths among combined motorist/cyclist deaths\n"
    "All police-reported NYC motor-vehicle crashes dated 2013–2025",
    fontsize=13,
)
ax.set_xlabel("Calendar year")
ax.set_ylabel("Share of motorist + cyclist deaths (%)")
ax.set_xticks(shares["year"].astype(int))
ax.set_ylim(0, 100)
ax.legend(frameon=False)
ax.grid(axis="y", alpha=0.25)
fig.text(
    0.5,
    0.01,
    "Denominator excludes pedestrians and other categories; shares are not exposure-adjusted risk rates.",
    ha="center",
    fontsize=9,
)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(OUT / "option_2.png", dpi=180)
plt.close(fig)
