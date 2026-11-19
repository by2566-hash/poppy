from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
START = "2013-01-01"
END = "2025-12-31"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

data_path = str(DATA).replace("'", "''")
con = duckdb.connect()
counts = con.execute(
    f"""SELECT isodow(crash_date) AS weekday_num, count(*) AS crashes
        FROM read_parquet('{data_path}')
        WHERE crash_date >= DATE '{START}' AND crash_date <= DATE '{END}'
        GROUP BY weekday_num ORDER BY weekday_num"""
).df()

calendar = pd.DataFrame({"date": pd.date_range(START, END, freq="D")})
calendar["weekday_num"] = calendar["date"].dt.isocalendar().day.astype(int)
date_counts = calendar.groupby("weekday_num").size().reindex(range(1, 8), fill_value=0)

values = pd.DataFrame({"weekday_num": range(1, 8), "weekday": WEEKDAYS})
values = values.merge(counts, on="weekday_num", how="left")
values["crashes"] = values["crashes"].fillna(0).astype("int64")
values["share_pct"] = values["crashes"] / values["crashes"].sum() * 100
values["calendar_dates"] = values["weekday_num"].map(date_counts).astype("int64")
values["average_crashes_per_calendar_date"] = values["crashes"] / values["calendar_dates"]

values[["weekday", "crashes", "share_pct"]].to_csv(
    OUT / "values_1.csv", index=False, float_format="%.6f"
)
values[["weekday", "crashes", "calendar_dates", "average_crashes_per_calendar_date"]].to_csv(
    OUT / "values_2.csv", index=False, float_format="%.6f"
)


def save_bar(option_id, metric_column, title, ylabel, subtitle, value_format):
    fig, ax = plt.subplots(figsize=(10, 5.6), layout="constrained")
    bars = ax.bar(values["weekday"], values[metric_column], color="#3977a8", width=0.72)
    ax.set_title(title, fontsize=15, pad=16)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Day of week")
    ax.grid(axis="y", color="#d9dfe5", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", rotation=20)
    for bar, value in zip(bars, values[metric_column]):
        ax.annotate(value_format(value),
                    (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=8)
    fig.text(0.5, -0.015, subtitle, ha="center", fontsize=9, color="#444444")
    fig.savefig(OUT / f"option_{option_id}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


save_bar(
    1,
    "crashes",
    "Police-reported NYC crashes by weekday, 2013–2025",
    "Recorded crashes",
    "Limitation: includes only police-reported crashes with usable dates; not every crash that occurred.",
    lambda x: f"{int(x):,}",
)
save_bar(
    2,
    "average_crashes_per_calendar_date",
    "Average police-reported NYC crashes per weekday date, 2013–2025",
    "Average recorded crashes per calendar date",
    "Limitation: includes only police-reported crashes with usable dates; not adjusted for traffic exposure.",
    lambda x: f"{x:,.1f}",
)
