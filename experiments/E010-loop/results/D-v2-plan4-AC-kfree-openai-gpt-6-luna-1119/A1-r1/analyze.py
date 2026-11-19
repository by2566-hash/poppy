import csv
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
DATA = (ROOT / "data" / "crashes.parquet").as_posix()
con = duckdb.connect()
con.execute(f"CREATE VIEW crashes AS SELECT * FROM read_parquet('{DATA}')")

annual = con.execute(
    """
    SELECT
      EXTRACT(YEAR FROM crash_date)::INTEGER AS year,
      SUM(number_of_pedestrians_injured)::BIGINT AS reported_pedestrian_injuries,
      SUM(number_of_pedestrians_killed)::BIGINT AS reported_pedestrian_deaths
    FROM crashes
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
      AND upper(trim(borough)) = 'BROOKLYN'
    GROUP BY 1
    ORDER BY 1
    """
).df()

# The data check found complete outcome columns and Brooklyn crash records for
# every full calendar year in the final plan; still reindex to make year coverage
# explicit and avoid silently omitting a year if source data change.
annual = annual.set_index("year").reindex(range(2013, 2026)).rename_axis("year").reset_index()
if annual.isna().any().any():
    raise ValueError("Unexpected missing year or outcome in the final-plan population")
annual["reported_pedestrian_casualties"] = (
    annual["reported_pedestrian_injuries"] + annual["reported_pedestrian_deaths"]
)

annual.to_csv(OUT / "values_1.csv", index=False, quoting=csv.QUOTE_MINIMAL)
annual[["year", "reported_pedestrian_deaths"]].to_csv(
    OUT / "values_2.csv", index=False, quoting=csv.QUOTE_MINIMAL
)

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})

fig, ax = plt.subplots(figsize=(10.8, 6.2))
ax.plot(
    annual["year"], annual["reported_pedestrian_casualties"],
    color="#155D86", linewidth=3, marker="o", markersize=5.5,
)
ax.fill_between(annual["year"], annual["reported_pedestrian_casualties"], color="#155D86", alpha=0.10)
ax.set_title("Pedestrian injuries and deaths in Brooklyn crashes", loc="left", fontsize=17, weight="bold", pad=36)
ax.text(
    0, 1.025,
    "Annual reported pedestrian casualties • Brooklyn • 2013–2025\nCrash counts, not exposure-adjusted; borough is missing on 30.9% of dated city crashes; partial 2026 omitted.",
    transform=ax.transAxes, ha="left", va="bottom", fontsize=9.5, color="#404040", linespacing=1.5,
)
ax.set_ylabel("Reported pedestrians injured or killed")
ax.set_xlabel("Crash year")
ax.set_xticks(annual["year"])
ax.set_xticklabels(annual["year"], rotation=45, ha="right")
ax.grid(axis="y", color="#D9E0E5", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.set_ylim(bottom=0)
ax.annotate(
    f"{int(annual.iloc[0]['reported_pedestrian_casualties']):,}",
    (annual.iloc[0]["year"], annual.iloc[0]["reported_pedestrian_casualties"]),
    xytext=(6, 8), textcoords="offset points", color="#155D86", fontsize=9, weight="bold",
)
ax.annotate(
    f"{int(annual.iloc[-1]['reported_pedestrian_casualties']):,}",
    (annual.iloc[-1]["year"], annual.iloc[-1]["reported_pedestrian_casualties"]),
    xytext=(-5, 9), textcoords="offset points", ha="right", color="#155D86", fontsize=9, weight="bold",
)
fig.tight_layout(rect=(0, 0, 1, 0.92))
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight", facecolor="white")
plt.close(fig)

fig, ax = plt.subplots(figsize=(10.8, 6.2))
ax.plot(
    annual["year"], annual["reported_pedestrian_deaths"],
    color="#B23A48", linewidth=3, marker="o", markersize=5.5,
)
ax.fill_between(annual["year"], annual["reported_pedestrian_deaths"], color="#B23A48", alpha=0.10)
ax.set_title("Pedestrians killed in Brooklyn crashes", loc="left", fontsize=17, weight="bold", pad=36)
ax.text(
    0, 1.025,
    "Annual reported pedestrian deaths • Brooklyn • 2013–2025\nCrash counts, not exposure-adjusted; borough is missing on 30.9% of dated city crashes; partial 2026 omitted.",
    transform=ax.transAxes, ha="left", va="bottom", fontsize=9.5, color="#404040", linespacing=1.5,
)
ax.set_ylabel("Reported pedestrian deaths")
ax.set_xlabel("Crash year")
ax.set_xticks(annual["year"])
ax.set_xticklabels(annual["year"], rotation=45, ha="right")
ax.grid(axis="y", color="#D9E0E5", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.set_ylim(bottom=0)
ax.annotate(
    f"{int(annual.iloc[0]['reported_pedestrian_deaths']):,}",
    (annual.iloc[0]["year"], annual.iloc[0]["reported_pedestrian_deaths"]),
    xytext=(6, 8), textcoords="offset points", color="#B23A48", fontsize=9, weight="bold",
)
ax.annotate(
    f"{int(annual.iloc[-1]['reported_pedestrian_deaths']):,}",
    (annual.iloc[-1]["year"], annual.iloc[-1]["reported_pedestrian_deaths"]),
    xytext=(-5, 9), textcoords="offset points", ha="right", color="#B23A48", fontsize=9, weight="bold",
)
fig.tight_layout(rect=(0, 0, 1, 0.92))
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight", facecolor="white")
plt.close(fig)

print(annual.to_string(index=False))
