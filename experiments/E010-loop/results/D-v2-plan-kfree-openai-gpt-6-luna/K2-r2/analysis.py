from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
parquet_path = str(ROOT / "data/crashes.parquet").replace("'", "''")
conn = duckdb.connect()

counts = conn.execute(
    f"""
    SELECT isodow(crash_date) AS weekday_number, count(*) AS crash_rows
    FROM read_parquet('{parquet_path}')
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY isodow(crash_date)
    ORDER BY weekday_number
    """
).fetchdf()

weekdays = pd.DataFrame(
    {"weekday_number": range(1, 8), "weekday": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
)
counts = weekdays.merge(counts, on="weekday_number", how="left").fillna({"crash_rows": 0})
counts["crash_rows"] = counts["crash_rows"].astype("int64")

counts[["weekday", "crash_rows"]].to_csv(OUT / "values_1.csv", index=False)
fig, ax = plt.subplots(figsize=(10, 5.8))
bars = ax.bar(counts["weekday"], counts["crash_rows"], color="#3274A1")
ax.bar_label(bars, labels=[f"{v:,.0f}" for v in counts["crash_rows"]], padding=3, fontsize=9)
ax.set_title("Total NYC Police-Reported Crashes by Weekday\n2013–2025", fontsize=15, pad=18)
ax.text(
    0.5,
    1.01,
    "Observed records only; date endpoints do not independently verify complete reporting.",
    transform=ax.transAxes,
    ha="center",
    va="bottom",
    fontsize=9,
    color="#555555",
)
ax.set_ylabel("Crash records")
ax.set_xlabel("Day of week (crash date)")
ax.tick_params(axis="x", rotation=18)
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

calendar = pd.date_range("2013-01-01", "2025-12-31", freq="D")
occurrences = pd.Series(calendar.dayofweek).value_counts().sort_index()
occurrence_table = pd.DataFrame(
    {
        "weekday_number": range(1, 8),
        "weekday": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "calendar_day_occurrences": [int(occurrences.get(day, 0)) for day in range(7)],
    }
)
average = occurrence_table.merge(counts[["weekday_number", "crash_rows"]], on="weekday_number", how="left")
average["mean_crashes_per_calendar_day"] = average["crash_rows"] / average["calendar_day_occurrences"]
average[["weekday", "crash_rows", "calendar_day_occurrences", "mean_crashes_per_calendar_day"]].to_csv(
    OUT / "values_2.csv", index=False, float_format="%.6f"
)

fig, ax = plt.subplots(figsize=(10, 5.8))
bars = ax.bar(average["weekday"], average["mean_crashes_per_calendar_day"], color="#E1812C")
ax.bar_label(bars, labels=[f"{v:,.1f}" for v in average["mean_crashes_per_calendar_day"]], padding=3, fontsize=9)
ax.set_title("Mean NYC Police-Reported Crashes per Calendar Date of Weekday\n2013–2025", fontsize=15, pad=18)
ax.text(
    0.5,
    1.01,
    "Calendar-date average, not a per-trip risk rate; observed reports only.",
    transform=ax.transAxes,
    ha="center",
    va="bottom",
    fontsize=9,
    color="#555555",
)
ax.set_ylabel("Crash records per calendar date")
ax.set_xlabel("Day of week (crash date)")
ax.tick_params(axis="x", rotation=18)
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)

print(counts[["weekday", "crash_rows"]].to_string(index=False))
print(average[["weekday", "calendar_day_occurrences", "mean_crashes_per_calendar_day"]].to_string(index=False))
