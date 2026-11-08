from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"

con = duckdb.connect()
con.execute(f"CREATE VIEW crashes AS SELECT * FROM read_parquet('{DATA.as_posix()}')")
date_bounds = con.execute(
    "SELECT min(crash_date), max(crash_date) FROM crashes"
).fetchone()
days_observed = (date_bounds[1] - date_bounds[0]).days + 1

# Night is 20:00–05:59; daytime is 06:00–19:59.
period_case = """CASE WHEN EXTRACT(hour FROM crash_time) >= 20
                         OR EXTRACT(hour FROM crash_time) < 6
                    THEN 'Night (20:00–05:59)'
                    ELSE 'Day (06:00–19:59)' END"""

counts = con.execute(
    f"""SELECT {period_case} AS period, count(*) AS crashes
        FROM crashes GROUP BY period"""
).df()
period_order = ["Night (20:00–05:59)", "Day (06:00–19:59)"]
counts["period"] = pd.Categorical(counts["period"], period_order, ordered=True)
counts = counts.sort_values("period").reset_index(drop=True)
counts["hours_observed"] = counts["period"].map(
    {period_order[0]: days_observed * 10, period_order[1]: days_observed * 14}
).astype("int64")
counts["crashes_per_hour"] = counts["crashes"] / counts["hours_observed"]
counts.to_csv(OUT / "values_1.csv", index=False, float_format="%.6f")

severity = con.execute(
    f"""SELECT {period_case} AS period,
               count(*) AS crashes,
               sum(CASE WHEN number_of_pedestrians_injured > 0
                              OR number_of_pedestrians_killed > 0
                              OR number_of_cyclist_injured > 0
                              OR number_of_cyclist_killed > 0
                              OR number_of_motorist_injured > 0
                              OR number_of_motorist_killed > 0
                        THEN 1 ELSE 0 END) AS injury_or_fatal_crashes
        FROM crashes GROUP BY period"""
).df()
severity["period"] = pd.Categorical(severity["period"], period_order, ordered=True)
severity = severity.sort_values("period").reset_index(drop=True)
severity["injury_or_fatal_crashes"] = severity["injury_or_fatal_crashes"].astype("int64")
severity["pct_injury_or_fatal"] = (
    severity["injury_or_fatal_crashes"] / severity["crashes"] * 100
)
severity.to_csv(OUT / "values_2.csv", index=False, float_format="%.6f")

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
colors = ["#c4513b", "#3478a8"]

fig, ax = plt.subplots(figsize=(9, 5.3))
bars = ax.barh(["Night", "Day"], counts["crashes_per_hour"], color=colors, height=0.58)
ax.invert_yaxis()
ax.set_xlabel("Reported crashes per observed clock-hour")
ax.set_title("Fewer crashes are reported per clock-hour at night", loc="left", weight="bold", pad=24)
ax.text(
    0, 1.015,
    f"NYC crashes, {date_bounds[0]} to {date_bounds[1]} · Night 20:00–05:59; day 06:00–19:59",
    transform=ax.transAxes, fontsize=9, color="#4f5963",
)
ax.text(
    0, -0.20,
    "Per clock-hour, not adjusted for how many people or vehicles are on the road.",
    transform=ax.transAxes, fontsize=9, color="#4f5963",
)
ax.grid(axis="x", color="#d9dee3", linewidth=0.8)
ax.set_axisbelow(True)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(axis="y", length=0)
for bar, row in zip(bars, counts.itertuples()):
    ax.text(
        bar.get_width() + max(counts["crashes_per_hour"]) * 0.012,
        bar.get_y() + bar.get_height() / 2,
        f"{row.crashes_per_hour:.1f}  ({row.crashes:,} crashes)",
        va="center", fontsize=10,
    )
ax.set_xlim(0, max(counts["crashes_per_hour"]) * 1.43)
fig.subplots_adjust(left=0.15, right=0.97, top=0.82, bottom=0.22)
fig.savefig(OUT / "option_1.png", dpi=180, facecolor="white")
plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 5.3))
bars = ax.barh(["Night", "Day"], severity["pct_injury_or_fatal"], color=colors, height=0.58)
ax.invert_yaxis()
ax.set_xlabel("Share of reported crashes involving ≥1 injured or killed person")
ax.set_title("A larger share of nighttime crashes involve injury or death", loc="left", weight="bold", pad=24)
ax.text(
    0, 1.015,
    f"NYC crashes, {date_bounds[0]} to {date_bounds[1]} · Night 20:00–05:59; day 06:00–19:59",
    transform=ax.transAxes, fontsize=9, color="#4f5963",
)
ax.text(
    0, -0.20,
    "Outcome conditional on a reported crash; does not measure risk per trip or mile.",
    transform=ax.transAxes, fontsize=9, color="#4f5963",
)
ax.grid(axis="x", color="#d9dee3", linewidth=0.8)
ax.set_axisbelow(True)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(axis="y", length=0)
for bar, row in zip(bars, severity.itertuples()):
    ax.text(
        bar.get_width() + max(severity["pct_injury_or_fatal"]) * 0.012,
        bar.get_y() + bar.get_height() / 2,
        f"{row.pct_injury_or_fatal:.1f}%  ({row.injury_or_fatal_crashes:,} / {row.crashes:,})",
        va="center", fontsize=10,
    )
ax.set_xlim(0, max(severity["pct_injury_or_fatal"]) * 1.52)
fig.subplots_adjust(left=0.15, right=0.97, top=0.82, bottom=0.22)
fig.savefig(OUT / "option_2.png", dpi=180, facecolor="white")
plt.close(fig)

print("Data period:", date_bounds[0], "through", date_bounds[1], "(", days_observed, "days )")
print("Option 1 values:\n", counts.to_string(index=False))
print("Option 2 values:\n", severity.to_string(index=False))
