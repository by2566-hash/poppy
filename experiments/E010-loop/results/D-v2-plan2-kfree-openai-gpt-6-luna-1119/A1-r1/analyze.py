from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"

con = duckdb.connect()
path = str(DATA).replace("'", "''")
yearly = con.execute(
    f"""
    SELECT year(crash_date) AS year,
           sum(number_of_pedestrians_injured) AS pedestrian_injured,
           sum(number_of_pedestrians_killed) AS pedestrian_killed
    FROM read_parquet('{path}')
    WHERE upper(trim(borough)) = 'BROOKLYN'
      AND crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year(crash_date)
    ORDER BY year
    """
).df()
yearly["year"] = yearly["year"].astype(int)
yearly["pedestrian_injured"] = yearly["pedestrian_injured"].astype("int64")
yearly["pedestrian_killed"] = yearly["pedestrian_killed"].astype("int64")
yearly["total_pedestrian_casualties"] = yearly["pedestrian_injured"] + yearly["pedestrian_killed"]

values_1 = yearly[["year", "pedestrian_injured", "pedestrian_killed", "total_pedestrian_casualties"]]
values_1.to_csv(OUT / "values_1.csv", index=False)
values_2 = yearly[["year", "pedestrian_killed"]].rename(columns={"pedestrian_killed": "pedestrian_fatalities"})
values_2.to_csv(OUT / "values_2.csv", index=False)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.titleweight": "bold",
    "axes.titlesize": 19,
    "axes.labelsize": 11,
})


def draw_series(years, values, *, title, subtitle, ylabel, color, outfile, value_format):
    fig, ax = plt.subplots(figsize=(10.5, 6.2))
    fig.patch.set_facecolor("#f7f5ef")
    ax.set_facecolor("#f7f5ef")
    ax.plot(years, values, color=color, linewidth=3.2, marker="o", markersize=6.5,
            markerfacecolor="#f7f5ef", markeredgewidth=2.2)
    ax.fill_between(years, values, min(0, min(values)), color=color, alpha=0.10)
    ax.set_title(title, loc="left", pad=34, color="#17232d")
    ax.text(0, 1.035, subtitle, transform=ax.transAxes, fontsize=10.5,
            color="#42515d", va="bottom")
    ax.set_ylabel(ylabel, color="#34434e", labelpad=8)
    ax.set_xticks(years)
    ax.set_xticklabels([str(year) for year in years], rotation=0)
    ax.set_xlim(min(years) - 0.35, max(years) + 0.8)
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", color="#cbd0cf", linewidth=0.8, alpha=0.75)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#85919a")
    ax.tick_params(axis="y", length=0, colors="#47545d")
    ax.tick_params(axis="x", length=0, pad=8, colors="#47545d")
    ax.annotate(value_format(values[0]), (years[0], values[0]), xytext=(4, 9),
                textcoords="offset points", color=color, fontsize=10, fontweight="bold")
    ax.annotate(value_format(values[-1]), (years[-1], values[-1]), xytext=(8, 9),
                textcoords="offset points", color=color, fontsize=10, fontweight="bold")
    fig.text(0.01, 0.015,
             "Source: NYC police-reported motor-vehicle crash records. Counts, not exposure-adjusted risk; 2026 partial through June 11 is excluded.",
             fontsize=8.5, color="#58646c")
    fig.tight_layout(rect=(0, 0.055, 1, 1))
    fig.savefig(OUT / outfile, dpi=180, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


years = values_1["year"].tolist()
draw_series(
    years,
    values_1["total_pedestrian_casualties"].tolist(),
    title="Pedestrian casualties in Brooklyn crashes",
    subtitle="Annual people injured + killed · police-reported motor-vehicle crashes",
    ylabel="Pedestrians injured or killed",
    color="#b64632",
    outfile="option_1.png",
    value_format=lambda value: f"{value:,}",
)
draw_series(
    years,
    values_2["pedestrian_fatalities"].tolist(),
    title="Pedestrian deaths in Brooklyn crashes",
    subtitle="Annual people killed · police-reported motor-vehicle crashes",
    ylabel="Pedestrians killed",
    color="#245a73",
    outfile="option_2.png",
    value_format=lambda value: f"{value:,}",
)

for filename in ("values_1.csv", "values_2.csv"):
    table = pd.read_csv(OUT / filename)
    print(filename)
    print(table.iloc[[0, -1]].to_string(index=False))
