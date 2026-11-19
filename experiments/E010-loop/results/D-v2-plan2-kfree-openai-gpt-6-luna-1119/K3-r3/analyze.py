from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
PARQUET = ROOT / "data" / "crashes.parquet"

con = duckdb.connect()
counts = con.execute(
    """
    SELECT EXTRACT(YEAR FROM crash_date)::INTEGER AS year,
           SUM(number_of_motorist_killed)::BIGINT AS motorist_deaths,
           SUM(number_of_cyclist_killed)::BIGINT AS cyclist_deaths
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
    """,
    [str(PARQUET)],
).df()
con.close()

counts["motorist_deaths"] = counts["motorist_deaths"].astype("int64")
counts["cyclist_deaths"] = counts["cyclist_deaths"].astype("int64")
counts.to_csv(OUT / "values_1.csv", index=False)

fig, ax = plt.subplots(figsize=(11, 6.4))
ax.plot(counts["year"], counts["motorist_deaths"], marker="o", linewidth=2.5, label="Motorist deaths", color="#275D8C")
ax.plot(counts["year"], counts["cyclist_deaths"], marker="o", linewidth=2.5, label="Cyclist deaths", color="#E17C35")
ax.set_title("Annual motorist and cyclist deaths in NYC, 2013–2025", fontsize=15, weight="bold", pad=20)
ax.text(
    0.5, 1.015,
    "Police-reported deaths among NYC crash rows; date spans cover each calendar year, but completeness is unverified; no exposure adjustment",
    transform=ax.transAxes, ha="center", va="bottom", fontsize=9, color="#555555",
)
ax.set_xlabel("Crash year")
ax.set_ylabel("Deaths (count)")
ax.set_xticks(counts["year"])
ax.grid(axis="y", color="#D9DEE5", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, ncol=2, loc="upper right")
fig.tight_layout()
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

shares = counts.copy()
shares["combined_motorist_cyclist_deaths"] = shares["motorist_deaths"] + shares["cyclist_deaths"]
shares["motorist_share"] = shares["motorist_deaths"] / shares["combined_motorist_cyclist_deaths"]
shares["cyclist_share"] = shares["cyclist_deaths"] / shares["combined_motorist_cyclist_deaths"]
shares.to_csv(OUT / "values_2.csv", index=False)

fig, ax = plt.subplots(figsize=(11, 6.4))
years = shares["year"].to_numpy()
motorist_share = shares["motorist_share"].to_numpy()
cyclist_share = shares["cyclist_share"].to_numpy()
ax.bar(years, motorist_share * 100, color="#275D8C", label="Motorist share")
ax.bar(years, cyclist_share * 100, bottom=motorist_share * 100, color="#E17C35", label="Cyclist share")
ax.set_title("Composition of annual motorist + cyclist deaths in NYC, 2013–2025", fontsize=15, weight="bold", pad=20)
ax.text(
    0.5, 1.015,
    "Police-reported deaths; each bar totals 100% of these two categories only; yearly completeness is unverified; no exposure adjustment",
    transform=ax.transAxes, ha="center", va="bottom", fontsize=9, color="#555555",
)
ax.set_xlabel("Crash year")
ax.set_ylabel("Share of motorist + cyclist deaths (%)")
ax.set_xticks(years)
ax.set_ylim(0, 100)
ax.grid(axis="y", color="#D9DEE5", linewidth=0.8)
ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, ncol=2, loc="upper right")
fig.tight_layout()
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)
