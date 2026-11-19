import csv

import duckdb
import matplotlib.pyplot as plt

PARQUET = "./data/crashes.parquet"
VALUES = "./out/values_1.csv"
CHART = "./out/option_1.png"

con = duckdb.connect()
rows = con.execute(
    f"""
    SELECT year(crash_date) AS year,
           sum(number_of_pedestrians_killed)::BIGINT AS pedestrian_deaths
    FROM read_parquet('{PARQUET}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
    """
).fetchall()

with open(VALUES, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["year", "pedestrians_killed_recorded_count"])
    writer.writerows(rows)

years = [row[0] for row in rows]
deaths = [row[1] for row in rows]

fig, ax = plt.subplots(figsize=(11, 6))
ax.bar(years, deaths, color="#2878A8", width=0.78)
ax.set_title(
    "Pedestrians killed in NYC police-reported motor vehicle crashes\n"
    "Annual recorded count, 2013–2025",
    loc="left",
    fontsize=14,
    weight="bold",
    pad=16,
)
ax.text(
    0,
    1.01,
    "Raw counts; not adjusted for crash volume or pedestrian exposure. "
    "Observed date bounds cover every year; reporting completeness is unverified.",
    transform=ax.transAxes,
    fontsize=9,
    color="#555555",
    va="bottom",
)
ax.set_xlabel("Year of crash date")
ax.set_ylabel("Pedestrians killed (recorded count)")
ax.set_xticks(years)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(CHART, dpi=180, bbox_inches="tight")
