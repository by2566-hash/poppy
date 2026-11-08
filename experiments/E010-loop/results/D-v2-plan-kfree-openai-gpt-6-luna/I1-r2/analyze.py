import duckdb
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
SOURCE = (ROOT / "data" / "crashes.parquet").as_posix().replace("'", "''")

con = duckdb.connect()
base = f"""
    SELECT year(crash_date)::INTEGER AS year,
           number_of_motorist_killed
    FROM read_parquet('{SOURCE}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
      AND number_of_motorist_killed IS NOT NULL
      AND number_of_motorist_killed >= 0
"""

deaths = con.execute(
    f"""
    SELECT year, sum(number_of_motorist_killed)::BIGINT AS motorist_deaths,
           count(*)::BIGINT AS included_crashes
    FROM ({base})
    GROUP BY year
    ORDER BY year
    """
).fetchdf()
years = pd.DataFrame({"year": range(2013, 2026)})
deaths = years.merge(deaths, how="left", on="year").fillna(0)
deaths[["year", "motorist_deaths", "included_crashes"]] = deaths[
    ["year", "motorist_deaths", "included_crashes"]
].astype("int64")
deaths.to_csv(OUT / "values_1.csv", index=False)

fig, ax = plt.subplots(figsize=(10.5, 5.8))
ax.bar(deaths["year"], deaths["motorist_deaths"], color="#246B8E", width=0.72)
ax.set_title(
    "Annual motorist deaths in police-reported NYC crashes\n2013–2025",
    loc="left", fontsize=15, weight="bold", pad=20,
)
ax.text(
    0, 1.025,
    "Absolute reported-death count, not adjusted for miles driven; within-year date continuity not evaluated.",
    transform=ax.transAxes, fontsize=9, color="#555555", va="bottom",
)
ax.set_xlabel("Crash year")
ax.set_ylabel("Motorist deaths (people)")
ax.set_xticks(deaths["year"])
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

share = con.execute(
    f"""
    SELECT year,
           count(*) FILTER (WHERE number_of_motorist_killed >= 1)::BIGINT
               AS crashes_with_motorist_death,
           count(*)::BIGINT AS eligible_crashes
    FROM ({base})
    GROUP BY year
    ORDER BY year
    """
).fetchdf()
share = years.merge(share, how="left", on="year").fillna(0)
share[["year", "crashes_with_motorist_death", "eligible_crashes"]] = share[
    ["year", "crashes_with_motorist_death", "eligible_crashes"]
].astype("int64")
share["crash_share"] = share["crashes_with_motorist_death"] / share["eligible_crashes"]
share["crash_share_percent"] = 100 * share["crash_share"]
share.to_csv(OUT / "values_2.csv", index=False, float_format="%.8f")

fig, ax = plt.subplots(figsize=(10.5, 5.8))
ax.plot(
    share["year"], share["crash_share_percent"],
    color="#B55532", marker="o", linewidth=2.2, markersize=5.5,
)
ax.set_title(
    "Crashes with ≥1 motorist death as a share of police-reported NYC crashes\n2013–2025",
    loc="left", fontsize=15, weight="bold", pad=20,
)
ax.text(
    0, 1.025,
    "Crash-level prevalence, not per-mile risk or individual probability; within-year date continuity not evaluated.",
    transform=ax.transAxes, fontsize=9, color="#555555", va="bottom",
)
ax.set_xlabel("Crash year")
ax.set_ylabel("Crashes with ≥1 motorist death (%)")
ax.yaxis.set_major_formatter(FuncFormatter(lambda value, position: f"{value:.02f}%"))
ax.set_xticks(share["year"])
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)
