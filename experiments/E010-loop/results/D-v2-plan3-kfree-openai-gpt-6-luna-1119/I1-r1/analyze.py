import duckdb
import matplotlib.pyplot as plt
import pandas as pd


DATA = "data/crashes.parquet"
con = duckdb.connect()

annual = con.execute(
    """
    SELECT
        year(crash_date) AS year,
        count(*) AS crash_rows,
        sum(number_of_motorist_killed) AS reported_motorist_deaths,
        count(*) FILTER (WHERE number_of_motorist_killed > 0) AS crashes_with_motorist_death
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year(crash_date)
    ORDER BY year
    """,
    [DATA],
).fetchdf()
annual["motorist_deaths_per_1000_crashes"] = (
    1000 * annual["reported_motorist_deaths"] / annual["crash_rows"]
)
annual["crashes_with_motorist_death_pct"] = (
    100 * annual["crashes_with_motorist_death"] / annual["crash_rows"]
)

values_1 = annual[["year", "reported_motorist_deaths", "crash_rows", "motorist_deaths_per_1000_crashes"]]
values_1.to_csv("out/values_1.csv", index=False)
fig, ax = plt.subplots(figsize=(10, 5.6))
ax.plot(annual["year"], annual["motorist_deaths_per_1000_crashes"], marker="o", linewidth=2)
ax.set_title("Reported motorist deaths per 1,000 police-reported NYC crashes", pad=35)
ax.text(
    0.5,
    1.02,
    "Complete calendar years 2013–2025; all eligible crash records",
    transform=ax.transAxes,
    ha="center",
    va="bottom",
    fontsize=10,
)
ax.set_xlabel("Crash year")
ax.set_ylabel("Reported motorist deaths per 1,000 crashes")
ax.set_xticks(annual["year"])
ax.grid(axis="y", alpha=0.3)
fig.text(0.5, 0.015, "Limitation: miles driven are not in this dataset, so this is not deaths per mile.", ha="center", fontsize=9)
fig.tight_layout(rect=(0, 0.05, 1, 0.94))
fig.savefig("out/option_1.png", dpi=180)
plt.close(fig)

values_2 = annual[["year", "crashes_with_motorist_death", "crash_rows", "crashes_with_motorist_death_pct"]]
values_2.to_csv("out/values_2.csv", index=False)
fig, ax = plt.subplots(figsize=(10, 5.6))
ax.plot(annual["year"], annual["crashes_with_motorist_death_pct"], marker="o", linewidth=2, color="#d55e00")
ax.set_title("Share of police-reported NYC crashes with a motorist death", pad=35)
ax.text(
    0.5,
    1.02,
    "A crash qualifies when its reported motorist-death count is greater than zero; 2013–2025",
    transform=ax.transAxes,
    ha="center",
    va="bottom",
    fontsize=9,
)
ax.set_xlabel("Crash year")
ax.set_ylabel("Crashes with ≥1 motorist death (%)")
ax.set_xticks(annual["year"])
ax.grid(axis="y", alpha=0.3)
fig.text(0.5, 0.015, "Limitation: miles driven are not in this dataset, so this is not deaths per mile.", ha="center", fontsize=9)
fig.tight_layout(rect=(0, 0.05, 1, 0.94))
fig.savefig("out/option_2.png", dpi=180)
plt.close(fig)
