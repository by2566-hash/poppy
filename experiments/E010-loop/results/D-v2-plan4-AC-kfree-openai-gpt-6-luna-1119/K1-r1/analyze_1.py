import csv
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt


root = Path(__file__).resolve().parent.parent
con = duckdb.connect()
values = con.execute(
    """
    SELECT year(crash_date) AS year,
           sum(number_of_pedestrians_killed)::BIGINT AS pedestrian_fatalities
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
    """,
    [str(root / "data" / "crashes.parquet")],
).fetchall()

with (root / "out" / "values_1.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["year", "pedestrian_fatalities"])
    writer.writerows(values)

years = [row[0] for row in values]
counts = [row[1] for row in values]
fig, ax = plt.subplots(figsize=(11, 6.2))
bars = ax.bar(years, counts, color="#2676a8", width=0.72)
ax.set_title(
    "Pedestrian fatalities in police-reported NYC motor vehicle crashes, by year",
    fontsize=14,
    weight="bold",
    pad=34,
)
ax.text(
    0.5,
    1.015,
    "Sum of pedestrian deaths recorded per crash; complete calendar-year date coverage in the file",
    transform=ax.transAxes,
    ha="center",
    va="bottom",
    fontsize=9,
    color="#4d5963",
)
ax.set_xlabel("Calendar year of crash")
ax.set_ylabel("Pedestrians killed (count)")
ax.set_xticks(years)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", color="#d9e0e5", linewidth=0.8)
ax.set_axisbelow(True)
for bar, count in zip(bars, counts):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5, f"{count}", ha="center", va="bottom", fontsize=8)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.text(
    0.01,
    0.01,
    "Limitation: counts include only police-reported crashes and fatalities recorded in this dataset.",
    ha="left",
    fontsize=8,
    color="#4d5963",
)
fig.tight_layout(rect=(0, 0.04, 1, 0.98))
fig.savefig(root / "out" / "option_1.png", dpi=180, bbox_inches="tight")
