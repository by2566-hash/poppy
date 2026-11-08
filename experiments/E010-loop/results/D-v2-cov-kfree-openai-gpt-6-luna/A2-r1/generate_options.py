import json
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
SOURCE = ROOT / "data" / "crashes.parquet"
OUT.mkdir(exist_ok=True)

con = duckdb.connect()
source_sql = str(SOURCE).replace("'", "''")
con.execute(f"CREATE VIEW crashes AS SELECT * FROM read_parquet('{source_sql}')")

coverage = con.execute(
    """
    SELECT count(*) AS all_rows,
           count(*) FILTER (WHERE crash_date IS NULL OR crash_time IS NULL) AS null_date_time,
           count(*) FILTER (WHERE year(crash_date) = 2012) AS rows_2012,
           count(*) FILTER (WHERE year(crash_date) = 2026) AS rows_2026
    FROM crashes
    """
).fetchdf().iloc[0]
all_rows = int(coverage.all_rows)
partial_year_rows = {2012: int(coverage.rows_2012), 2026: int(coverage.rows_2026)}
partial_year_shares = {year: rows / all_rows for year, rows in partial_year_rows.items()}

# Use only complete calendar years in the file (2013–2025). Night and day are
# equal-length 12-hour windows, so reported crashes per clock-hour compare
# frequency without favoring a longer period.
periods = con.execute(
    """
    WITH eligible AS (
      SELECT *, CASE WHEN hour(crash_time) >= 7 AND hour(crash_time) < 19
                     THEN 'Day (7 a.m.–6:59 p.m.)'
                     ELSE 'Night (7 p.m.–6:59 a.m.)' END AS period
      FROM crashes
      WHERE year(crash_date) BETWEEN 2013 AND 2025
    )
    SELECT period,
           count(*) AS crash_rows,
           count(*) FILTER (WHERE number_of_persons_injured IS NOT NULL
                             AND number_of_persons_killed IS NOT NULL) AS valid_severity_rows,
           count(*) FILTER (WHERE number_of_persons_injured IS NULL
                             OR number_of_persons_killed IS NULL) AS null_severity_rows,
           count(*) FILTER (WHERE number_of_persons_injured > 0
                             OR number_of_persons_killed > 0) AS injury_or_fatal_crashes,
           sum(number_of_persons_injured) AS persons_injured,
           sum(number_of_persons_killed) AS persons_killed,
           count(DISTINCT crash_date) AS observed_dates
    FROM eligible
    GROUP BY period
    """
).fetchdf()
order = ["Day (7 a.m.–6:59 p.m.)", "Night (7 p.m.–6:59 a.m.)"]
periods = periods.set_index("period").loc[order].reset_index()
periods["crash_rows"] = periods.crash_rows.astype(int)
periods["valid_severity_rows"] = periods.valid_severity_rows.astype(int)
periods["null_severity_rows"] = periods.null_severity_rows.astype(int)
periods["injury_or_fatal_crashes"] = periods.injury_or_fatal_crashes.astype(int)
periods["observed_dates"] = periods.observed_dates.astype(int)
periods["clock_hours"] = periods.observed_dates * 12
periods["crashes_per_clock_hour"] = periods.crash_rows / periods.clock_hours
periods["injury_or_fatal_share_pct"] = (
    periods.injury_or_fatal_crashes / periods.valid_severity_rows * 100
)

partial_text = "; ".join(
    f"{year}: {rows:,} rows ({share:.2%} of all file rows)"
    for year, rows, share in (
        (year, partial_year_rows[year], partial_year_shares[year])
        for year in (2012, 2026)
    )
)

# Option 1: crash frequency standardized by the number of observed clock-hours.
frequency_values = periods[
    ["period", "crash_rows", "observed_dates", "clock_hours", "crashes_per_clock_hour"]
].copy()
frequency_values.to_csv(OUT / "values_1.csv", index=False, float_format="%.6f")
fig, ax = plt.subplots(figsize=(8.5, 5.2))
bars = ax.bar(
    ["Day\n7 a.m.–6:59 p.m.", "Night\n7 p.m.–6:59 a.m."],
    periods.crashes_per_clock_hour,
    color=["#4472C4", "#263B5A"],
    width=0.58,
)
ax.bar_label(bars, fmt="%.1f", padding=4, fontsize=11)
ax.set_ylabel("Police-reported crashes per observed clock-hour")
ax.set_title("Reported NYC crashes per hour of day or night, 2013–2025")
ax.set_ylim(0, periods.crashes_per_clock_hour.max() * 1.18)
ax.text(
    0.5,
    -0.20,
    "Equal 12-hour windows; complete calendar years only. Crash counts are not adjusted for traffic volume.",
    transform=ax.transAxes,
    ha="center",
    fontsize=9,
)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Option 2: likelihood that a reported crash involved injury or death.
severity_values = periods[
    [
        "period",
        "crash_rows",
        "valid_severity_rows",
        "null_severity_rows",
        "injury_or_fatal_crashes",
        "injury_or_fatal_share_pct",
    ]
].copy()
severity_values["excluded_partial_year_rows_2012"] = partial_year_rows[2012]
severity_values["excluded_partial_year_share_2012"] = partial_year_shares[2012]
severity_values["excluded_partial_year_rows_2026"] = partial_year_rows[2026]
severity_values["excluded_partial_year_share_2026"] = partial_year_shares[2026]
severity_values.to_csv(OUT / "values_2.csv", index=False, float_format="%.6f")
fig, ax = plt.subplots(figsize=(8.5, 5.2))
bars = ax.bar(
    ["Day\n7 a.m.–6:59 p.m.", "Night\n7 p.m.–6:59 a.m."],
    periods.injury_or_fatal_share_pct,
    color=["#4472C4", "#263B5A"],
    width=0.58,
)
ax.bar_label(bars, fmt="%.2f%%", padding=4, fontsize=11)
ax.set_ylabel("Crashes involving ≥1 injured or killed person (%)")
ax.set_title("Share of reported crashes involving injury or death, 2013–2025")
ax.set_ylim(0, periods.injury_or_fatal_share_pct.max() * 1.20)
ax.text(
    0.5,
    -0.20,
    "Denominator: crashes with nonmissing injury and death counts; complete calendar years only.",
    transform=ax.transAxes,
    ha="center",
    fontsize=9,
)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)

