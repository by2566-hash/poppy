from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import calendar


ROOT = Path(__file__).resolve().parents[1]
DATA = str(ROOT / "data" / "crashes.parquet")
OUT = Path(__file__).resolve().parent
GROUPS = ["Day", "Night", "Unknown time"]
PALETTE = {"Day": "#4C78A8", "Night": "#E45756", "Unknown time": "#9D9D9D"}


def load(option_id):
    cols = "crash_date, crash_time"
    if option_id == 2:
        cols += ", number_of_persons_injured, number_of_persons_killed"
    extra_filter = ""
    if option_id == 2:
        extra_filter = " AND number_of_persons_injured IS NOT NULL AND number_of_persons_killed IS NOT NULL"
    sql = f"""
        SELECT {cols}
        FROM read_parquet('{DATA}')
        WHERE crash_date >= DATE '2013-01-01'
          AND crash_date < DATE '2026-01-01'
          AND year(crash_date) BETWEEN 2013 AND 2025
          {extra_filter}
    """
    df = duckdb.connect().execute(sql).fetchdf()
    hour = pd.to_datetime(df["crash_time"].astype("string"), format="mixed", errors="coerce").dt.hour
    df["time_group"] = np.select(
        [hour.isna(), (hour >= 20) | (hour < 6)],
        ["Unknown time", "Night"],
        default="Day",
    )
    return df


def option_1():
    df = load(1)
    crash_counts = df.groupby("time_group").size().reindex(GROUPS, fill_value=0)
    complete_days = sum(366 if calendar.isleap(year) else 365 for year in range(2013, 2026))
    hours_by_group = {"Day": complete_days * 14, "Night": complete_days * 10, "Unknown time": 0}
    values = pd.DataFrame({"time_group": GROUPS, "crash_count": [int(crash_counts[g]) for g in GROUPS]})
    values["nominal_clock_hours"] = values["time_group"].map(hours_by_group)
    values["crashes_per_nominal_clock_hour"] = np.where(
        values["nominal_clock_hours"] > 0,
        values["crash_count"] / values["nominal_clock_hours"],
        np.nan,
    )
    values.to_csv(OUT / "values_1.csv", index=False)

    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    shown = values.loc[values["nominal_clock_hours"] > 0]
    bars = ax.bar(shown["time_group"], shown["crashes_per_nominal_clock_hour"], color=[PALETTE[g] for g in shown["time_group"]], width=0.62)
    ax.bar_label(bars, labels=[f"{x:.2f}" for x in shown["crashes_per_nominal_clock_hour"]], padding=4, fontsize=9)
    ax.set_ylabel("Police-reported crashes per nominal clock-hour")
    ax.set_xlabel("Night = 20:00–05:59 (10 hours/day); Day = 06:00–19:59 (14 hours/day)")
    ax.set_title("NYC reported crashes per nominal clock-hour\nComplete calendar years 2013–2025", loc="left", fontsize=14, weight="bold", pad=16)
    fig.text(0.125, 0.02, "No traffic-exposure adjustment; nominal hours ignore daylight-saving changes. Midnight records may include defaults.", fontsize=9, color="#444444")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.22)
    ax.set_axisbelow(True)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def option_2():
    df = load(2)
    grouped = df.groupby("time_group").agg(
        crash_denominator=("crash_date", "size"),
        persons_injured_total=("number_of_persons_injured", "sum"),
        persons_killed_total=("number_of_persons_killed", "sum"),
    ).reindex(GROUPS)
    grouped["crash_denominator"] = grouped["crash_denominator"].fillna(0).astype("int64")
    grouped[["persons_injured_total", "persons_killed_total"]] = grouped[["persons_injured_total", "persons_killed_total"]].fillna(0)
    for col in ["persons_injured_total", "persons_killed_total"]:
        grouped[col] = grouped[col].astype("int64")
    grouped["persons_injured_per_1000_crashes"] = np.where(
        grouped["crash_denominator"] > 0,
        grouped["persons_injured_total"] * 1000 / grouped["crash_denominator"],
        np.nan,
    )
    grouped["persons_killed_per_1000_crashes"] = np.where(
        grouped["crash_denominator"] > 0,
        grouped["persons_killed_total"] * 1000 / grouped["crash_denominator"],
        np.nan,
    )
    values = grouped.rename_axis("time_group").reset_index()
    values.to_csv(OUT / "values_2.csv", index=False, float_format="%.6f")

    fig, axes = plt.subplots(1, 2, figsize=(11, 5.4))
    measures = [
        ("persons_injured_per_1000_crashes", "Persons injured per 1,000 crashes", "#4C78A8"),
        ("persons_killed_per_1000_crashes", "Persons killed per 1,000 crashes", "#E45756"),
    ]
    for ax, (column, label, color) in zip(axes, measures):
        valid = values["crash_denominator"] > 0
        subset = values.loc[valid]
        bars = ax.bar(subset["time_group"], subset[column], color=[PALETTE[g] for g in subset["time_group"]], width=0.62)
        ax.bar_label(bars, labels=[f"{x:.2f}" for x in subset[column]], padding=3, fontsize=9)
        ax.set_title(label, fontsize=11, weight="bold")
        ax.set_ylabel("People per 1,000 crashes")
        ax.tick_params(axis="x", rotation=15)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=0.22)
        ax.set_axisbelow(True)
    fig.suptitle("NYC reported injury and death burden per crash\nComplete-case crashes in complete calendar years 2013–2025", x=0.07, ha="left", fontsize=14, weight="bold")
    fig.text(0.07, 0.015, "Not exposure-adjusted danger; 42 records missing an outcome were excluded, and midnight times may include defaults.", fontsize=9, color="#444444")
    fig.tight_layout(rect=(0.04, 0.07, 1, 0.88))
    fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


option_1()
option_2()
