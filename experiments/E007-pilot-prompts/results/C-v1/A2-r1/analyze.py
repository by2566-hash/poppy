"""Are NYC streets more dangerous at night? Hourly severity analysis of motor-vehicle crashes."""
import os

import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

PARQUET = "./data/crashes.parquet"
OUTDIR = "./out"
os.makedirs(OUTDIR, exist_ok=True)

con = duckdb.connect()

# Hourly stats. Night = 22:00-05:59 (8 hrs), Day = 06:00-21:59 (16 hrs).
hourly = con.execute(f"""
    SELECT hour(crash_time) AS hour,
           CASE WHEN hour(crash_time) >= 22 OR hour(crash_time) < 6
                THEN 'Night (10pm-6am)' ELSE 'Day (6am-10pm)' END AS period,
           COUNT(*) AS crashes,
           SUM(COALESCE(number_of_persons_injured, 0)) AS persons_injured,
           SUM(COALESCE(number_of_persons_killed, 0)) AS persons_killed,
           SUM(CASE WHEN COALESCE(number_of_persons_killed, 0) > 0 THEN 1 ELSE 0 END) AS fatal_crashes,
           SUM(COALESCE(number_of_pedestrians_injured, 0)) AS ped_injured,
           SUM(COALESCE(number_of_pedestrians_killed, 0)) AS ped_killed
    FROM '{PARQUET}'
    GROUP BY 1, 2
    ORDER BY 1
""").df()

hourly["injured_per_crash"] = hourly["persons_injured"] / hourly["crashes"]
hourly["killed_per_1000_crashes"] = 1000 * hourly["persons_killed"] / hourly["crashes"]
hourly["fatal_crash_pct"] = 100 * hourly["fatal_crashes"] / hourly["crashes"]

period = con.execute(f"""
    SELECT CASE WHEN hour(crash_time) >= 22 OR hour(crash_time) < 6
                THEN 'Night (10pm-6am)' ELSE 'Day (6am-10pm)' END AS period,
           COUNT(*) AS crashes,
           SUM(COALESCE(number_of_persons_injured, 0)) AS persons_injured,
           SUM(COALESCE(number_of_persons_killed, 0)) AS persons_killed,
           SUM(CASE WHEN COALESCE(number_of_persons_killed, 0) > 0 THEN 1 ELSE 0 END) AS fatal_crashes
    FROM '{PARQUET}'
    GROUP BY 1
""").df()

period["injured_per_crash"] = period["persons_injured"] / period["crashes"]
period["killed_per_1000_crashes"] = 1000 * period["persons_killed"] / period["crashes"]
period["fatal_crash_pct"] = 100 * period["fatal_crashes"] / period["crashes"]
period["crashes_per_hour_of_day"] = period["crashes"] / (period["period"].str.startswith("Night").map({True: 8, False: 16}))
period = period.set_index("period").loc[["Night (10pm-6am)", "Day (6am-10pm)"]].reset_index()

# Robustness: same night/day severity ratio by year
yearly = con.execute(f"""
    SELECT year(crash_date) AS yr,
           CASE WHEN hour(crash_time) >= 22 OR hour(crash_time) < 6
                THEN 'Night' ELSE 'Day' END AS period,
           COUNT(*) AS crashes,
           SUM(COALESCE(number_of_persons_killed, 0)) AS persons_killed
    FROM '{PARQUET}'
    WHERE year(crash_date) BETWEEN 2016 AND 2025
    GROUP BY 1, 2
""").df()
yearly["killed_per_1000_crashes"] = 1000 * yearly["persons_killed"] / yearly["crashes"]
piv = yearly.pivot(index="yr", columns="period", values="killed_per_1000_crashes")
piv["night_vs_day_ratio"] = piv["Night"] / piv["Day"]

night = period.loc[period["period"].str.startswith("Night")].iloc[0]
day = period.loc[period["period"].str.startswith("Day")].iloc[0]

# ---- Chart ----
fig, axes = plt.subplots(1, 3, figsize=(15, 5.2))

