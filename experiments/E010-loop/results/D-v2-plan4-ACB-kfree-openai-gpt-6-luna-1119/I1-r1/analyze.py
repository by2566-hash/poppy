from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"
con = duckdb.connect()
annual = con.execute(
    """
    SELECT year(crash_date) AS year,
           count(*) AS crash_records,
           sum(number_of_motorist_killed) AS motorist_deaths
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
      AND number_of_motorist_killed IS NOT NULL
    GROUP BY year
    ORDER BY year
    """,
    [str(DATA)],
).df()
con.close()
annual["motorist_deaths_per_1000_crashes"] = (
    1000 * annual["motorist_deaths"] / annual["crash_records"]
)

annual[["year", "motorist_deaths", "crash_records"]].to_csv(
    OUT / "values_1.csv", index=False
)
annual[
    ["year", "motorist_deaths", "crash_records", "motorist_deaths_per_1000_crashes"]
].to_csv(OUT / "values_2.csv", index=False)

plt.rcParams.update({"font.size": 10, "axes.titlesize": 14, "axes.labelsize": 11})

fig, ax = plt.subplots(figsize=(11, 6))
ax.bar(annual["year"], annual["motorist_deaths"], color="#2369a1", width=0.75)
ax.set_title(
    "Annual count of reported motorist deaths in NYC police-reported crashes\n"
    "(2013–2025)",
    loc="left",
    pad=34,
)
ax.text(
    0,
    1.015,
    "Per-mile risk cannot be measured: the crash data contain no miles-driven denominator.",
    transform=ax.transAxes,
    color="#555555",
    fontsize=9,
    va="bottom",
)
ax.set_xlabel("Calendar year of crash")
ax.set_ylabel("Reported motorist deaths")
ax.set_xticks(annual["year"])
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(11, 6))
ax.plot(
    annual["year"],
    annual["motorist_deaths_per_1000_crashes"],
    color="#a74336",
    marker="o",
    linewidth=2,
)
ax.set_title(
    "Reported motorist deaths per 1,000 NYC police-reported crashes\n"
    "with known motorist-death counts (2013–2025)",
    loc="left",
    pad=34,
)
ax.text(
    0,
    1.015,
    "Not a per-mile measure: no miles-driven denominator. 2019–20 denominator falls by 98,568 crash records.",
    transform=ax.transAxes,
    color="#555555",
    fontsize=9,
    va="bottom",
)
ax.set_xlabel("Calendar year of crash")
ax.set_ylabel("Reported motorist deaths per 1,000 crash records")
ax.set_xticks(annual["year"])
ax.tick_params(axis="x", rotation=45)
ax.grid(alpha=0.25)
fig.tight_layout()
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)
