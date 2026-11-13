import json
from pathlib import Path

import duckdb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


OUT = Path("out")
OUT.mkdir(exist_ok=True)
con = duckdb.connect()
parquet = "./data/crashes.parquet"

summary = con.execute(
    """
    WITH by_time AS (
        SELECT
            CASE WHEN EXTRACT(HOUR FROM crash_time) >= 18
                       OR EXTRACT(HOUR FROM crash_time) < 6
                 THEN 'Night (6pm–5:59am)'
                 ELSE 'Day (6am–5:59pm)' END AS period,
            number_of_persons_injured AS injured,
            number_of_persons_killed AS killed
        FROM read_parquet(?)
    )
    SELECT
        period,
        COUNT(*) AS crash_records,
        COUNT(*) FILTER (WHERE injured IS NOT NULL AND killed IS NOT NULL) AS complete_crashes,
        COUNT(*) FILTER (WHERE injured IS NOT NULL AND killed IS NOT NULL AND injured + killed > 0) AS harm_crashes,
        COUNT(*) FILTER (WHERE injured IS NOT NULL AND killed IS NOT NULL AND killed > 0) AS fatal_crashes,
        SUM(injured) FILTER (WHERE injured IS NOT NULL AND killed IS NOT NULL) AS injured_persons,
        SUM(killed) FILTER (WHERE injured IS NOT NULL AND killed IS NOT NULL) AS killed_persons
    FROM by_time
    GROUP BY period
    """,
    [parquet],
).fetchdf()
order = ["Day (6am–5:59pm)", "Night (6pm–5:59am)"]
summary["period"] = pd.Categorical(summary["period"], categories=order, ordered=True)
summary = summary.sort_values("period").reset_index(drop=True)
summary["casualties"] = summary["injured_persons"] + summary["killed_persons"]
summary["harm_crash_pct"] = 100 * summary["harm_crashes"] / summary["complete_crashes"]
summary["casualties_per_100"] = 100 * summary["casualties"] / summary["complete_crashes"]
summary["fatal_crashes_per_1000"] = 1000 * summary["fatal_crashes"] / summary["complete_crashes"]

date_range = con.execute(
    "SELECT MIN(crash_date), MAX(crash_date) FROM read_parquet(?)", [parquet]
).fetchone()
period_text = f"Data: {date_range[0]} to {date_range[1]}"
colors = ["#4C78A8", "#E45756"]


