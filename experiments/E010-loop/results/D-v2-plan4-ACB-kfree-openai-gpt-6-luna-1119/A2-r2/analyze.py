import csv
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
PARQUET = (ROOT / "data" / "crashes.parquet").as_posix()
YEARS = list(range(2013, 2026))
YEAR_SQL = ",".join(map(str, YEARS))
con = duckdb.connect()
con.execute(f"CREATE VIEW crashes AS SELECT * FROM read_parquet('{PARQUET}')")


def save_values(option_id, rows, columns):
    frame = pd.DataFrame(rows, columns=columns)
    frame.to_csv(OUT / f"values_{option_id}.csv", index=False, float_format="%.6f")
    return frame


def chart_lines(frame, option_id, metric, title, subtitle, y_label, value_column, percent=False):
    fig, ax = plt.subplots(figsize=(11, 6.2))
    groups = frame["time_group"].drop_duplicates().tolist()
    styles = {
        "Night": ("#b33b3b", "o"),
        "Day": ("#28698f", "s"),
        "Midnight/unknown": ("#7b6a9a", "D"),
    }
    for group in groups:
        part = frame[frame["time_group"] == group]
        color, marker = styles[group]
        ax.plot(part["year"], part[value_column], color=color, marker=marker,
                linewidth=2.2, markersize=5, label=group)
    ax.set_title(title, fontsize=15, weight="bold", loc="left", pad=18)
    fig.text(0.125, 0.91, subtitle, fontsize=9.3, color="#555555")
    ax.set_xlabel("Calendar year")
    ax.set_ylabel(y_label)
    ax.set_xticks(YEARS)
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", color="#d9d9d9", linewidth=0.7)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, ncol=min(3, len(groups)), loc="best")
    if percent:
        ax.set_ylim(bottom=0)
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    fig.savefig(OUT / f"option_{option_id}.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


# Option 1: shares of all annual crash rows, with midnight/unavailable times shown separately.
query1 = f"""
WITH classified AS (
  SELECT year(crash_date) AS year,
         CASE
           WHEN crash_time IS NULL OR crash_time = TIME '00:00:00' THEN 'Midnight/unknown'
           WHEN crash_time >= TIME '20:00:00' OR crash_time < TIME '06:00:00' THEN 'Night'
           ELSE 'Day'
         END AS time_group
  FROM crashes
  WHERE year(crash_date) IN ({YEAR_SQL})
), counts AS (
  SELECT year, time_group, count(*) AS crash_count
  FROM classified GROUP BY year, time_group
), annual AS (
  SELECT year, count(*) AS denominator_crashes FROM classified GROUP BY year
)
SELECT counts.year, counts.time_group, counts.crash_count,
       annual.denominator_crashes,
       100.0 * counts.crash_count / annual.denominator_crashes AS share_pct
FROM counts JOIN annual USING (year)
ORDER BY year, CASE time_group WHEN 'Night' THEN 1 WHEN 'Day' THEN 2 ELSE 3 END
"""
rows1 = con.execute(query1).fetchall()
frame1 = save_values(1, rows1, ["year", "time_group", "crash_count", "denominator_crashes", "share_pct"])
chart_lines(
    frame1, 1, "annual share of recorded crashes",
    "Share of all recorded NYC motor-vehicle crashes, by time of day (2013–2025)",
    "Police-reported crashes; midnight/unknown shown separately. Recorded crashes do not provide traffic exposure.",
    "Share of annual crash records (%)", "share_pct", percent=True,
)

# Option 2: average recorded persons injured plus killed per eligible crash.
query2 = f"""
WITH eligible AS (
  SELECT year(crash_date) AS year,
         CASE WHEN crash_time >= TIME '20:00:00' OR crash_time < TIME '06:00:00'
              THEN 'Night' ELSE 'Day' END AS time_group,
         number_of_persons_injured + number_of_persons_killed AS casualties
  FROM crashes
  WHERE year(crash_date) IN ({YEAR_SQL})
    AND crash_time IS NOT NULL AND crash_time <> TIME '00:00:00'
    AND number_of_persons_injured IS NOT NULL
    AND number_of_persons_killed IS NOT NULL
), aggregates AS (
  SELECT year, time_group, count(*) AS eligible_crashes,
         sum(casualties) AS recorded_casualties
  FROM eligible GROUP BY year, time_group
)
SELECT year, time_group, recorded_casualties, eligible_crashes,
       1.0 * recorded_casualties / eligible_crashes AS mean_casualties_per_crash
FROM aggregates
ORDER BY year, CASE time_group WHEN 'Night' THEN 1 ELSE 2 END
"""
rows2 = con.execute(query2).fetchall()
frame2 = save_values(2, rows2, ["year", "time_group", "recorded_casualties", "eligible_crashes", "mean_casualties_per_crash"])
chart_lines(
    frame2, 2, "mean person casualties per crash",
    "Recorded persons injured or killed per eligible NYC crash (2013–2025)",
    "Police-reported motor-vehicle crashes; excludes partial years, midnight times and missing casualty totals; not exposure-adjusted.",
    "Mean injured + killed persons per crash", "mean_casualties_per_crash",
)

# Option 3: share of eligible crashes with at least one recorded death.
query3 = f"""
WITH eligible AS (
  SELECT year(crash_date) AS year,
         CASE WHEN crash_time >= TIME '20:00:00' OR crash_time < TIME '06:00:00'
              THEN 'Night' ELSE 'Day' END AS time_group,
         number_of_persons_killed
  FROM crashes
  WHERE year(crash_date) IN ({YEAR_SQL})
    AND crash_time IS NOT NULL AND crash_time <> TIME '00:00:00'
    AND number_of_persons_killed IS NOT NULL
), aggregates AS (
  SELECT year, time_group, count(*) AS eligible_crashes,
         count(*) FILTER (WHERE number_of_persons_killed > 0) AS fatal_crashes
  FROM eligible GROUP BY year, time_group
)
SELECT year, time_group, fatal_crashes, eligible_crashes,
       100.0 * fatal_crashes / eligible_crashes AS fatal_crash_pct
FROM aggregates
ORDER BY year, CASE time_group WHEN 'Night' THEN 1 ELSE 2 END
"""
rows3 = con.execute(query3).fetchall()
frame3 = save_values(3, rows3, ["year", "time_group", "fatal_crashes", "eligible_crashes", "fatal_crash_pct"])
chart_lines(
    frame3, 3, "share of crashes with a death",
    "Annual share of eligible NYC motor-vehicle crashes involving a death (2013–2025)",
    "Police-reported crashes; excludes partial years, midnight times and missing death totals; not exposure-adjusted.",
    "Crashes with ≥1 person killed (%)", "fatal_crash_pct", percent=True,
)
