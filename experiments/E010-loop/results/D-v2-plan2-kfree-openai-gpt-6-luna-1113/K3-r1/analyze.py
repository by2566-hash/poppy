import duckdb
import matplotlib.pyplot as plt
import pandas as pd


con = duckdb.connect()
annual = con.execute(
    """
    SELECT
        year(crash_date) AS year,
        sum(number_of_motorist_killed) AS motorist_deaths,
        sum(number_of_cyclist_killed) AS cyclist_deaths
    FROM read_parquet('data/crashes.parquet')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year(crash_date)
    ORDER BY year
    """
).fetchdf()
con.close()

expected_years = pd.DataFrame({"year": range(2013, 2026)})
annual = expected_years.merge(annual, on="year", how="left").fillna(0)
annual[["motorist_deaths", "cyclist_deaths"]] = annual[
    ["motorist_deaths", "cyclist_deaths"]
].astype(int)

# Framing 1: annual absolute reported deaths, with no denominator.
counts = annual.melt(
    id_vars="year",
    value_vars=["motorist_deaths", "cyclist_deaths"],
    var_name="category",
    value_name="reported_deaths",
)
counts["category"] = counts["category"].map(
    {"motorist_deaths": "Motorist", "cyclist_deaths": "Cyclist"}
)
counts.to_csv("out/values_1.csv", index=False)

fig, ax = plt.subplots(figsize=(10.5, 5.8))
colors = {"Motorist": "#315a7d", "Cyclist": "#c47732"}
for category in ["Motorist", "Cyclist"]:
    series = counts[counts["category"] == category]
    ax.plot(
        series["year"], series["reported_deaths"],
        marker="o", linewidth=2.3, markersize=5.5,
        color=colors[category], label=category,
    )
ax.set_title("Reported motorist and cyclist deaths by crash year, NYC (2013–2025)", pad=20)
ax.text(
    0.5, 1.015,
    "Annual absolute deaths reported across police-reported crash records; not adjusted for travel exposure",
    transform=ax.transAxes, ha="center", va="bottom", fontsize=9,
)
ax.set_xlabel("Calendar year of crash")
ax.set_ylabel("Reported deaths")
ax.set_xticks(range(2013, 2026))
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig("out/option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Framing 2: annual composition among motorist and cyclist deaths only.
annual["combined_deaths"] = annual["motorist_deaths"] + annual["cyclist_deaths"]
shares = annual.melt(
    id_vars=["year", "combined_deaths"],
    value_vars=["motorist_deaths", "cyclist_deaths"],
    var_name="category",
    value_name="reported_deaths",
)
shares["category"] = shares["category"].map(
    {"motorist_deaths": "Motorist", "cyclist_deaths": "Cyclist"}
)
shares["share_percent"] = shares["reported_deaths"] / shares["combined_deaths"] * 100
shares.to_csv("out/values_2.csv", index=False)

wide_shares = shares.pivot(index="year", columns="category", values="share_percent")
fig, ax = plt.subplots(figsize=(10.5, 5.8))
ax.bar(
    wide_shares.index, wide_shares["Motorist"],
    color=colors["Motorist"], label="Motorist",
)
ax.bar(
    wide_shares.index, wide_shares["Cyclist"],
    bottom=wide_shares["Motorist"], color=colors["Cyclist"], label="Cyclist",
)
ax.set_title("Motorist and cyclist share of their combined deaths, NYC (2013–2025)", pad=20)
ax.text(
    0.5, 1.015,
    "Each year totals 100%; denominator includes only reported motorist and cyclist deaths",
    transform=ax.transAxes, ha="center", va="bottom", fontsize=9,
)
ax.set_xlabel("Calendar year of crash")
ax.set_ylabel("Share of combined motorist and cyclist deaths (%)")
ax.set_xticks(range(2013, 2026))
ax.tick_params(axis="x", rotation=45)
ax.set_ylim(0, 100)
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)
ax.legend(frameon=False, loc="upper right")
fig.tight_layout()
fig.savefig("out/option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)
