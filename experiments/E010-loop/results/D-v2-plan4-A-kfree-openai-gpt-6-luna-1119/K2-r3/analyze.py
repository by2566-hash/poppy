from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

con = duckdb.connect()
counts = con.execute(
    """
    SELECT dayname(crash_date) AS weekday,
           count(*) AS crash_count
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date <= DATE '2025-12-31'
    GROUP BY weekday
    """,
    [str(DATA)],
).df()
counts["weekday"] = pd.Categorical(counts["weekday"], WEEKDAYS, ordered=True)
counts = counts.sort_values("weekday").reset_index(drop=True)
total = int(counts["crash_count"].sum())
counts["share_of_included_crashes"] = counts["crash_count"] / total
counts.to_csv(OUT / "values_1.csv", index=False, float_format="%.8f")

fig, ax = plt.subplots(figsize=(10, 5.8))
bars = ax.bar(counts["weekday"].astype(str), counts["crash_count"], color="#3977a8")
ax.set_title("NYC police-reported crashes by weekday (2013–2025)\nCount and share of all dated crashes")
ax.set_ylabel("Number of crashes")
ax.set_xlabel("Weekday of crash_date")
ax.ticklabel_format(axis="y", style="plain")
ax.grid(axis="y", alpha=0.25)
for bar, share in zip(bars, counts["share_of_included_crashes"]):
    ax.annotate(f"{share:.1%}", (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 4), textcoords="offset points", ha="center", fontsize=9)
fig.text(0.01, 0.01, "Limitation: police-reported counts are not exposure-adjusted; within-year date coverage is unverified.", fontsize=9)
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(OUT / "option_1.png", dpi=160, bbox_inches="tight")
plt.close(fig)

dates = pd.date_range("2013-01-01", "2025-12-31", freq="D")
weekday_days = pd.Series(dates.day_name()).value_counts().reindex(WEEKDAYS)
average = counts[["weekday", "crash_count"]].copy()
average["calendar_dates_of_weekday"] = average["weekday"].astype(str).map(weekday_days)
average["average_crashes_per_weekday_date"] = (
    average["crash_count"] / average["calendar_dates_of_weekday"]
)
average.to_csv(OUT / "values_2.csv", index=False, float_format="%.8f")

fig, ax = plt.subplots(figsize=(10, 5.8))
bars = ax.bar(average["weekday"].astype(str), average["average_crashes_per_weekday_date"], color="#d17b35")
ax.set_title("Average crashes per weekday date (2013–2025)\nNYC police-reported motor vehicle crashes")
ax.set_ylabel("Average crashes per calendar occurrence of weekday")
ax.set_xlabel("Weekday of crash_date")
ax.grid(axis="y", alpha=0.25)
for bar, value in zip(bars, average["average_crashes_per_weekday_date"]):
    ax.annotate(f"{value:,.1f}", (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 4), textcoords="offset points", ha="center", fontsize=9)
fig.text(0.01, 0.01, "Limitation: calendar weekday dates are the denominator, not verified days of complete reporting or traffic exposure.", fontsize=9)
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(OUT / "option_2.png", dpi=160, bbox_inches="tight")
plt.close(fig)
