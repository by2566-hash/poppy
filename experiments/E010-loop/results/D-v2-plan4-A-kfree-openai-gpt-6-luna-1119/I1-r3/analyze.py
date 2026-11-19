import csv

import duckdb
import matplotlib.pyplot as plt

PARQUET = "data/crashes.parquet"
YEARS = list(range(2013, 2026))

rows = duckdb.connect().execute(
    """
    SELECT year(crash_date) AS year,
           count(*) AS crash_rows,
           sum(number_of_motorist_killed) AS motorists_killed
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
      AND number_of_motorist_killed IS NOT NULL
    GROUP BY year
    ORDER BY year
    """,
    [PARQUET],
).fetchall()

by_year = {year: (crashes, killed) for year, crashes, killed in rows}
if list(by_year) != YEARS:
    raise ValueError(f"Expected one result for each year 2013-2025; got {list(by_year)}")

data = [
    {
        "year": year,
        "crash_rows_with_observed_motorist_killed": by_year[year][0],
        "motorists_killed": by_year[year][1],
        "motorists_killed_per_1000_crashes": 1000 * by_year[year][1] / by_year[year][0],
    }
    for year in YEARS
]

with open("out/values_1.csv", "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
with open("out/values_2.csv", "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)

plt.figure(figsize=(10, 5.6))
plt.plot([d["year"] for d in data], [d["motorists_killed"] for d in data], marker="o", linewidth=2)
plt.xticks(YEARS, rotation=45)
plt.ylabel("Motorists killed (people)")
plt.title("Annual motorists killed in police-reported NYC crashes, 2013–2025", pad=38)
plt.suptitle("Annual total; all dated crash rows with observed motorist-killed values\nNot a per-mile risk measure: miles driven are unavailable.", y=0.96, fontsize=9)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout(rect=(0, 0, 1, 0.89))
plt.savefig("out/option_1.png", dpi=180, bbox_inches="tight")
plt.close()

plt.figure(figsize=(10, 5.6))
plt.plot(
    [d["year"] for d in data],
    [d["motorists_killed_per_1000_crashes"] for d in data],
    marker="o",
    linewidth=2,
)
plt.xticks(YEARS, rotation=45)
plt.ylabel("Motorists killed per 1,000 crashes")
plt.title("Motorists killed per 1,000 police-reported NYC crashes, 2013–2025", pad=38)
plt.suptitle("Denominator: dated crash rows with observed motorist-killed values\nCrash-based rate, not per-mile risk: miles driven are unavailable.", y=0.96, fontsize=9)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout(rect=(0, 0, 1, 0.89))
plt.savefig("out/option_2.png", dpi=180, bbox_inches="tight")
plt.close()
