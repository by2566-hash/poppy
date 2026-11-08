import json
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)
PARQUET = ROOT / "data" / "crashes.parquet"
YEARS = "2013 through 2025 (the 13 complete calendar years in the file)"

con = duckdb.connect()
summary = con.execute(
    """
    WITH selected AS (
      SELECT *,
        CASE WHEN extract(hour FROM crash_time) >= 20
                   OR extract(hour FROM crash_time) < 6
             THEN 'Night (8pm–5:59am)' ELSE 'Day (6am–7:59pm)' END AS period
      FROM read_parquet(?)
      WHERE extract(year FROM crash_date) BETWEEN 2013 AND 2025
        AND crash_time IS NOT NULL
    )
    SELECT period, count(*) AS crashes,
      count(*) FILTER (WHERE number_of_persons_injured IS NOT NULL
                       AND number_of_persons_killed IS NOT NULL) AS known_harm,
      count(*) FILTER (WHERE number_of_persons_injured IS NULL
                       OR number_of_persons_killed IS NULL) AS missing_harm,
      count(*) FILTER (WHERE number_of_persons_injured > 0
                       OR number_of_persons_killed > 0) AS harm_crashes,
      count(*) FILTER (WHERE number_of_persons_killed IS NOT NULL) AS known_death,
      count(*) FILTER (WHERE number_of_persons_killed > 0) AS fatal_crashes,
      sum(number_of_persons_killed) AS killed_people,
      sum(number_of_persons_injured) AS injured_people,
      count(DISTINCT crash_date) AS dates
    FROM selected GROUP BY period
    """,
    [str(PARQUET)],
).df().set_index("period")

coverage = con.execute(
    """
    SELECT count(*) AS all_rows,
      count(*) FILTER (WHERE extract(year FROM crash_date) = 2012) AS rows_2012,
      count(*) FILTER (WHERE extract(year FROM crash_date) = 2026) AS rows_2026,
      count(*) FILTER (WHERE extract(year FROM crash_date) BETWEEN 2013 AND 2025
                       AND (number_of_persons_injured IS NULL
                            OR number_of_persons_killed IS NULL)) AS missing_harm,
      count(*) FILTER (WHERE extract(year FROM crash_date) BETWEEN 2013 AND 2025
                       AND number_of_persons_killed IS NULL) AS missing_death,
      count(*) FILTER (WHERE extract(year FROM crash_date) BETWEEN 2013 AND 2025
                       AND crash_time IS NULL) AS missing_time
    FROM read_parquet(?)
    """,
    [str(PARQUET)],
).fetchone()
all_rows, n2012, n2026, missing_harm, missing_death, missing_time = coverage
excluded_years_share = (n2012 + n2026) / all_rows * 100
year_2012_share = n2012 / all_rows * 100
year_2026_share = n2026 / all_rows * 100

night = "Night (8pm–5:59am)"
day = "Day (6am–7:59pm)"
order = [day, night]


def rate(numerator, denominator, multiplier):
    return numerator / denominator * multiplier


