import csv
from datetime import date
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt


DATA = "data/crashes.parquet"
OUT = Path("out")
START = date(2013, 1, 1)
END_EXCLUSIVE = date(2026, 1, 1)
CALENDAR_DAYS = (END_EXCLUSIVE - START).days
HOURS_PER_DAY = {"Night": 10, "Day": 14}
ORDER = ["Night", "Day"]

con = duckdb.connect()

crash_rows = con.execute(
    f"""
    SELECT CASE
             WHEN extract(hour FROM crash_time) >= 20 OR extract(hour FROM crash_time) < 6 THEN 'Night'
             ELSE 'Day'
           END AS period,
           count(*) AS crash_rows
    FROM read_parquet('{DATA}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
      AND crash_time IS NOT NULL
    GROUP BY period
    """
).fetchall()
counts_by_period = dict(crash_rows)

hours = {period: CALENDAR_DAYS * HOURS_PER_DAY[period] for period in ORDER}
rates = {period: counts_by_period[period] / hours[period] for period in ORDER}

with (OUT / "values_1.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["period", "crash_rows", "calendar_days", "scheduled_hours", "crashes_per_clock_hour"])
    for period in ORDER:
        writer.writerow([period, counts_by_period[period], CALENDAR_DAYS, hours[period], f"{rates[period]:.8f}"])

fig, ax = plt.subplots(figsize=(9, 5.4))
colors = ["#365f91", "#95abc3"]
bars = ax.barh(ORDER, [rates[p] for p in ORDER], color=colors, height=0.58)
ax.invert_yaxis()
ax.set_xlabel("Police-reported crashes per scheduled clock-hour")
ax.set_title("NYC police-reported crash frequency per clock-hour\n2013–2025; all reported motor-vehicle crashes", loc="left", fontsize=15, weight="bold", pad=17)
ax.text(0, 1.025, "Night: 20:00–05:59 (10 h/day)  |  Day: 06:00–19:59 (14 h/day)", transform=ax.transAxes, fontsize=10, color="#4a5562")
ax.text(0, -0.20, "Limitation: clock-time normalization only; traffic and traveler exposure are unavailable, so this is not risk per trip or person.", transform=ax.transAxes, fontsize=9, color="#4a5562")
ax.grid(axis="x", color="#d9dee5", linewidth=0.8)
ax.set_axisbelow(True)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(axis="y", length=0, labelsize=11)
ax.tick_params(axis="x", length=0)
for bar, period in zip(bars, ORDER):
    ax.text(bar.get_width() + max(rates.values()) * 0.012, bar.get_y() + bar.get_height() / 2,
            f"{rates[period]:,.2f} / h  ({counts_by_period[period]:,} reports)", va="center", fontsize=10)
ax.set_xlim(0, max(rates.values()) * 1.43)
fig.subplots_adjust(left=0.19, right=0.98, top=0.79, bottom=0.22)
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

severity_rows = con.execute(
    f"""
    SELECT CASE
             WHEN extract(hour FROM crash_time) >= 20 OR extract(hour FROM crash_time) < 6 THEN 'Night'
             ELSE 'Day'
           END AS period,
           count(*) AS classifiable_crash_rows,
           count(*) FILTER (
             WHERE number_of_persons_injured > 0 OR number_of_persons_killed > 0
           ) AS crashes_with_injury_or_death
    FROM read_parquet('{DATA}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
      AND crash_time IS NOT NULL
      AND number_of_persons_injured IS NOT NULL
      AND number_of_persons_killed IS NOT NULL
    GROUP BY period
    """
).fetchall()
severity = {
    period: {"denominator": denominator, "injury_or_death": outcome_count}
    for period, denominator, outcome_count in severity_rows
}
shares = {
    period: severity[period]["injury_or_death"] / severity[period]["denominator"] * 100
    for period in ORDER
}

with (OUT / "values_2.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["period", "classifiable_crash_rows", "crashes_with_injury_or_death", "share_pct"])
    for period in ORDER:
        writer.writerow([
            period,
            severity[period]["denominator"],
            severity[period]["injury_or_death"],
            f"{shares[period]:.6f}",
        ])

fig, ax = plt.subplots(figsize=(9, 5.4))
bars = ax.barh(ORDER, [shares[p] for p in ORDER], color=colors, height=0.58)
ax.invert_yaxis()
ax.set_xlabel("Share of classifiable crash reports involving injury or death")
ax.set_title("Injury or death in NYC crash reports by time of day\n2013–2025; crashes with both total outcome counts present", loc="left", fontsize=15, weight="bold", pad=17)
ax.text(0, 1.025, "Outcome: at least one person injured or killed in the reported crash", transform=ax.transAxes, fontsize=10, color="#4a5562")
ax.text(0, -0.20, "Limitation: conditional on a reported crash; no traffic or traveler exposure denominator, so not risk per trip or person.", transform=ax.transAxes, fontsize=9, color="#4a5562")
ax.grid(axis="x", color="#d9dee5", linewidth=0.8)
ax.set_axisbelow(True)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(axis="y", length=0, labelsize=11)
ax.tick_params(axis="x", length=0)
for bar, period in zip(bars, ORDER):
    ax.text(bar.get_width() + max(shares.values()) * 0.012, bar.get_y() + bar.get_height() / 2,
            f"{shares[period]:.1f}%  ({severity[period]['injury_or_death']:,} / {severity[period]['denominator']:,})", va="center", fontsize=10)
ax.set_xlim(0, max(shares.values()) * 1.44)
fig.subplots_adjust(left=0.19, right=0.98, top=0.79, bottom=0.22)
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)

con.close()
