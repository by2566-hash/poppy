from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"

query = """
WITH scoped AS (
    SELECT
        CASE
            WHEN crash_time IS NULL THEN 'Unknown'
            WHEN crash_time >= TIME '21:00:00' OR crash_time < TIME '06:00:00' THEN 'Night'
            ELSE 'Day'
        END AS time_period,
        number_of_persons_injured + number_of_persons_killed AS casualties
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
      AND number_of_persons_injured IS NOT NULL
      AND number_of_persons_killed IS NOT NULL
)
SELECT
    time_period,
    COUNT(*) AS crashes,
    SUM(casualties) AS reported_casualties,
    SUM(CASE WHEN casualties > 0 THEN 1 ELSE 0 END) AS crashes_with_casualty
FROM scoped
GROUP BY time_period
"""
df = duckdb.sql(query, params=[str(DATA)]).df()
df["time_period"] = pd.Categorical(df["time_period"], ["Day", "Night"], ordered=True)
df = df.sort_values("time_period").reset_index(drop=True)
df["mean_casualties_per_crash"] = df["reported_casualties"] / df["crashes"]
df["share_crashes_with_casualty_pct"] = 100 * df["crashes_with_casualty"] / df["crashes"]

value_columns = [
    "time_period",
    "crashes",
    "reported_casualties",
    "mean_casualties_per_crash",
    "crashes_with_casualty",
    "share_crashes_with_casualty_pct",
]

plt.rcParams.update({"font.size": 11, "axes.titlesize": 13})

for option_id, metric_column, y_label, title, value_format in [
    (
        1,
        "mean_casualties_per_crash",
        "Reported injured + killed people per crash",
        "Mean reported casualties per crash — NYC, 2013–2025",
        "{:.3f}",
    ),
    (
        2,
        "share_crashes_with_casualty_pct",
        "Crashes with ≥1 reported injury or death (%)",
        "Share of reported crashes with a casualty — NYC, 2013–2025",
        "{:.1f}%",
    ),
]:
    df[value_columns].to_csv(OUT / f"values_{option_id}.csv", index=False)
    fig, ax = plt.subplots(figsize=(8.4, 5.4))
    colors = ["#426A8C", "#D66A45"]
    values = df[metric_column].to_numpy()
    bars = ax.bar(df["time_period"].astype(str), values, color=colors, width=0.58)
    ax.bar_label(
        bars,
        labels=[value_format.format(value) for value in values],
        padding=5,
        fontsize=12,
        fontweight="bold",
    )
    ax.set_title(title, loc="left", fontweight="bold", pad=18)
    ax.text(
        0,
        1.02,
        "Night = 21:00–05:59; Day = 06:00–20:59",
        transform=ax.transAxes,
        fontsize=10,
        color="#444444",
    )
    ax.set_ylabel(y_label)
    ax.set_xlabel("")
    ax.grid(axis="y", color="#D9DEE3", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#AAB2B9")
    max_value = max(values)
    ax.set_ylim(0, max_value * 1.24 if max_value else 1)
    for bar, count in zip(bars, df["crashes"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            0.02 * ax.get_ylim()[1],
            f"n={count:,} crashes",
            ha="center",
            va="bottom",
            fontsize=9,
            color="#FFFFFF",
            fontweight="bold",
        )
    fig.text(
        0.01,
        0.015,
        "Police-reported crashes only; per-crash severity/share is not exposure-adjusted. 00:00 counts as night and may include default-coded times.",
        fontsize=8.2,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(OUT / f"option_{option_id}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
