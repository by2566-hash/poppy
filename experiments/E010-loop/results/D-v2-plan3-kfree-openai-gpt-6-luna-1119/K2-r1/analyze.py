import os

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


DATA_PATH = "data/crashes.parquet"
OUT_DIR = "out"
START = "2013-01-01"
END = "2025-12-31"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

os.makedirs(OUT_DIR, exist_ok=True)
connection = duckdb.connect()
query = f"""
    SELECT CAST(EXTRACT(ISODOW FROM crash_date) AS INTEGER) AS weekday_number,
           COUNT(*) AS crash_rows
    FROM read_parquet(?)
    WHERE crash_date >= DATE '{START}' AND crash_date <= DATE '{END}'
    GROUP BY weekday_number
"""
counts = connection.execute(query, [DATA_PATH]).fetchdf()
counts["weekday"] = counts["weekday_number"].map(lambda day: WEEKDAYS[day - 1])
counts = counts.set_index("weekday").reindex(WEEKDAYS).reset_index()
counts["crash_rows"] = counts["crash_rows"].fillna(0).astype("int64")


def save_chart(frame, value_column, title, ylabel, value_format, footnote, filename):
    fig, ax = plt.subplots(figsize=(10, 5.6))
    bars = ax.bar(frame["weekday"], frame[value_column], color="#277DA1")
    ax.set_title(title, loc="left", fontsize=13, pad=14)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Weekday of crash_date")
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", rotation=20)
    for bar, value in zip(bars, frame[value_column]):
        ax.annotate(value_format(value), (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=8)
    fig.text(0.01, 0.015, footnote, ha="left", va="bottom", fontsize=8, color="#444444")
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(os.path.join(OUT_DIR, filename), dpi=170, bbox_inches="tight")
    plt.close(fig)


population_note = (
    "NYC police-reported crash rows dated 2013–2025; not exposure-adjusted risk. "
    "Annual row totals varied substantially."
)

# Option 1: pooled raw counts.
option1 = counts[["weekday", "crash_rows"]].copy()
option1.to_csv(os.path.join(OUT_DIR, "values_1.csv"), index=False)
save_chart(
    option1, "crash_rows",
    "Crash rows by weekday | NYC police-reported crashes, 2013–2025",
    "Crash rows", lambda value: f"{int(value):,}", population_note, "option_1.png",
)

# Option 2: each weekday's share of all in-period crash rows.
option2 = counts[["weekday", "crash_rows"]].copy()
total_rows = int(option2["crash_rows"].sum())
option2["share_of_in_period_crash_rows_pct"] = option2["crash_rows"] / total_rows * 100
option2.to_csv(os.path.join(OUT_DIR, "values_2.csv"), index=False, float_format="%.8f")
save_chart(
    option2, "share_of_in_period_crash_rows_pct",
    "Share of all crash rows by weekday | NYC police-reported crashes, 2013–2025",
    "Share of in-period crash rows (%)", lambda value: f"{value:.2f}%", population_note, "option_2.png",
)

# Option 3: pooled weekday crash rows divided by calendar occurrences of that weekday.
calendar_dates = pd.date_range(START, END, freq="D")
occurrences = pd.Series(calendar_dates.weekday).value_counts().sort_index()
option3 = counts[["weekday", "crash_rows"]].copy()
option3["calendar_occurrences"] = [int(occurrences.loc[i]) for i in range(7)]
option3["mean_crash_rows_per_calendar_day"] = option3["crash_rows"] / option3["calendar_occurrences"]
option3.to_csv(os.path.join(OUT_DIR, "values_3.csv"), index=False, float_format="%.8f")
save_chart(
    option3, "mean_crash_rows_per_calendar_day",
    "Mean crash rows per calendar weekday | NYC police-reported crashes, 2013–2025",
    "Mean crash rows per occurrence of weekday", lambda value: f"{value:,.2f}", population_note, "option_3.png",
)

print(f"Included crash rows: {total_rows:,}")
for filename in ("values_1.csv", "values_2.csv", "values_3.csv"):
    print(f"\n{filename}")
    print(pd.read_csv(os.path.join(OUT_DIR, filename)).to_string(index=False))
