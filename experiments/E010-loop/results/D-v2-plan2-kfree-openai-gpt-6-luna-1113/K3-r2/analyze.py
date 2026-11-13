from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "crashes.parquet"

query = f"""
    SELECT
        EXTRACT(YEAR FROM crash_date)::INTEGER AS year,
        SUM(number_of_motorist_killed)::BIGINT AS motorist_deaths,
        SUM(number_of_cyclist_killed)::BIGINT AS cyclist_deaths
    FROM read_parquet('{DATA.as_posix()}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
"""
values = duckdb.connect().execute(query).df()
values.to_csv(OUT / "values_1.csv", index=False)

# Framing 1: annual absolute counts, shown as paired bars.
years = values["year"].to_numpy()
x = np.arange(len(years))
width = 0.38
fig, ax = plt.subplots(figsize=(12, 6.5))
ax.bar(x - width / 2, values["motorist_deaths"], width, label="Motorist deaths", color="#245b8f")
ax.bar(x + width / 2, values["cyclist_deaths"], width, label="Cyclist deaths", color="#e07a2d")
ax.set_title("Motorist and cyclist deaths per year in NYC police-reported crashes\n(annual fatality counts, 2013–2025)", pad=14)
ax.set_xlabel("Calendar year")
ax.set_ylabel("Deaths recorded")
ax.set_xticks(x, years)
ax.legend(frameon=False)
ax.grid(axis="y", alpha=0.25)
ax.spines[["top", "right"]].set_visible(False)
fig.text(0.5, 0.015, "Limitation: recorded totals, not exposure-adjusted risk rates.", ha="center", fontsize=9)
fig.tight_layout(rect=(0, 0.045, 1, 1))
fig.savefig(OUT / "option_1.png", dpi=180)
plt.close(fig)

# Framing 2: annual composition among these two categories only.
shares = values.copy()
two_group_total = shares["motorist_deaths"] + shares["cyclist_deaths"]
shares["motorist_share_pct"] = shares["motorist_deaths"] / two_group_total * 100
shares["cyclist_share_pct"] = shares["cyclist_deaths"] / two_group_total * 100
shares[["year", "motorist_share_pct", "cyclist_share_pct"]].to_csv(OUT / "values_2.csv", index=False, float_format="%.6f")

fig, ax = plt.subplots(figsize=(12, 6.5))
ax.bar(years, shares["motorist_share_pct"], label="Motorist deaths", color="#245b8f", width=0.75)
ax.bar(years, shares["cyclist_share_pct"], bottom=shares["motorist_share_pct"], label="Cyclist deaths", color="#e07a2d", width=0.75)
ax.set_title("Share of motorist-plus-cyclist deaths in NYC police-reported crashes\n(annual composition, 2013–2025)", pad=14)
ax.set_xlabel("Calendar year")
ax.set_ylabel("Share of the two-category total (%)")
ax.set_ylim(0, 100)
ax.set_xticks(years)
ax.legend(frameon=False, loc="center left", bbox_to_anchor=(1.01, 0.5))
ax.grid(axis="y", alpha=0.25)
ax.spines[["top", "right"]].set_visible(False)
fig.text(0.5, 0.015, "Limitation: denominator includes motorist and cyclist deaths only; shares are not risk rates.", ha="center", fontsize=9)
fig.tight_layout(rect=(0, 0.045, 0.88, 1))
fig.savefig(OUT / "option_2.png", dpi=180)
plt.close(fig)
