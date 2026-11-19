import csv
import json
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
PARQUET = ROOT / "data" / "crashes.parquet"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

con = duckdb.connect()
records = con.execute(
    "SELECT isodow(crash_date) AS weekday_number, count(*) AS crash_records "
    "FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' "
    "AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1",
    [str(PARQUET)],
).df()
con.close()

counts = {int(row.weekday_number): int(row.crash_records) for row in records.itertuples()}
day_counts = [counts.get(day, 0) for day in range(1, 8)]
calendar_dates = pd.date_range("2013-01-01", "2025-12-31", freq="D")
date_occurrences = calendar_dates.dayofweek.value_counts().reindex(range(7), fill_value=0).tolist()

for option_id in (1, 2):
    plan = json.loads((OUT / f"plan_{option_id}.json").read_text())["final_plan"]
    values = pd.DataFrame(
        {
            "weekday": WEEKDAYS,
            "crash_records": day_counts,
            "calendar_date_occurrences": date_occurrences,
        }
    )
    if option_id == 1:
        values["metric_value"] = values["crash_records"]
        ylabel = "Police-reported crash records"
        title = "Police-reported crash records by weekday, 2013–2025"
        note = "Pooled totals; not adjusted for traffic exposure or weekday-date frequency."
    else:
        values["metric_value"] = values["crash_records"] / values["calendar_date_occurrences"]
        ylabel = "Mean crash records per calendar date"
        title = "Mean police-reported crashes per weekday date, 2013–2025"
        note = "Calendar dates are the denominator; this is not traffic-exposure-adjusted risk."

    values.to_csv(OUT / f"values_{option_id}.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    fig, ax = plt.subplots(figsize=(10, 5.7))
    ax.bar(values["weekday"], values["metric_value"], color="#2878B5")
    ax.set_title(title, fontsize=14, pad=18)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Day of week")
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    fig.text(0.5, 0.015, note, ha="center", fontsize=9, color="#444444")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(OUT / f"option_{option_id}.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
