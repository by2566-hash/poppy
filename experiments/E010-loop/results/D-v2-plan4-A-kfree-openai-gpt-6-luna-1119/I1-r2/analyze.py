from pathlib import Path

import duckdb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
source = str(ROOT / "data" / "crashes.parquet").replace("'", "''")
con = duckdb.connect()
annual = con.execute(
    f"""
    SELECT
      year(crash_date) AS year,
      count(*) AS crash_rows,
      coalesce(sum(number_of_motorist_killed), 0) AS motorist_deaths,
      count(*) FILTER (WHERE number_of_motorist_killed >= 1)
        AS crashes_with_motorist_death
    FROM read_parquet('{source}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
    """
).fetchdf()

annual["motorist_deaths_per_1000_crashes"] = (
    annual["motorist_deaths"] / annual["crash_rows"] * 1000
)
annual["share_crashes_with_motorist_death_pct"] = (
    annual["crashes_with_motorist_death"] / annual["crash_rows"] * 100
)

option_data = {
    1: annual[["year", "crash_rows", "motorist_deaths"]].copy(),
    2: annual[
        [
            "year",
            "crash_rows",
            "crashes_with_motorist_death",
            "share_crashes_with_motorist_death_pct",
        ]
    ].copy(),
    3: annual[
        [
            "year",
            "crash_rows",
            "motorist_deaths",
            "motorist_deaths_per_1000_crashes",
        ]
    ].copy(),
}

chart_specs = {
    1: {
        "column": "motorist_deaths",
        "title": "Motorists killed per year in NYC police-reported crashes",
        "limitation": "Annual death count; crash data has no miles-driven denominator, so this is not per-mile risk.",
        "ylabel": "Motorists killed (count)",
        "format": "{:.0f}",
    },
    2: {
        "column": "share_crashes_with_motorist_death_pct",
        "title": "Share of NYC police-reported crashes with a motorist death",
        "limitation": "Each crash counts once; no miles-driven denominator, so this is not per-mile risk.",
        "ylabel": "Crashes with ≥1 motorist death (%)",
        "format": "{:.2f}%",
    },
    3: {
        "column": "motorist_deaths_per_1000_crashes",
        "title": "Motorists killed per 1,000 NYC police-reported crashes",
        "limitation": "Crash denominator, not miles driven; this is not a per-mile risk measure.",
        "ylabel": "Motorists killed per 1,000 crashes",
        "format": "{:.2f}",
    },
}

for option_id, values in option_data.items():
    values.to_csv(OUT / f"values_{option_id}.csv", index=False, float_format="%.8f")
    spec = chart_specs[option_id]
    fig, ax = plt.subplots(figsize=(10, 5.8))
    ax.plot(
        values["year"],
        values[spec["column"]],
        marker="o",
        linewidth=2.2,
        markersize=5,
        color="#176B87",
    )
    ax.set_title(spec["title"], fontsize=14, weight="bold", pad=27)
    fig.text(
        0.5,
        0.91,
        spec["limitation"],
        ha="center",
        va="center",
        fontsize=9,
        color="#555555",
    )
    ax.set_xlabel("Calendar year of crash")
    ax.set_ylabel(spec["ylabel"])
    ax.set_xticks(values["year"])
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", alpha=0.28)
    ax.spines[["top", "right"]].set_visible(False)
    left = values.iloc[0]
    right = values.iloc[-1]
    ax.annotate(
        spec["format"].format(left[spec["column"]]),
        (left["year"], left[spec["column"]]),
        xytext=(5, 7),
        textcoords="offset points",
        fontsize=8,
    )
    ax.annotate(
        spec["format"].format(right[spec["column"]]),
        (right["year"], right[spec["column"]]),
        xytext=(-42, 7),
        textcoords="offset points",
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.87))
    fig.savefig(OUT / f"option_{option_id}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

print(annual.to_string(index=False))
