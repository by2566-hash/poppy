import csv
from collections import Counter
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


DATA = "data/crashes.parquet"
OUT = Path("out")
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

con = duckdb.connect()
counts = con.execute(
    f"""SELECT isodow(crash_date) AS weekday_number, count(*) AS crash_count
        FROM read_parquet('{DATA}')
        WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
        GROUP BY weekday_number ORDER BY weekday_number"""
).fetchall()
count_by_day = {WEEKDAYS[weekday_number - 1]: crash_count for weekday_number, crash_count in counts}

calendar_dates = pd.date_range("2013-01-01", "2025-12-31", freq="D")
occurrences = Counter(calendar_dates.day_name())
population_total = sum(count_by_day.values())

with (OUT / "values_1.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["weekday", "crash_count", "population_total", "share_of_selected_crashes"])
    for weekday in WEEKDAYS:
        count = count_by_day.get(weekday, 0)
        writer.writerow([weekday, count, population_total, count / population_total])

with (OUT / "values_2.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["weekday", "crash_count", "calendar_occurrences", "mean_crashes_per_occurrence"])
    for weekday in WEEKDAYS:
        count = count_by_day.get(weekday, 0)
        denominator = occurrences[weekday]
        writer.writerow([weekday, count, denominator, count / denominator])

limitation = "Police-reported crashes in the file only; full year boundary dates do not independently verify record completeness."

for option, metric, values, ylabel, number_format in [
    (1, "Police-reported crash count", [count_by_day[d] for d in WEEKDAYS], "Crash count", ",.0f"),
    (
        2,
        "Mean police-reported crashes per calendar weekday occurrence",
        [count_by_day[d] / occurrences[d] for d in WEEKDAYS],
        "Mean crashes per calendar date",
        ",.1f",
    ),
]:
    fig, ax = plt.subplots(figsize=(10, 5.6))
    bars = ax.bar(WEEKDAYS, values, color="#376996")
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Weekday of crash_date")
    ax.set_title(f"{metric}, NYC police-reported crashes, 2013–2025", fontsize=14, pad=14)
    ax.text(
        0.5,
        1.015,
        limitation,
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=8.5,
        color="#444444",
        wrap=True,
    )
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", rotation=20)
    ax.bar_label(bars, labels=[format(value, number_format) for value in values], padding=3, fontsize=8)
    fig.tight_layout(rect=(0, 0, 1, 0.91))
    fig.savefig(OUT / f"option_{option}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