def save_chart(option_id, title, ylabel, values, fmt, note):
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    bars = ax.bar(["Day\n6am–7:59pm", "Night\n8pm–5:59am"], values,
                  color=["#3977a8", "#e17c36"], width=0.58)
    ax.set_title(title, loc="left", fontsize=14, weight="bold", pad=14)
    ax.set_ylabel(ylabel)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.22)
    ax.set_axisbelow(True)
    ax.bar_label(bars, labels=[fmt.format(v) for v in values], padding=5,
                 fontsize=11, weight="bold")
    ax.text(0, -0.22, note, transform=ax.transAxes, fontsize=8.5,
            color="#444444", va="top", wrap=True)
    ax.margins(y=0.18)
    fig.tight_layout()
    fig.savefig(OUT / f"option_{option_id}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


# Framing 1: share of crashes that involved at least one injured or killed person.
harm_rows = []
harm_values = []
for period in order:
    row = summary.loc[period]
    value = rate(row.harm_crashes, row.known_harm, 100)
    harm_values.append(value)
    harm_rows.append({
        "period": period, "harm_crashes": int(row.harm_crashes),
        "crashes_with_both_outcomes_reported": int(row.known_harm),
        "crashes_missing_injury_or_death_value": int(row.missing_harm),
        "harm_crash_percent": value,
    })
pd.DataFrame(harm_rows).to_csv(OUT / "values_1.csv", index=False)
save_chart(1, "A larger share of nighttime crashes involved injury or death",
           "Crashes with ≥1 person injured or killed (%)", harm_values,
           "{:.1f}%", f"NYC police-reported crashes, {YEARS}; excludes crashes missing either outcome count.")

# Framing 2: fatal crashes per 1,000 crashes with a reported killed-person count.
fatal_rows = []
fatal_values = []
for period in order:
    row = summary.loc[period]
    value = rate(row.fatal_crashes, row.known_death, 1000)
    fatal_values.append(value)
    fatal_rows.append({
        "period": period, "crashes_with_at_least_one_person_killed": int(row.fatal_crashes),
        "crashes_with_killed_count_reported": int(row.known_death),
        "crashes_missing_killed_count": int(row.crashes - row.known_death),
        "fatal_crashes_per_1000_crashes": value,
    })
pd.DataFrame(fatal_rows).to_csv(OUT / "values_2.csv", index=False)
save_chart(2, "Fatal crashes were more common among nighttime crashes",
           "Crashes with ≥1 death per 1,000 crashes", fatal_values,
           "{:.2f}", f"NYC police-reported crashes, {YEARS}; denominator includes crashes with a reported killed count.")

# Framing 3: crash count normalized only by the clock-hours in each time band.
volume_rows = []
volume_values = []
for period, hours_per_day in [(day, 14), (night, 10)]:
    row = summary.loc[period]
    hours = int(row.dates) * hours_per_day
    value = row.crashes / hours
    volume_values.append(value)
    volume_rows.append({
        "period": period, "crashes": int(row.crashes), "observed_calendar_dates": int(row.dates),
        "clock_hours_in_period": hours_per_day, "period_clock_hours": hours,
        "crashes_per_clock_hour": value,
    })
pd.DataFrame(volume_rows).to_csv(OUT / "values_3.csv", index=False)
save_chart(3, "More crashes occurred per clock-hour during daytime",
           "Police-reported crashes per clock-hour", volume_values,
           "{:.1f}", f"NYC police-reported crashes, {YEARS}; clock-time normalization is not adjusted for traffic volume.")

fmt_pct = lambda x: f"{x:.1f}%"
fmt_rate = lambda x: f"{x:.2f}"
fmt_hour = lambda x: f"{x:.1f}"
exclusion_years = (
    f"all {n2012:,} 2012 rows ({year_2012_share:.2f}% of the file; only July–December is present) "
    f"and all {n2026:,} 2026 rows ({year_2026_share:.2f}%; only January 1–June 11 is present), "
    f"together {excluded_years_share:.2f}%"
)

options = [
    {
        "id": 1,
        "metric": "Crash involvement in any reported injury or death",
        "denominator": "Crashes with non-NULL values for both persons injured and persons killed",
        "grouping": "Day (6am–7:59pm) vs night (8pm–5:59am)",
        "chart_type": "Two-bar comparison of percentages",
        "reason": "The share of crashes involving harm compares how often a reported collision has a human consequence in each time band.",
        "probability": 0.40,
        "answer": f"The file cannot establish whether streets are more dangerous at night without travel exposure, but {fmt_pct(harm_values[1])} of nighttime crashes involved injury or death versus {fmt_pct(harm_values[0])} of daytime crashes.",
        "interpretation": (
            f"This answers whether a reported crash was more likely to involve injury or death at night: the chart shows {fmt_pct(harm_values[1])} at night versus {fmt_pct(harm_values[0])} by day. "
            "This is a defensible severity comparison because the denominator is all crashes with both outcome counts observed, rather than raw counts that differ with the number of crashes. "
            "It does not measure the chance of a person being hurt per trip or per mile, since traffic and travel exposure are not in this file. "
            f"It uses {YEARS}; it excludes {exclusion_years}, {missing_harm:,} included-year rows ({missing_harm / all_rows * 100:.3f}% of all file rows) missing an injury or death value, and no rows for NULL crash time."
        ),
    },
    {
        "id": 2,
        "metric": "Crashes with at least one person killed per 1,000 crashes",
        "denominator": "Crashes with a non-NULL persons-killed count",
        "grouping": "Day (6am–7:59pm) vs night (8pm–5:59am)",
        "chart_type": "Two-bar comparison of fatal crashes per 1,000 crashes",
        "reason": "Fatal-crash frequency isolates the most severe outcome and is less diluted by non-injury collisions than a broad harm measure.",
        "probability": 0.35,
        "answer": f"The file cannot establish whether streets are more dangerous at night without travel exposure, but fatal crashes occurred at {fmt_rate(fatal_values[1])} per 1,000 nighttime crashes versus {fmt_rate(fatal_values[0])} per 1,000 daytime crashes ({fatal_values[1] / fatal_values[0]:.1f} times as high at night).",
        "interpretation": (
            f"This answers whether a reported crash was more likely to be fatal at night: the chart shows {fmt_rate(fatal_values[1])} fatal crashes per 1,000 at night and {fmt_rate(fatal_values[0])} by day. "
            "It is a defensible news measure because it focuses on the clearest severe outcome and uses crashes with known killed counts as the denominator. "
            "It does not establish fatality risk per traveler, trip, or mile, because exposure is unavailable, and it says nothing about less severe injuries. "
            f"It uses {YEARS}; it excludes {exclusion_years}, {missing_death:,} included-year rows ({missing_death / all_rows * 100:.3f}% of all file rows) with NULL persons-killed counts, and no rows for NULL crash time."
        ),
    },
    {
        "id": 3,
        "metric": "Police-reported crashes per clock-hour",
        "denominator": "Clock-hours in each time band over all observed dates (14 daytime hours or 10 nighttime hours per date)",
        "grouping": "Day (6am–7:59pm) vs night (8pm–5:59am)",
        "chart_type": "Two-bar comparison of crashes per clock-hour",
        "reason": "Clock-hour normalization makes the volume comparison fairer because the daytime and nighttime bands have different durations.",
        "probability": 0.25,
        "answer": f"The file cannot establish whether streets are more dangerous without travel exposure; it records {fmt_hour(volume_values[1])} crashes per nighttime clock-hour versus {fmt_hour(volume_values[0])} per daytime clock-hour.",
        "interpretation": (
            f"This answers how many reported collisions occur in each time band after accounting for its duration: the chart shows {fmt_hour(volume_values[1])} per nighttime clock-hour versus {fmt_hour(volume_values[0])} by day. "
            "It is a defensible volume comparison because it accounts for the 10 nighttime versus 14 daytime hours in each date. "
            "It leaves relative danger unanswered because it is not adjusted for traffic volume, and crash severity is not distinguished. "
            f"It uses {YEARS}; it excludes {exclusion_years} and no rows for NULL crash time (none in the file); no outcome field is needed."
        ),
    },
]

with (OUT / "options.json").open("w", encoding="utf-8") as f:
    json.dump({"options": options}, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(json.dumps({
    "summary": summary.reset_index().to_dict(orient="records"),
    "values": {"harm_percent": harm_values, "fatal_per_1000": fatal_values,
               "crashes_per_hour": volume_values},
    "coverage": {"all_rows": all_rows, "rows_2012": n2012, "rows_2026": n2026,
                 "missing_harm": missing_harm, "missing_death": missing_death,
                 "missing_time": missing_time},
}, default=float, ensure_ascii=False, indent=2))
