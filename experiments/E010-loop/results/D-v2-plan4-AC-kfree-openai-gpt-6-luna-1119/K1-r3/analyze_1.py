from pathlib import Path

import duckdb
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"

data = duckdb.sql(
    """
    SELECT
        year(crash_date) AS year,
        sum(number_of_pedestrians_killed) AS pedestrians_killed
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
    """,
    params=[str(DATA)],
).df()

data.to_csv(OUT / "values_1.csv", index=False)

fig, ax = plt.subplots(figsize=(10, 5.5))
bars = ax.bar(data["year"].astype(str), data["pedestrians_killed"], color="#176B87")
ax.bar_label(bars, fmt="%.0f", padding=3, fontsize=8)
ax.set_title(
    "Pedestrians killed in police-reported NYC motor vehicle crashes\n"
    "Annual sum of recorded pedestrian fatalities, by crash year",
    fontsize=13,
    pad=15,
)
ax.set_xlabel("Calendar year of crash")
ax.set_ylabel("Pedestrians killed (count)")
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)
fig.text(
    0.5,
    0.01,
    "2013–2025; full calendar-year coverage. Counts reflect police-reported crash records and are not independently validated.",
    ha="center",
    fontsize=8,
)
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
