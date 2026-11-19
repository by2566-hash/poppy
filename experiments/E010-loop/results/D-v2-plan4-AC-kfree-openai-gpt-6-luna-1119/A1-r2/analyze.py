import csv
import json
from pathlib import Path

import duckdb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titleweight": "bold",
})

con = duckdb.connect()
source = f"read_parquet('{DATA.as_posix()}')"
plans = [json.loads((OUT / f"plan_{i}.json").read_text()) for i in (1, 2, 3)]

for plan in plans:
    pid = plan["id"]
    if pid == 1:
        value_col = "pedestrian_casualties"
        aggregate = "sum(number_of_pedestrians_injured + number_of_pedestrians_killed)"
        outcome_filter = "number_of_pedestrians_injured IS NOT NULL AND number_of_pedestrians_killed IS NOT NULL"
        color = "#1667A8"
        label = "Pedestrians injured or killed"
        chart_title = "Pedestrian casualties in Brooklyn police-reported crashes"
        metric_note = "Casualties = pedestrians injured + pedestrians killed"
    elif pid == 2:
        value_col = "pedestrians_killed"
        aggregate = "sum(number_of_pedestrians_killed)"
        outcome_filter = "number_of_pedestrians_killed IS NOT NULL"
        color = "#B4232D"
        label = "Pedestrians killed"
        chart_title = "Pedestrian deaths in Brooklyn police-reported crashes"
        metric_note = "Fatality count summed across Brooklyn crash records"
    else:
        value_col = "pedestrians_injured"
        aggregate = "sum(number_of_pedestrians_injured)"
        outcome_filter = "number_of_pedestrians_injured IS NOT NULL"
        color = "#D17A00"
        label = "Pedestrians injured"
        chart_title = "Pedestrian injuries in Brooklyn police-reported crashes"
        metric_note = "Injury count summed across Brooklyn crash records"

    rows = con.execute(
        f"SELECT year(crash_date) AS year, {aggregate} AS \"{value_col}\" "
        f"FROM {source} "
        "WHERE crash_date BETWEEN DATE '2013-01-01' AND DATE '2025-12-31' "
        "AND lower(trim(coalesce(borough, ''))) = 'brooklyn' "
        f"AND {outcome_filter} "
        "GROUP BY 1 ORDER BY 1"
    ).fetchall()
    years = [int(row[0]) for row in rows]
    values = [int(row[1]) for row in rows]

    value_path = OUT / f"values_{pid}.csv"
    with value_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["year", value_col])
        writer.writerows(zip(years, values))

    fig, ax = plt.subplots(figsize=(10.8, 6.2))
    fig.subplots_adjust(top=0.78, bottom=0.15, left=0.11, right=0.96)
    ax.plot(years, values, color=color, linewidth=2.8, marker="o", markersize=6.5,
            markerfacecolor="white", markeredgewidth=2.2)
    ax.fill_between(years, values, [0] * len(values), color=color, alpha=0.08)
    ax.set_xlim(2012.6, 2025.4)
    ax.set_xticks(years)
    ax.set_xticklabels([str(y) for y in years], rotation=45, ha="right")
    ax.set_ylim(bottom=0)
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    ax.set_ylabel(f"People per calendar year ({label.lower()})", labelpad=10)
    ax.set_xlabel("Crash year", labelpad=10)
    ax.grid(axis="y", color="#D8DEE6", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["left"].set_color("#AAB3BE")
    ax.spines["bottom"].set_color("#AAB3BE")
    ax.annotate(f"{values[0]:,}", (years[0], values[0]), xytext=(6, 9),
                textcoords="offset points", fontsize=9, fontweight="bold", color=color)
    ax.annotate(f"{values[-1]:,}", (years[-1], values[-1]), xytext=(-6, 9),
                textcoords="offset points", ha="right", fontsize=9,
                fontweight="bold", color=color)
    fig.suptitle(chart_title,
                 x=0.11, y=0.96, ha="left", fontsize=16, fontweight="bold")
    fig.text(0.11, 0.865,
             f"Annual count · {metric_note} · Complete years 2013–2025",
             ha="left", fontsize=9.5, color="#4B5563")
    fig.text(0.11, 0.825,
             "Not exposure-adjusted risk · 2026 partial and excluded · "
             "crashes with unknown borough excluded",
             ha="left", fontsize=9.5, color="#4B5563")
    fig.savefig(OUT / f"option_{pid}.png", dpi=180, facecolor="white")
    plt.close(fig)

    print(pid, years[0], values[0], years[-1], values[-1], len(rows))
