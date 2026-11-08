from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
con = duckdb.connect()
source = "read_parquet('" + str(DATA).replace("'", "''") + "')"
years = "year(crash_date) BETWEEN 2013 AND 2025"
valid_datetime = f"crash_date IS NOT NULL AND crash_time IS NOT NULL AND {years}"
period = "CASE WHEN hour(crash_time) >= 19 OR hour(crash_time) < 7 THEN 'Night' ELSE 'Day' END"
ordered = "CASE WHEN period = 'Day' THEN 1 ELSE 2 END"

# Option 1: crash volume in two equal-length time windows over identical years.
volume = con.execute(
    f"SELECT {period} AS period, count(*)::BIGINT AS crash_count "
    f"FROM {source} WHERE {valid_datetime} "
    f"GROUP BY 1 ORDER BY {ordered}"
).df()
volume.to_csv(OUT / "values_1.csv", index=False)

fig, ax = plt.subplots(figsize=(8.5, 5.2))
colors = ["#4878A8", "#D27C32"]
bars = ax.bar(volume["period"], volume["crash_count"], color=colors, width=0.58)
ax.set_title("Total police-reported crashes by 12-hour period\nNYC, 2013–2025 (N=2,132,218)", loc="left", weight="bold", pad=14)
ax.text(0, 1.015, "Night: 7 p.m.–6:59 a.m.  |  Day: 7 a.m.–6:59 p.m.  |  Counts are not adjusted for traffic exposure.",
        transform=ax.transAxes, fontsize=9, color="#444444", va="bottom")
ax.set_ylabel("Police-reported crashes")
ax.set_xlabel("")
ax.ticklabel_format(axis="y", style="plain")
ax.grid(axis="y", color="#dddddd", linewidth=0.8)
ax.set_axisbelow(True)
for bar, value in zip(bars, volume["crash_count"]):
    ax.annotate(f"{value:,.0f}", (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 5), textcoords="offset points", ha="center", fontsize=10)
fig.tight_layout(rect=(0, 0, 1, 0.93))
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Option 2: among crashes with known valid person counts, compare the share
# with at least one person reported injured or killed.
severity = con.execute(
    f"SELECT {period} AS period, count(*)::BIGINT AS eligible_crashes, "
    "count(*) FILTER (WHERE number_of_persons_injured > 0 OR number_of_persons_killed > 0)::BIGINT "
    "AS crashes_with_injury_or_fatality "
    f"FROM {source} WHERE {valid_datetime} "
    "AND number_of_persons_injured IS NOT NULL AND number_of_persons_injured >= 0 "
    "AND number_of_persons_killed IS NOT NULL AND number_of_persons_killed >= 0 "
    f"GROUP BY 1 ORDER BY {ordered}"
).df()
severity["share_pct"] = 100 * severity["crashes_with_injury_or_fatality"] / severity["eligible_crashes"]
severity.to_csv(OUT / "values_2.csv", index=False)

fig, ax = plt.subplots(figsize=(8.5, 5.2))
bars = ax.bar(severity["period"], severity["share_pct"], color=colors, width=0.58)
ax.set_title("Police-reported crashes with injury or fatality\nShare of NYC crashes with known person counts, 2013–2025", loc="left", weight="bold", pad=14)
ax.text(0, 1.015, "Night: 7 p.m.–6:59 a.m.  |  Day: 7 a.m.–6:59 p.m.  |  Conditional on a reported crash; not exposure-adjusted.",
        transform=ax.transAxes, fontsize=9, color="#444444", va="bottom")
ax.set_ylabel("Crashes with injury or fatality (%)")
ax.set_xlabel("")
ax.set_ylim(0, max(severity["share_pct"]) * 1.2)
ax.grid(axis="y", color="#dddddd", linewidth=0.8)
ax.set_axisbelow(True)
for bar, value in zip(bars, severity["share_pct"]):
    ax.annotate(f"{value:.1f}%", (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 5), textcoords="offset points", ha="center", fontsize=10)
fig.tight_layout(rect=(0, 0, 1, 0.93))
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)

print(pd.concat([volume.assign(option=1), severity.assign(option=2)], ignore_index=True, sort=False).to_string(index=False))