day, night = periods.iloc[0], periods.iloc[1]
frequency_answer = (
    f"NYC recorded {day.crashes_per_clock_hour:.1f} police-reported crashes per clock-hour by day versus "
    f"{night.crashes_per_clock_hour:.1f} at night in 2013–2025, so reported crash frequency was higher by day."
)
severity_answer = (
    f"Among crashes with known injury and death counts, {night.injury_or_fatal_share_pct:.2f}% at night involved an injured or killed person, "
    f"versus {day.injury_or_fatal_share_pct:.2f}% by day, a higher share at night."
)
full_year_rows = int(periods.crash_rows.sum())
severity_null_rows = int(periods.null_severity_rows.sum())
severity_null_share = severity_null_rows / full_year_rows
complete_year_filter_note = (
    f"Rows excluded are all rows from the partial coverage years 2012 ({partial_year_rows[2012]:,} rows, "
    f"{partial_year_shares[2012]:.2%} of the file) and 2026 ({partial_year_rows[2026]:,} rows, "
    f"{partial_year_shares[2026]:.2%} of the file); no rows are excluded for missing crash date/time."
)
options = {
    "options": [
        {
            "id": 1,
            "metric": "Police-reported crash frequency",
            "denominator": "Observed clock-hours in each equal-length 12-hour period",
            "grouping": "Day (7 a.m.–6:59 p.m.) vs night (7 p.m.–6:59 a.m.)",
            "chart_type": "Two-bar comparison",
            "reason": "A per-hour comparison makes crash frequency comparable between the equal-length day and night windows and directly shows when crashes are recorded more often.",
            "probability": 0.55,
            "answer": frequency_answer,
            "interpretation": (
                "This addresses whether police-reported crashes occur more frequently at night by comparing the mean count per clock-hour, with equal 12-hour day and night windows. "
                "The chart shows the per-hour crash frequency in each window, a defensible count-based proxy for danger when no traffic-exposure measure is available. "
                "It does not answer whether an individual trip or road user faces greater risk, because the file has no traffic volume, travel distance, or road-user exposure; it also does not compare injury severity. "
                + complete_year_filter_note
            ),
        },
        {
            "id": 2,
            "metric": "Share of crashes involving injury or death",
            "denominator": "Crashes with nonmissing persons-injured and persons-killed counts, within each period",
            "grouping": "Day (7 a.m.–6:59 p.m.) vs night (7 p.m.–6:59 a.m.)",
            "chart_type": "Two-bar percentage comparison",
            "reason": "Comparing the fraction of crashes that harm someone distinguishes crash severity from the number of crashes occurring in each period.",
            "probability": 0.45,
            "answer": severity_answer,
            "interpretation": (
                "This addresses whether a reported crash is more likely to involve harm at night by comparing injury-or-fatality crashes as a share of crashes with complete severity counts. "
                "The chart shows the observed harm-involvement share for each period, a defensible severity measure independent of the total number of crashes. "
                "It does not establish per-trip danger or compare the number of people harmed per crash, and it is not adjusted for traffic exposure. "
                + f"Rows excluded are all rows from the partial coverage years 2012 ({partial_year_rows[2012]:,} rows, {partial_year_shares[2012]:.2%} of the file) and 2026 ({partial_year_rows[2026]:,} rows, {partial_year_shares[2026]:.2%} of the file), plus {severity_null_rows:,} complete-year crash rows ({severity_null_share:.4%} of complete-year rows) with a NULL injury or death count; no rows are excluded for missing crash date/time."
            ),
        },
    ]
}
(OUT / "options.json").write_text(json.dumps(options, indent=2) + "\n", encoding="utf-8")

print("Coverage:", all_rows, "rows total;", partial_text)
print("Included complete-year rows:", full_year_rows)
print("Severity NULL rows excluded:", severity_null_rows, f"({severity_null_share:.4%})")
print(periods[["period", "crash_rows", "clock_hours", "crashes_per_clock_hour", "valid_severity_rows", "injury_or_fatal_crashes", "injury_or_fatal_share_pct"]].to_string(index=False))
print("Saved charts, values, and options.json in", OUT)
