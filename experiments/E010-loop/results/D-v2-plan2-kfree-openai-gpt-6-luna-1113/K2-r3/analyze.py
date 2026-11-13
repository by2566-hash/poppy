import duckdb
import matplotlib.pyplot as plt
import pandas as pd

DATA = "data/crashes.parquet"
START = "2013-01-01"
END = "2025-12-31"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

con = duckdb.connect()
counts = con.execute(
    """SELECT dayofweek(crash_date) AS duckdb_dow, COUNT(*) AS crashes
       FROM read_parquet(?)
       WHERE crash_date >= DATE '2013-01-01' AND crash_date <= DATE '2025-12-31'
       GROUP BY duckdb_dow""",
    [DATA],
).df()
# DuckDB dayofweek is Sunday=0 through Saturday=6; convert to Monday=0 through Sunday=6.
counts["weekday_order"] = (counts["duckdb_dow"] + 6) % 7
counts = counts.set_index("weekday_order").reindex(range(7), fill_value=0)
counts.index.name = "weekday_order"
counts = counts.reset_index()
counts["weekday"] = WEEKDAYS
counts["crashes"] = counts["crashes"].astype("int64")

dates = pd.date_range(START, END, freq="D")
exposure = pd.Series(dates.weekday).value_counts().reindex(range(7), fill_value=0).sort_index()
values = counts[["weekday", "crashes"]].copy()
values.to_csv("out/values_1.csv", index=False)

daily = counts[["weekday", "weekday_order", "crashes"]].copy()
daily["calendar_dates"] = daily["weekday_order"].map(exposure).astype("int64")
daily["avg_crashes_per_calendar_date"] = daily["crashes"] / daily["calendar_dates"]
daily[["weekday", "crashes", "calendar_dates", "avg_crashes_per_calendar_date"]].to_csv(
    "out/values_2.csv", index=False, float_format="%.6f"
)

plt.rcParams.update({"font.size": 10, "axes.titlesize": 14, "axes.labelsize": 11})

fig, ax = plt.subplots(figsize=(10, 5.7))
bars = ax.bar(WEEKDAYS, counts["crashes"], color="#2878B5")
ax.set_title("Police-reported crash records by weekday | NYC, 2013–2025", pad=14, weight="bold")
ax.text(
    0.5, 1.015,
    "All 2,132,218 records with crash dates in the 13-year period; weekdays ordered Monday–Sunday",
    transform=ax.transAxes, ha="center", va="bottom", fontsize=9, color="#444444",
)
ax.set_ylabel("Crash records")
ax.set_xlabel("Weekday of crash date")
ax.grid(axis="y", color="#DDDDDD", linewidth=0.8)
ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)
ax.bar_label(bars, labels=[f"{int(v):,}" for v in counts["crashes"]], padding=3, fontsize=8)
fig.text(
    0.5, 0.015,
    "Limitation: pooled counts reflect crash-record volume, not risk per trip or distance traveled.",
    ha="center", fontsize=8, color="#555555",
)
fig.tight_layout(rect=[0, 0.05, 1, 0.95])
fig.savefig("out/option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 5.7))
bars = ax.bar(WEEKDAYS, daily["crashes"] / daily["calendar_dates"], color="#38A17A")
ax.set_title(
    "Average police-reported crash records per weekday date | NYC, 2013–2025",
    pad=14, weight="bold",
)
ax.text(
    0.5, 1.015,
    "Crash records divided by calendar dates of each weekday, inclusive of 2013-01-01 to 2025-12-31",
    transform=ax.transAxes, ha="center", va="bottom", fontsize=9, color="#444444",
)
ax.set_ylabel("Mean crash records per calendar date")
ax.set_xlabel("Weekday")
ax.grid(axis="y", color="#DDDDDD", linewidth=0.8)
ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)
ax.bar_label(bars, labels=[f"{v:,.1f}" for v in daily["crashes"] / daily["calendar_dates"]], padding=3, fontsize=8)
fig.text(
    0.5, 0.015,
    "Limitation: adjusts for weekday-date counts only, not traffic exposure or year-specific changes.",
    ha="center", fontsize=8, color="#555555",
)
fig.tight_layout(rect=[0, 0.05, 1, 0.95])
fig.savefig("out/option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)
