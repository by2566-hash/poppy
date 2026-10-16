Revise an analysis based on a reviewer's numbered issues.

Question:
How are NYC crashes distributed across the days of the week, 2013 to 2025?

Data description:
Data file: ./data/crashes.parquet (one row per police-reported motor vehicle crash in New York City; read it with DuckDB or pandas).
Columns: crash_date (DATE), crash_time (TIME), borough (VARCHAR, may be NULL), zip_code, latitude, longitude,
on_street_name, cross_street_name, number_of_persons_injured (INT), number_of_persons_killed (INT),
number_of_pedestrians_injured, number_of_pedestrians_killed, number_of_cyclist_injured, number_of_cyclist_killed,
number_of_motorist_injured, number_of_motorist_killed, contributing_factor_vehicle_1 ... contributing_factor_vehicle_5 (VARCHAR),
collision_id (BIGINT), vehicle_type_code1 ... vehicle_type_code5 (VARCHAR).
Python 3 with duckdb, pandas and matplotlib is available.

Current code:
# file: analyze.py
import duckdb
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SRC = "./data/crashes.parquet"
con = duckdb.connect()

counts = con.execute(
    """
    SELECT strftime(crash_date, '%u')::INT AS dow, COUNT(*) AS crashes
    FROM read_parquet(?)
    WHERE crash_date BETWEEN DATE '2013-01-01' AND DATE '2025-12-31'
      AND crash_date IS NOT NULL
    GROUP BY 1
    """,
    [SRC],
).df()

dates = con.execute(
    """
    WITH d AS (SELECT unnest(generate_series(DATE '2013-01-01', DATE '2025-12-31', INTERVAL '1 day')) AS dt)
    SELECT strftime(dt, '%u')::INT AS dow, COUNT(*) AS n_days
    FROM d GROUP BY 1
    """
).df()

df = dates.merge(counts, on="dow", how="left").fillna({"crashes": 0})
df["crashes"] = df["crashes"].astype(int)

names = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}
df["day"] = df["dow"].map(names)
df["share_pct"] = 100 * df["crashes"] / df["crashes"].sum()
df["avg_per_day"] = df["crashes"] / df["n_days"]
df = df.sort_values("dow").reset_index(drop=True)

total = df["crashes"].sum()
weekend = df.loc[df["dow"].isin([6, 7]), "crashes"].sum()
weekday = total - weekend
fri = df.loc[df["dow"] == 5, "crashes"].iloc[0]
sun = df.loc[df["dow"] == 7, "crashes"].iloc[0]
peak = df.loc[df["crashes"].idxmax()]
low = df.loc[df["crashes"].idxmin()]

out = df[["dow", "day", "crashes", "share_pct", "n_days", "avg_per_day"]].copy()
out.columns = ["dow", "day_of_week", "crashes", "share_pct", "n_days", "avg_crashes_per_day"]
out.to_csv("./out/values.csv", index=False)

print(out.to_string(index=False))
print(f"total={total} weekend={weekend} ({100*weekend/total:.1f}%) weekday={weekday} ({100*weekday/total:.1f}%)")
print(f"peak={peak['day']} {peak['crashes']} ({peak['share_pct']:.1f}%) low={low['day']} {low['crashes']} ({low['share_pct']:.1f}%)")
print(f"Fri/Sun ratio = {fri/sun:.3f}")

fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

colors = ["#4C72B0"] * 5 + ["#C44E52", "#C44E52"]
ax = axes[0]
bars = ax.bar(df["day"], df["crashes"], color=colors, edgecolor="black", linewidth=0.5)
for b, v, p in zip(bars, df["crashes"], df["share_pct"]):
    ax.text(b.get_x() + b.get_width() / 2, v + 4000, f"{v:,.0f}\n{p:.1f}%",
            ha="center", va="bottom", fontsize=9)
ax.set_title("NYC police-reported crashes by day of week\n(2013–2025, n = %s)" % f"{total:,}")
ax.set_ylabel("Total crashes")
ax.set_ylim(0, df["crashes"].max() * 1.18)
ax.grid(axis="y", alpha=0.3)
ax.set_axisbelow(True)

ax = axes[1]
bars = ax.bar(df["day"], df["avg_per_day"], color=colors, edgecolor="black", linewidth=0.5)
for b, v in zip(bars, df["avg_per_day"]):
    ax.text(b.get_x() + b.get_width() / 2, v + 30, f"{v:,.0f}", ha="center", va="bottom", fontsize=9)
ax.set_title("Average crashes per occurrence of each weekday\n(normalised for uneven weekday counts)")
ax.set_ylabel("Crashes per day")
ax.set_ylim(0, df["avg_per_day"].max() * 1.15)
ax.grid(axis="y", alpha=0.3)
ax.set_axisbelow(True)

for ax in axes:
    ax.set_xlabel("Day of week")

fig.tight_layout()
fig.savefig("./out/initial.png", dpi=150)
print("saved ./out/initial.png and ./out/values.csv")


Current plotted values (values.csv):
dow,day_of_week,crashes,share_pct,n_days,avg_crashes_per_day
1,Mon,304518,14.281747926337738,678,449.14159292035396
2,Tue,313488,14.702436617644162,679,461.69072164948454
3,Wed,311111,14.590956459423943,679,458.1899852724595
4,Thu,318376,14.931681469718388,678,469.5811209439528
5,Fri,338800,15.889557259154552,678,499.70501474926255
6,Sat,288381,13.524930377663072,678,425.3407079646018
7,Sun,257544,12.078689890058145,678,379.85840707964604


Current written answer:
Across 2013–2025 NYC recorded 2,132,218 crashes, and the weekly pattern is a steady build to Friday followed by a weekend drop: Fri is the peak (338,800; 15.9%; ~500/day), Thu next (318,376; 470/day), then Wed (311,111), Tue (313,488) and Mon the softest weekday (304,518; 449/day), while Sat falls to 288,381 (425/day) and Sunday is the clear low at 257,544 (12.1%; ~380/day) — Friday sees 32% more crashes than Sunday, and weekdays (5 of 7 days) carry 74.4% of all crashes.

Reviewer's issues:
1. Written answer, ranking sentence: it says "...Thu next (318,376; 470/day), then Wed (311,111), Tue (313,488)..." in what reads as descending order, but Tue (313,488) > Wed (311,111); the correct order after Thu is Tue then Wed. Relatedly, the claim of "a steady build to Friday" is not what the numbers show — Tue (313,488) dips below... rather Tue exceeds Wed (311,111), so the pattern is not monotone across weekdays.

Instructions:
- Go through the issues one by one. For each, either fix it, or check it and keep the original if the reviewer was wrong, or state that it cannot be addressed with this data.
- Change nothing the reviewer did not flag: same data, filters, numbers, chart type and wording of the written answer, unless fixing an issue requires it.
- Write and run the revised code yourself. Save the chart to ./out/revised.png and the plotted data to ./out/revised_values.csv, even if only the written answer changes.
- When finished, reply in exactly this format, with one line per issue in the reviewer's numbering:
CHANGES:
1. <fixed | kept | cannot address>: <what you changed, or why you kept it or could not address it>
2. ...
ANSWER: <the revised short written answer, based on the numbers you computed>
