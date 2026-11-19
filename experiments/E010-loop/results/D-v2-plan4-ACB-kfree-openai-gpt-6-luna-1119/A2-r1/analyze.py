from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
con = duckdb.connect()
con.from_parquet(str(ROOT / "data/crashes.parquet")).create_view("crashes")

base = """
    WITH eligible AS (
        SELECT year(crash_date) AS year,
               CASE
                   WHEN hour(crash_time) >= 20 OR hour(crash_time) < 6 THEN 'Night'
                   ELSE 'Day'
               END AS time_period,
               number_of_persons_injured,
               number_of_persons_killed
        FROM crashes
        WHERE crash_date >= DATE '2013-01-01'
          AND crash_date < DATE '2026-01-01'
          AND crash_time IS NOT NULL
          AND number_of_persons_injured IS NOT NULL
          AND number_of_persons_killed IS NOT NULL
    )
"""

for option_id in (1, 2):
    if option_id == 1:
        metric_sql = "COUNT(*) FILTER (WHERE number_of_persons_injured > 0 OR number_of_persons_killed > 0)"
        metric_label = "Share of reported crashes with ≥1 person injured or killed"
        ylabel = "Crashes with ≥1 person injured or killed (%)"
        title = "NYC share of reported crashes with injury or death\n2013–2025, complete observed calendar years"
        output_name = "share_injury_or_death"
        percent = True
    else:
        metric_sql = "SUM(number_of_persons_injured + number_of_persons_killed)"
        metric_label = "Mean number of persons injured plus killed per reported crash"
        ylabel = "Injured and killed persons per crash"
        title = "NYC mean injured and killed persons per reported crash\n2013–2025, complete observed calendar years"
        output_name = "mean_harmed_persons_per_crash"
        percent = False

    query = f"""
        {base}
        SELECT year, time_period,
               {metric_sql} AS numerator,
               COUNT(*) AS denominator,
               ({metric_sql})::DOUBLE / COUNT(*) AS metric_value
        FROM eligible
        GROUP BY year, time_period
        ORDER BY year, CASE time_period WHEN 'Day' THEN 0 ELSE 1 END
    """
    df = con.execute(query).df()
    df.insert(0, "metric", metric_label)
    df.to_csv(OUT / f"values_{option_id}.csv", index=False, float_format="%.8f")

    fig, ax = plt.subplots(figsize=(11.5, 6.4))
    for period, color, marker in (("Day", "#2677a8", "o"), ("Night", "#d66a27", "s")):
        subset = df[df["time_period"] == period]
        y = subset["metric_value"] * (100 if percent else 1)
        ax.plot(subset["year"], y, label=period, color=color, marker=marker,
                markersize=4, linewidth=2)
    ax.set_title(title, loc="left", fontsize=16, weight="bold", pad=18)
    ax.text(0, 1.01,
            "Per-crash measure, not travel risk: traffic/exposure is unavailable; reported midnight times may include defaults.",
            transform=ax.transAxes, fontsize=9.5, color="#555555", va="bottom")
    ax.set_xlabel("Crash year")
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, 50 if percent else 0.7)
    ax.set_xticks(list(range(2013, 2026, 2)))
    ax.grid(axis="y", color="#dddddd", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(title="Crash time", frameon=False, ncol=2, loc="best")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(OUT / f"option_{option_id}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
