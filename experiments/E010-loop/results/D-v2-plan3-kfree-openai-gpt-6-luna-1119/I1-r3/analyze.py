from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"

con = duckdb.connect()
df = con.execute(
    """
    SELECT
        year(crash_date) AS year,
        count(*) AS eligible_crash_rows,
        sum(number_of_motorist_killed) AS motorist_deaths,
        sum(CASE WHEN number_of_motorist_killed > 0 THEN 1 ELSE 0 END)
            AS crashes_with_motorist_death
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
      AND number_of_motorist_killed IS NOT NULL
    GROUP BY year(crash_date)
    ORDER BY year
    """,
    [str(DATA)],
).fetchdf()

# The data check established full year coverage and no missing outcome values
# for 2013–2025, so the eligible row count is the annual reported-crash base.
df["motorist_deaths_per_1000_crashes"] = (
    1000 * df["motorist_deaths"] / df["eligible_crash_rows"]
)
df["crashes_with_motorist_death_pct"] = (
    100 * df["crashes_with_motorist_death"] / df["eligible_crash_rows"]
)

option_1 = df[
    ["year", "eligible_crash_rows", "motorist_deaths", "motorist_deaths_per_1000_crashes"]
].copy()
option_1.to_csv(OUT / "values_1.csv", index=False, float_format="%.6f")

option_2 = df[
    ["year", "eligible_crash_rows", "crashes_with_motorist_death", "crashes_with_motorist_death_pct"]
].copy()
option_2.to_csv(OUT / "values_2.csv", index=False, float_format="%.6f")

for option, y_col, y_label, title in [
    (
        1,
        "motorist_deaths_per_1000_crashes",
        "Motorist deaths per 1,000 reported crashes",
        "Motorist deaths per 1,000 reported NYC crashes, 2013–2025",
    ),
    (
        2,
        "crashes_with_motorist_death_pct",
        "Reported crashes with ≥1 motorist death (%)",
        "Share of reported NYC crashes with ≥1 motorist death, 2013–2025",
    ),
]:
    fig, ax = plt.subplots(figsize=(10, 5.7))
    ax.plot(df["year"], df[y_col], marker="o", linewidth=2, color="#176B87")
    ax.set_xticks(df["year"])
    ax.tick_params(axis="x", rotation=45)
    ax.set_ylabel(y_label)
    ax.set_xlabel("Crash year")
    ax.grid(axis="y", alpha=0.25)
    ax.set_title(title, loc="left", fontsize=14, weight="bold", pad=25)
    fig.text(
        0.125,
        0.92,
        "All police-reported NYC motor vehicle crashes; not a per-mile risk measure (miles driven unavailable).",
        ha="left",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    fig.savefig(OUT / f"option_{option}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