ax = axes[0]
colors = ["#1a3a6b" if (h >= 22 or h < 6) else "#f0a05a" for h in hourly["hour"]]
ax.bar(hourly["hour"], hourly["killed_per_1000_crashes"], color=colors, width=0.85)
ax.axvspan(-0.5, 5.5, color="#1a3a6b", alpha=0.08)
ax.axvspan(21.5, 23.5, color="#1a3a6b", alpha=0.08)
ax.set_xlabel("Hour of crash")
ax.set_ylabel("People killed per 1,000 crashes")
ax.set_title("Every crash is deadlier after dark", fontsize=12, fontweight="bold")
ax.set_xticks(range(0, 24))
ax.text(1.5, ax.get_ylim()[1] * 0.92, "NIGHT", ha="center", color="#1a3a6b", fontweight="bold")
ax.text(14, ax.get_ylim()[1] * 0.92, "DAY", ha="center", color="#b06010", fontweight="bold")
ax.grid(axis="y", alpha=0.3)

ax = axes[1]
xpos = [0, 1]
kpc = [night["killed_per_1000_crashes"], day["killed_per_1000_crashes"]]
bars = ax.bar(xpos, kpc, color=["#1a3a6b", "#f0a05a"], width=0.55)
for b, v in zip(bars, kpc):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.02, f"{v:.2f}", ha="center", fontweight="bold")
ax.set_xticks(xpos)
ax.set_xticklabels(["Night\n(10pm-6am)", "Day\n(6am-10pm)"])
ax.set_ylabel("People killed per 1,000 crashes")
ax.set_title(
    f"Night crashes are {night['killed_per_1000_crashes'] / day['killed_per_1000_crashes']:.1f}x as deadly",
    fontsize=12, fontweight="bold",
)
night_crash_share = 100 * night["crashes"] / period["crashes"].sum()
night_death_share = 100 * night["persons_killed"] / period["persons_killed"].sum()
ax.text(
    0.72, 0.72,
    f"Night = {night_crash_share:.0f}% of crashes\nbut {night_death_share:.0f}% of deaths",
    transform=ax.transAxes, ha="center", va="top", fontsize=9.5,
    bbox=dict(boxstyle="round,pad=0.35", fc="#fff8e7", ec="#c9a66b", alpha=0.95),
)
ax.grid(axis="y", alpha=0.3)

ax = axes[2]
fpc = [night["fatal_crash_pct"], day["fatal_crash_pct"]]
bars = ax.bar(xpos, fpc, color=["#1a3a6b", "#f0a05a"], width=0.55)
for b, v in zip(bars, fpc):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.008, f"{v:.2f}%", ha="center", fontweight="bold")
ax.set_xticks(xpos)
ax.set_xticklabels(["Night\n(10pm-6am)", "Day\n(6am-10pm)"])
ax.set_ylabel("% of crashes that kill someone")
ax.set_title("Share of crashes that are fatal", fontsize=12, fontweight="bold")
ax.grid(axis="y", alpha=0.3)

fig.suptitle(
    "NYC crashes, 2012–mid-2026 (N = {:,}): fewer crashes at night, but far more lethal per crash".format(
        int(hourly["crashes"].sum())
    ),
    fontsize=13, fontweight="bold", y=1.02,
)
fig.tight_layout()
fig.savefig(f"{OUTDIR}/initial.png", dpi=150, bbox_inches="tight")

# ---- CSV: hourly + period summary ----
hourly_out = hourly.copy()
hourly_out.insert(0, "row_type", "hour")
period_out = period.copy()
period_out.insert(0, "row_type", "period_summary")
period_out["hour"] = period_out["period"].str.split().str[0].str.lower()
combined = pd.concat([hourly_out, period_out], ignore_index=True)
combined.to_csv(f"{OUTDIR}/values.csv", index=False)

print("=== Period summary ===")
print(period.to_string(index=False))
print("\n=== Hourly ===")
print(hourly[["hour", "period", "crashes", "killed_per_1000_crashes", "injured_per_crash", "fatal_crash_pct"]].to_string(index=False))
print("\n=== Night/Day lethality ratio by year (2016-2025) ===")
print(piv.round(2).to_string())
print(f"\nRatio of night-to-day deaths per 1,000 crashes: {night['killed_per_1000_crashes']/day['killed_per_1000_crashes']:.2f}")
print(f"Crash share at night: {100*night['crashes']/period['crashes'].sum():.1f}% of crashes, but "
      f"{100*night['persons_killed']/period['persons_killed'].sum():.1f}% of deaths")
print(f"Injuries per crash: night {night['injured_per_crash']:.3f} vs day {day['injured_per_crash']:.3f}")
