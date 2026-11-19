import duckdb
import matplotlib.pyplot as plt
import pandas as pd

SOURCE = "./data/crashes.parquet"
START_YEAR = 2013
END_YEAR = 2025

values = duckdb.connect().execute(
    """
    SELECT
        year(crash_date) AS year,
        sum(number_of_pedestrians_killed) AS reported_pedestrian_deaths
    FROM read_parquet(?)
    WHERE crash_date >= make_date(?, 1, 1)
      AND crash_date < make_date(? + 1, 1, 1)
    GROUP BY year(crash_date)
    ORDER BY year
    """,
    [SOURCE, START_YEAR, END_YEAR],
).df()
values["year"] = values["year"].astype(int)
values["reported_pedestrian_deaths"] = values["reported_pedestrian_deaths"].astype(int)
values.to_csv("./out/values_1.csv", index=False)

plt.style.use("seaborn-v0_8-whitegrid")
fig, ax = plt.subplots(figsize=(11, 6.5))
ax.bar(values["year"].astype(str), values["reported_pedestrian_deaths"], color="#2b6f8a", width=0.72)
ax.set_title(
    "Annual reported pedestrian deaths in NYC motor vehicle crashes\n"
    "Population: all police-reported crash records, 2013–2025",
    loc="left",
    fontsize=15,
    weight="bold",
    pad=18,
)
ax.text(
    0,
    1.015,
    "Limitation: reported counts only; these are counts, not exposure-adjusted rates.",
    transform=ax.transAxes,
    fontsize=10,
    color="#555555",
)
ax.set_xlabel("Calendar year of crash")
ax.set_ylabel("Sum of reported pedestrians killed")
ax.tick_params(axis="x", rotation=0)
ax.set_ylim(bottom=0)
fig.tight_layout(rect=(0, 0, 1, 0.93))
fig.savefig("./out/option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

print(values.to_string(index=False))
