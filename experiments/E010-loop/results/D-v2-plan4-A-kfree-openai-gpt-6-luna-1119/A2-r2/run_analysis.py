import csv
import datetime as dt
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
DATA = str(ROOT / "data" / "crashes.parquet")
FIRST = dt.date(2013, 1, 1)
AFTER_LAST = dt.date(2026, 1, 1)
YEARS = range(2013, 2026)
CALENDAR_DAYS = sum((dt.date(y + 1, 1, 1) - dt.date(y, 1, 1)).days for y in YEARS)
BASE_FILTER = "crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' AND crash_time <> TIME '00:00:00'"
PERIOD_CASE = "CASE WHEN crash_time >= TIME '06:00:00' AND crash_time < TIME '20:00:00' THEN 'Day' ELSE 'Night' END"
PERIOD_HOURS = {"Day": 14, "Night": 10}
COLORS = {"Day": "#2673a6", "Night": "#d97732"}
con = duckdb.connect()
con.execute(f"CREATE VIEW crashes AS SELECT * FROM read_parquet('{DATA}')")


def values_for(option_id, outcome_col=None):
    filter_sql = BASE_FILTER
    if outcome_col:
        filter_sql += f" AND {outcome_col} IS NOT NULL"
        metric_expr = f"count(*) FILTER (WHERE {outcome_col} > 0)"
        sql = f"""SELECT {PERIOD_CASE} AS period, count(*) AS denominator,
                         {metric_expr} AS numerator
                  FROM crashes WHERE {filter_sql}
                  GROUP BY period ORDER BY CASE period WHEN 'Day' THEN 1 ELSE 2 END"""
    else:
        sql = f"""SELECT {PERIOD_CASE} AS period, count(*) AS numerator
                  FROM crashes WHERE {filter_sql}
                  GROUP BY period ORDER BY CASE period WHEN 'Day' THEN 1 ELSE 2 END"""
    rows = con.execute(sql).fetchall()
    by_period = {r[0]: r[1:] for r in rows}
    plotted = []
    for period in ("Day", "Night"):
        if outcome_col:
            denominator, numerator = by_period[period]
            value = numerator / denominator
            unit = "share of crashes"
        else:
            (numerator,) = by_period[period]
            denominator = CALENDAR_DAYS * PERIOD_HOURS[period]
            value = numerator / denominator
            unit = "crashes per clock-hour slot per calendar day"
        plotted.append({
            "group": period,
            "numerator_crashes": numerator,
            "denominator": denominator,
            "value": value,
            "unit": unit,
        })

    with (OUT / f"values_{option_id}.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=plotted[0].keys())
        writer.writeheader()
        writer.writerows(plotted)
    return plotted


def make_chart(option_id, values, title, subtitle, ylabel, percent=False, quality_note=""):
    fig, ax = plt.subplots(figsize=(8.3, 5.2))
    groups = [v["group"] for v in values]
    heights = [v["value"] * (100 if percent else 1) for v in values]
    bars = ax.bar(groups, heights, color=[COLORS[g] for g in groups], width=0.55)
    ax.set_title(title, fontsize=15, fontweight="bold", loc="left", pad=18)
    ax.text(0, 1.015, subtitle, transform=ax.transAxes, ha="left", va="bottom", fontsize=9.5, color="#454545")
    ax.set_ylabel(ylabel)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#dddddd", linewidth=0.7)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", length=0, labelsize=11)
    for bar, height in zip(bars, heights):
        label = f"{height:.2f}%" if percent else f"{height:.2f}"
        ax.annotate(label, (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 5), textcoords="offset points", ha="center", fontsize=10)
    ax.set_ylim(0, max(heights) * 1.22)
    fig.text(0.01, 0.012,
             "2013–2025; day 06:00–19:59, night 20:00–05:59. Excludes 23,787 crashes at 00:00 (potential default time); partial years excluded. "
             f"{quality_note} "
             "Crash records lack traffic-exposure data, so this is not risk per trip or mile.",
             ha="left", va="bottom", fontsize=8, color="#555555", wrap=True)
    fig.tight_layout(rect=[0, 0.09, 1, 0.96])
    fig.savefig(OUT / f"option_{option_id}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


first = values_for(1)
make_chart(
    1, first,
    "Average NYC police-reported crashes per clock-hour slot per day",
    "One row per reported crash; complete years 2013–2025",
    "Crashes per clock-hour slot per calendar day",
)

injury = values_for(2, "number_of_persons_injured")
make_chart(
    2, injury,
    "NYC crashes involving injury as a share of crashes with known injury counts",
    "One row per reported crash; complete years 2013–2025",
    "Crashes with ≥1 person injured (%)",
    percent=True,
    quality_note="Also excludes 18 crashes missing injury counts.",
)

fatal = values_for(3, "number_of_persons_killed")
make_chart(
    3, fatal,
    "NYC fatal crashes as a share of crashes with known death counts",
    "One row per reported crash; complete years 2013–2025",
    "Crashes with ≥1 person killed (%)",
    percent=True,
    quality_note="Also excludes 35 crashes missing death counts.",
)
