from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
PARQUET = ROOT / "data" / "crashes.parquet"

parquet_sql_path = str(PARQUET).replace("'", "''")
con = duckdb.connect()
data = con.execute(
    f"""SELECT year(crash_date) AS year,
               sum(number_of_pedestrians_killed)::BIGINT AS pedestrian_deaths_recorded,
               count(*)::BIGINT AS crash_rows
        FROM read_parquet('{parquet_sql_path}')
        WHERE crash_date >= DATE '2013-01-01'
          AND crash_date < DATE '2026-01-01'
        GROUP BY year
        ORDER BY year"""
).df()

expected_years = list(range(2013, 2026))
if data["year"].tolist() != expected_years:
    raise ValueError(f"Unexpected years in result: {data['year'].tolist()}")
data.to_csv(OUT / "values_1.csv", index=False)

plt.figure(figsize=(12, 6.5))
bars = plt.bar(
    data["year"].astype(str),
    data["pedestrian_deaths_recorded"],
    color="#3274A1",
    width=0.72,
)
plt.title(
    "Annual pedestrian deaths recorded in NYC police-reported motor vehicle crashes\n"
    "Sum of per-crash pedestrian-killed counts, 2013–2025",
    fontsize=15,
    pad=16,
)
plt.ylabel("Pedestrian deaths recorded (count)")
plt.xlabel("Calendar year of crash")
plt.grid(axis="y", alpha=0.25)
plt.gca().set_axisbelow(True)
plt.bar_label(bars, fmt="%.0f", padding=3, fontsize=8)
plt.figtext(
    0.5,
    0.015,
    "Limitation: counts reflect the supplied police-reported crash file; date coverage is Jan–Dec in each year, but external completeness is not verified.",
    ha="center",
    fontsize=8,
    wrap=True,
)
plt.tight_layout(rect=(0, 0.05, 1, 1))
plt.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close()
