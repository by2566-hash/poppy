import sys
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


option_id = int(sys.argv[1])
root = Path(__file__).resolve().parents[1]
out = Path(__file__).resolve().parent
data = root / "data" / "crashes.parquet"
chart_type = "bar" if option_id == 1 else "line"

con = duckdb.connect()
query = """
    SELECT year(crash_date) AS year,
           sum(number_of_pedestrians_killed)::BIGINT AS pedestrians_killed
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
"""
values = con.execute(query, [str(data)]).df()
values.to_csv(out / f"values_{option_id}.csv", index=False)

fig, ax = plt.subplots(figsize=(10, 5.8))
if chart_type == "bar":
    ax.bar(values["year"], values["pedestrians_killed"], color="#176B87", width=0.72)
else:
    ax.plot(
        values["year"], values["pedestrians_killed"],
        color="#176B87", marker="o", linewidth=2.4, markersize=5.5,
    )
ax.set_xticks(values["year"])
ax.set_xlabel("Calendar year of crash")
ax.set_ylabel("Pedestrians killed (annual total)")
ax.set_ylim(bottom=0)
ax.set_title("Annual pedestrians killed in NYC motor vehicle crashes, 2013–2025", pad=28)
fig.text(
    0.5, 0.925,
    "Police-reported crash records; full calendar years. Counts, not rates.",
    ha="center", va="center", fontsize=9, color="#444444",
)
ax.grid(axis="y", alpha=0.25)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(rect=(0, 0, 1, 0.9))
fig.savefig(out / f"option_{option_id}.png", dpi=180, bbox_inches="tight")
plt.close(fig)
