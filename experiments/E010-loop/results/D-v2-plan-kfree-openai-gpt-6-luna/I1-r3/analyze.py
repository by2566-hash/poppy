from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
PARQUET = ROOT / "data" / "crashes.parquet"
YEARS = list(range(2013, 2026))

parquet_path = str(PARQUET).replace("'", "''")
con = duckdb.connect()
annual = con.execute(
    f"""
    SELECT year(crash_date)::INTEGER AS year,
           count(*)::BIGINT AS crash_records,
           sum(number_of_motorist_killed)::BIGINT AS motorist_deaths,
           count(*) FILTER (WHERE number_of_motorist_killed > 0)::BIGINT AS crashes_with_motorist_death
    FROM read_parquet('{parquet_path}')
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
    """
).fetchdf()
con.close()

annual["motorist_deaths_per_1000_crash_records"] = annual["motorist_deaths"] / annual["crash_records"] * 1000
annual["share_crashes_with_motorist_death_percent"] = annual["crashes_with_motorist_death"] / annual["crash_records"] * 100

if annual["year"].tolist() != YEARS:
    raise ValueError("Unexpected missing or extra year in the final planned population")

values1 = annual[["year", "motorist_deaths"]].copy()
values1.to_csv(OUT / "values_1.csv", index=False, float_format="%.6f")

values2 = annual[["year", "motorist_deaths", "crash_records", "motorist_deaths_per_1000_crash_records"]].copy()
values2.to_csv(OUT / "values_2.csv", index=False, float_format="%.6f")

values3 = annual[["year", "crashes_with_motorist_death", "crash_records", "share_crashes_with_motorist_death_percent"]].copy()
values3.to_csv(OUT / "values_3.csv", index=False, float_format="%.6f")

plt.rcParams.update({"font.size": 10, "axes.titlesize": 13, "axes.labelsize": 10})

fig, ax = plt.subplots(figsize=(10, 5.5))
ax.bar(annual["year"].astype(str), annual["motorist_deaths"], color="#28677e")
ax.set_title("Annual motorist deaths in police-reported NYC crashes\n2013–2025; count of motorists killed", loc="left", pad=24)
ax.text(0, 1.01, "Not a per-mile risk: miles driven are not recorded in this crash file.", transform=ax.transAxes, fontsize=9, color="#555555", va="bottom")
ax.set_xlabel("Crash year")
ax.set_ylabel("Motorists killed (count)")
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 5.5))
ax.plot(annual["year"], annual["motorist_deaths_per_1000_crash_records"], marker="o", linewidth=2.2, color="#b05237")
ax.set_title("Motorist deaths per 1,000 police-reported NYC crashes\n2013–2025; all crash records in each year's denominator", loc="left", pad=24)
ax.text(0, 1.01, "Crash-volume adjusted, not per-mile risk: miles driven are not recorded.", transform=ax.transAxes, fontsize=9, color="#555555", va="bottom")
ax.set_xlabel("Crash year")
ax.set_ylabel("Motorist deaths per 1,000 crash records")
ax.set_xticks(YEARS)
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 5.5))
ax.plot(annual["year"], annual["share_crashes_with_motorist_death_percent"], marker="o", linewidth=2.2, color="#5b7d42")
ax.set_title("Share of police-reported NYC crashes with a motorist death\n2013–2025; crash-level proportion", loc="left", pad=24)
ax.text(0, 1.01, "Not individual per-mile risk: miles driven and motorist exposure are not recorded.", transform=ax.transAxes, fontsize=9, color="#555555", va="bottom")
ax.set_xlabel("Crash year")
ax.set_ylabel("Crashes with ≥1 motorist killed (%)")
ax.set_xticks(YEARS)
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(OUT / "option_3.png", dpi=180, bbox_inches="tight")
plt.close(fig)
