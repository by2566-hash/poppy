import csv
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
DATA = str(ROOT / "data" / "crashes.parquet")
con = duckdb.connect()
source = f"read_parquet('{DATA}')"
base = f"{source} WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'"
period = """CASE
    WHEN crash_time IS NULL THEN 'Unknown/invalid time'
    WHEN HOUR(crash_time) >= 20 OR HOUR(crash_time) < 6 THEN 'Night'
    ELSE 'Day'
END"""
order = {"Day": 0, "Night": 1, "Unknown/invalid time": 2}


def save_chart(option_id, rows, title, subtitle, ylabel, formatter):
    categories = ["Day", "Night", "Unknown/invalid time"] if option_id == 1 else ["Day", "Night"]
    by_group = {row["group"]: row for row in rows}
    for group in categories:
        if group not in by_group:
            by_group[group] = {
                "group": group,
                "metric_value": 0.0,
                "numerator": 0,
                "denominator": None if option_id == 1 else 0,
            }
    rows = [by_group[group] for group in categories]
    with (OUT / f"values_{option_id}.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["group", "metric_value", "numerator", "denominator"])
        writer.writeheader()
        writer.writerows(rows)

    values = [float(row["metric_value"]) for row in rows]
    colors = ["#5b8db8", "#d77a36", "#a3a3a3"][: len(rows)]
    fig, ax = plt.subplots(figsize=(8.3, 5.2))
    bars = ax.bar([row["group"] for row in rows], values, color=colors, width=0.62)
    fig.suptitle(title, fontsize=12, weight="bold", y=0.97)
    fig.text(0.5, 0.87, subtitle, ha="center", va="center", fontsize=9, color="#444444")
    ax.set_ylabel(ylabel)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.22)
    ax.set_axisbelow(True)
    for bar, value in zip(bars, values):
        ax.annotate(formatter(value), (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 5), textcoords="offset points", ha="center", va="bottom", fontsize=9)
    fig.subplots_adjust(top=0.80, bottom=0.12)
    fig.savefig(OUT / f"option_{option_id}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


# Option 1: raw crash-record frequency, retaining the unknown group even though
# the final-year time check found none.
result = con.execute(
    f"""SELECT {period} AS time_group, COUNT(*) AS crash_count
        FROM {base}
        GROUP BY time_group"""
).fetchall()
rows = [
    {"group": group, "metric_value": count, "numerator": count, "denominator": ""}
    for group, count in result
]
rows.sort(key=lambda row: order[row["group"]])
save_chart(
    1,
    rows,
    "Police-reported crash counts by time of day\nNYC crashes, complete calendar years 2013–2025",
    "Raw counts are not adjusted for traffic exposure; 23,787 midnight values retained as night",
    "Crash records",
    lambda value: f"{value:,.0f}",
)

# Options 2 and 3 use identical complete-case eligible populations and time
# groups; only the outcome summary differs.
complete = f"{base} AND number_of_persons_injured IS NOT NULL AND number_of_persons_killed IS NOT NULL AND crash_time IS NOT NULL"
result = con.execute(
    f"""SELECT {period} AS time_group,
               COUNT(*) AS eligible_crashes,
               COUNT(*) FILTER (WHERE number_of_persons_injured > 0 OR number_of_persons_killed > 0) AS injury_or_death_crashes
        FROM {complete}
        GROUP BY time_group"""
).fetchall()
rows = []
for group, denominator, numerator in result:
    rows.append({
        "group": group,
        "metric_value": 100.0 * numerator / denominator,
        "numerator": numerator,
        "denominator": denominator,
    })
rows.sort(key=lambda row: order[row["group"]])
save_chart(
    2,
    rows,
    "Share of crashes with ≥1 reported injury or death\nEligible NYC police-reported crashes, 2013–2025",
    "Not a traffic-exposure risk; 42 records missing outcome totals excluded",
    "Crashes with injury/death (%)",
    lambda value: f"{value:.2f}%",
)

result = con.execute(
    f"""SELECT {period} AS time_group,
               COUNT(*) AS eligible_crashes,
               SUM(number_of_persons_injured + number_of_persons_killed) AS reported_person_casualties
        FROM {complete}
        GROUP BY time_group"""
).fetchall()
rows = [
    {
        "group": group,
        "metric_value": casualties / denominator,
        "numerator": casualties,
        "denominator": denominator,
    }
    for group, denominator, casualties in result
]
rows.sort(key=lambda row: order[row["group"]])
save_chart(
    3,
    rows,
    "Mean reported injured + killed persons per crash\nEligible NYC police-reported crashes, 2013–2025",
    "Not a traffic-exposure risk; 42 records missing outcome totals excluded",
    "Reported persons injured + killed per crash",
    lambda value: f"{value:.3f}",
)

print("Saved charts and plotted values for options 1–3.")
