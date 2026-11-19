import csv
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
PARQUET = ROOT / "data" / "crashes.parquet"
parquet_sql_path = str(PARQUET).replace("'", "''")

con = duckdb.connect()
counts = con.execute(
    f"""
    SELECT EXTRACT(ISODOW FROM crash_date)::INTEGER AS weekday_num,
           COUNT(*)::BIGINT AS crash_records
    FROM read_parquet('{parquet_sql_path}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY weekday_num
    ORDER BY weekday_num
    """
).fetchall()

weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
crash_counts = [0] * 7
for weekday_num, n in counts:
    crash_counts[weekday_num - 1] = n
total = sum(crash_counts)
shares = [n / total * 100 for n in crash_counts]

with (OUT / "values_1.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["weekday", "crash_records"])
    writer.writerows(zip(weekdays, crash_counts))
with (OUT / "values_2.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["weekday", "crash_records", "share_percent"])
    writer.writerows((day, n, share) for day, n, share in zip(weekdays, crash_counts, shares))

subtitle = (
    "All dated police-reported crash records; not exposure-adjusted. "
    "Crashes without a usable date cannot be assigned to the period."
)

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(weekdays, crash_counts, color="#3977a8")
ax.set_title("Police-reported NYC crash records by weekday | 2013–2025", pad=32)
ax.text(0.5, 1.015, subtitle, transform=ax.transAxes, ha="center", va="bottom", fontsize=9, wrap=True)
ax.set_ylabel("Crash records")
ax.set_xlabel("Day of week from crash date")
ax.tick_params(axis="x", rotation=20)
ax.bar_label(bars, labels=[f"{n:,}" for n in crash_counts], padding=3, fontsize=8)
ax.set_ylim(0, max(crash_counts) * 1.14)
fig.tight_layout()
fig.savefig(OUT / "option_1.png", dpi=160, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(weekdays, shares, color="#458b69")
ax.set_title("Share of police-reported NYC crash records by weekday | 2013–2025", pad=32)
ax.text(0.5, 1.015, subtitle, transform=ax.transAxes, ha="center", va="bottom", fontsize=9, wrap=True)
ax.set_ylabel("Share of in-period crash records (%)")
ax.set_xlabel("Day of week from crash date")
ax.tick_params(axis="x", rotation=20)
ax.bar_label(bars, labels=[f"{p:.1f}%" for p in shares], padding=3, fontsize=8)
ax.set_ylim(0, max(shares) * 1.14)
fig.tight_layout()
fig.savefig(OUT / "option_2.png", dpi=160, bbox_inches="tight")
plt.close(fig)
