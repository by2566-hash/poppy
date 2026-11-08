import json
from pathlib import Path

import duckdb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


OUT = Path("out")
DATA = "data/crashes.parquet"
con = duckdb.connect()

by_year = con.execute(
    """
    SELECT year(crash_date) AS year, count(*) AS crashes
    FROM read_parquet(?)
    GROUP BY year
    ORDER BY year
    """,
    [DATA],
).fetchdf()
total_rows = int(by_year["crashes"].sum())
included_rows = int(by_year.loc[by_year.year.between(2013, 2025), "crashes"].sum())
boundary_rows = total_rows - included_rows
boundary_share = 100 * boundary_rows / total_rows

summary = con.execute(
    """
    WITH x AS (
      SELECT *,
        CASE WHEN hour(crash_time) >= 18 OR hour(crash_time) < 6
             THEN $$Night$$ ELSE $$Day$$ END AS period
      FROM read_parquet(?)
      WHERE year(crash_date) BETWEEN 2013 AND 2025
    )
    SELECT period,
      count(*) AS crashes,
      count(*) FILTER (
        WHERE number_of_persons_injured IS NOT NULL
          AND number_of_persons_killed IS NOT NULL
      ) AS serious_eligible,
      count(*) FILTER (
        WHERE number_of_persons_injured > 0 OR number_of_persons_killed > 0
      ) AS serious_crashes,
      count(*) FILTER (WHERE number_of_persons_killed IS NOT NULL) AS fatal_eligible,
      count(*) FILTER (WHERE number_of_persons_killed > 0) AS fatal_crashes
    FROM x
    GROUP BY period
    """,
    [DATA],
).fetchdf().set_index("period").loc[["Day", "Night"]]

colors = {"Day": "#e69f00", "Night": "#3b75af"}
periods = ["Day", "Night"]
night_day = summary.loc["Night"]
day_day = summary.loc["Day"]
serious_day_rate = 100 * day_day.serious_crashes / day_day.serious_eligible
serious_night_rate = 100 * night_day.serious_crashes / night_day.serious_eligible
fatal_day_rate = 100 * day_day.fatal_crashes / day_day.fatal_eligible
fatal_night_rate = 100 * night_day.fatal_crashes / night_day.fatal_eligible
serious_missing_day = int(day_day.crashes - day_day.serious_eligible)
serious_missing_night = int(night_day.crashes - night_day.serious_eligible)
fatal_missing_day = int(day_day.crashes - day_day.fatal_eligible)
fatal_missing_night = int(night_day.crashes - night_day.fatal_eligible)


def plot_bars(values, ylabel, title, subtitle, filename, percent=False, precision=2,
              millions=False):
    fig, ax = plt.subplots(figsize=(8, 5.2))
    bars = ax.bar(periods, values, color=[colors[p] for p in periods], width=0.58)
    fig.suptitle(title, x=0.08, y=0.97, ha="left", fontsize=15, weight="bold")
    fig.text(0.08, 0.905, subtitle, fontsize=9.5, color="#454545", va="bottom")
    ax.set_ylabel(ylabel)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#dddddd", linewidth=0.7)
    ax.set_axisbelow(True)
    for bar, value in zip(bars, values):
        label = f"{value:,.{precision}f}%" if percent else f"{value:,.0f}"
        ax.annotate(label, (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 5), textcoords="offset points", ha="center",
                    fontsize=10, weight="bold")
    ax.set_ylim(0, max(values) * 1.22)
    if millions:
        from matplotlib.ticker import FuncFormatter

        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x / 1_000_000:.1f}"))
    fig.text(0.01, 0.015,
             "NYC police-reported crashes, 2013–2025; night = 18:00–05:59; day = 06:00–17:59. "
             "Crash records do not measure traffic exposure.",
             fontsize=8, color="#555555")
    fig.subplots_adjust(left=0.12, right=0.98, bottom=0.16, top=0.82)
    fig.savefig(OUT / filename, dpi=180, bbox_inches="tight")
    plt.close(fig)


# Option 1: observed crash counts in two equal-length daily clock windows.
counts = [int(summary.loc[p, "crashes"]) for p in periods]
pd.DataFrame({"period": periods, "crashes": counts}).to_csv(OUT / "values_1.csv", index=False)
plot_bars(counts, "Police-reported crashes (millions)", "More crashes are recorded during the day",
          "Observed crash counts in equal 12-hour clock windows", "option_1.png",
          millions=True)

# Option 2: crash-level proportion with at least one injured or killed person.
serious_n = [int(summary.loc[p, "serious_crashes"]) for p in periods]
serious_d = [int(summary.loc[p, "serious_eligible"]) for p in periods]
serious_rates = [100 * n / d for n, d in zip(serious_n, serious_d)]
pd.DataFrame({"period": periods, "crashes_with_injury_or_death": serious_n,
              "crashes_with_complete_injury_and_death_fields": serious_d,
              "share_percent": serious_rates}).to_csv(OUT / "values_2.csv", index=False)
plot_bars(serious_rates, "Crashes with injury or death (%)",
          "Nighttime crashes more often involve reported harm",
          "Share of crashes with at least one person injured or killed",
          "option_2.png", percent=True)

# Option 3: crash-level proportion with at least one death.
fatal_n = [int(summary.loc[p, "fatal_crashes"]) for p in periods]
fatal_d = [int(summary.loc[p, "fatal_eligible"]) for p in periods]
fatal_rates = [100 * n / d for n, d in zip(fatal_n, fatal_d)]
pd.DataFrame({"period": periods, "fatal_crashes": fatal_n,
              "crashes_with_known_persons_killed": fatal_d,
              "fatal_crash_share_percent": fatal_rates}).to_csv(OUT / "values_3.csv", index=False)
