import json
import os

import duckdb
import matplotlib
from matplotlib.ticker import PercentFormatter

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


DATA_PATH = "data/crashes.parquet"
OUT_DIR = "out"
os.makedirs(OUT_DIR, exist_ok=True)

con = duckdb.connect()
rows = con.execute(
    """
    WITH base AS (
      SELECT crash_date,
             EXTRACT(hour FROM crash_time)::INTEGER AS hour,
             COALESCE(number_of_persons_injured, 0) AS injured,
             COALESCE(number_of_persons_killed, 0) AS killed
      FROM read_parquet(?)
      WHERE crash_time IS NOT NULL
    )
    SELECT CASE WHEN hour >= 20 OR hour < 6 THEN 'Night' ELSE 'Day' END AS period,
           COUNT(*) AS crashes,
           COUNT(DISTINCT crash_date) AS dates,
           COUNT(*) FILTER (WHERE injured > 0 OR killed > 0) AS injury_or_fatal_crashes,
           COUNT(*) FILTER (WHERE killed > 0) AS fatal_crashes
    FROM base
    GROUP BY period
    """,
    [DATA_PATH],
).fetchdf().set_index("period")

period_order = ["Night", "Day"]
period_hours = {"Night": 10, "Day": 14}
all_dates = int(rows["dates"].max())
night_crashes = int(rows.loc["Night", "crashes"])
day_crashes = int(rows.loc["Day", "crashes"])
night_injury_fatal = int(rows.loc["Night", "injury_or_fatal_crashes"])
day_injury_fatal = int(rows.loc["Day", "injury_or_fatal_crashes"])
night_fatal = int(rows.loc["Night", "fatal_crashes"])
day_fatal = int(rows.loc["Day", "fatal_crashes"])

crash_values = pd.DataFrame(
    [
        {
            "period": period,
            "crashes": int(rows.loc[period, "crashes"]),
            "dates": all_dates,
            "clock_hours_per_date": period_hours[period],
            "eligible_clock_hours": all_dates * period_hours[period],
            "average_crashes_per_clock_hour": float(
                rows.loc[period, "crashes"] / (all_dates * period_hours[period])
            ),
        }
        for period in period_order
    ]
)
crash_values.to_csv(f"{OUT_DIR}/values_1.csv", index=False)

severity_values = pd.DataFrame(
    [
        {
            "period": period,
            "crashes": int(rows.loc[period, "crashes"]),
            "crashes_with_injury_or_death": int(rows.loc[period, "injury_or_fatal_crashes"]),
            "share_with_injury_or_death": float(
                rows.loc[period, "injury_or_fatal_crashes"] / rows.loc[period, "crashes"]
            ),
        }
        for period in period_order
    ]
)
severity_values.to_csv(f"{OUT_DIR}/values_2.csv", index=False)

fatal_values = pd.DataFrame(
    [
        {
            "period": period,
            "crashes": int(rows.loc[period, "crashes"]),
            "fatal_crashes": int(rows.loc[period, "fatal_crashes"]),
            "share_fatal": float(rows.loc[period, "fatal_crashes"] / rows.loc[period, "crashes"]),
        }
        for period in period_order
    ]
)
fatal_values.to_csv(f"{OUT_DIR}/values_3.csv", index=False)


def draw_bars(values, value_column, filename, title, ylabel, percent=False):
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    colors = ["#376996", "#D58A35"]
    vals = values[value_column].tolist()
    bars = ax.bar(values["period"], vals, color=colors, width=0.56)
    ax.set_title(title, loc="left", fontsize=15, weight="bold", pad=14)
    ax.set_ylabel(ylabel)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#D9DEE5", linewidth=0.8)
    ax.set_axisbelow(True)
    pad = max(vals) * 0.025
    for bar, value in zip(bars, vals):
        if percent:
            label = f"{value:.2%}" if max(vals) < 0.01 else f"{value:.1%}"
        else:
            label = f"{value:,.1f}"
        ax.text(bar.get_x() + bar.get_width() / 2, value + pad, label,
                ha="center", va="bottom", fontsize=12, weight="bold")
    ax.set_ylim(0, max(vals) * 1.18)
    if percent:
        ax.yaxis.set_major_formatter(
            PercentFormatter(xmax=1, decimals=2 if max(vals) < 0.01 else 0)
        )
    fig.text(
        0.01, 0.01,
        "Night = 8 pm–5:59 am; day = 6 am–7:59 pm. NYC crash records, 2012-07-01 to 2026-06-11; not exposure-adjusted, and clock time is not daylight.",
        ha="left", va="bottom", fontsize=8, color="#4B5563",
    )
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(f"{OUT_DIR}/{filename}", dpi=180, bbox_inches="tight")
    plt.close(fig)


