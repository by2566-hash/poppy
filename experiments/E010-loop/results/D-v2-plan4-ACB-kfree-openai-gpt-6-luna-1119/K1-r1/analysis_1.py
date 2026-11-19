from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
query = """
    SELECT
        year(crash_date)::INTEGER AS year,
        sum(number_of_pedestrians_killed)::BIGINT AS pedestrians_killed
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
"""
values = duckdb.connect().execute(query, [str(ROOT / "data" / "crashes.parquet")]).df()
values.to_csv(OUT / "values_1.csv", index=False)

fig, ax = plt.subplots(figsize=(10, 5.8))
bars = ax.bar(values["year"].astype(str), values["pedestrians_killed"], color="#3b82a0")
ax.bar_label(bars, fmt="{:,.0f}", padding=3, fontsize=8)
ax.set_title("Pedestrians killed per year in police-reported NYC motor vehicle crashes\n2013–2025; sum of recorded pedestrian fatalities")
ax.set_xlabel("Crash year")
ax.set_ylabel("Pedestrians killed (count)")
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)
fig.text(
    0.01,
    0.01,
    "Limitation: counts are recorded in this police-reported crash file; completeness beyond its reporting scope is not verified.",
    ha="left",
    fontsize=8,
)
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
