from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
YEARS = "crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'"
PERIOD = "CASE WHEN crash_time < TIME '06:00:00' OR crash_time >= TIME '20:00:00' THEN 'Night' ELSE 'Day' END"
PERIODS = ["Night", "Day"]
COLORS = {"Night": "#263e72", "Day": "#d58b24"}


def aggregate(option_id, fields, extra_where, expression, numerator_label, denominator_label):
    con = duckdb.connect()
    selected = ", ".join(f'"{field}"' for field in fields)
    data_path = str(DATA).replace("'", "''")
    con.execute(f"CREATE VIEW scoped AS SELECT {selected} FROM read_parquet('{data_path}')")
    rows = con.execute(f"""
        SELECT {PERIOD} AS period,
               count(*) AS denominator,
               sum(CASE WHEN {expression} THEN 1 ELSE 0 END) AS numerator
        FROM scoped
        WHERE {YEARS} AND crash_time IS NOT NULL {extra_where}
        GROUP BY period
    """).fetchdf()
    con.close()
    rows = rows.set_index("period").reindex(PERIODS).fillna(0).reset_index()
    rows["numerator"] = rows["numerator"].astype("int64")
    rows["denominator"] = rows["denominator"].astype("int64")
    rows["metric"] = rows["numerator"] / rows["denominator"]
    rows = rows.rename(columns={"numerator": numerator_label, "denominator": denominator_label})
    return rows


def chart(option_id, rows, value_column, title, subtitle, ylabel, percent=False):
    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    colors = [COLORS[p] for p in rows["period"]]
    values = rows["metric"].tolist()
    bars = ax.bar(rows["period"], values, color=colors, width=0.58)
    ax.set_title(title, fontsize=15, weight="bold", pad=20)
    fig.text(0.5, 0.91, subtitle, ha="center", va="center", fontsize=9.5, color="#444444")
    ax.set_ylabel(ylabel, labelpad=10)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#dddddd", linewidth=0.7)
    ax.set_axisbelow(True)
    if percent:
        ax.yaxis.set_major_formatter(PercentFormatter(1.0))
        ax.set_ylim(0, max(values) * 1.24)
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, value + max(values) * 0.025,
                    f"{value:.2%}", ha="center", va="bottom", fontsize=11)
    else:
        ax.set_ylim(0, max(values) * 1.2)
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, value + max(values) * 0.025,
                    f"{value:,.2f}", ha="center", va="bottom", fontsize=11)
    fig.text(0.5, 0.025, "Source: NYC police-reported motor vehicle crashes, 2013-2025. "
             "Night = 20:00-05:59; day = 06:00-19:59.",
             ha="center", fontsize=8, color="#555555")
    fig.tight_layout(rect=[0.04, 0.07, 0.98, 0.88])
    fig.savefig(OUT / f"option_{option_id}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


calendar_days = sum((pd.Timestamp(year=year, month=12, day=31) -
                     pd.Timestamp(year=year, month=1, day=1)).days + 1
                    for year in range(2013, 2026))

# Option 1: normalize raw crash occurrence by time available in each period.
crash_counts = aggregate(
    1,
    ["crash_date", "crash_time"],
    "",
    "TRUE",
    "crashes",
    "rows_used",
)
crash_counts = crash_counts.drop(columns=["rows_used", "metric"])
crash_counts["period_hours"] = crash_counts["period"].map(
    {"Night": calendar_days * 10, "Day": calendar_days * 14}
)
crash_counts["crashes_per_clock_hour"] = crash_counts["crashes"] / crash_counts["period_hours"]
crash_counts["metric"] = crash_counts["crashes_per_clock_hour"]
crash_counts[["period", "crashes", "period_hours", "crashes_per_clock_hour"]].to_csv(
    OUT / "values_1.csv", index=False
)
chart(1, crash_counts, "crashes_per_clock_hour",
      "NYC police-reported crashes per clock-hour, 2013-2025",
      "Night = 8 p.m.-5:59 a.m.; hourly rates are not adjusted for traffic exposure.",
      "Reported crashes per clock-hour")

# Option 2: any injury or death among complete-case reported crashes.
injury = aggregate(
    2,
    ["crash_date", "crash_time", "number_of_persons_injured", "number_of_persons_killed"],
    "AND number_of_persons_injured IS NOT NULL AND number_of_persons_killed IS NOT NULL",
    "number_of_persons_injured > 0 OR number_of_persons_killed > 0",
    "crashes_with_injury_or_death",
    "complete_case_crashes",
)
injury["share_with_injury_or_death"] = injury["metric"]
injury[["period", "complete_case_crashes", "crashes_with_injury_or_death",
        "share_with_injury_or_death"]].to_csv(OUT / "values_2.csv", index=False)
chart(2, injury, "share_with_injury_or_death",
      "Share of reported NYC crashes with injury or death, 2013-2025",
      "Among crashes with both casualty counts recorded; not a per-trip or per-person risk.",
      "Share of crashes", percent=True)

# Option 3: a stricter severity outcome, at least one death.
fatal = aggregate(
    3,
    ["crash_date", "crash_time", "number_of_persons_killed"],
    "AND number_of_persons_killed IS NOT NULL",
    "number_of_persons_killed > 0",
    "crashes_with_at_least_one_death",
    "crashes_with_death_count_recorded",
)
fatal["share_with_at_least_one_death"] = fatal["metric"]
fatal[["period", "crashes_with_death_count_recorded", "crashes_with_at_least_one_death",
       "share_with_at_least_one_death"]].to_csv(OUT / "values_3.csv", index=False)
chart(3, fatal, "share_with_at_least_one_death",
      "Share of reported NYC crashes with a death, 2013-2025",
      "Among crashes with death counts recorded; not a per-trip or per-person fatality risk.",
      "Share of crashes", percent=True)
