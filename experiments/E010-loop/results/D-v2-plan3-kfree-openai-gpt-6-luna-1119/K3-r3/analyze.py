from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


OUT = Path("out")
con = duckdb.connect()
annual = con.execute(
    """SELECT YEAR(crash_date) AS year,
              SUM(number_of_motorist_killed)::BIGINT AS motorist_deaths,
              SUM(number_of_cyclist_killed)::BIGINT AS cyclist_deaths
       FROM read_parquet('data/crashes.parquet')
       WHERE crash_date >= DATE '2013-01-01'
         AND crash_date < DATE '2026-01-01'
       GROUP BY YEAR(crash_date)
       ORDER BY year"""
).df()
con.close()

years = list(range(2013, 2026))
annual = annual.set_index("year").reindex(years).rename_axis("year").reset_index()
annual["motorist_deaths"] = annual["motorist_deaths"].astype("int64")
annual["cyclist_deaths"] = annual["cyclist_deaths"].astype("int64")
annual["cyclist_deaths_per_100_motorist_deaths"] = (
    100 * annual["cyclist_deaths"] / annual["motorist_deaths"]
)

values_1 = annual[["year", "motorist_deaths", "cyclist_deaths"]]
values_1.to_csv(OUT / "values_1.csv", index=False)

fig, ax = plt.subplots(figsize=(10.5, 6.2))
ax.plot(annual["year"], annual["motorist_deaths"], marker="o", linewidth=2.4,
        color="#245b8f", label="Motorist deaths")
ax.plot(annual["year"], annual["cyclist_deaths"], marker="o", linewidth=2.4,
        color="#d47a22", label="Cyclist deaths")
ax.set_title("Annual recorded motorist and cyclist deaths in NYC police-reported crashes\n2013–2025",
             fontsize=14, pad=18)
ax.set_xlabel("Crash year")
ax.set_ylabel("Deaths (annual count)")
ax.set_xticks(years)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
ax.legend(frameon=False)
fig.text(0.5, 0.015,
         "Full observed calendar years; counts are not normalized for crash volume or road-user exposure.",
         ha="center", fontsize=9, color="#555555")
fig.tight_layout(rect=(0, 0.045, 1, 1))
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

values_2 = annual[["year", "cyclist_deaths_per_100_motorist_deaths",
                   "cyclist_deaths", "motorist_deaths"]]
values_2.to_csv(OUT / "values_2.csv", index=False, float_format="%.4f")

fig, ax = plt.subplots(figsize=(10.5, 6.2))
ax.plot(annual["year"], annual["cyclist_deaths_per_100_motorist_deaths"],
        marker="o", linewidth=2.4, color="#6a4c93")
ax.set_title("Cyclist deaths per 100 motorist deaths in NYC police-reported crashes\n2013–2025",
             fontsize=14, pad=18)
ax.set_xlabel("Crash year")
ax.set_ylabel("Cyclist deaths per 100 motorist deaths")
ax.set_xticks(years)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
fig.text(0.5, 0.015,
         "Ratio denominator is motorist deaths; this is not an exposure-based risk rate.",
         ha="center", fontsize=9, color="#555555")
fig.tight_layout(rect=(0, 0.045, 1, 1))
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)
