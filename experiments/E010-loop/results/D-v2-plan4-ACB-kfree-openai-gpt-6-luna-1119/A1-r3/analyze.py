from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


DATA = "data/crashes.parquet"
OUT = Path("out")
YEARS = list(range(2013, 2026))

con = duckdb.connect()
annual = con.execute(
    f"""
    SELECT YEAR(crash_date) AS year,
           COUNT(*) AS brooklyn_crash_rows,
           SUM(number_of_pedestrians_injured) AS pedestrian_injured,
           SUM(number_of_pedestrians_killed) AS pedestrian_killed,
           COUNT(*) FILTER (
               WHERE number_of_pedestrians_injured > 0
                  OR number_of_pedestrians_killed > 0
           ) AS crashes_with_pedestrian_casualty
    FROM read_parquet('{DATA}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
      AND UPPER(TRIM(COALESCE(borough, ''))) = 'BROOKLYN'
    GROUP BY YEAR(crash_date)
    ORDER BY year
    """
).df()
con.close()

annual = annual.set_index("year").reindex(YEARS).fillna(0).reset_index()
annual["year"] = annual["year"].astype(int)
for col in [
    "brooklyn_crash_rows",
    "pedestrian_injured",
    "pedestrian_killed",
    "crashes_with_pedestrian_casualty",
]:
    annual[col] = annual[col].astype(int)
annual["pedestrian_casualties"] = annual["pedestrian_injured"] + annual["pedestrian_killed"]
annual["share_crashes_with_pedestrian_casualty_pct"] = (
    100 * annual["crashes_with_pedestrian_casualty"] / annual["brooklyn_crash_rows"]
)

values_1 = annual[[
    "year", "pedestrian_injured", "pedestrian_killed", "pedestrian_casualties",
    "brooklyn_crash_rows",
]]
values_1.to_csv(OUT / "values_1.csv", index=False)

values_2 = annual[[
    "year", "crashes_with_pedestrian_casualty", "brooklyn_crash_rows",
    "share_crashes_with_pedestrian_casualty_pct",
]].rename(columns={
    "crashes_with_pedestrian_casualty": "crash_rows_with_pedestrian_casualty",
    "brooklyn_crash_rows": "all_eligible_brooklyn_crash_rows_denominator",
    "share_crashes_with_pedestrian_casualty_pct": "share_pct",
})
values_2.to_csv(OUT / "values_2.csv", index=False)

values_3 = annual[["year", "pedestrian_killed", "brooklyn_crash_rows"]].rename(columns={
    "pedestrian_killed": "pedestrians_killed",
})
values_3.to_csv(OUT / "values_3.csv", index=False)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titlesize": 17,
    "axes.labelsize": 11,
})

def decorate(ax, title, subtitle, ylabel):
    ax.set_title(title, loc="left", pad=30, fontweight="bold")
    ax.text(
        0, 1.025, subtitle, transform=ax.transAxes,
        ha="left", va="bottom", fontsize=9, color="#4B5563",
    )
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Crash year")
    ax.set_xticks(YEARS)
    ax.set_xticklabels(YEARS, rotation=45, ha="right")
    ax.grid(axis="y", color="#D9DEE7", linewidth=0.8)
    ax.set_axisbelow(True)


fig, ax = plt.subplots(figsize=(10, 5.8), constrained_layout=True)
ax.plot(YEARS, annual["pedestrian_casualties"], color="#176B87", linewidth=2.8,
        marker="o", markersize=5)
decorate(
    ax,
    "Pedestrian casualties in Brooklyn, 2013–2025",
    "Injured + killed in police-reported crashes; not adjusted for pedestrian exposure. Partial 2026 omitted.",
    "Reported pedestrian casualties",
)
ax.set_ylim(bottom=0)
fig.text(0.01, -0.02, "Source: NYC police-reported motor vehicle crash records", fontsize=8, color="#596273")
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 5.8), constrained_layout=True)
ax.plot(YEARS, annual["share_crashes_with_pedestrian_casualty_pct"], color="#B55233",
        linewidth=2.8, marker="o", markersize=5)
decorate(
    ax,
    "Brooklyn crash reports involving a pedestrian casualty, 2013–2025",
    "Share of Brooklyn police-reported crash rows; not a per-trip risk measure. Partial 2026 omitted.",
    "Share of crash reports (%)",
)
ax.set_ylim(bottom=0)
fig.text(0.01, -0.02, "Source: NYC police-reported motor vehicle crash records", fontsize=8, color="#596273")
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 5.8), constrained_layout=True)
ax.bar(YEARS, annual["pedestrian_killed"], color="#713B75", width=0.72)
decorate(
    ax,
    "Pedestrians killed in Brooklyn crashes, 2013–2025",
    "Reported pedestrian deaths; a severe but narrow measure, not adjusted for pedestrian exposure. Partial 2026 omitted.",
    "Reported pedestrian deaths",
)
ax.set_ylim(bottom=0)
fig.text(0.01, -0.02, "Source: NYC police-reported motor vehicle crash records", fontsize=8, color="#596273")
fig.savefig(OUT / "option_3.png", dpi=180, bbox_inches="tight")
plt.close(fig)
