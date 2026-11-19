from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
PARQUET = ROOT / "data" / "crashes.parquet"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

con = duckdb.connect()
weekday_counts = con.execute(
    f"""
    SELECT
      CASE dayofweek(crash_date)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
      END AS weekday,
      count(*) AS crash_records
    FROM read_parquet('{PARQUET.as_posix()}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY weekday
    """
).df()
con.close()

counts = (
    pd.DataFrame({"weekday": WEEKDAYS})
    .merge(weekday_counts, on="weekday", how="left")
    .fillna({"crash_records": 0})
)
counts["crash_records"] = counts["crash_records"].astype("int64")
counts.to_csv(OUT / "values_1.csv", index=False)

plt.figure(figsize=(10, 5.8))
plt.bar(counts["weekday"], counts["crash_records"], color="#3977a8")
plt.title("Total police-reported crash records by weekday\nNYC crashes dated 2013–2025", fontsize=14, pad=18)
plt.suptitle("One row per reported crash; complete reporting on every day is not verified.", y=0.94, fontsize=9, color="#555555")
plt.ylabel("Crash records")
plt.xlabel("Weekday of crash_date")
plt.xticks(rotation=25, ha="right")
plt.grid(axis="y", alpha=0.2)
plt.tight_layout(rect=[0, 0, 1, 0.9])
plt.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close()

# The final plan defines the denominator as all calendar dates in the inclusive
# 2013-01-01 through 2025-12-31 span, independent of whether a crash occurred.
calendar = pd.date_range("2013-01-01", "2025-12-31", freq="D")
calendar_counts = pd.Series(calendar.day_name()).value_counts()
average = counts.copy()
average["weekday_calendar_dates"] = average["weekday"].map(calendar_counts).astype("int64")
average["mean_crash_records_per_calendar_date"] = (
    average["crash_records"] / average["weekday_calendar_dates"]
)
average.to_csv(OUT / "values_2.csv", index=False, float_format="%.6f")

plt.figure(figsize=(10, 5.8))
plt.bar(average["weekday"], average["mean_crash_records_per_calendar_date"], color="#548c62")
plt.title(
    "Mean police-reported crash records per calendar date of weekday\n"
    "NYC crashes dated January 1, 2013–December 31, 2025",
    fontsize=13,
    pad=18,
)
plt.suptitle("Calendar-date denominator; complete reporting on every day is not verified.", y=0.94, fontsize=9, color="#555555")
plt.ylabel("Mean crash records per weekday date")
plt.xlabel("Weekday of crash_date")
plt.xticks(rotation=25, ha="right")
plt.grid(axis="y", alpha=0.2)
plt.tight_layout(rect=[0, 0, 1, 0.9])
plt.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close()
