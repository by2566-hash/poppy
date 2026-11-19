import csv
import json
from pathlib import Path

import duckdb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
NAVY = "#17324d"
TEAL = "#078b87"
CORAL = "#dc6655"
GRAY = "#687985"
con = duckdb.connect()

rows = con.execute(
    """
    SELECT year(crash_date) AS year,
           sum(number_of_pedestrians_injured) AS pedestrian_injuries,
           sum(number_of_pedestrians_killed) AS pedestrian_deaths,
           count(*) AS brooklyn_crash_rows,
           count(*) FILTER (WHERE number_of_pedestrians_injured + number_of_pedestrians_killed > 0)
             AS crashes_with_pedestrian_casualty
    FROM read_parquet(?)
    WHERE lower(trim(coalesce(borough,''))) = 'brooklyn'
      AND crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
      AND number_of_pedestrians_injured IS NOT NULL
      AND number_of_pedestrians_killed IS NOT NULL
    GROUP BY year ORDER BY year
    """,
    [str(DATA)],
).fetchall()

years = [r[0] for r in rows]
injuries = [int(r[1]) for r in rows]
deaths = [int(r[2]) for r in rows]
crash_rows = [int(r[3]) for r in rows]
casualty_crashes = [int(r[4]) for r in rows]
casualties = [a + b for a, b in zip(injuries, deaths)]
shares = [100 * n / d for n, d in zip(casualty_crashes, crash_rows)]


def style_axis(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cad3d8")
    ax.spines["bottom"].set_color("#cad3d8")
    ax.tick_params(colors=GRAY, labelsize=9)
    ax.grid(axis="y", color="#e5eaed", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_xticks(years)
    ax.set_xticklabels([str(y) for y in years], rotation=45, ha="right")


def save_values(option_id, headers, value_rows):
    with (OUT / f"values_{option_id}.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(value_rows)


def plot(option_id, title, subtitle, metric_label, values, color, chart_type="line", percent=False):
    fig, ax = plt.subplots(figsize=(10.8, 5.9), dpi=170)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    if chart_type == "bar":
        ax.bar(years, values, color=CORAL, width=0.72)
    else:
        ax.plot(years, values, color=color, linewidth=2.8, marker="o", markersize=5.2,
                markerfacecolor="white", markeredgewidth=2)
        ax.scatter([years[-1]], [values[-1]], color=color, s=42, zorder=4)
    style_axis(ax)
    if percent:
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=100, decimals=0))
    ax.set_ylabel(metric_label, fontsize=10, color=NAVY, labelpad=10)
    ax.set_xlabel("Crash year", fontsize=10, color=NAVY, labelpad=8)
    fig.suptitle(title, x=0.09, y=0.97, ha="left", fontsize=16, fontweight="bold", color=NAVY)
    fig.text(0.09, 0.91, subtitle, ha="left", fontsize=9.4, color=GRAY)
    fig.text(0.09, 0.025, "Source: NYC police-reported motor vehicle crash records. Complete calendar years only.",
             ha="left", fontsize=8, color=GRAY)
    fig.subplots_adjust(left=0.1, right=0.98, top=0.83, bottom=0.19)
    fig.savefig(OUT / f"option_{option_id}.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


for option_id in (1, 2, 3):
    plan = json.loads((OUT / f"plan_{option_id}.json").read_text())
    assert plan["years"] == "Complete calendar years 2013 through 2025; exclude 2026 because coverage ends 2026-06-11"

save_values(1,
            ["year", "pedestrian_injuries", "pedestrian_deaths", "pedestrian_casualties", "brooklyn_crash_rows"],
            zip(years, injuries, deaths, casualties, crash_rows))
plot(1,
     "Pedestrian casualties in Brooklyn crashes, 2013–2025",
     "Injured + killed pedestrians per year; counts from police-reported crashes, not adjusted for walking exposure.",
     "Pedestrian casualties", casualties, TEAL)

save_values(2,
            ["year", "pedestrians_killed", "brooklyn_crash_rows"],
            zip(years, deaths, crash_rows))
plot(2,
     "Pedestrians killed in Brooklyn crashes, 2013–2025",
     "Annual fatalities in police-reported crashes; counts do not measure risk per pedestrian trip.",
     "Pedestrians killed", deaths, CORAL, chart_type="bar")

save_values(3,
            ["year", "crashes_with_pedestrian_casualty", "brooklyn_crash_rows", "share_percent"],
            zip(years, casualty_crashes, crash_rows, shares))
plot(3,
     "Brooklyn crashes involving pedestrian casualties, 2013–2025",
     "Share of crash reports with ≥1 pedestrian injured or killed; denominator is all Brooklyn crash reports.",
     "Share of Brooklyn crash reports", shares, NAVY, percent=True)