plot_bars(fatal_rates, "Fatal crashes (%)", "Fatal crashes are a larger share at night",
          "Share of crashes with at least one person killed",
          "option_3.png", percent=True, precision=3)

serious_ratio = serious_night_rate / serious_day_rate
fatal_ratio = fatal_night_rate / fatal_day_rate
options = [
    {
        "id": 1,
        "metric": "Police-reported crash count",
        "denominator": "None; raw counts of crash records",
        "grouping": "Night 18:00–05:59 vs day 06:00–17:59; complete calendar years 2013–2025",
        "chart_type": "Two-bar count chart",
        "reason": "A newsroom may need the absolute number of reported collisions in equal-length clock windows to describe when crash burden occurs.",
        "probability": 0.22,
        "answer": f"Among complete years 2013–2025, police reports logged {counts[1]:,} crashes at night versus {counts[0]:,} by day, so recorded crashes were more numerous by day; these counts do not establish per-trip danger.",
        "interpretation": f"This framing answers whether more reported crashes occur during nighttime than daytime hours: it counts crashes in equal 12-hour clock windows and shows {counts[1]:,} at night versus {counts[0]:,} by day. A count comparison is a defensible measure of observed crash burden across those equal-length windows, but it does not establish higher per-traveler risk. It leaves unanswered whether a crash is more likely to injure or kill someone, and whether exposure to traffic differs by time. It excludes all 2012 and 2026 records ({boundary_rows:,} rows, {boundary_share:.2f}% of the file) to compare complete calendar years 2013–2025; no rows are excluded for missing crash time.",
    },
    {
        "id": 2,
        "metric": "Share of crashes involving at least one injured or killed person",
        "denominator": "Crashes with non-NULL values for both number_of_persons_injured and number_of_persons_killed",
        "grouping": "Night 18:00–05:59 vs day 06:00–17:59; complete calendar years 2013–2025",
        "chart_type": "Two-bar percentage chart",
        "reason": "A newsroom may prefer the share of crashes with reported harm, which compares collision severity without treating every crash as equally consequential.",
        "probability": 0.53,
        "answer": f"{serious_night_rate:.2f}% of nighttime crashes involved an injury or death versus {serious_day_rate:.2f}% of daytime crashes ({serious_ratio:.2f} times the daytime share), although this is severity conditional on a reported crash rather than per-trip risk.",
        "interpretation": f"This framing answers whether a reported crash was more likely to involve injury or death at night: the share is {serious_night_rate:.2f}% at night and {serious_day_rate:.2f}% by day. This binary crash-level outcome is a defensible, easily interpreted measure of reported harm conditional on a crash. It leaves unanswered the risk per trip or mile, because the file contains no traffic-exposure denominator. It excludes all 2012 and 2026 records ({boundary_rows:,} rows, {boundary_share:.2f}% of the file) for complete-year comparison, plus {serious_missing_day:,} daytime rows ({100*serious_missing_day/day_day.crashes:.4f}%) and {serious_missing_night:,} nighttime rows ({100*serious_missing_night/night_day.crashes:.4f}%) in 2013–2025 because at least one required injury/death field is NULL.",
    },
    {
        "id": 3,
        "metric": "Share of crashes with at least one person killed",
        "denominator": "Crashes with non-NULL number_of_persons_killed",
        "grouping": "Night 18:00–05:59 vs day 06:00–17:59; complete calendar years 2013–2025",
        "chart_type": "Two-bar percentage chart",
        "reason": "A separate fatal-crash share isolates the most consequential outcome and shows whether nighttime collisions are disproportionately fatal.",
        "probability": 0.25,
        "answer": f"Fatal crashes made up {fatal_night_rate:.3f}% of nighttime crashes ({fatal_n[1]:,}/{fatal_d[1]:,}) versus {fatal_day_rate:.3f}% by day ({fatal_n[0]:,}/{fatal_d[0]:,}), about {fatal_ratio:.2f} times the daytime share; this is not per-trip risk.",
        "interpretation": f"This framing answers whether a reported crash was more likely to be fatal at night: fatal crashes were {fatal_night_rate:.3f}% of nighttime crashes and {fatal_day_rate:.3f}% of daytime crashes. Fatality share is a defensible severity indicator focused on the most consequential crash outcome. It leaves unanswered the chance of being killed per trip or mile, since the file has no traffic-exposure denominator. It excludes all 2012 and 2026 records ({boundary_rows:,} rows, {boundary_share:.2f}% of the file) for complete-year comparison, plus {fatal_missing_day:,} daytime rows ({100*fatal_missing_day/day_day.crashes:.4f}%) and {fatal_missing_night:,} nighttime rows ({100*fatal_missing_night/night_day.crashes:.4f}%) in 2013–2025 because number_of_persons_killed is NULL.",
    },
]

(OUT / "options.json").write_text(json.dumps({"options": options}, indent=2) + "\n")
print(json.dumps({
    "all_rows": total_rows,
    "included_complete_year_rows": included_rows,
    "boundary_rows_excluded": boundary_rows,
    "boundary_share_percent": boundary_share,
    "summary": summary.reset_index().to_dict(orient="records"),
    "serious_rates_percent": serious_rates,
    "fatal_rates_percent": fatal_rates,
    "serious_night_day_ratio": serious_ratio,
    "fatal_night_day_ratio": fatal_ratio,
}, indent=2, default=int))