draw_bars(
    crash_values, "average_crashes_per_clock_hour", "option_1.png",
    "Recorded crashes per clock-hour", "Average crashes per clock-hour across dates",
)
draw_bars(
    severity_values, "share_with_injury_or_death", "option_2.png",
    "Crashes involving injury or death", "Share of crashes",
    percent=True,
)
draw_bars(
    fatal_values, "share_fatal", "option_3.png",
    "Crashes involving at least one death", "Share of crashes",
    percent=True,
)

options = {
    "options": [
        {
            "id": 1,
            "metric": "Average recorded crashes per clock-hour",
            "denominator": "Number of dates in the dataset multiplied by clock-hours in each period (10 night, 14 day)",
            "grouping": "Night (8 pm–5:59 am) vs day (6 am–7:59 pm)",
            "chart_type": "Bar chart",
            "reason": "A clock-hour average compares the observed crash burden across periods of unequal length without treating the ten-hour night as equal in duration to the fourteen-hour day.",
            "probability": 0.3,
            "answer": f"The records average {crash_values.loc[0, 'average_crashes_per_clock_hour']:.1f} crashes per nighttime clock-hour versus {crash_values.loc[1, 'average_crashes_per_clock_hour']:.1f} per daytime clock-hour; without traffic exposure data, this cannot establish greater crash risk per trip at night.",
            "interpretation": f"This framing answers when the dataset records the most crashes per hour, averaging {crash_values.loc[0, 'average_crashes_per_clock_hour']:.1f} per night clock-hour and {crash_values.loc[1, 'average_crashes_per_clock_hour']:.1f} per daytime clock-hour. It is defensible for comparing crash burden while accounting for the unequal number of hours in the two periods. It leaves unanswered risk per trip or mile, and clock time does not identify actual darkness.",
        },
        {
            "id": 2,
            "metric": "Share of crashes with at least one person injured or killed",
            "denominator": "All crash records with a recorded time in the same period",
            "grouping": "Night (8 pm–5:59 am) vs day (6 am–7:59 pm)",
            "chart_type": "Bar chart",
            "reason": "The crash-level share of events with harm directly compares the observed severity of reported crashes across night and day.",
            "probability": 0.45,
            "answer": f"Injury-or-death crashes made up {night_injury_fatal / night_crashes:.1%} of nighttime records versus {day_injury_fatal / day_crashes:.1%} of daytime records, but this conditional comparison cannot show per-trip risk.",
            "interpretation": f"This framing addresses whether a reported crash is more likely to involve harm at night: {night_injury_fatal / night_crashes:.1%} of night crashes involved an injury or death, compared with {day_injury_fatal / day_crashes:.1%} by day. It is defensible because each crash contributes once to a severity share, regardless of the number of people hurt. It leaves unanswered the risk of being in a crash in the first place per trip, person, or mile, and uses clock-time rather than actual light conditions.",
        },
        {
            "id": 3,
            "metric": "Share of crashes with at least one person killed",
            "denominator": "All crash records with a recorded time in the same period",
            "grouping": "Night (8 pm–5:59 am) vs day (6 am–7:59 pm)",
            "chart_type": "Bar chart",
            "reason": "A fatal-crash share isolates the most severe reported outcome and gives a news report a focused measure of crash severity.",
            "probability": 0.25,
            "answer": f"Fatal crashes were {night_fatal / night_crashes:.2%} of nighttime records versus {day_fatal / day_crashes:.2%} of daytime records, though this does not establish greater per-trip danger at night.",
            "interpretation": f"This framing focuses on the most severe recorded outcome: {night_fatal / night_crashes:.2%} of nighttime crashes involved a death, compared with {day_fatal / day_crashes:.2%} of daytime crashes. The denominator is crashes, so it shows fatality severity conditional on a crash, not fatality risk for travelers. It leaves unanswered exposure-adjusted danger, and the dataset does not say whether crashes occurred in darkness.",
        },
    ]
}
with open(f"{OUT_DIR}/options.json", "w", encoding="utf-8") as f:
    json.dump(options, f, indent=2, ensure_ascii=False)
    f.write("\n")

print("Date range: 2012-07-01 to 2026-06-11")
print("Clock-time records:", int(rows["crashes"].sum()))
print(crash_values.to_string(index=False))
print(severity_values.to_string(index=False))
print(fatal_values.to_string(index=False))
