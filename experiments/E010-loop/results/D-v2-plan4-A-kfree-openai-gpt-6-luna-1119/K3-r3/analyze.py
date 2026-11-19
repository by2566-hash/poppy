import csv
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
source = (ROOT / "data" / "crashes.parquet").as_posix().replace("'", "''")
data = duckdb.connect().execute(
    f"""
    SELECT year(crash_date) AS year,
           sum(number_of_motorist_killed)::BIGINT AS motorist_deaths,
           sum(number_of_cyclist_killed)::BIGINT AS cyclist_deaths
    FROM read_parquet('{source}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year(crash_date)
    ORDER BY year
    """
).fetchall()
years = [row[0] for row in data]
motorist = [int(row[1]) for row in data]
cyclist = [int(row[2]) for row in data]
combined = [m + c for m, c in zip(motorist, cyclist)]
motorist_pct = [100 * m / d for m, d in zip(motorist, combined)]
cyclist_pct = [100 * c / d for c, d in zip(cyclist, combined)]

with (OUT / "values_1.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(("year", "motorist_deaths", "cyclist_deaths"))
    writer.writerows(zip(years, motorist, cyclist))

with (OUT / "values_2.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(("year", "motorist_deaths", "cyclist_deaths", "combined_deaths", "motorist_share_pct", "cyclist_share_pct"))
    writer.writerows(zip(years, motorist, cyclist, combined, motorist_pct, cyclist_pct))

plt.style.use("seaborn-v0_8-whitegrid")
fig, ax = plt.subplots(figsize=(10, 5.8))
ax.plot(years, motorist, marker="o", linewidth=2.4, color="#245a9b", label="Motorist deaths")
ax.plot(years, cyclist, marker="o", linewidth=2.4, color="#e27628", label="Cyclist deaths")
ax.set_title("Annual motorist and cyclist deaths in police-reported NYC crashes, 2013–2025", fontsize=13, pad=22)
ax.text(0.5, 1.015, "Recorded deaths; unadjusted counts (not exposure-adjusted)", transform=ax.transAxes, ha="center", va="bottom", fontsize=9, color="#555555")
ax.set_xlabel("Crash year")
ax.set_ylabel("People killed (annual total)")
ax.set_xticks(years)
ax.tick_params(axis="x", rotation=45)
ax.legend(frameon=False, ncol=2, loc="upper left", bbox_to_anchor=(1.01, 1.0))
fig.tight_layout()
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 5.8))
ax.bar(years, motorist_pct, color="#245a9b", label="Motorist share")
ax.bar(years, cyclist_pct, bottom=motorist_pct, color="#e27628", label="Cyclist share")
ax.set_title("Annual motorist and cyclist shares of their combined deaths in police-reported NYC crashes, 2013–2025", fontsize=13, pad=22)
ax.text(0.5, 1.015, "Composition only: excludes other road-user deaths and does not show absolute totals", transform=ax.transAxes, ha="center", va="bottom", fontsize=9, color="#555555")
ax.set_xlabel("Crash year")
ax.set_ylabel("Share of annual motorist + cyclist deaths")
ax.set_ylim(0, 100)
ax.set_xticks(years)
ax.tick_params(axis="x", rotation=45)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
ax.legend(frameon=False, ncol=2, loc="upper left", bbox_to_anchor=(1.01, 1.0))
fig.tight_layout()
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)
