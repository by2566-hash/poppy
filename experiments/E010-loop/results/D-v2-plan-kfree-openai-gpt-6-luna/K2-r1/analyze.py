import csv
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


OUT = Path("out")
DATA = "data/crashes.parquet"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

con = duckdb.connect()
date_filter = "crash_date BETWEEN DATE '2013-01-01' AND DATE '2025-12-31'"
daily = con.execute(
    f"""
    SELECT year(crash_date) AS year, isodow(crash_date) AS weekday_num, count(*) AS crash_count
    FROM read_parquet('{DATA}')
    WHERE {date_filter}
    GROUP BY year, weekday_num
    ORDER BY year, weekday_num
    """
).df()

weekday_totals = (daily.groupby("weekday_num", as_index=False)["crash_count"].sum()
                  .set_index("weekday_num").reindex(range(1, 8), fill_value=0)
                  .rename_axis("weekday_num").reset_index())
weekday_totals["weekday"] = WEEKDAYS
population_total = int(weekday_totals["crash_count"].sum())
weekday_totals["share_pct"] = weekday_totals["crash_count"] / population_total * 100

with (OUT / "values_1.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["weekday", "crash_count", "eligible_total"])
    for row in weekday_totals.itertuples(index=False):
        writer.writerow([row.weekday, int(row.crash_count), population_total])

fig, ax = plt.subplots(figsize=(10, 5.8))
bars = ax.bar(weekday_totals["weekday"], weekday_totals["crash_count"], color="#277da1")
ax.set_title(f"Police-reported NYC crash count by weekday\n2013–2025 (n={population_total:,} dated records)", pad=16)
ax.set_ylabel("Crash records")
ax.set_xlabel("Day of week")
ax.grid(axis="y", alpha=0.25)
ax.spines[["top", "right"]].set_visible(False)
ax.tick_params(axis="x", rotation=20)
ax.bar_label(bars, labels=[f"{int(v):,}" for v in weekday_totals["crash_count"]], padding=3, fontsize=9)
fig.text(0.5, 0.015, "Limitation: police-reported crashes only; full year endpoints are observed, but reporting completeness is not established.", ha="center", fontsize=8.5)
fig.tight_layout(rect=[0, 0.055, 1, 1])
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

with (OUT / "values_2.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["weekday", "crash_count", "eligible_total", "share_pct"])
    for row in weekday_totals.itertuples(index=False):
        writer.writerow([row.weekday, int(row.crash_count), population_total, f"{row.share_pct:.6f}"])

fig, ax = plt.subplots(figsize=(9.5, 5.8))
bars = ax.barh(weekday_totals["weekday"], weekday_totals["share_pct"], color="#43aa8b")
ax.invert_yaxis()
ax.set_title(f"Share of police-reported NYC crashes by weekday\n2013–2025; denominator = {population_total:,} dated records", pad=16)
ax.set_xlabel("Share of all eligible crash records (%)")
ax.set_ylabel("Day of week")
ax.grid(axis="x", alpha=0.25)
ax.spines[["top", "right"]].set_visible(False)
ax.bar_label(bars, labels=[f"{v:.2f}%" for v in weekday_totals["share_pct"]], padding=4, fontsize=9)
fig.text(0.5, 0.015, "Limitation: composition of police-reported records, not all real-world crashes; reporting completeness is not established.", ha="center", fontsize=8.5)
fig.tight_layout(rect=[0, 0.055, 1, 1])
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)

annual = daily.pivot(index="year", columns="weekday_num", values="crash_count").reindex(
    index=range(2013, 2026), columns=range(1, 8), fill_value=0
).fillna(0).astype(int)
annual_totals = annual.sum(axis=1)
annual_shares = annual.div(annual_totals, axis=0) * 100

with (OUT / "values_3.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["year", "weekday", "crash_count", "year_total", "share_pct"])
    for year in annual.index:
        for weekday_num, weekday in enumerate(WEEKDAYS, start=1):
            writer.writerow([
                int(year), weekday, int(annual.loc[year, weekday_num]),
                int(annual_totals.loc[year]), f"{annual_shares.loc[year, weekday_num]:.6f}"
            ])

fig, ax = plt.subplots(figsize=(10.5, 7.2))
image = ax.imshow(annual_shares.to_numpy(), aspect="auto", cmap="YlGnBu", vmin=annual_shares.to_numpy().min(), vmax=annual_shares.to_numpy().max())
ax.set_xticks(range(7), WEEKDAYS, rotation=30, ha="right")
ax.set_yticks(range(len(annual_shares.index)), annual_shares.index)
ax.set_title("Within-year share of police-reported NYC crash records by weekday\n2013–2025; each year's denominator is that year's dated records", pad=18)
ax.set_xlabel("Day of week")
ax.set_ylabel("Calendar year")
for i in range(len(annual_shares.index)):
    for j in range(7):
        value = annual_shares.iloc[i, j]
        ax.text(j, i, f"{value:.1f}%", ha="center", va="center", fontsize=7.5,
                color="white" if value >= annual_shares.to_numpy().mean() + 0.6 else "black")
cbar = fig.colorbar(image, ax=ax, pad=0.02)
cbar.set_label("Share of that year's crash records (%)")
fig.text(0.5, 0.015, "Limitation: shares describe police-reported records and do not adjust for reporting or exposure changes.", ha="center", fontsize=8.5)
fig.tight_layout(rect=[0, 0.045, 1, 1])
fig.savefig(OUT / "option_3.png", dpi=180, bbox_inches="tight")
plt.close(fig)
