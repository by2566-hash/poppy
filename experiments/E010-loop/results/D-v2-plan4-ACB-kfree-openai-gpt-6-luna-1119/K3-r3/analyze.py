from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "crashes.parquet"
data_path = str(DATA).replace("'", "''")

con = duckdb.connect()
annual = con.execute(
    f"""SELECT year(crash_date) AS year,
               sum(number_of_motorist_killed)::BIGINT AS motorist_deaths,
               sum(number_of_cyclist_killed)::BIGINT AS cyclist_deaths
        FROM read_parquet('{data_path}')
        WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
        GROUP BY year ORDER BY year"""
).df()
con.close()

expected_years = list(range(2013, 2026))
annual["year"] = annual["year"].astype(int)
annual = annual.set_index("year").reindex(expected_years).rename_axis("year").reset_index()
if annual[["motorist_deaths", "cyclist_deaths"]].isna().any().any():
    raise ValueError("An expected year has no annual result or a missing death total")
annual[["motorist_deaths", "cyclist_deaths"]] = annual[["motorist_deaths", "cyclist_deaths"]].astype(int)

# Option 1: absolute recorded death totals by road-user class and crash year.
counts = annual.melt(
    id_vars="year", var_name="road_user", value_name="deaths"
)
counts["road_user"] = counts["road_user"].map(
    {"motorist_deaths": "Motorist", "cyclist_deaths": "Cyclist"}
)
counts.to_csv(OUT / "values_1.csv", index=False)

fig, ax = plt.subplots(figsize=(11, 6.2))
for road_user, color, marker in (
    ("Motorist", "#245b87", "o"),
    ("Cyclist", "#d47719", "s"),
):
    subset = counts[counts["road_user"] == road_user]
    ax.plot(subset["year"], subset["deaths"], label=road_user, color=color, marker=marker, linewidth=2.2)
ax.set_title("Recorded motorist and cyclist deaths per year\nNYC police-reported motor vehicle crashes, 2013–2025", loc="left", fontsize=14, weight="bold", pad=18)
ax.text(0, 1.015, "Unstandardized counts; crash data have no travel or population exposure denominator.", transform=ax.transAxes, fontsize=9, color="#555555")
ax.set_xlabel("Crash year")
ax.set_ylabel("Recorded deaths (sum of crash-level killed counts)")
ax.set_xticks(expected_years)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", color="#dddddd", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Option 2: annual composition of the combined motorist-plus-cyclist deaths.
annual["combined_deaths"] = annual["motorist_deaths"] + annual["cyclist_deaths"]
shares = pd.DataFrame(
    {
        "year": annual["year"],
        "Motorist": 100 * annual["motorist_deaths"] / annual["combined_deaths"],
        "Cyclist": 100 * annual["cyclist_deaths"] / annual["combined_deaths"],
    }
).melt(id_vars="year", var_name="road_user", value_name="share_percent")
shares.to_csv(OUT / "values_2.csv", index=False)

fig, ax = plt.subplots(figsize=(11, 6.2))
years = annual["year"].to_numpy()
motorist_share = 100 * annual["motorist_deaths"].to_numpy() / annual["combined_deaths"].to_numpy()
cyclist_share = 100 * annual["cyclist_deaths"].to_numpy() / annual["combined_deaths"].to_numpy()
ax.bar(years, motorist_share, color="#245b87", label="Motorist")
ax.bar(years, cyclist_share, bottom=motorist_share, color="#d47719", label="Cyclist")
ax.set_title("Share of recorded motorist-and-cyclist deaths by year\nNYC police-reported motor vehicle crashes, 2013–2025", loc="left", fontsize=14, weight="bold", pad=18)
ax.text(0, 1.015, "Composition only: pedestrian deaths are excluded, and no exposure denominator is available for risk comparisons.", transform=ax.transAxes, fontsize=9, color="#555555")
ax.set_xlabel("Crash year")
ax.set_ylabel("Share of motorist + cyclist deaths (%)")
ax.set_xticks(years)
ax.set_ylim(0, 100)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", color="#dddddd", linewidth=0.8)
ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, loc="center left", bbox_to_anchor=(1.01, 0.5))
fig.tight_layout(rect=(0, 0, 0.88, 1))
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)
