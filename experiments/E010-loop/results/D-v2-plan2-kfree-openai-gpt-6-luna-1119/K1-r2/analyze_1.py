import csv
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"

data_path = str(DATA).replace("'", "''")
con = duckdb.connect()
rows = con.execute(
    f"""
    SELECT YEAR(crash_date) AS year,
           SUM(number_of_pedestrians_killed) AS pedestrians_killed
    FROM read_parquet('{data_path}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
    """
).fetchall()
con.close()

expected_years = list(range(2013, 2026))
values = {int(year): int(count) for year, count in rows}
if set(values) != set(expected_years):
    raise ValueError(f"Expected one group for each year 2013–2025; got {sorted(values)}")

values_path = OUT / "values_1.csv"
with values_path.open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["year", "pedestrians_killed"])
    writer.writerows((year, values[year]) for year in expected_years)

fig, ax = plt.subplots(figsize=(11, 6.2))
bars = ax.bar(expected_years, [values[year] for year in expected_years], color="#276FBF", width=0.72)
ax.set_title(
    "Pedestrians killed per year in NYC police-reported motor vehicle crashes\n2013–2025",
    fontsize=15,
    pad=20,
)
ax.set_xlabel("Crash year")
ax.set_ylabel("Pedestrian deaths (people)")
ax.set_xticks(expected_years)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)
ax.bar_label(bars, labels=[f"{values[year]:,}" for year in expected_years], padding=3, fontsize=8)
fig.text(
    0.5,
    0.015,
    "Counts include police-reported crashes; endpoint dates are present for each year, but within-year completeness is unverified.",
    ha="center",
    fontsize=9,
)
fig.tight_layout(rect=[0, 0.055, 1, 1])
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)
