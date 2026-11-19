from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "crashes.parquet"


def load_annual_counts():
    path = str(DATA).replace("'", "''")
    con = duckdb.connect()
    counts = con.execute(f"""
        SELECT EXTRACT(YEAR FROM crash_date)::INTEGER AS year,
               SUM(number_of_motorist_killed)::BIGINT AS motorist_deaths,
               SUM(number_of_cyclist_killed)::BIGINT AS cyclist_deaths
        FROM read_parquet('{path}')
        WHERE crash_date >= DATE '2013-01-01'
          AND crash_date < DATE '2026-01-01'
          AND number_of_motorist_killed IS NOT NULL
          AND number_of_cyclist_killed IS NOT NULL
        GROUP BY year
        ORDER BY year
    """).df()
    con.close()
    return counts


def main():
    annual = load_annual_counts()
    categories = ["motorist", "cyclist"]
    colors = {"motorist": "#3366a6", "cyclist": "#e28b32"}

    # Framing 1: annual fatality counts.
    values1 = annual.melt(
        id_vars="year", var_name="road_user", value_name="deaths"
    )
    values1["road_user"] = values1["road_user"].str.replace("_deaths", "", regex=False)
    values1.to_csv(OUT / "values_1.csv", index=False)
    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    for user in categories:
        series = values1[values1.road_user == user]
        ax.plot(series.year, series.deaths, marker="o", linewidth=2.2,
                markersize=4.5, color=colors[user], label=user.capitalize())
    ax.set_title("Annual motorist and cyclist deaths in police-reported NYC crashes, 2013–2025", pad=22)
    ax.text(0.5, 1.015, "Annual counts of deaths recorded in crashes; full calendar years",
            transform=ax.transAxes, ha="center", va="bottom", fontsize=9)
    ax.set_xlabel("Crash year")
    ax.set_ylabel("Deaths")
    ax.set_xticks(annual.year)
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False, ncol=2, loc="upper right")
    ax.text(0, -0.22,
            "Limitation: police-reported crashes only; counts are not adjusted for travel exposure.",
            transform=ax.transAxes, ha="left", va="top", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # Framing 2: each road-user category's share of the combined two-category total.
    values2 = values1.copy()
    annual_totals = annual.assign(denominator=annual.motorist_deaths + annual.cyclist_deaths)[["year", "denominator"]]
    values2 = values2.merge(annual_totals, on="year", validate="many_to_one")
    values2["share"] = values2.deaths / values2.denominator
    values2["share_percent"] = values2.share * 100
    values2.to_csv(OUT / "values_2.csv", index=False)

    pivot = values2.pivot(index="year", columns="road_user", values="share_percent")
    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    ax.bar(pivot.index, pivot.motorist, color=colors["motorist"], label="Motorist")
    ax.bar(pivot.index, pivot.cyclist, bottom=pivot.motorist,
           color=colors["cyclist"], label="Cyclist")
    ax.set_title("Share of motorist-plus-cyclist deaths in police-reported NYC crashes, 2013–2025", pad=22)
    ax.text(0.5, 1.015, "Each bar totals 100%; share of these two recorded road-user categories",
            transform=ax.transAxes, ha="center", va="bottom", fontsize=9)
    ax.set_xlabel("Crash year")
    ax.set_ylabel("Share of combined deaths (%)")
    ax.set_xticks(pivot.index)
    ax.set_ylim(0, 100)
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, ncol=2, loc="upper right")
    ax.text(0, -0.22,
            "Limitation: denominator includes only motorists and cyclists killed in police-reported crashes.",
            transform=ax.transAxes, ha="left", va="top", fontsize=8.5)
    fig.tight_layout()
    fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
