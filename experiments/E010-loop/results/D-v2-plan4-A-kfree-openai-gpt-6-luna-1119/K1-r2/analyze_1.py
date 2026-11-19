import csv

import duckdb
import matplotlib.pyplot as plt


PARQUET = "data/crashes.parquet"
START_YEAR = 2013
END_YEAR = 2025

db = duckdb.connect()
rows = db.execute(
    """
    SELECT year(crash_date) AS year,
           sum(number_of_pedestrians_killed) AS pedestrian_deaths
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
    """,
    [PARQUET],
).fetchall()

with open("out/values_1.csv", "w", newline="") as output:
    writer = csv.writer(output)
    writer.writerow(["year", "pedestrian_deaths"])
    writer.writerows(rows)

years = [row[0] for row in rows]
deaths = [row[1] for row in rows]

fig, ax = plt.subplots(figsize=(10, 5.8))
bars = ax.bar(years, deaths, color="#286090", width=0.72)
ax.bar_label(bars, padding=3, fontsize=8)
ax.set_title(
    "Pedestrian deaths recorded in police-reported NYC motor vehicle crashes\n"
    "Annual count, grouped by crash year (2013–2025)",
    loc="left",
    fontsize=13,
    pad=14,
)
ax.text(
    0,
    1.01,
    "Limitation: police-reported crashes only; observed dates span each full calendar year.",
    transform=ax.transAxes,
    fontsize=9,
    color="#555555",
)
ax.set_xlabel("Calendar year of crash")
ax.set_ylabel("Pedestrian deaths (sum of recorded deaths)")
ax.set_xticks(range(START_YEAR, END_YEAR + 1))
ax.grid(axis="y", color="#dddddd", linewidth=0.7)
ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig("out/option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)
