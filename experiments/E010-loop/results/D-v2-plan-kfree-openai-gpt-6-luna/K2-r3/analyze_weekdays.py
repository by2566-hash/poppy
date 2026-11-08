import csv
from datetime import date, timedelta

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


DATA = "data/crashes.parquet"
START = date(2013, 1, 1)
END = date(2025, 12, 31)
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

con = duckdb.connect()
counts = con.execute(
    """
    SELECT EXTRACT(ISODOW FROM crash_date)::INTEGER AS weekday_number,
           COUNT(*)::BIGINT AS crashes
    FROM read_parquet('data/crashes.parquet')
    WHERE crash_date >= DATE '2013-01-01' AND crash_date <= DATE '2025-12-31'
    GROUP BY weekday_number
    ORDER BY weekday_number
    """
).df()

counts = pd.DataFrame({"weekday_number": range(1, 8)}).merge(counts, how="left", on="weekday_number")
counts["crashes"] = counts["crashes"].fillna(0).astype("int64")
counts["weekday"] = WEEKDAYS
total = int(counts["crashes"].sum())
counts["share_percent"] = counts["crashes"] / total * 100

date_counts = {day: 0 for day in range(1, 8)}
current = START
while current <= END:
    date_counts[current.isoweekday()] += 1
    current += timedelta(days=1)
counts["calendar_dates"] = counts["weekday_number"].map(date_counts)
counts["mean_crashes_per_calendar_date"] = counts["crashes"] / counts["calendar_dates"]

values_1 = counts[["weekday", "crashes", "share_percent"]]
values_1.to_csv("out/values_1.csv", index=False, float_format="%.4f")
values_2 = counts[["weekday", "crashes", "calendar_dates", "mean_crashes_per_calendar_date"]]
values_2.to_csv("out/values_2.csv", index=False, float_format="%.4f")

limitation = "Police-reported records only; date extents span full years, but source completeness within the interval is not independently verified."

fig, ax = plt.subplots(figsize=(10, 5.6))
bars = ax.bar(counts["weekday"], counts["crashes"], color="#4169a1")
ax.set_title("Police-reported crash records by weekday\nNYC, 2013–2025", fontsize=15, pad=14)
ax.set_ylabel("Crash records")
ax.set_xlabel("Day of week")
ax.ticklabel_format(axis="y", style="plain")
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)
ax.bar_label(bars, labels=[f"{int(value):,}" for value in counts["crashes"]], padding=3, fontsize=9)
fig.text(0.5, 0.012, limitation, ha="center", fontsize=8, wrap=True)
fig.tight_layout(rect=[0, 0.05, 1, 1])
fig.savefig("out/option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 5.6))
bars = ax.bar(counts["weekday"], counts["mean_crashes_per_calendar_date"], color="#418777")
ax.set_title("Average police-reported crashes per calendar date, by weekday\nNYC, 2013–2025", fontsize=15, pad=14)
ax.set_ylabel("Mean crash records per date")
ax.set_xlabel("Day of week")
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)
ax.bar_label(bars, labels=[f"{value:,.1f}" for value in counts["mean_crashes_per_calendar_date"]], padding=3, fontsize=9)
fig.text(0.5, 0.012, limitation, ha="center", fontsize=8, wrap=True)
fig.tight_layout(rect=[0, 0.05, 1, 1])
fig.savefig("out/option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)
