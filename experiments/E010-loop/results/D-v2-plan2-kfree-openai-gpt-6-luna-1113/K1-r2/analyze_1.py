import duckdb
import matplotlib.pyplot as plt
import pandas as pd


DATA_PATH = "data/crashes.parquet"
VALUES_PATH = "out/values_1.csv"
CHART_PATH = "out/option_1.png"

con = duckdb.connect()
values = con.execute(
    """
    SELECT
      year(crash_date) AS year,
      sum(number_of_pedestrians_killed)::BIGINT AS pedestrian_fatalities
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
    """,
    [DATA_PATH],
).df()
values["year"] = values["year"].astype(int)
values.to_csv(VALUES_PATH, index=False)

fig, ax = plt.subplots(figsize=(11, 6.5))
ax.bar(values["year"].astype(str), values["pedestrian_fatalities"], color="#2463A6", width=0.72)
ax.set_title(
    "Annual recorded pedestrian fatalities in police-reported NYC motor vehicle crashes",
    fontsize=14,
    weight="bold",
    pad=24,
)
ax.text(
    0.5,
    1.015,
    "Crash year 2013–2025; reported records only (date bounds span each full calendar year)",
    transform=ax.transAxes,
    ha="center",
    va="bottom",
    fontsize=9,
    color="#444444",
)
ax.set_xlabel("Calendar year of crash")
ax.set_ylabel("Pedestrians killed (annual count)")
ax.grid(axis="y", color="#D9DEE5", linewidth=0.7)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.tight_layout()
fig.savefig(CHART_PATH, dpi=180, bbox_inches="tight")
plt.close(fig)
