import csv
import json
import os
from collections import Counter
from datetime import date, timedelta

import duckdb
import matplotlib.pyplot as plt


DATA_PATH = "data/crashes.parquet"
OUT_DIR = "out"
START = date(2013, 1, 1)
END_EXCLUSIVE = date(2026, 1, 1)
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

os.makedirs(OUT_DIR, exist_ok=True)
db = duckdb.connect()
totals = db.execute(
    """
    SELECT COUNT(*) AS file_rows,
           COUNT(*) FILTER (WHERE crash_date IS NULL) AS null_dates,
           COUNT(*) FILTER (WHERE crash_date >= ? AND crash_date < ?) AS period_rows,
           COUNT(*) FILTER (WHERE crash_date IS NOT NULL AND (crash_date < ? OR crash_date >= ?)) AS outside_period
    FROM read_parquet(?)
    """,
    [START, END_EXCLUSIVE, START, END_EXCLUSIVE, DATA_PATH],
).fetchone()
file_rows, null_dates, period_rows, outside_period = map(int, totals)

weekday_counts = {name: 0 for name in WEEKDAYS}
for dow, n in db.execute(
    """
    SELECT extract(isodow FROM crash_date)::INTEGER AS weekday_number, COUNT(*)
    FROM read_parquet(?)
    WHERE crash_date >= ? AND crash_date < ?
    GROUP BY 1
    """,
    [DATA_PATH, START, END_EXCLUSIVE],
).fetchall():
    weekday_counts[WEEKDAYS[dow - 1]] = int(n)

date_counts = Counter()
current = START
while current < END_EXCLUSIVE:
    date_counts[WEEKDAYS[current.weekday()]] += 1
    current += timedelta(days=1)

assert sum(weekday_counts.values()) == period_rows
assert sum(date_counts.values()) == (END_EXCLUSIVE - START).days

rows1 = []
for weekday in WEEKDAYS:
    n = weekday_counts[weekday]
    rows1.append({
        "weekday": weekday,
        "crash_count": n,
        "share_of_crashes_pct": 100 * n / period_rows,
    })

rows2 = []
for weekday in WEEKDAYS:
    n = weekday_counts[weekday]
    dates = date_counts[weekday]
    rows2.append({
        "weekday": weekday,
        "crash_count": n,
        "calendar_dates": dates,
        "crashes_per_calendar_date": n / dates,
    })

def save_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


save_csv(f"{OUT_DIR}/values_1.csv", rows1)
save_csv(f"{OUT_DIR}/values_2.csv", rows2)

plt.figure(figsize=(10, 5.8))
bars = plt.bar([r["weekday"] for r in rows1], [r["crash_count"] for r in rows1], color="#3978a8")
plt.title("NYC motor vehicle crashes by weekday, 2013–2025")
plt.ylabel("Crash records")
plt.xlabel("Day of week")
plt.grid(axis="y", alpha=0.25)
plt.bar_label(bars, labels=[f'{r["crash_count"]:,}' for r in rows1], padding=3, fontsize=8)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/option_1.png", dpi=160)
plt.close()

plt.figure(figsize=(10, 5.8))
bars = plt.bar([r["weekday"] for r in rows2], [r["crashes_per_calendar_date"] for r in rows2], color="#d2833f")
plt.title("Average NYC crashes per calendar date by weekday, 2013–2025")
plt.ylabel("Crashes per date of that weekday")
plt.xlabel("Day of week")
plt.grid(axis="y", alpha=0.25)
plt.bar_label(bars, labels=[f'{r["crashes_per_calendar_date"]:.1f}' for r in rows2], padding=3, fontsize=8)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/option_2.png", dpi=160)
plt.close()

highest1 = max(rows1, key=lambda r: r["crash_count"])
lowest1 = min(rows1, key=lambda r: r["crash_count"])
highest2 = max(rows2, key=lambda r: r["crashes_per_calendar_date"])
lowest2 = min(rows2, key=lambda r: r["crashes_per_calendar_date"])
outside_pct = 100 * outside_period / file_rows
null_pct = 100 * null_dates / file_rows

options = {
    "options": [
        {
            "id": 1,
            "metric": "Total crash records",
            "denominator": f"All crash records dated 2013–2025 (n={period_rows:,})",
            "grouping": "Day of week",
            "chart_type": "Ordered bar chart",
            "reason": "A direct count and share show how the requested period's crash records are distributed across weekdays.",
            "probability": 0.6,
            "answer": f'{highest1["weekday"]} had the most crashes ({highest1["crash_count"]:,}, {highest1["share_of_crashes_pct"]:.2f}% of the period total), while {lowest1["weekday"]} had the fewest ({lowest1["crash_count"]:,}, {lowest1["share_of_crashes_pct"]:.2f}%).',
            "interpretation": f'This answers how the total crashes in 2013–2025 are divided across weekdays; {highest1["weekday"]} leads with {highest1["crash_count"]:,} crashes ({highest1["share_of_crashes_pct"]:.2f}%), and {lowest1["weekday"]} has {lowest1["crash_count"]:,} ({lowest1["share_of_crashes_pct"]:.2f}%). It is defensible because each file row represents one crash and the denominator is all dated crash rows in the requested period. It does not adjust for slight differences in how many calendar dates of each weekday occur in the period. The date filter leaves out {outside_period:,} rows ({outside_pct:.2f}% of the file) dated outside 2013–2025; no rows with a NULL crash_date were excluded ({null_pct:.2f}%), and no included year is partial.',
        },
        {
            "id": 2,
            "metric": "Average crash records per calendar date",
            "denominator": "Number of calendar dates for each weekday in 2013–2025",
            "grouping": "Day of week",
            "chart_type": "Ordered bar chart",
            "reason": "Dividing by the number of dates of each weekday controls for the small weekday-exposure differences in the 13-year interval.",
            "probability": 0.4,
            "answer": f'{highest2["weekday"]} averaged {highest2["crashes_per_calendar_date"]:.1f} crashes per date, the highest rate, versus {lowest2["weekday"]} at {lowest2["crashes_per_calendar_date"]:.1f}, the lowest.',
            "interpretation": f'This answers how frequently a date of each weekday had crash records on average; {highest2["weekday"]} averaged {highest2["crashes_per_calendar_date"]:.1f} crashes per date and {lowest2["weekday"]} averaged {lowest2["crashes_per_calendar_date"]:.1f}. This is defensible because each weekday is divided by its actual number of calendar dates in the requested period, which accounts for unequal weekday-date counts. It does not express each weekday as a share of all crashes. The date filter leaves out {outside_period:,} rows ({outside_pct:.2f}% of the file) dated outside 2013–2025; no rows with a NULL crash_date were excluded ({null_pct:.2f}%), and no included year is partial.',
        },
    ]
}
with open(f"{OUT_DIR}/options.json", "w", encoding="utf-8") as f:
    json.dump(options, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(json.dumps({
    "file_rows": file_rows,
    "period_rows": period_rows,
    "outside_period_rows": outside_period,
    "null_dates": null_dates,
    "weekday_counts": rows1,
    "date_counts": dict(date_counts),
    "weekday_rates": rows2,
}, indent=2))
