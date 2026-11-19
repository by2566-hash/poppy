import csv
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
PARQUET = ROOT / "data" / "crashes.parquet"
con = duckdb.connect()
con.execute(
    "CREATE VIEW crashes AS SELECT crash_date, crash_time, "
    "number_of_persons_injured, number_of_persons_killed "
    f"FROM read_parquet('{PARQUET}')"
)

GROUP_SQL = """
CASE
  WHEN crash_time IS NULL THEN 'Missing/unclassifiable time'
  WHEN HOUR(crash_time) >= 20 OR HOUR(crash_time) < 6 THEN 'Night (20:00–05:59)'
  ELSE 'Daytime (06:00–19:59)'
END
"""
ORDER = ["Night (20:00–05:59)", "Daytime (06:00–19:59)", "Missing/unclassifiable time"]
COLORS = ["#315b8a", "#8fa9c2", "#b5b5b5"]


def save_csv(name, fields, rows):
    with (OUT / name).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def ordered_rows(rows):
    return sorted(rows, key=lambda row: ORDER.index(row["time_group"]))


def make_chart(filename, title, subtitle, categories, values, ylabel, formatter, note, integer_axis=False):
    colors = [COLORS[ORDER.index(category)] for category in categories]
    fig, ax = plt.subplots(figsize=(9.2, 5.5))
    bars = ax.bar(categories, values, color=colors, width=0.62)
    ax.set_title(title, fontsize=15, weight="bold", loc="left", pad=28)
    ax.text(0, 1.015, subtitle, transform=ax.transAxes, fontsize=9.5, color="#444444", va="bottom")
    ax.set_ylabel(ylabel)
    if integer_axis:
        ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:,.0f}"))
    ax.grid(axis="y", alpha=0.25, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="x", labelrotation=0, labelsize=9)
    upper = max(values) if values else 1
    ax.set_ylim(0, upper * 1.18 if upper else 1)
    for bar, value in zip(bars, values):
        ax.annotate(formatter(value), (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 5), textcoords="offset points", ha="center", va="bottom", fontsize=10)
    fig.text(0.01, 0.015, note, ha="left", va="bottom", fontsize=8.2, color="#444444", wrap=True)
    fig.tight_layout(rect=[0, 0.09, 1, 0.92])
    fig.savefig(OUT / filename, dpi=180, bbox_inches="tight")
    plt.close(fig)


# Framing 1: absolute police-reported crash-record counts.
raw = con.execute(
    f"SELECT {GROUP_SQL} AS time_group, COUNT(*) AS crash_records "
    "FROM crashes WHERE crash_date IS NOT NULL GROUP BY time_group"
).fetchall()
rows1 = ordered_rows([{"time_group": group, "crash_records": count} for group, count in raw])
save_csv("values_1.csv", ["time_group", "crash_records"], rows1)
make_chart(
    "option_1.png",
    "Police-reported NYC crash records by time of day",
    "All crash records dated July 2012–June 2026",
    [row["time_group"] for row in rows1],
    [row["crash_records"] for row in rows1],
    "Crash records",
    lambda value: f"{value:,.0f}",
    "Counts are not adjusted for travel exposure. 2012 and 2026 are partial years; exact 00:00 times are counted as night and may include defaults.",
    integer_axis=True,
)

# Framing 2: record-level share with a reported injury or death.
raw = con.execute(
    f"""
    SELECT {GROUP_SQL} AS time_group,
           COUNT(*) FILTER (WHERE number_of_persons_injured + number_of_persons_killed >= 1) AS injury_or_death_crashes,
           COUNT(*) AS eligible_crash_records
    FROM crashes
    WHERE crash_date IS NOT NULL
      AND number_of_persons_injured IS NOT NULL
      AND number_of_persons_killed IS NOT NULL
    GROUP BY time_group
    """
).fetchall()
rows2 = ordered_rows([
    {
        "time_group": group,
        "injury_or_death_crashes": numerator,
        "eligible_crash_records": denominator,
        "share_percent": 100 * numerator / denominator if denominator else None,
    }
    for group, numerator, denominator in raw
])
save_csv("values_2.csv", ["time_group", "injury_or_death_crashes", "eligible_crash_records", "share_percent"], rows2)
make_chart(
    "option_2.png",
    "Share of eligible NYC crash reports involving injury or death",
    "Share with ≥1 person injured or killed; July 2012–June 2026",
    [row["time_group"] for row in rows2],
    [row["share_percent"] for row in rows2],
    "Eligible crash reports with injury or death (%)",
    lambda value: f"{value:.1f}%",
    "Eligible records have both person counts reported. 8,919 records with a missing count are excluded; partial years and possible midnight defaults remain. Not exposure-adjusted.",
)

# Framing 3: mean number of reported injured plus killed persons per eligible crash.
raw = con.execute(
    f"""
    SELECT {GROUP_SQL} AS time_group,
           SUM(number_of_persons_injured + number_of_persons_killed) AS reported_people_injured_or_killed,
           COUNT(*) AS eligible_crash_records,
           AVG(number_of_persons_injured + number_of_persons_killed) AS mean_people_per_crash
    FROM crashes
    WHERE crash_date IS NOT NULL
      AND number_of_persons_injured IS NOT NULL
      AND number_of_persons_killed IS NOT NULL
    GROUP BY time_group
    """
).fetchall()
rows3 = ordered_rows([
    {
        "time_group": group,
        "reported_people_injured_or_killed": total,
        "eligible_crash_records": denominator,
        "mean_people_per_crash": mean,
    }
    for group, total, denominator, mean in raw
])
save_csv("values_3.csv", ["time_group", "reported_people_injured_or_killed", "eligible_crash_records", "mean_people_per_crash"], rows3)
make_chart(
    "option_3.png",
    "Reported injured or killed persons per eligible NYC crash",
    "Mean persons injured + killed per crash report; July 2012–June 2026",
    [row["time_group"] for row in rows3],
    [row["mean_people_per_crash"] for row in rows3],
    "Mean reported persons injured or killed per crash",
    lambda value: f"{value:.3f}",
    "Uses records with both person counts reported; 8,919 records are excluded. Partial years and possible midnight defaults remain; this is not exposure-adjusted.",
)
