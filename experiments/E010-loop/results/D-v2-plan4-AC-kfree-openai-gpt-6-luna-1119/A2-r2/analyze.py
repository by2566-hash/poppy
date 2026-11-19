from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)

sql = """
WITH eligible AS (
    SELECT
        crash_time,
        number_of_persons_injured AS injured,
        number_of_persons_killed AS killed,
        CASE
            WHEN crash_time = TIME '00:00:00' THEN '00:00 (possibly default)'
            WHEN crash_time >= TIME '20:00:00' OR crash_time < TIME '06:00:00' THEN 'Night'
            ELSE 'Day'
        END AS time_group
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
      AND crash_time IS NOT NULL
      AND number_of_persons_injured IS NOT NULL
      AND number_of_persons_killed IS NOT NULL
), grouped AS (
    SELECT
        time_group,
        COUNT(*) AS crash_count,
        SUM(CASE WHEN injured > 0 OR killed > 0 THEN 1 ELSE 0 END) AS crashes_with_injury_or_death,
        SUM(injured) AS injured_persons,
        SUM(killed) AS killed_persons
    FROM eligible
    GROUP BY time_group
)
SELECT
    time_group,
    crash_count,
    crashes_with_injury_or_death,
    100.0 * crashes_with_injury_or_death / crash_count AS pct_crashes_with_injury_or_death,
    injured_persons,
    killed_persons,
    injured_persons + killed_persons AS total_casualties,
    1.0 * (injured_persons + killed_persons) / crash_count AS mean_casualties_per_crash
FROM grouped
ORDER BY CASE time_group WHEN 'Day' THEN 1 WHEN 'Night' THEN 2 ELSE 3 END
"""

con = duckdb.connect()
values = con.execute(sql, [str(SOURCE)]).fetchdf()
values.to_csv(OUT / "analysis_groups.csv", index=False)

values_1 = values[["time_group", "crash_count", "crashes_with_injury_or_death", "pct_crashes_with_injury_or_death"]].copy()
values_1.to_csv(OUT / "values_1.csv", index=False)

values_2 = values[["time_group", "crash_count", "injured_persons", "killed_persons", "total_casualties", "mean_casualties_per_crash"]].copy()
values_2.to_csv(OUT / "values_2.csv", index=False)


def make_chart(option_id, y_column, title, ylabel, filename, value_format):
    fig, ax = plt.subplots(figsize=(9.2, 5.6))
    x = range(len(values))
    bars = ax.bar(x, values[y_column], color=["#3973ac", "#d97732", "#777777"], width=0.58)
    ax.set_xticks(list(x), ["Day\n06:00–19:59", "Night\n20:00–05:59 except 00:00", "00:00\npossibly default"])
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, values[y_column].max() * 1.32)
    ax.set_title(title, loc="left", fontsize=14, weight="bold", pad=28)
    ax.text(
        0,
        1.015,
        "No traffic or pedestrian exposure denominator; 00:00 is separate because it may be a default timestamp.",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=9,
        color="#444444",
    )
    ax.grid(axis="y", color="#dddddd", linewidth=0.7)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    offset = max(values[y_column].max() * 0.035, 0.01)
    for bar, row in zip(bars, values.itertuples(index=False)):
        val = getattr(row, y_column)
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + offset,
            f"{value_format(val)}\nn={row.crash_count:,}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(OUT / filename, dpi=180, bbox_inches="tight")
    plt.close(fig)


make_chart(
    1,
    "pct_crashes_with_injury_or_death",
    "NYC reported crashes (complete years 2013–2025): injury-or-death share",
    "Crashes with ≥1 person injured or killed (%)",
    "option_1.png",
    lambda value: f"{value:.2f}%",
)
make_chart(
    2,
    "mean_casualties_per_crash",
    "NYC reported crashes (complete years 2013–2025): injured/killed persons per crash",
    "Persons injured or killed per crash",
    "option_2.png",
    lambda value: f"{value:.3f}",
)

print(values.to_string(index=False))
