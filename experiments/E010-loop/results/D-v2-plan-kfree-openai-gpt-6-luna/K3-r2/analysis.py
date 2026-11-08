from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "crashes.parquet"
data_path = str(DATA).replace("'", "''")

con = duckdb.connect()
annual = con.execute(f"""
    SELECT year(crash_date) AS year,
           sum(number_of_cyclist_killed) AS cyclist_deaths,
           sum(number_of_motorist_killed) AS motorist_deaths
    FROM read_parquet('{data_path}')
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY year ORDER BY year
""").df()

expected_years = pd.DataFrame({"year": range(2013, 2026)})
annual = expected_years.merge(annual, on="year", how="left")
if annual[["cyclist_deaths", "motorist_deaths"]].isna().any().any():
    raise ValueError("At least one planned year has no recorded death counts; review the check and plan.")
annual[["cyclist_deaths", "motorist_deaths"]] = annual[["cyclist_deaths", "motorist_deaths"]].astype("int64")
annual.to_csv(OUT / "values_1.csv", index=False)

fig, ax = plt.subplots(figsize=(10.5, 5.8))
ax.plot(annual["year"], annual["motorist_deaths"], marker="o", linewidth=2.2, label="Motorist deaths")
ax.plot(annual["year"], annual["cyclist_deaths"], marker="o", linewidth=2.2, label="Cyclist deaths")
ax.set_title("Annual deaths recorded in police-reported NYC motor-vehicle crashes, 2013–2025\nMotorist and cyclist counts", fontsize=13, pad=14)
ax.set_xlabel("Crash year")
ax.set_ylabel("Deaths (count)")
ax.set_xticks(annual["year"])
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
ax.legend(frameon=False)
fig.text(0.5, 0.015, "Limitation: counts are not adjusted for population or travel exposure; zero-valued crash records are retained.", ha="center", fontsize=9)
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

annual["combined_deaths"] = annual["cyclist_deaths"] + annual["motorist_deaths"]
annual["cyclist_share_pct"] = annual["cyclist_deaths"] / annual["combined_deaths"] * 100
annual["motorist_share_pct"] = annual["motorist_deaths"] / annual["combined_deaths"] * 100
if (annual["combined_deaths"] == 0).any():
    raise ValueError("At least one year has no deaths in either group; its planned shares are undefined.")
annual[["year", "cyclist_deaths", "motorist_deaths", "combined_deaths", "cyclist_share_pct", "motorist_share_pct"]].to_csv(OUT / "values_2.csv", index=False, float_format="%.4f")

fig, ax = plt.subplots(figsize=(10.5, 5.8))
ax.plot(annual["year"], annual["motorist_share_pct"], marker="o", linewidth=2.2, label="Motorist share")
ax.plot(annual["year"], annual["cyclist_share_pct"], marker="o", linewidth=2.2, label="Cyclist share")
ax.set_title("Share of cyclist-plus-motorist deaths in police-reported NYC motor-vehicle crashes, 2013–2025\nAnnual composition by road-user group", fontsize=13, pad=14)
ax.set_xlabel("Crash year")
ax.set_ylabel("Share of combined deaths (%)")
ax.set_ylim(0, 100)
ax.set_xticks(annual["year"])
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
ax.legend(frameon=False)
fig.text(0.5, 0.015, "Limitation: denominator includes only cyclist and motorist deaths; shares are not exposure-adjusted risks.", ha="center", fontsize=9)
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)
