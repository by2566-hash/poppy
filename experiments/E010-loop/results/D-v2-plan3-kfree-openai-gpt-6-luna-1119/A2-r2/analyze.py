from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


DATA = "data/crashes.parquet"
OUT = Path("out")
con = duckdb.connect()

# Complete calendar years only; the period labels and definitions follow the
# final plans. Unknown times are retained as a separate (empty in these data)
# group. Midnight stays in the night group as recorded.
base = f"""
    WITH population AS (
      SELECT year(crash_date) AS year,
        CASE
          WHEN crash_time IS NULL OR try_cast(crash_time AS TIME) IS NULL THEN 'Unknown'
          WHEN hour(crash_time) >= 20 OR hour(crash_time) < 6 THEN 'Night'
          ELSE 'Day'
        END AS period,
        number_of_persons_injured,
        number_of_persons_killed
      FROM read_parquet('{DATA}')
      WHERE crash_date >= DATE '2013-01-01'
        AND crash_date < DATE '2026-01-01'
    )
"""
calendar = pd.DataFrame(
    [(year, (366 if year in (2016, 2020, 2024) else 365)) for year in range(2013, 2026)],
    columns=["year", "days_in_year"],
)
periods = pd.DataFrame({"period": ["Night", "Day", "Unknown"]})
grid = calendar.assign(_key=1).merge(periods.assign(_key=1), on="_key").drop(columns="_key")


def save_chart(df, option, title, subtitle, ylabel, filename, metric_col):
    fig, ax = plt.subplots(figsize=(11, 6.2))
    for period in ["Night", "Day"]:
        subset = df[df["period"] == period]
        ax.plot(subset["year"], subset[metric_col], marker="o", linewidth=2.2, label=period)
    ax.set_title(title, loc="left", fontsize=15, weight="bold", pad=28)
    ax.text(0, 1.015, subtitle, transform=ax.transAxes, fontsize=9, color="#555555", va="bottom")
    ax.set_xlabel("Calendar year")
    ax.set_ylabel(ylabel)
    ax.set_xticks(sorted(df["year"].unique()))
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False, ncol=2, loc="best")
    fig.tight_layout()
    fig.savefig(OUT / filename, dpi=180, bbox_inches="tight")
    plt.close(fig)


# Option 1: crash records per 1,000 elapsed clock-hours in each period/year.
counts = con.execute(
    base + """
    SELECT year, period, count(*) AS crash_records
    FROM population GROUP BY year, period
    """
).df()
values1 = grid.merge(counts, how="left", on=["year", "period"]).fillna({"crash_records": 0})
values1["hours_in_period"] = values1["days_in_year"] * values1["period"].map(
    {"Night": 10, "Day": 14, "Unknown": 24}
)
values1["crashes_per_1000_clock_hours"] = (
    values1["crash_records"] / values1["hours_in_period"] * 1000
)
values1["population_crash_records"] = values1["crash_records"]
values1.drop(columns="days_in_year").to_csv(OUT / "values_1.csv", index=False)
save_chart(
    values1, 1,
    "NYC police-reported crashes per 1,000 clock-hours",
    "All dated crashes, 2013-2025; clock-hours are not road-user exposure.",
    "Crash records per 1,000 elapsed clock-hours", "option_1.png",
    "crashes_per_1000_clock_hours",
)

# Option 2: share of crashes with any reported injury or death, among rows
# with both outcome counts present.
injury_event = con.execute(
    base + """
    SELECT year, period,
      count(*) FILTER (WHERE number_of_persons_injured IS NOT NULL
                        AND number_of_persons_killed IS NOT NULL) AS eligible_crashes,
      count(*) FILTER (WHERE number_of_persons_injured IS NOT NULL
                        AND number_of_persons_killed IS NOT NULL
                        AND (number_of_persons_injured > 0 OR number_of_persons_killed > 0)) AS injury_or_death_crashes
    FROM population GROUP BY year, period
    """
).df()
values2 = grid.merge(injury_event, how="left", on=["year", "period"])
values2[["eligible_crashes", "injury_or_death_crashes"]] = values2[
    ["eligible_crashes", "injury_or_death_crashes"]
].fillna(0)
values2["percent_injury_or_death_crashes"] = values2.apply(
    lambda r: (100 * r.injury_or_death_crashes / r.eligible_crashes) if r.eligible_crashes else float("nan"), axis=1
)
values2.to_csv(OUT / "values_2.csv", index=False)
save_chart(
    values2, 2,
    "Share of NYC crashes involving injury or death",
    "Crashes with both outcome counts reported, 2013-2025; not risk per trip or mile.",
    "Crashes with ≥1 injured or killed person (%)", "option_2.png",
    "percent_injury_or_death_crashes",
)

# Option 3: average number of reported injured persons per crash, excluding
# rows without a reported injury count.
injury_mean = con.execute(
    base + """
    SELECT year, period,
      count(*) FILTER (WHERE number_of_persons_injured IS NOT NULL) AS eligible_crashes,
      sum(number_of_persons_injured) FILTER (WHERE number_of_persons_injured IS NOT NULL) AS reported_injured_persons
    FROM population GROUP BY year, period
    """
).df()
values3 = grid.merge(injury_mean, how="left", on=["year", "period"])
values3[["eligible_crashes", "reported_injured_persons"]] = values3[
    ["eligible_crashes", "reported_injured_persons"]
].fillna(0)
values3["injured_persons_per_crash"] = values3.apply(
    lambda r: (r.reported_injured_persons / r.eligible_crashes) if r.eligible_crashes else float("nan"), axis=1
)
values3.to_csv(OUT / "values_3.csv", index=False)
save_chart(
    values3, 3,
    "Reported injured persons per NYC crash",
    "Crashes with an injury count reported, 2013-2025; not risk per trip or mile.",
    "Reported injured persons per crash", "option_3.png",
    "injured_persons_per_crash",
)
