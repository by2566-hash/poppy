from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


DATA = "data/crashes.parquet"
OUT = Path("out")
con = duckdb.connect()

# This query implements both final plans: complete years 2013–2025, known
# injury/death counts, with exact midnight and missing times grouped separately.
rows = con.execute(
    f"""
    WITH selected AS (
        SELECT number_of_persons_injured AS injured,
               number_of_persons_killed AS killed,
               CASE
                   WHEN crash_time IS NULL OR crash_time = TIME '00:00:00'
                       THEN 'Uncertain time'
                   WHEN crash_time >= TIME '18:00:00' OR crash_time < TIME '06:00:00'
                       THEN 'Night'
                   ELSE 'Day'
               END AS time_group
        FROM read_parquet('{DATA}')
        WHERE crash_date >= DATE '2013-01-01'
          AND crash_date < DATE '2026-01-01'
          AND number_of_persons_injured IS NOT NULL
          AND number_of_persons_killed IS NOT NULL
    )
    SELECT time_group,
           count(*) AS crashes,
           count(*) FILTER (WHERE injured > 0 OR killed > 0) AS crashes_with_injury_or_death,
           sum(injured + killed) AS people_injured_or_killed
    FROM selected
    GROUP BY time_group
    """
).fetchdf()

order = ["Day", "Night", "Uncertain time"]
rows["time_group"] = pd.Categorical(rows["time_group"], categories=order, ordered=True)
rows = rows.sort_values("time_group").reset_index(drop=True)
rows["share_crashes_with_injury_or_death_pct"] = (
    rows["crashes_with_injury_or_death"] / rows["crashes"] * 100
)
rows["people_injured_or_killed_per_crash"] = (
    rows["people_injured_or_killed"] / rows["crashes"]
)

option1 = rows[["time_group", "crashes", "crashes_with_injury_or_death",
                "share_crashes_with_injury_or_death_pct"]].copy()
option1.to_csv(OUT / "values_1.csv", index=False, float_format="%.6f")
option2 = rows[["time_group", "crashes", "people_injured_or_killed",
                "people_injured_or_killed_per_crash"]].copy()
option2.to_csv(OUT / "values_2.csv", index=False, float_format="%.6f")

note = ("Police-reported crashes, 2013–2025; partial 2012 and 2026 excluded. "
        "Not adjusted for traffic exposure; exact-midnight/NULL times shown as uncertain.")

fig, ax = plt.subplots(figsize=(8.5, 5.4))
bars = ax.bar(option1["time_group"].astype(str),
              option1["share_crashes_with_injury_or_death_pct"],
              color=["#4C78A8", "#E45756", "#9D9DA1"])
ax.set_title("Crashes with reported injury or death by time of crash\nNYC police-reported crashes, 2013–2025", fontsize=14)
ax.set_ylabel("Crashes with ≥1 person injured or killed (%)")
ax.set_xlabel("Crash time")
ax.bar_label(bars, labels=[f"{v:.1f}%" for v in option1["share_crashes_with_injury_or_death_pct"]], padding=4)
ax.text(0.5, -0.22, note, transform=ax.transAxes, ha="center", va="top", fontsize=8, wrap=True)
ax.spines[["top", "right"]].set_visible(False)
ax.set_ylim(0, max(option1["share_crashes_with_injury_or_death_pct"]) * 1.18)
fig.tight_layout()
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(8.5, 5.4))
bars = ax.bar(option2["time_group"].astype(str),
              option2["people_injured_or_killed_per_crash"],
              color=["#4C78A8", "#E45756", "#9D9DA1"])
ax.set_title("Reported people injured or killed per crash by time\nNYC police-reported crashes, 2013–2025", fontsize=14)
ax.set_ylabel("Mean people injured + killed per crash")
ax.set_xlabel("Crash time")
ax.bar_label(bars, labels=[f"{v:.3f}" for v in option2["people_injured_or_killed_per_crash"]], padding=4)
ax.text(0.5, -0.22, note, transform=ax.transAxes, ha="center", va="top", fontsize=8, wrap=True)
ax.spines[["top", "right"]].set_visible(False)
ax.set_ylim(0, max(option2["people_injured_or_killed_per_crash"]) * 1.18)
fig.tight_layout()
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)

print(option1.to_string(index=False))
print(option2.to_string(index=False))
