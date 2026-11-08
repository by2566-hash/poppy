from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"
data_sql_path = str(DATA).replace("'", "''")

con = duckdb.connect()
con.execute(
    f"""CREATE VIEW crashes AS
        SELECT crash_date, crash_time, number_of_persons_injured, number_of_persons_killed
        FROM read_parquet('{data_sql_path}')"""
)

base = """crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
          AND crash_time IS NOT NULL
          AND number_of_persons_injured IS NOT NULL
          AND number_of_persons_killed IS NOT NULL"""
daypart = "CASE WHEN hour(crash_time) >= 6 AND hour(crash_time) < 20 THEN 'Day (6am–7:59pm)' ELSE 'Night (8pm–5:59am)' END"

# Framing 1: share of crashes with any recorded person injury or death.
share = con.execute(
    f"""SELECT {daypart} AS daypart,
               count(*) AS reported_crashes,
               count(*) FILTER (WHERE number_of_persons_injured > 0 OR number_of_persons_killed > 0) AS injury_or_fatality_crashes,
               100.0 * count(*) FILTER (WHERE number_of_persons_injured > 0 OR number_of_persons_killed > 0) / count(*) AS share_percent
        FROM crashes WHERE {base}
        GROUP BY daypart ORDER BY CASE WHEN daypart LIKE 'Day%' THEN 1 ELSE 2 END"""
).df()
share.to_csv(OUT / "values_1.csv", index=False, float_format="%.6f")

plt.style.use("seaborn-v0_8-whitegrid")
fig, ax = plt.subplots(figsize=(8.4, 5.6))
colors = ["#336B87", "#D07837"]
bars = ax.bar(share["daypart"], share["share_percent"], color=colors, width=0.58)
for bar, pct, n in zip(bars, share["share_percent"], share["reported_crashes"]):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.35,
            f"{pct:.1f}%\n(n={n:,})", ha="center", va="bottom", fontsize=10)
ax.set_ylabel("Crashes with ≥1 person injured or killed (%)")
ax.set_xlabel("")
ax.set_ylim(0, max(share["share_percent"]) * 1.23)
fig.suptitle("Injury-or-fatality crash share by daypart", fontsize=15, fontweight="bold", y=0.98)
ax.set_title("NYC police-reported crashes, complete years 2013–2025\nNo traffic-volume denominator; crash share measures severity conditional on a reported crash.", fontsize=9.5, pad=12)
fig.tight_layout(rect=[0, 0, 1, 0.90])
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Framing 2: separate counts of injured and killed persons per 1,000 eligible crashes.
rates = con.execute(
    f"""WITH by_daypart AS (
            SELECT {daypart} AS daypart, count(*) AS reported_crashes,
                   sum(number_of_persons_injured) AS persons_injured,
                   sum(number_of_persons_killed) AS persons_killed
            FROM crashes WHERE {base}
            GROUP BY daypart
        )
        SELECT daypart, reported_crashes, 'Persons injured' AS outcome,
               persons_injured AS recorded_persons,
               1000.0 * persons_injured / reported_crashes AS per_1000_crashes
        FROM by_daypart
        UNION ALL
        SELECT daypart, reported_crashes, 'Persons killed' AS outcome,
               persons_killed AS recorded_persons,
               1000.0 * persons_killed / reported_crashes AS per_1000_crashes
        FROM by_daypart
        ORDER BY outcome, daypart"""
).df()
rates["recorded_persons"] = rates["recorded_persons"].astype("int64")
rates.to_csv(OUT / "values_2.csv", index=False, float_format="%.6f")

fig, axes = plt.subplots(1, 2, figsize=(10.6, 5.5))
outcomes = ["Persons injured", "Persons killed"]
dayparts = ["Day (6am–7:59pm)", "Night (8pm–5:59am)"]
daypart_colors = {dayparts[0]: "#336B87", dayparts[1]: "#D07837"}
for ax, outcome in zip(axes, outcomes):
    subset = rates[rates["outcome"] == outcome].set_index("daypart").loc[dayparts].reset_index()
    bars = ax.barh(["Day", "Night"], subset["per_1000_crashes"],
                   color=[daypart_colors[x] for x in subset["daypart"]], height=0.56)
    ax.invert_yaxis()
    ax.set_title(outcome, fontsize=12, fontweight="bold")
    ax.set_xlabel("Recorded people per 1,000 crashes")
    ax.set_ylabel("")
    ax.set_xlim(0, max(subset["per_1000_crashes"]) * 1.8)
    for bar, rate, count in zip(bars, subset["per_1000_crashes"], subset["recorded_persons"]):
        ax.text(bar.get_width() + max(subset["per_1000_crashes"]) * 0.025,
                bar.get_y() + bar.get_height() / 2,
                f"{rate:.2f}  ({int(count):,} people)", va="center", fontsize=9)
fig.suptitle("Recorded injury and death burden per 1,000 reported crashes", fontsize=14, fontweight="bold", y=0.98)
fig.text(0.5, 0.91, "NYC police-reported crashes, complete years 2013–2025 | No traffic-volume denominator; not risk per trip or mile.",
         ha="center", fontsize=9)
fig.tight_layout(rect=[0, 0, 1, 0.87])
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)

con.close()
