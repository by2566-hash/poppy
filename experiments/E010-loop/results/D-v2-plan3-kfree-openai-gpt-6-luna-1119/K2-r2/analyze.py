from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

con = duckdb.connect()
data_path = str(DATA).replace("'", "''")
query = f"""
    SELECT isodow(crash_date) AS weekday_number,
           strftime(crash_date, '%A') AS weekday,
           COUNT(*) AS crash_rows
    FROM read_parquet('{data_path}')
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY weekday_number, weekday
    ORDER BY weekday_number
"""
df = con.execute(query).df()
df = (pd.DataFrame({"weekday": WEEKDAYS})
      .merge(df, on="weekday", how="left")
      .fillna({"crash_rows": 0, "weekday_number": 0}))
df["crash_rows"] = df["crash_rows"].astype("int64")
total = int(df["crash_rows"].sum())
df["share_percent"] = df["crash_rows"] / total * 100

df[["weekday", "crash_rows"]].to_csv(OUT / "values_1.csv", index=False)
df[["weekday", "crash_rows", "share_percent"]].to_csv(OUT / "values_2.csv", index=False, float_format="%.6f")

for option_id, metric, value_column, ylabel, title in [
    (1, "Crash-record count", "crash_rows", "Number of crash records",
     "Police-reported NYC crash-row counts by weekday | 2013–2025"),
    (2, "Share of crash records", "share_percent", "Share of all eligible crash records (%)",
     "Share of NYC police-reported crash records by weekday | 2013–2025"),
]:
    fig, ax = plt.subplots(figsize=(9, 5.4))
    bars = ax.bar(df["weekday"], df[value_column], color="#2476a8", width=0.72)
    ax.set_title(title, fontsize=14, pad=16)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Weekday of crash date (Monday–Sunday)")
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", rotation=25)
    if option_id == 2:
        ax.set_ylim(0, float(df[value_column].max()) * 1.16)
        for bar, value in zip(bars, df[value_column]):
            ax.annotate(f"{value:.1f}%", (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        xytext=(0, 4), textcoords="offset points", ha="center", fontsize=9)
    fig.text(0.5, 0.015,
             "Pooled police-reported crash rows; not adjusted for calendar-day counts or travel exposure. "
             "Annual record totals vary.",
             ha="center", fontsize=8, color="#444444")
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(OUT / f"option_{option_id}.png", dpi=170, bbox_inches="tight")
    plt.close(fig)