def save_bar(frame, id_, value_col, ylabel, title, formatter, note):
    fig, ax = plt.subplots(figsize=(8.6, 5.1))
    bars = ax.bar(frame["period"].astype(str), frame[value_col], color=colors, width=0.62)
    ax.set_title(title, fontsize=15, weight="bold", pad=14)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", alpha=0.22)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_ylim(0, max(frame[value_col]) * 1.24)
    for bar, value in zip(bars, frame[value_col]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(frame[value_col]) * 0.025,
                formatter(value), ha="center", va="bottom", fontsize=11, weight="bold")
    fig.text(0.5, 0.02, f"{period_text}  •  {note}", ha="center", fontsize=8.5, color="#555555")
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(OUT / f"option_{id_}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


# 1: equal-duration crash counts (all reported crashes)
v1 = summary[["period", "crash_records"]].copy()
v1["share_of_all_crashes_pct"] = 100 * v1["crash_records"] / v1["crash_records"].sum()
v1.to_csv(OUT / "values_1.csv", index=False)
save_bar(v1, 1, "crash_records", "Reported crashes", "Crash reports by equal 12-hour block",
         lambda x: f"{x:,.0f}", "Crash counts are not adjusted for traffic exposure")

# Severity-rate data use only crashes with known injured and killed totals.
v2 = summary[["period", "complete_crashes", "harm_crashes", "harm_crash_pct"]].copy()
v2.to_csv(OUT / "values_2.csv", index=False)
save_bar(v2, 2, "harm_crash_pct", "Crashes with ≥1 person injured or killed (%)",
         "Share of crashes involving an injury or death", lambda x: f"{x:.1f}%",
         "Denominator: crashes with known injury and death totals")

v3 = summary[["period", "complete_crashes", "injured_persons", "killed_persons", "casualties", "casualties_per_100"]].copy()
v3.to_csv(OUT / "values_3.csv", index=False)
save_bar(v3, 3, "casualties_per_100", "People injured or killed per 100 crashes",
         "Person casualties per 100 crashes", lambda x: f"{x:.1f}",
         "Casualties are people injured plus killed; denominator has known totals")

v4 = summary[["period", "complete_crashes", "fatal_crashes", "fatal_crashes_per_1000"]].copy()
v4.to_csv(OUT / "values_4.csv", index=False)
save_bar(v4, 4, "fatal_crashes_per_1000", "Crashes with ≥1 death per 1,000 crashes",
         "Fatal-crash rate among reported crashes", lambda x: f"{x:.2f}",
         "Denominator: crashes with known injury and death totals")

day = summary.iloc[0]
night = summary.iloc[1]
options = {
    "options": [
        {
            "id": 1,
            "metric": "Number of reported crashes",
            "denominator": "None; raw count over each equal 12-hour block",
            "grouping": "Night 6pm–5:59am versus day 6am–5:59pm",
            "chart_type": "Two-bar count chart",
            "reason": "Crash volume communicates the absolute reported burden in each equally long part of the day.",
            "probability": 0.18,
            "answer": f"The file records {int(night.crash_records):,} nighttime crashes versus {int(day.crash_records):,} daytime crashes, but those counts alone cannot establish per-trip danger because traffic exposure is unavailable.",
            "interpretation": "This framing answers which equal-length time block has more reported crashes: the daytime block has more. Counts are useful for describing total crash burden, but without traffic or travel exposure they do not show the risk of a crash for a person traveling at night.",
        },
        {
            "id": 2,
            "metric": "Percentage of crashes with at least one person injured or killed",
            "denominator": "Crashes with nonmissing person-injured and person-killed totals",
            "grouping": "Night 6pm–5:59am versus day 6am–5:59pm",
            "chart_type": "Two-bar percentage chart",
            "reason": "The share of crashes with any human harm is an intuitive crash-level measure of severity.",
            "probability": 0.34,
            "answer": f"Among crashes with known outcomes, {night.harm_crash_pct:.1f}% of nighttime crashes involved injury or death, versus {day.harm_crash_pct:.1f}% of daytime crashes.",
            "interpretation": "This framing answers whether a reported crash is more likely to involve a harmed person at night; the nighttime share is higher. It compares severity conditional on a crash and excludes records with missing injury or death totals, but it does not estimate risk per trip or explain why the difference occurs.",
        },
        {
            "id": 3,
            "metric": "People injured or killed per 100 crashes",
            "denominator": "Crashes with nonmissing person-injured and person-killed totals",
            "grouping": "Night 6pm–5:59am versus day 6am–5:59pm",
            "chart_type": "Two-bar rate chart",
            "reason": "A casualty count per crash captures the total human toll, including multiple people harmed in one collision.",
            "probability": 0.25,
            "answer": f"The data show {night.casualties_per_100:.1f} people injured or killed per 100 nighttime crashes, compared with {day.casualties_per_100:.1f} per 100 daytime crashes.",
            "interpretation": "This framing answers whether the average reported nighttime crash produces more casualties, and the nighttime casualty total per 100 crashes is higher. It accounts for multiple people harmed in one crash and uses crashes with known outcomes, but cannot establish per-traveler risk because exposure is not measured.",
        },
        {
            "id": 4,
            "metric": "Crashes with at least one death per 1,000 crashes",
            "denominator": "Crashes with nonmissing person-injured and person-killed totals",
            "grouping": "Night 6pm–5:59am versus day 6am–5:59pm",
            "chart_type": "Two-bar rate chart",
            "reason": "Fatal crashes are a distinct, high-severity outcome and the per-crash rate adjusts for the different number of crashes in each block.",
            "probability": 0.23,
            "answer": f"There were {night.fatal_crashes_per_1000:.2f} fatal crashes per 1,000 nighttime crashes versus {day.fatal_crashes_per_1000:.2f} per 1,000 daytime crashes.",
            "interpretation": "This framing answers whether a crash is more likely to be fatal at night, and the observed rate among reported crashes is higher at night. It isolates the most severe outcome with a per-crash denominator, but it does not estimate a traveler's fatality risk or account for differences in traffic exposure.",
        },
    ]
}
(OUT / "options.json").write_text(json.dumps(options, indent=2) + "\n")
print(summary.to_string(index=False))
print(f"Saved charts, values, and options.json in {OUT}")
