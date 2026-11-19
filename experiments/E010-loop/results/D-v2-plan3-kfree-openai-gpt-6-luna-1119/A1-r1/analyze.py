from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


OUT = Path(__file__).parent
DATA = OUT.parent / "data" / "crashes.parquet"
START_YEAR = 2013
END_YEAR = 2025

con = duckdb.connect()
source = f"read_parquet('{DATA.as_posix()}')"
base_filter = (
    "lower(trim(borough)) = 'brooklyn' "
    f"AND crash_date >= DATE '{START_YEAR}-01-01' "
    f"AND crash_date < DATE '{END_YEAR + 1}-01-01'"
)

casualties = con.execute(
    f"""
    SELECT year(crash_date) AS year,
           sum(number_of_pedestrians_injured) AS pedestrian_injuries,
           sum(number_of_pedestrians_killed) AS pedestrian_deaths,
           sum(number_of_pedestrians_injured + number_of_pedestrians_killed)
               AS pedestrian_casualties
    FROM {source}
    WHERE {base_filter}
    GROUP BY year
    ORDER BY year
    """
).df()
casualties[["pedestrian_injuries", "pedestrian_deaths", "pedestrian_casualties"]] = (
    casualties[["pedestrian_injuries", "pedestrian_deaths", "pedestrian_casualties"]]
    .astype("int64")
)
casualties.to_csv(OUT / "values_1.csv", index=False)

deaths = casualties[["year", "pedestrian_deaths"]].rename(
    columns={"pedestrian_deaths": "pedestrian_deaths"}
)
deaths["pedestrian_deaths"] = deaths["pedestrian_deaths"].astype("int64")
deaths.to_csv(OUT / "values_2.csv", index=False)

crash_share = con.execute(
    f"""
    SELECT year(crash_date) AS year,
           count(*) AS brooklyn_crash_rows,
           count(*) FILTER (
               WHERE number_of_pedestrians_injured > 0
                  OR number_of_pedestrians_killed > 0
           ) AS crashes_with_pedestrian_casualty,
           100.0 * count(*) FILTER (
               WHERE number_of_pedestrians_injured > 0
                  OR number_of_pedestrians_killed > 0
           ) / count(*) AS share_pct
    FROM {source}
    WHERE {base_filter}
    GROUP BY year
    ORDER BY year
    """
).df()
crash_share.to_csv(OUT / "values_3.csv", index=False)


def make_line_chart(df, y_column, title, subtitle, ylabel, filename, color):
    fig, ax = plt.subplots(figsize=(10.5, 6.2))
    ax.plot(df["year"], df[y_column], color=color, linewidth=2.7, marker="o", markersize=5)
    ax.set_title(title, loc="left", fontsize=17, fontweight="bold", pad=24)
    ax.text(
        0,
        1.015,
        subtitle,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=9.5,
        color="#555555",
    )
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Crash year", fontsize=11)
    ax.set_xticks(df["year"])
    ax.set_xticklabels(df["year"].astype(int), rotation=45, ha="right")
    ax.grid(axis="y", color="#d9d9d9", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#999999")
    ax.tick_params(axis="both", labelsize=9, color="#999999")
    ax.margins(x=0.035)
    fig.tight_layout()
    fig.savefig(OUT / filename, dpi=180, bbox_inches="tight")
    plt.close(fig)


make_line_chart(
    casualties,
    "pedestrian_casualties",
    "Pedestrians injured or killed in Brooklyn crashes, 2013–2025",
    "Annual reported people injured + killed; counts are not exposure-adjusted safety rates. Complete years only.",
    "Pedestrian casualties (people)",
    "option_1.png",
    "#b33c2e",
)
make_line_chart(
    deaths,
    "pedestrian_deaths",
    "Pedestrian deaths in Brooklyn crashes, 2013–2025",
    "Annual reported deaths; counts are not exposure-adjusted fatality rates. Complete years only.",
    "Pedestrian deaths (people)",
    "option_2.png",
    "#303f8c",
)
make_line_chart(
    crash_share,
    "share_pct",
    "Share of Brooklyn crash reports with a pedestrian casualty, 2013–2025",
    "Each crash record counts once; this is not a pedestrian-exposure risk rate. Complete years only.",
    "Crash records with pedestrian injury/death (%)",
    "option_3.png",
    "#087e73",
)
