from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
DATA = str(ROOT / "data" / "crashes.parquet")
GROUPS = ["Night", "Daytime", "00:00:00 recorded (potential default)"]
COLORS = ["#B7472A", "#2878A0", "#888888"]

con = duckdb.connect()
df = con.execute(
    """
    SELECT CASE
             WHEN crash_time = TIME '00:00:00' THEN '00:00:00 recorded (potential default)'
             WHEN EXTRACT(HOUR FROM crash_time) >= 20 OR EXTRACT(HOUR FROM crash_time) < 6 THEN 'Night'
             ELSE 'Daytime'
           END AS time_group,
           COUNT(*) AS crashes,
           COUNT(*) FILTER (
             WHERE number_of_persons_injured > 0 OR number_of_persons_killed > 0
           ) AS injury_or_death_crashes,
           SUM(number_of_persons_injured) AS persons_injured,
           SUM(number_of_persons_killed) AS persons_killed
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
      AND crash_time IS NOT NULL
      AND number_of_persons_injured IS NOT NULL
      AND number_of_persons_killed IS NOT NULL
    GROUP BY time_group
    """,
    [DATA],
).df()
con.close()

df["time_group"] = pd.Categorical(df["time_group"], categories=GROUPS, ordered=True)
df = df.sort_values("time_group").reset_index(drop=True)
df["share_injury_or_death_crashes_pct"] = 100 * df["injury_or_death_crashes"] / df["crashes"]
df["persons_killed_or_injured"] = df["persons_injured"] + df["persons_killed"]
df["persons_killed_or_injured_per_crash"] = df["persons_killed_or_injured"] / df["crashes"]

option_1 = df[["time_group", "crashes", "injury_or_death_crashes", "share_injury_or_death_crashes_pct"]].copy()
option_1["time_group"] = option_1["time_group"].astype(str)
option_1.to_csv(OUT / "values_1.csv", index=False, float_format="%.6f")

option_2 = df[["time_group", "crashes", "persons_injured", "persons_killed", "persons_killed_or_injured", "persons_killed_or_injured_per_crash"]].copy()
option_2["time_group"] = option_2["time_group"].astype(str)
option_2.to_csv(OUT / "values_2.csv", index=False, float_format="%.6f")


def style_axis(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#D8D8D8", linewidth=0.7, alpha=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", length=0, pad=9)


fig, ax = plt.subplots(figsize=(9.2, 5.6), layout="constrained")
bars = ax.bar(
    range(len(df)),
    df["share_injury_or_death_crashes_pct"],
    color=COLORS,
    width=0.62,
)
ax.set_xticks(range(len(df)), ["Night\n8 p.m.–5:59 a.m.", "Daytime\n6 a.m.–7:59 p.m.", "00:00:00\nseparate"])
ax.set_ylabel("Crashes involving injury or death (%)")
ax.set_title("Share of eligible NYC police-reported crashes involving injury or death\n2013–2025", loc="left", fontsize=15, weight="bold", pad=19)
fig.text(0.01, 0.905, "Conditional on a reported crash; no traffic-exposure denominator. Exact-midnight records are separated as possible default timestamps.", fontsize=9, color="#555555")
for bar, row in zip(bars, df.itertuples()):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.28, f"{row.share_injury_or_death_crashes_pct:.1f}%\n(n={row.crashes:,})", ha="center", va="bottom", fontsize=10, weight="bold")
ax.set_ylim(0, max(df["share_injury_or_death_crashes_pct"]) * 1.21)
style_axis(ax)
fig.savefig(OUT / "option_1.png", dpi=180, facecolor="white")
plt.close(fig)


fig, ax = plt.subplots(figsize=(9.2, 5.6), layout="constrained")
bars = ax.bar(
    range(len(df)),
    df["persons_killed_or_injured_per_crash"],
    color=COLORS,
    width=0.62,
)
ax.set_xticks(range(len(df)), ["Night\n8 p.m.–5:59 a.m.", "Daytime\n6 a.m.–7:59 p.m.", "00:00:00\nseparate"])
ax.set_ylabel("Persons injured or killed per crash")
ax.set_title("Mean injured and killed persons per eligible NYC police-reported crash\n2013–2025", loc="left", fontsize=15, weight="bold", pad=19)
fig.text(0.01, 0.905, "Casualties per recorded crash, not per trip or road user; exact-midnight records are separated as possible default timestamps.", fontsize=9, color="#555555")
for bar, row in zip(bars, df.itertuples()):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.012, f"{row.persons_killed_or_injured_per_crash:.3f}\n(n={row.crashes:,})", ha="center", va="bottom", fontsize=10, weight="bold")
ax.set_ylim(0, max(df["persons_killed_or_injured_per_crash"]) * 1.22)
style_axis(ax)
fig.savefig(OUT / "option_2.png", dpi=180, facecolor="white")
plt.close(fig)
