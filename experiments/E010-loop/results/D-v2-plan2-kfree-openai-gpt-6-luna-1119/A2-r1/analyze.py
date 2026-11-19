from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"

con = duckdb.connect()
query = f"""
WITH eligible AS (
    SELECT
        CASE
            WHEN crash_time = TIME '00:00:00' THEN '00:00 (possible default)'
            WHEN EXTRACT(HOUR FROM crash_time) >= 20 OR EXTRACT(HOUR FROM crash_time) < 6 THEN 'Night'
            ELSE 'Day'
        END AS time_group,
        number_of_persons_injured,
        number_of_persons_killed
    FROM read_parquet('{DATA.as_posix()}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
      AND crash_time IS NOT NULL
      AND number_of_persons_injured IS NOT NULL
      AND number_of_persons_killed IS NOT NULL
)
SELECT
    time_group,
    COUNT(*) AS eligible_crashes,
    COUNT(*) FILTER (
        WHERE number_of_persons_injured > 0 OR number_of_persons_killed > 0
    ) AS crashes_involving_injury_or_death,
    SUM(number_of_persons_injured + number_of_persons_killed) AS reported_casualties
FROM eligible
GROUP BY time_group
"""
values = con.execute(query).fetchdf()
order = ["Day", "Night", "00:00 (possible default)"]
values["time_group"] = pd.Categorical(values["time_group"], categories=order, ordered=True)
values = values.sort_values("time_group").reset_index(drop=True)
values["pct_crashes_involving_injury_or_death"] = (
    100 * values["crashes_involving_injury_or_death"] / values["eligible_crashes"]
)
values["mean_casualties_per_crash"] = (
    values["reported_casualties"] / values["eligible_crashes"]
)

share_cols = [
    "time_group",
    "eligible_crashes",
    "crashes_involving_injury_or_death",
    "pct_crashes_involving_injury_or_death",
]
values[share_cols].to_csv(OUT / "values_1.csv", index=False, float_format="%.6f")

fig, ax = plt.subplots(figsize=(9, 5.5))
bars = ax.bar(
    values["time_group"].astype(str),
    values["pct_crashes_involving_injury_or_death"],
    color=["#4378a8", "#d97732", "#8a8a8a"],
    width=0.62,
)
ax.set_ylabel("Crashes involving injury or death (%)")
ax.set_title("Share of NYC police-reported crashes with injury or death\n2013–2025 complete years")
ax.set_ylim(0, max(values["pct_crashes_involving_injury_or_death"]) * 1.18)
ax.grid(axis="y", alpha=0.22)
ax.set_axisbelow(True)
for bar, pct, n in zip(bars, values["pct_crashes_involving_injury_or_death"], values["eligible_crashes"]):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{pct:.1f}%\nn={n:,}",
            ha="center", va="bottom", fontsize=9)
fig.text(
    0.5,
    0.015,
    "One row per reported crash; exact 00:00 shown separately. No traffic-exposure denominator, so this is not per-trip or per-mile risk.",
    ha="center",
    fontsize=8,
)
fig.tight_layout(rect=(0, 0.07, 1, 1))
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

casualty_cols = [
    "time_group",
    "eligible_crashes",
    "reported_casualties",
    "mean_casualties_per_crash",
]
values[casualty_cols].to_csv(OUT / "values_2.csv", index=False, float_format="%.6f")

fig, ax = plt.subplots(figsize=(9, 5.5))
bars = ax.bar(
    values["time_group"].astype(str),
    values["mean_casualties_per_crash"],
    color=["#4378a8", "#d97732", "#8a8a8a"],
    width=0.62,
)
ax.set_ylabel("Reported injured + killed people per crash")
ax.set_title("Mean reported casualties per NYC police-reported crash\n2013–2025 complete years")
ax.set_ylim(0, max(values["mean_casualties_per_crash"]) * 1.18)
ax.grid(axis="y", alpha=0.22)
ax.set_axisbelow(True)
for bar, mean, n in zip(bars, values["mean_casualties_per_crash"], values["eligible_crashes"]):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{mean:.3f}\nn={n:,}",
            ha="center", va="bottom", fontsize=9)
fig.text(
    0.5,
    0.015,
    "One row per reported crash; exact 00:00 shown separately. No traffic-exposure denominator, so this is not per-trip or per-mile risk.",
    ha="center",
    fontsize=8,
)
fig.tight_layout(rect=(0, 0.07, 1, 1))
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)

print(values.to_string(index=False))
