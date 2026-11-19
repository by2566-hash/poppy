import csv
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
data_path = str(DATA).replace("'", "''")
con = duckdb.connect()

annual = con.execute(
    f"""
    SELECT year(crash_date) AS year,
           sum(number_of_motorist_killed) AS motorists_killed,
           count(*) AS crash_records,
           count(*) FILTER (WHERE number_of_motorist_killed > 0) AS crashes_with_motorist_death
    FROM read_parquet('{data_path}')
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
    """
).fetchall()

# Framing 1: annual deaths count (no exposure denominator).
values_1 = OUT / "values_1.csv"
with values_1.open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["year", "motorists_killed", "crash_records"])
    writer.writerows((year, killed, crashes) for year, killed, crashes, _ in annual)

years = [row[0] for row in annual]
deaths = [row[1] for row in annual]
fig, ax = plt.subplots(figsize=(10, 5.5))
ax.plot(years, deaths, marker="o", linewidth=2, color="#2a6f97")
ax.set_title("Motorists killed in NYC police-reported crashes, by crash year", pad=28)
ax.text(
    0.5, 1.015,
    "Annual count, 2013–2025; not per-mile risk (vehicle-miles traveled unavailable)",
    transform=ax.transAxes, ha="center", va="bottom", fontsize=9,
)
ax.set_xlabel("Calendar year of crash_date")
ax.set_ylabel("Reported motorists killed")
ax.set_xticks(years)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Framing 2: fatal crash record share among all reported crashes.
values_2 = OUT / "values_2.csv"
with values_2.open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["year", "crashes_with_motorist_death", "all_crash_records", "share_percent"])
    for year, _, crashes, fatal_crashes in annual:
        writer.writerow([year, fatal_crashes, crashes, 100 * fatal_crashes / crashes])

shares = [100 * row[3] / row[2] for row in annual]
fig, ax = plt.subplots(figsize=(10, 5.5))
ax.plot(years, shares, marker="o", linewidth=2, color="#bc4749")
ax.set_title("Share of NYC police-reported crash records with a motorist death", pad=28)
ax.text(
    0.5, 1.015,
    "Annual share, 2013–2025; records with ≥1 motorist killed / all crash records; not per-mile risk",
    transform=ax.transAxes, ha="center", va="bottom", fontsize=9,
)
ax.set_xlabel("Calendar year of crash_date")
ax.set_ylabel("Crash records involving motorist death (%)")
ax.set_xticks(years)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)
