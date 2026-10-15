import os
import numpy as np
import pandas as pd
import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.makedirs("out", exist_ok=True)

df = duckdb.sql("""
SELECT year(crash_date) AS year,
       count(*) AS reported_crashes,
       sum(number_of_persons_injured) AS persons_injured,
       sum(number_of_persons_killed) AS persons_killed,
       sum(number_of_motorist_injured) AS motorist_injured,
       sum(number_of_motorist_killed) AS motorist_killed,
       sum(number_of_pedestrians_killed) AS pedestrian_killed,
       sum(number_of_cyclist_killed) AS cyclist_killed
FROM 'data/crashes.parquet'
WHERE crash_date BETWEEN DATE '2013-01-01' AND DATE '2025-12-31'
GROUP BY 1
ORDER BY 1
""").df()

base = float(df.loc[df.year == 2013, "motorist_killed"].iloc[0])
last = float(df.loc[df.year == 2025, "motorist_killed"].iloc[0])

# Miles driven is not in the data, so express risk as an index that holds VMT flat.
df["motorist_deaths_per_mile_index"] = df["motorist_killed"] / base * 100.0
df["motorist_deaths_per_1000_crashes"] = df["motorist_killed"] / df["reported_crashes"] * 1000

df.to_csv("out/revised_values.csv", index=False)

breakeven_pct = last / base * 100.0

fig, ax = plt.subplots(1, 2, figsize=(13, 5.5))

a = ax[0]
a.bar(df.year, df.motorist_killed, color="#4C72B0", label="Motorist deaths (occupants)")
a.plot(df.year, df.persons_killed, "o-", color="#C44E52", lw=1.5, ms=4,
       label="All road-user deaths")
a.annotate(f"{int(base)}", (2013, base), textcoords="offset points", xytext=(0, 8),
           ha="center", fontsize=10, fontweight="bold")
a.annotate(f"{int(last)}", (2025, last), textcoords="offset points", xytext=(0, 8),
           ha="center", fontsize=10, fontweight="bold")
a.set_title("Motor vehicle deaths per year, NYC (crash reports)")
a.set_ylabel("Deaths per year")
a.set_xticks(list(df.year))
a.tick_params(axis="x", rotation=60)
a.grid(axis="y", alpha=0.3)
a.legend(frameon=False, fontsize=9)

b = ax[1]
vmt = np.linspace(0.60, 1.20, 241)
risk = (last / base) / vmt * 100.0
b.plot(vmt * 100, risk, color="#4C72B0", lw=2,
       label="2025 risk vs 2013 risk (index)")
b.axhline(100, color="black", ls="--", lw=1, label="No change (100)")
b.axvspan(60, breakeven_pct, color="#C44E52", alpha=0.12,
          label="Risk above 2013 (decline fails)")
b.axvspan(breakeven_pct, 120, color="#55A868", alpha=0.12,
          label="Risk below 2013 (decline holds)")
b.axvline(breakeven_pct, color="black", ls=":", lw=1)
b.plot([100], [last / base * 100], "o", color="#C44E52", ms=8)
b.annotate(f"miles flat: {last/base*100:.0f}\n(risk -{100-last/base*100:.0f}%)",
           (100, last / base * 100), textcoords="offset points", xytext=(12, 6),
           fontsize=9, color="#C44E52")
b.plot([breakeven_pct], [100], "o", color="black", ms=7)
b.annotate(f"break-even\n{breakeven_pct:.0f}%", (breakeven_pct, 100),
           textcoords="offset points", xytext=(-8, -36), ha="right", fontsize=9)
b.set_title("2025 vs 2013 motorist risk per mile,\nfor different assumptions about miles driven")
b.set_xlabel("Miles driven in 2025 as % of 2013")
b.set_ylabel("Risk per mile, 2025 = % of 2013")
b.set_xlim(60, 120)
b.set_ylim(55, 180)
b.grid(alpha=0.3)
b.legend(frameon=False, fontsize=8, loc="upper right")

fig.suptitle("Did the risk of a motorist being killed per mile driven fall in NYC, 2013-2025?",
             fontsize=13, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig("out/revised.png", dpi=150)

print(df.to_string(index=False))
print(f"2013 motorist deaths: {base:.0f}, 2025: {last:.0f}, change: {last/base*100-100:.1f}%")
print(f"Break-even VMT ratio 2025/2013: {last/base:.3f}")
print(f"2013 rate/1000 crashes: {base/df.loc[df.year==2013,'reported_crashes'].iloc[0]*1000:.3f}, "
      f"2025: {last/df.loc[df.year==2025,'reported_crashes'].iloc[0]*1000:.3f}")

cr19 = df.loc[df.year == 2019, "reported_crashes"].iloc[0]
cr25 = df.loc[df.year == 2025, "reported_crashes"].iloc[0]
pi19 = df.loc[df.year == 2019, "persons_injured"].iloc[0]
pi25 = df.loc[df.year == 2025, "persons_injured"].iloc[0]
mi19 = df.loc[df.year == 2019, "motorist_injured"].iloc[0]
mi25 = df.loc[df.year == 2025, "motorist_injured"].iloc[0]
print(f"reported_crashes 2019->2025: {cr19:.0f}->{cr25:.0f} ({(cr25/cr19-1)*100:.1f}%)")
print(f"persons_injured 2019->2025: {pi19:.0f}->{pi25:.0f} ({(pi25/pi19-1)*100:.1f}%)")
print(f"motorist_injured 2019->2025: {mi19:.0f}->{mi25:.0f} ({(mi25/mi19-1)*100:.1f}%)")
