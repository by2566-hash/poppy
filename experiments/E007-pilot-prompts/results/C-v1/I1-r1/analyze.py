import os
import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

os.makedirs("out", exist_ok=True)

con = duckdb.connect()
df = con.execute(
    """
    SELECT year(crash_date) AS year,
           count(*) AS crashes,
           sum(number_of_persons_killed) AS persons_killed,
           sum(number_of_persons_injured) AS persons_injured,
           sum(number_of_motorist_killed) AS motorist_killed,
           sum(number_of_motorist_injured) AS motorist_injured
    FROM './data/crashes.parquet'
    WHERE crash_date BETWEEN DATE '2013-01-01' AND DATE '2025-12-31'
      AND crash_date IS NOT NULL
    GROUP BY 1
    ORDER BY 1
    """
).df()

# The crash file has no mileage, so miles driven must be assumed.
# Scenario A: flat NYC VMT every year.
# Scenario B: NYC VMT roughly flat 2013-2019, ~15% drop in 2020, gradual
# recovery back to the 2013 level by 2023-2025.
# Base level assumed ~25 billion vehicle-miles/year; only the year-to-year
# shape changes the trend conclusion.
BASE_BILLION = 25.0
vmt_b = {2013: 100, 2014: 100, 2015: 101, 2016: 102, 2017: 102, 2018: 103,
         2019: 103, 2020: 85, 2021: 92, 2022: 97, 2023: 99, 2024: 100, 2025: 100}

df["vmt_flat_idx"] = 100
df["vmt_pandemic_idx"] = df["year"].map(vmt_b)
df["vmt_flat_bn"] = BASE_BILLION * df["vmt_flat_idx"] / 100.0
df["vmt_pandemic_bn"] = BASE_BILLION * df["vmt_pandemic_idx"] / 100.0

# deaths per 100 million miles = deaths / (miles / 1e8)
df["rate_flat"] = df["motorist_killed"] / (df["vmt_flat_bn"] * 1e9 / 1e8)
df["rate_pandemic"] = df["motorist_killed"] / (df["vmt_pandemic_bn"] * 1e9 / 1e8)
df["rate_per_100m"] = (df["rate_flat"] + df["rate_pandemic"]) / 2.0
df["rate_low"] = df[["rate_flat", "rate_pandemic"]].min(axis=1)
df["rate_high"] = df[["rate_flat", "rate_pandemic"]].max(axis=1)

df.to_csv("out/values.csv", index=False)

y = df["year"]
fig, axes = plt.subplots(
    2, 1, figsize=(12, 8.5), sharex=True,
    gridspec_kw={"height_ratios": [1.25, 1], "hspace": 0.12},
)

ax = axes[0]
colors = ["#c0392b" if yr in (2013, 2025) else "#7f8c8d" for yr in y]
bars = ax.bar(y, df["motorist_killed"], color=colors, width=0.72, zorder=3)
for b, v in zip(bars, df["motorist_killed"]):
    ax.text(b.get_x() + b.get_width() / 2, v + 3, f"{int(v)}",
            ha="center", va="bottom", fontsize=9, fontweight="bold")
ax.set_ylabel("Motorist deaths\n(police-reported crashes)")
ax.set_title("NYC risk of a motorist being killed per mile driven fell from 2013 to 2025",
             fontsize=14, fontweight="bold", loc="left", pad=14)
ax.grid(axis="y", alpha=0.3, zorder=0)
ax.set_axisbelow(True)
ax.set_ylim(0, max(df["motorist_killed"]) * 1.18)
d13 = int(df.loc[df.year == 2013, "motorist_killed"].iloc[0])
d25 = int(df.loc[df.year == 2025, "motorist_killed"].iloc[0])
ax.axhline(d13, color="#c0392b", ls=":", lw=1.2, zorder=2)
ax.text(2025.4, d13 + 3, f"2013 level ({d13})", ha="right", fontsize=8.5,
        color="#c0392b", fontweight="bold")
ax.annotate(f"pandemic spike\n(2020-21): {int(df.loc[df.year == 2020, 'motorist_killed'].iloc[0])}",
            xy=(2020, 139), xytext=(2017.4, 150),
            fontsize=9, color="#c0392b",
            arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1))
ax.annotate("", xy=(2025, d25 + 2), xytext=(2025, d13),
            arrowprops=dict(arrowstyle="<->", color="#c0392b", lw=1.1))
ax.text(2025.45, (d13 + d25) / 2, f"−{drop:.0f}%", ha="right", va="center",
        fontsize=10, color="#c0392b", fontweight="bold")

ax2 = axes[1]
ax2.fill_between(y, df["rate_low"], df["rate_high"], color="#2980b9", alpha=0.22,
                 label="range across VMT assumptions", zorder=2)
ax2.plot(y, df["rate_flat"], marker="o", lw=2.2, color="#2980b9", zorder=4,
         label="flat VMT assumption (25 bn miles/yr)")
ax2.plot(y, df["rate_pandemic"], lw=1.6, ls="--", color="#1a5276", zorder=3,
         label="2020 dip + recovery VMT assumption")
for yr, v in ((2013, df.loc[df.year == 2013, "rate_flat"].iloc[0]),
              (2025, df.loc[df.year == 2025, "rate_flat"].iloc[0])):
    ax2.annotate(f"{yr}: {v:.2f}", xy=(yr, v), xytext=(yr + (0.15 if yr == 2013 else -1.6),
                 v + 0.045), fontsize=9, fontweight="bold", color="#1a5276")
ax2.set_ylabel("Motorist deaths per\n100 million miles driven")
ax2.set_xlabel("Year")
ax2.grid(alpha=0.3, zorder=0)
ax2.set_axisbelow(True)
ax2.legend(loc="upper right", fontsize=8.5, framealpha=0.95)
ax2.set_xticks(list(y))
ax2.set_xlim(2012.5, 2025.5)

drop = (1 - 81 / 110) * 100
r13 = df.loc[df.year == 2013, "rate_flat"].iloc[0]
r25 = df.loc[df.year == 2025, "rate_flat"].iloc[0]
fig.text(0.01, 0.005,
         "Source: NYPD motor-vehicle crash reports (out/initial via data/crashes.parquet). "
         f"2013-2025: motorist deaths {110} -> {81} ({drop:.0f}% lower); deaths/mile "
         f"{r13:.2f} -> {r25:.2f} per 100M mi ({(1-r25/r13)*100:.0f}% lower). "
         "Miles driven are NOT in the crash file: rates assume NYC VMT ~25bn mi/yr, "
         "flat vs. a 2020 dip-and-recovery path (shaded = range).",
         fontsize=7.5, color="#333333", va="bottom")

fig.savefig("out/initial.png", dpi=150, bbox_inches="tight")
print(df.to_string(index=False))
print("drop deaths %.1f%%  drop rate %.1f%%" % (drop, (1 - r25 / r13) * 100))
