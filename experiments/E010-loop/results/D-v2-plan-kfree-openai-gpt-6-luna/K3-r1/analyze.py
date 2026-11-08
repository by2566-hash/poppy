import csv
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import numpy as np


DATA = Path("data/crashes.parquet")
OUT = Path("out")
YEARS = list(range(2013, 2026))
con = duckdb.connect()
annual = con.execute(
    """
    SELECT YEAR(crash_date) AS year,
           SUM(number_of_motorist_killed) AS motorists,
           SUM(number_of_cyclist_killed) AS cyclists
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY year ORDER BY year
    """,
    [str(DATA)],
).fetchall()
annual_by_year = {row[0]: (int(row[1]), int(row[2])) for row in annual}
annual_by_year = {year: annual_by_year.get(year, (0, 0)) for year in YEARS}

groups = [("Motorist", 0), ("Cyclist", 1)]
values_1 = []
for year in YEARS:
    deaths = annual_by_year[year]
    for label, index in groups:
        values_1.append((year, label, deaths[index]))
with open(OUT / "values_1.csv", "w", newline="") as output:
    writer = csv.writer(output)
    writer.writerow(["year", "death_group", "deaths"])
    writer.writerows(values_1)

plt.figure(figsize=(10.5, 5.8))
for label, index, color in [("Motorist", 0, "#1f77b4"), ("Cyclist", 1, "#e67e22")]:
    plt.plot(
        YEARS,
        [annual_by_year[year][index] for year in YEARS],
        marker="o",
        linewidth=2.2,
        markersize=5,
        color=color,
        label=label,
    )
plt.title("Annual reported motorist and cyclist deaths in NYC crashes, 2013–2025", pad=14)
plt.xlabel("Crash year")
plt.ylabel("People killed (sum of crash-report counts)")
plt.xticks(YEARS, rotation=45)
plt.grid(axis="y", alpha=0.25)
plt.legend(frameon=False)
plt.figtext(
    0.5,
    0.01,
    "All police-reported NYC motor vehicle crashes; counts are not adjusted for population or travel exposure.",
    ha="center",
    fontsize=9,
)
plt.tight_layout(rect=(0, 0.05, 1, 1))
plt.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close()

values_2 = []
for year in YEARS:
    motorist_deaths, cyclist_deaths = annual_by_year[year]
    denominator = motorist_deaths + cyclist_deaths
    for label, deaths in [("Motorist", motorist_deaths), ("Cyclist", cyclist_deaths)]:
        share_pct = 100 * deaths / denominator if denominator else 0
        values_2.append((year, label, deaths, denominator, share_pct))
with open(OUT / "values_2.csv", "w", newline="") as output:
    writer = csv.writer(output)
    writer.writerow(["year", "death_group", "deaths", "motorist_plus_cyclist_deaths", "share_pct"])
    writer.writerows(values_2)

motorist_share = np.array(
    [100 * annual_by_year[year][0] / sum(annual_by_year[year]) if sum(annual_by_year[year]) else 0 for year in YEARS]
)
cyclist_share = 100 - motorist_share
plt.figure(figsize=(10.5, 5.8))
plt.bar(YEARS, motorist_share, color="#1f77b4", label="Motorist")
plt.bar(YEARS, cyclist_share, bottom=motorist_share, color="#e67e22", label="Cyclist")
plt.title("Share of reported motorist and cyclist deaths in NYC crashes, 2013–2025", pad=14)
plt.xlabel("Crash year")
plt.ylabel("Share of motorist + cyclist deaths")
plt.ylim(0, 100)
plt.yticks(np.arange(0, 101, 20), [f"{value}%" for value in range(0, 101, 20)])
plt.xticks(YEARS, rotation=45)
plt.grid(axis="y", alpha=0.25)
plt.legend(frameon=False, loc="upper right")
plt.figtext(
    0.5,
    0.01,
    "Denominator includes only motorist and cyclist deaths; pedestrian deaths are excluded.",
    ha="center",
    fontsize=9,
)
plt.tight_layout(rect=(0, 0.05, 1, 1))
plt.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close()
