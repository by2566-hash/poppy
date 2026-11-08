from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"

annual = duckdb.sql(
    f"""
    SELECT
        year(crash_date)::INTEGER AS year,
        count(*) AS brooklyn_crashes,
        sum(number_of_pedestrians_injured)::BIGINT AS pedestrian_injured,
        sum(number_of_pedestrians_killed)::BIGINT AS pedestrian_killed,
        count(*) FILTER (
            WHERE number_of_pedestrians_injured + number_of_pedestrians_killed > 0
        ) AS crashes_with_pedestrian_casualty
    FROM read_parquet('{DATA}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
      AND borough = 'BROOKLYN'
    GROUP BY year
    ORDER BY year
    """
).df()
annual["pedestrian_casualties"] = (
    annual["pedestrian_injured"] + annual["pedestrian_killed"]
)
annual["crashes_with_pedestrian_casualty_pct"] = (
    100 * annual["crashes_with_pedestrian_casualty"] / annual["brooklyn_crashes"]
)

missing = duckdb.sql(
    f"""
    SELECT
        count(*) AS all_crashes,
        count(*) FILTER (WHERE borough IS NULL) AS null_borough_crashes
    FROM read_parquet('{DATA}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    """
).df().iloc[0]
missing_pct = 100 * missing.null_borough_crashes / missing.all_crashes

annual.to_csv(OUT / "values_1.csv", index=False)
annual.to_csv(OUT / "values_2.csv", index=False)

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})

fig, ax = plt.subplots(figsize=(10.5, 5.8))
ax.bar(annual.year, annual.pedestrian_injured, color="#2478A8", label="Pedestrians injured")
ax.bar(
    annual.year,
    annual.pedestrian_killed,
    bottom=annual.pedestrian_injured,
    color="#B43C39",
    label="Pedestrians killed",
)
ax.set_title("Pedestrian casualties in Brooklyn crashes", loc="left", fontsize=17, weight="bold", pad=26)
ax.text(
    0,
    1.015,
    "Injured and killed pedestrians per year · NYC police-reported crashes · complete years",
    transform=ax.transAxes,
    color="#555555",
    fontsize=10,
)
ax.set_ylabel("Pedestrians injured or killed")
ax.set_xlabel("Crash year")
ax.set_xticks(annual.year)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", color="#D9DEE3", linewidth=0.8)
ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, ncols=2, loc="upper right")
fig.text(
    0.01,
    0.01,
    "Source: NYC motor vehicle crash records. 2026 omitted because coverage ends June 11.",
    color="#555555",
    fontsize=8.5,
)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(10.5, 5.8))
ax.plot(
    annual.year,
    annual.crashes_with_pedestrian_casualty_pct,
    color="#166B66",
    linewidth=2.8,
    marker="o",
    markersize=5,
)
ax.set_title("Share of Brooklyn crashes involving pedestrian harm", loc="left", fontsize=17, weight="bold", pad=26)
ax.text(
    0,
    1.015,
    "Crashes with ≥1 pedestrian injured or killed · share of all Brooklyn crashes",
    transform=ax.transAxes,
    color="#555555",
    fontsize=10,
)
ax.set_ylabel("Brooklyn crashes involving pedestrian harm (%)")
ax.set_xlabel("Crash year")
ax.set_xticks(annual.year)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", color="#D9DEE3", linewidth=0.8)
ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)
ax.annotate(
    f"{annual.iloc[0].crashes_with_pedestrian_casualty_pct:.1f}%",
    (annual.iloc[0].year, annual.iloc[0].crashes_with_pedestrian_casualty_pct),
    xytext=(5, 10),
    textcoords="offset points",
    fontsize=9,
)
ax.annotate(
    f"{annual.iloc[-1].crashes_with_pedestrian_casualty_pct:.1f}%",
    (annual.iloc[-1].year, annual.iloc[-1].crashes_with_pedestrian_casualty_pct),
    xytext=(-34, 10),
    textcoords="offset points",
    fontsize=9,
)
fig.text(
    0.01,
    0.01,
    "Source: NYC motor vehicle crash records. 2026 omitted because coverage ends June 11. This is a crash-based share, not pedestrian exposure risk.",
    color="#555555",
    fontsize=8.2,
)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)

print(annual.to_string(index=False))
print(f"null borough rows in 2013-2025: {int(missing.null_borough_crashes)} / {int(missing.all_crashes)} ({missing_pct:.4f}%)")
