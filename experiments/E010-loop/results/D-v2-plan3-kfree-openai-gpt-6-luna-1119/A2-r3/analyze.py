from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "crashes.parquet"

con = duckdb.connect()
query = f"""
    SELECT
      year(crash_date) AS year,
      CASE WHEN hour(crash_time) < 6 OR hour(crash_time) >= 20
           THEN 'Night' ELSE 'Day' END AS period,
      count(*) AS eligible_crashes,
      count(*) FILTER (
        WHERE number_of_persons_injured > 0 OR number_of_persons_killed > 0
      ) AS crashes_with_any_casualty,
      sum(number_of_persons_injured) AS persons_injured,
      sum(number_of_persons_killed) AS persons_killed
    FROM read_parquet('{DATA.as_posix()}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
      AND crash_time IS NOT NULL
      AND number_of_persons_injured IS NOT NULL
      AND number_of_persons_killed IS NOT NULL
    GROUP BY year, period
    ORDER BY year, CASE WHEN period = 'Day' THEN 0 ELSE 1 END
"""
values = con.execute(query).fetchdf()
con.close()
values["casualty_persons"] = values["persons_injured"] + values["persons_killed"]
values["crashes_with_casualty_pct"] = (
    100 * values["crashes_with_any_casualty"] / values["eligible_crashes"]
)
values["casualties_per_100_crashes"] = (
    100 * values["casualty_persons"] / values["eligible_crashes"]
)
values.to_csv(OUT / "values_1.csv", index=False, float_format="%.6f")
values.to_csv(OUT / "values_2.csv", index=False, float_format="%.6f")

colors = {"Day": "#2878B5", "Night": "#D1495B"}
labels = {"Day": "Day (06:00–19:59)", "Night": "Night (20:00–05:59)"}

for plan_id, metric_column, ylabel, title in [
    (
        1,
        "crashes_with_casualty_pct",
        "Crashes involving injury or death (%)",
        "Share of reported NYC crashes with injury or death by time, 2013–2025",
    ),
    (
        2,
        "casualties_per_100_crashes",
        "Injured or killed people per 100 crashes",
        "Injured and killed people per 100 reported NYC crashes by time, 2013–2025",
    ),
]:
    fig, ax = plt.subplots(figsize=(11, 6.3))
    for period in ("Day", "Night"):
        subset = values[values["period"] == period]
        ax.plot(
            subset["year"],
            subset[metric_column],
            marker="o",
            markersize=4,
            linewidth=2,
            color=colors[period],
            label=labels[period],
        )
    ax.set_title(title, loc="left", fontsize=14, weight="bold", pad=30)
    ax.text(
        0,
        1.025,
        "Complete-year police-reported crashes with known injury and death totals; not adjusted for traffic exposure.",
        transform=ax.transAxes,
        fontsize=9,
        color="#444444",
    )
    ax.set_xlabel("Calendar year")
    ax.set_ylabel(ylabel)
    ax.set_xticks(sorted(values["year"].unique()))
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", color="#dddddd", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, ncol=2, loc="upper right")
    fig.tight_layout()
    fig.savefig(OUT / f"option_{plan_id}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
