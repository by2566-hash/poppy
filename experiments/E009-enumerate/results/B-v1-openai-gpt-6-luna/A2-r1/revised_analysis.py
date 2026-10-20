import duckdb
import matplotlib.pyplot as plt
import pandas as pd


DATA_PATH = "data/crashes.parquet"
OUT_DIR = "out"

con = duckdb.connect()
summary = con.execute(
    """
    select case
               when extract(hour from crash_time) >= 20
                 or extract(hour from crash_time) < 6 then 1
               else 0
           end as is_night,
           count(*) as crashes,
           count(number_of_persons_injured) as known_injury,
           sum((number_of_persons_injured > 0)::int) as injury_crashes,
           count(number_of_persons_killed) as known_fatal,
           sum((number_of_persons_killed > 0)::int) as fatal_crashes,
           min(crash_date) as first_date,
           max(crash_date) as last_date,
           count(distinct crash_date) as observed_dates
    from read_parquet(?)
    where crash_time is not null
    group by 1
    order by 1
    """,
    [DATA_PATH],
).fetchdf()

labels = {0: "Day (6am–7:59pm)", 1: "Night (8pm–5:59am)"}
summary["period"] = summary["is_night"].map(labels)
summary["injury_rate_per_1000"] = (
    1000 * summary["injury_crashes"] / summary["known_injury"]
)
summary["fatal_rate_per_1000"] = (
    1000 * summary["fatal_crashes"] / summary["known_fatal"]
)
summary["avg_crashes_per_clock_hour_per_day"] = summary.apply(
    lambda row: row["crashes"]
    / (row["observed_dates"] * (10 if row["is_night"] else 14)),
    axis=1,
)

rows = []
for _, row in summary.iterrows():
    rows.append(
        {
            "period": row["period"],
            "outcome": "Crashes with at least one person injured",
            "events": int(row["injury_crashes"]),
            "denominator_crashes_with_known_outcome": int(row["known_injury"]),
            "rate_per_1000_crashes": row["injury_rate_per_1000"],
        }
    )
    rows.append(
        {
            "period": row["period"],
            "outcome": "Crashes with at least one person killed",
            "events": int(row["fatal_crashes"]),
            "denominator_crashes_with_known_outcome": int(row["known_fatal"]),
            "rate_per_1000_crashes": row["fatal_rate_per_1000"],
        }
    )

values = pd.DataFrame(rows)
values.to_csv(f"{OUT_DIR}/revised_values.csv", index=False)

fig, axes = plt.subplots(1, 2, figsize=(11, 5.2))
colors = ["#4C78A8", "#E45756"]
for ax, rate_col, title, event_col, denominator_col in [
    (
        axes[0],
        "injury_rate_per_1000",
        "Crashes involving injury",
        "injury_crashes",
        "known_injury",
    ),
    (
        axes[1],
        "fatal_rate_per_1000",
        "Crashes involving a death",
        "fatal_crashes",
        "known_fatal",
    ),
]:
    vals = [
        float(summary.loc[summary["is_night"] == index, rate_col].iloc[0])
        for index in (0, 1)
    ]
    bars = ax.bar(["Day", "Night"], vals, color=colors, width=0.62)
    ax.set_title(title, fontsize=13, weight="bold", pad=12)
    ax.set_ylabel("Crashes per 1,000 crashes")
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    ax.set_ylim(0, max(vals) * 1.27)
    for index, (bar, val) in enumerate(zip(bars, vals)):
        record = summary.loc[summary["is_night"] == index].iloc[0]
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            val + max(vals) * 0.035,
            f"{val:.1f}\n({int(record[event_col]):,} / {int(record[denominator_col]):,})",
            ha="center",
            va="bottom",
            fontsize=9,
        )

fig.suptitle(
    "Nighttime NYC crashes are more likely to be severe",
    fontsize=16,
    weight="bold",
    y=1.04,
)
fig.text(
    0.5,
    -0.015,
    "Day: 6am–7:59pm  |  Night: 8pm–5:59am  |  Excludes crashes missing a recorded time; each rate uses crashes with a recorded outcome field (injury or fatality, as applicable); not adjusted for traffic exposure.",
    ha="center",
    fontsize=9,
    color="#444444",
)
fig.tight_layout()
fig.savefig(f"{OUT_DIR}/revised.png", dpi=180, bbox_inches="tight")

day = summary.loc[summary["is_night"] == 0].iloc[0]
night = summary.loc[summary["is_night"] == 1].iloc[0]
print(
    "Reporting window:",
    summary["first_date"].min(),
    "to",
    summary["last_date"].max(),
    "| observed dates:",
    int(summary["observed_dates"].iloc[0]),
)
for _, row in summary.iterrows():
    print(
        f"{row['period']}: {int(row['crashes']):,} crashes; "
        f"injury {row['injury_rate_per_1000']:.2f}/1,000 "
        f"({int(row['injury_crashes']):,}/{int(row['known_injury']):,}); "
        f"fatal {row['fatal_rate_per_1000']:.2f}/1,000 "
        f"({int(row['fatal_crashes']):,}/{int(row['known_fatal']):,}); "
        "average crashes per clock-hour per day "
        f"{row['avg_crashes_per_clock_hour_per_day']:.2f}"
    )
print(
    "Night/day fatal-rate ratio:",
    f"{night['fatal_rate_per_1000'] / day['fatal_rate_per_1000']:.2f} times as high",
)
