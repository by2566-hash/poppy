import csv

import duckdb
import matplotlib.pyplot as plt


DATA_PATH = "data/crashes.parquet"
VALUES_PATH = "out/values_1.csv"
CHART_PATH = "out/option_1.png"

connection = duckdb.connect()
values = connection.execute(
    """
    SELECT
        EXTRACT(YEAR FROM crash_date)::INTEGER AS year,
        SUM(number_of_pedestrians_killed)::BIGINT AS pedestrian_fatalities
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
    """,
    [DATA_PATH],
).fetchall()

with open(VALUES_PATH, "w", newline="") as output:
    writer = csv.writer(output)
    writer.writerow(["year", "pedestrian_fatalities"])
    writer.writerows(values)

years = [row[0] for row in values]
fatalities = [row[1] for row in values]

fig, ax = plt.subplots(figsize=(11, 6))
ax.bar(years, fatalities, color="#2878B5", width=0.78)
ax.set_xticks(years)
ax.set_xticklabels(years, rotation=45, ha="right")
ax.set_ylabel("Pedestrian fatalities (count)")
ax.set_xlabel("Crash year")
ax.set_title(
    "Annual pedestrian fatalities in police-reported NYC motor vehicle crashes, 2013–2025",
    loc="left",
    pad=32,
)
ax.text(
    0,
    1.02,
    "Counts use number_of_pedestrians_killed summed by crash_date year; unreported crashes/deaths are not captured.",
    transform=ax.transAxes,
    ha="left",
    va="bottom",
    fontsize=9,
)
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(CHART_PATH, dpi=180, bbox_inches="tight")
plt.close(fig)
