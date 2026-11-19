import csv

import duckdb
import matplotlib.pyplot as plt

DATA = "data/crashes.parquet"
VALUES = "out/values_1.csv"
CHART = "out/option_1.png"

con = duckdb.connect()
rows = con.execute(f"""
    SELECT YEAR(crash_date) AS year,
           SUM(number_of_pedestrians_killed)::BIGINT AS pedestrians_killed
    FROM read_parquet('{DATA}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY YEAR(crash_date)
    ORDER BY year
""").fetchall()

with open(VALUES, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["year", "pedestrians_killed"])
    writer.writerows(rows)

years = [row[0] for row in rows]
counts = [row[1] for row in rows]

fig, ax = plt.subplots(figsize=(10, 5.8))
ax.plot(years, counts, marker="o", linewidth=2.2, color="#176B87")
ax.set_xticks(years)
ax.set_xticklabels(years, rotation=45, ha="right")
ax.set_ylabel("Pedestrians killed (recorded count)")
ax.set_xlabel("Calendar year of crash")
ax.set_title("Annual pedestrians killed in police-reported NYC motor vehicle crashes\n2013–2025; sum of recorded pedestrian deaths per crash", loc="left", pad=16)
fig.text(
    0.125,
    0.015,
    "Limitation: police-reported crash records; full date bounds do not establish reporting completeness.",
    ha="left",
    fontsize=9,
    color="#555555",
)
ax.grid(axis="y", alpha=0.25)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(rect=(0, 0.06, 1, 1))
fig.savefig(CHART, dpi=180, bbox_inches="tight")
