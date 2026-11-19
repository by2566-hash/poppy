from pathlib import Path

import duckdb
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"

con = duckdb.connect()
values = con.execute(
    """
    SELECT year(crash_date) AS year,
           sum(number_of_pedestrians_killed)::BIGINT AS pedestrians_killed
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date <= DATE '2025-12-31'
    GROUP BY year(crash_date)
    ORDER BY year
    """,
    [str(DATA)],
).df()
values["year"] = values["year"].astype(int)
values["pedestrians_killed"] = values["pedestrians_killed"].astype(int)
values.to_csv(OUT / "values_2.csv", index=False)

fig, ax = plt.subplots(figsize=(11, 6.2))
bars = ax.bar(
    values["year"],
    values["pedestrians_killed"],
    color="#176B87",
    width=0.72,
)
ax.set_title(
    "Annual count of pedestrians killed in police-reported NYC motor vehicle crashes, 2013–2025",
    fontsize=14,
    pad=26,
)
ax.text(
    0.5,
    1.015,
    "Annual totals from crash reports; deaths are not independently validated",
    transform=ax.transAxes,
    ha="center",
    va="bottom",
    fontsize=9,
    color="#555555",
)
ax.set_xlabel("Calendar year of crash")
ax.set_ylabel("Pedestrians killed (count)")
ax.set_xticks(values["year"])
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)
ax.bar_label(bars, padding=3, fontsize=8)
fig.tight_layout()
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)
