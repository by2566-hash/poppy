import calendar
import csv
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt


DATA = "data/crashes.parquet"
OUT = Path("out")
YEARS = list(range(2013, 2026))
YEAR_SQL = "2013 AND 2025"
GROUP_CASE = """
    CASE
      WHEN crash_time = TIME '00:00:00' THEN '00:00 recorded'
      WHEN hour(crash_time) BETWEEN 6 AND 19 THEN 'Day (06:00-19:59)'
      ELSE 'Night (20:00-23:59, 01:00-05:59)'
    END
"""
ORDER = [
    "Day (06:00-19:59)",
    "Night (20:00-23:59, 01:00-05:59)",
    "00:00 recorded",
]
HOURS_PER_DAY = {ORDER[0]: 14, ORDER[1]: 9, ORDER[2]: 1}
CALENDAR_DAYS = sum(366 if calendar.isleap(y) else 365 for y in YEARS)
con = duckdb.connect()


def write_values(option_id, fields, rows):
    with (OUT / f"values_{option_id}.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def draw(option_id, values, y_label, title, subtitle, formatter):
    plt.figure(figsize=(9.2, 5.6))
    labels = [row["group"] for row in values]
    vals = [float(row["metric_value"]) for row in values]
    colors = ["#3478a8", "#d67834", "#8b8b8b"]
    bars = plt.bar(labels, vals, color=colors)
    plt.ylabel(y_label)
    plt.title(title, loc="left", fontsize=14, fontweight="bold", pad=30)
    plt.suptitle(subtitle, x=0.125, y=0.925, ha="left", fontsize=9, color="#555555")
    plt.grid(axis="y", alpha=0.22)
    plt.gca().set_axisbelow(True)
    for bar, value in zip(bars, vals):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), formatter(value),
                 ha="center", va="bottom", fontsize=10)
    plt.tight_layout(rect=(0, 0, 1, 0.89))
    plt.savefig(OUT / f"option_{option_id}.png", dpi=180, bbox_inches="tight")
    plt.close()


# Option 1: count reported crashes by plan-defined time group. The rate
# denominator counts calendar clock-hour opportunities, not traffic exposure.
crash_counts = con.execute(f"""
    SELECT {GROUP_CASE} AS time_group, count(*) AS crashes
    FROM read_parquet('{DATA}')
    WHERE year(crash_date) BETWEEN {YEAR_SQL}
      AND crash_date IS NOT NULL AND crash_time IS NOT NULL
    GROUP BY time_group
""").fetchall()
count_map = dict(crash_counts)
values_1 = []
for group in ORDER:
    hours = HOURS_PER_DAY[group]
    opportunities = CALENDAR_DAYS * hours
    count = count_map.get(group, 0)
    values_1.append({
        "group": group,
        "crashes": count,
        "clock_hour_opportunities": opportunities,
        "metric_value": f"{count / opportunities:.6f}",
    })
write_values(1, ["group", "crashes", "clock_hour_opportunities", "metric_value"], values_1)
draw(
    1, values_1, "Reported crashes per calendar clock-hour opportunity",
    "Reported crashes per clock-hour opportunity | NYC police-reported crashes, 2013-2025",
    "00:00-stamped reports shown separately; no traffic-volume denominator, so this is not crash risk.",
    lambda x: f"{x:.2f}",
)

# Option 2: mean recorded persons injured among crashes with known injury
# counts, using the same date/time group definitions and year window.
injury_rows = con.execute(f"""
    SELECT {GROUP_CASE} AS time_group,
           count(*) AS crashes_with_known_injury_count,
           sum(number_of_persons_injured) AS persons_injured
    FROM read_parquet('{DATA}')
    WHERE year(crash_date) BETWEEN {YEAR_SQL}
      AND crash_date IS NOT NULL AND crash_time IS NOT NULL
      AND number_of_persons_injured IS NOT NULL
    GROUP BY time_group
""").fetchall()
injury_map = {group: (n, total) for group, n, total in injury_rows}
values_2 = []
for group in ORDER:
    n, total = injury_map.get(group, (0, 0))
    mean = total / n if n else 0
    values_2.append({
        "group": group,
        "crashes_with_known_injury_count": n,
        "persons_injured_sum": total,
        "mean_persons_injured_per_crash": f"{mean:.6f}",
        "metric_value": f"{mean:.6f}",
    })
write_values(2, ["group", "crashes_with_known_injury_count", "persons_injured_sum",
                 "mean_persons_injured_per_crash", "metric_value"], values_2)
draw(
    2, values_2, "Mean recorded persons injured per reported crash",
    "Mean injuries per reported crash | NYC police-reported crashes, 2013-2025",
    "00:00-stamped reports shown separately; per-crash injury burden is not traveler injury risk.",
    lambda x: f"{x:.3f}",
)
