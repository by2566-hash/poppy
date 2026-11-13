from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

con = duckdb.connect()
counts = con.execute(
    """
    SELECT CAST(date_part('isodow', crash_date) AS INTEGER) AS weekday_number,
           COUNT(*) AS crash_count
    FROM read_parquet(?)
    WHERE crash_date BETWEEN DATE '2013-01-01' AND DATE '2025-12-31'
    GROUP BY weekday_number
    ORDER BY weekday_number
    """,
    [str(DATA)],
).df()
counts["weekday"] = counts["weekday_number"].map(lambda n: WEEKDAYS[n - 1])
counts = counts.set_index("weekday").reindex(WEEKDAYS).reset_index()
counts["crash_count"] = counts["crash_count"].astype("int64")
total = int(counts["crash_count"].sum())
counts["share_percent"] = counts["crash_count"] / total * 100

option_1 = counts[["weekday", "crash_count"]].copy()
option_1.to_csv(OUT / "values_1.csv", index=False)

option_2 = counts[["weekday", "crash_count", "share_percent"]].copy()
option_2["share_percent"] = option_2["share_percent"].round(4)
option_2.to_csv(OUT / "values_2.csv", index=False)

plt.rcParams.update({"font.size": 10, "axes.titlesize": 15, "axes.labelsize": 11})

fig, ax = plt.subplots(figsize=(10, 5.8))
bars = ax.bar(option_1["weekday"], option_1["crash_count"], color="#3B78A8")
ax.bar_label(bars, labels=[f"{v:,.0f}" for v in option_1["crash_count"]], padding=3, fontsize=9)
ax.set_title("Count of NYC police-reported crashes by weekday, 2013–2025", pad=34)
ax.text(
    0.5,
    1.025,
    "All crashes dated 2013–2025; counts are not adjusted for weekday traffic exposure.",
    transform=ax.transAxes,
    ha="center",
    va="bottom",
    fontsize=9,
    color="#555555",
)
ax.set_ylabel("Police-reported crashes")
ax.set_xlabel("Weekday of crash_date")
ax.tick_params(axis="x", rotation=20)
ax.set_ylim(0, option_1["crash_count"].max() * 1.13)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 5.8))
bars = ax.bar(option_2["weekday"], option_2["share_percent"], color="#D17A32")
ax.bar_label(
    bars,
    labels=[f"{v:.1f}%" for v in option_2["share_percent"]],
    padding=3,
    fontsize=9,
)
ax.set_title("Share of NYC police-reported crashes by weekday, 2013–2025", pad=34)
ax.text(
    0.5,
    1.025,
    "Share of all crashes dated 2013–2025; not adjusted for weekday traffic exposure.",
    transform=ax.transAxes,
    ha="center",
    va="bottom",
    fontsize=9,
    color="#555555",
)
ax.set_ylabel("Share of all in-period crashes (%)")
ax.set_xlabel("Weekday of crash_date")
ax.tick_params(axis="x", rotation=20)
ax.set_ylim(0, option_2["share_percent"].max() * 1.13)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)
