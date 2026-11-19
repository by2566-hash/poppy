from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"
YEARS = list(range(2013, 2026))

con = duckdb.connect()
annual = con.execute(
    """
    SELECT year(crash_date) AS year,
           sum(number_of_motorist_killed)::BIGINT AS motorist_deaths,
           sum(number_of_cyclist_killed)::BIGINT AS cyclist_deaths
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
    """,
    [str(DATA)],
).df()

# Carry years with no records as zeroes, preserving the final plan's full span.
annual = annual.set_index("year").reindex(YEARS, fill_value=0).rename_axis("year").reset_index()
annual[["motorist_deaths", "cyclist_deaths"]] = annual[["motorist_deaths", "cyclist_deaths"]].astype("int64")

# Option 1: annual death counts, with road-user type as the two series.
values_1 = annual.melt(
    id_vars="year",
    value_vars=["motorist_deaths", "cyclist_deaths"],
    var_name="road_user",
    value_name="deaths",
)
values_1["road_user"] = values_1["road_user"].map(
    {"motorist_deaths": "Motorist", "cyclist_deaths": "Cyclist"}
)
values_1.to_csv(OUT / "values_1.csv", index=False)

fig, ax = plt.subplots(figsize=(10.5, 5.8))
colors = {"Motorist": "#2864a5", "Cyclist": "#d97822"}
for user in ("Motorist", "Cyclist"):
    subset = values_1[values_1["road_user"] == user]
    ax.plot(subset["year"], subset["deaths"], marker="o", linewidth=2.2,
            markersize=4.5, label=user, color=colors[user])
fig.text(0.06, 0.965, "Annual motorist and cyclist deaths in police-reported NYC crashes, 2013–2025",
         ha="left", va="top", fontsize=13, weight="bold")
fig.text(0.06, 0.915, "Recorded people killed; counts are not exposure-adjusted. 381 records dated 2013-01-01 are retained in 2013.",
         ha="left", va="top", fontsize=9, color="#555555")
ax.set_xlabel("Calendar year")
ax.set_ylabel("People killed")
ax.set_xticks(YEARS)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", color="#dddddd", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, ncol=2, loc="upper right")
fig.subplots_adjust(left=0.08, right=0.98, bottom=0.18, top=0.84)
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Option 2: annual composition of the deaths across these two road-user types.
values_2 = annual.copy()
values_2["combined_deaths"] = values_2["motorist_deaths"] + values_2["cyclist_deaths"]
values_2["motorist_share_pct"] = values_2["motorist_deaths"] / values_2["combined_deaths"] * 100
values_2["cyclist_share_pct"] = values_2["cyclist_deaths"] / values_2["combined_deaths"] * 100
values_2.to_csv(OUT / "values_2.csv", index=False, float_format="%.6f")

fig, ax = plt.subplots(figsize=(10.5, 5.8))
ax.stackplot(
    values_2["year"],
    values_2["motorist_share_pct"],
    values_2["cyclist_share_pct"],
    labels=["Motorist", "Cyclist"],
    colors=[colors["Motorist"], colors["Cyclist"]],
    alpha=0.92,
)
fig.text(0.06, 0.965, "Shares of motorist-plus-cyclist deaths in police-reported NYC crashes, 2013–2025",
         ha="left", va="top", fontsize=13, weight="bold")
fig.text(0.06, 0.915, "Each year's denominator includes only motorist and cyclist deaths; not exposure-adjusted. 381 records dated 2013-01-01 are retained in 2013.",
         ha="left", va="top", fontsize=9, color="#555555")
ax.set_xlabel("Calendar year")
ax.set_ylabel("Share of combined deaths (%)")
ax.set_ylim(0, 100)
ax.set_xticks(YEARS)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", color="#dddddd", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, ncol=2, loc="upper right")
fig.subplots_adjust(left=0.08, right=0.98, bottom=0.18, top=0.84)
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)
