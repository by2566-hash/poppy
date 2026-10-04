import duckdb
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

P = "./data/crashes.parquet"
OUT = "./out"
FULL = "year(crash_date) between 2013 and 2025"

con = duckdb.connect()

annual = con.sql(f"""
select year(crash_date) as yr,
       count(*) as crashes,
       sum(number_of_cyclist_injured)   as ci, sum(number_of_cyclist_killed)   as ck,
       sum(number_of_pedestrians_injured) as pi, sum(number_of_pedestrians_killed) as pk,
       sum(number_of_motorist_injured)  as mi, sum(number_of_motorist_killed)  as mk,
       100.0 * sum(case when number_of_persons_injured = 0 and number_of_persons_killed = 0
                        then 1 else 0 end) / count(*) as pct_no_injury
from '{P}' where {FULL} group by 1 order by 1
""").df()

annual["inj_tot"] = annual.ci + annual.pi + annual.mi
annual["fat_tot"] = annual.ck + annual.pk + annual.mk
annual["cyc_inj_share"] = 100 * annual.ci / annual.inj_tot
annual["cyc_fat_share"] = 100 * annual.ck / annual.fat_tot
for col, pref in [("cyc", "ci"), ("ped", "pi"), ("mot", "mi")]:
    annual[f"{col}_fatal_rate"] = 1000 * annual[("ck" if col == "cyc" else "pk" if col == "ped" else "mk")] / annual[pref]

window = con.sql(f"""
select year(crash_date) as yr, count(distinct crash_date) as ndays,
       sum(number_of_cyclist_injured) as ci, sum(number_of_cyclist_killed) as ck
from '{P}' where month(crash_date) between 1 and 6 and year(crash_date) between 2013 and 2026
group by 1 order by 1
""").df()
window["per_day"] = window.ci / window.ndays

trailing = con.sql(f"""
select case when crash_date >= date '2025-06-12' then 'Jun 2025 - Jun 2026'
            when crash_date >= date '2024-06-12' then 'Jun 2024 - Jun 2025'
            when crash_date >= date '2013-06-12' and crash_date < date '2014-06-12' then 'Jun 2013 - Jun 2014'
       end as grp,
       count(distinct crash_date) as ndays,
       sum(number_of_cyclist_injured) as ci, sum(number_of_cyclist_killed) as ck
from '{P}'
where (crash_date >= date '2025-06-12')
   or (crash_date >= date '2024-06-12' and crash_date < date '2025-06-12')
   or (crash_date >= date '2013-06-12' and crash_date < date '2014-06-12')
group by 1 order by 1
""").df()
trailing["per_day"] = trailing.ci / trailing.ndays

borough = con.sql(f"""
select borough,
  sum(case when year(crash_date) between 2013 and 2019 then number_of_cyclist_injured else 0 end) / 7.0 as pre,
  sum(case when year(crash_date) between 2023 and 2025 then number_of_cyclist_injured else 0 end) / 3.0 as post
from '{P}' where borough <> '' group by 1
""").df()
borough["pct"] = 100 * (borough.post / borough.pre - 1)
borough = borough.sort_values("pct", ascending=True)

plt.rcParams.update({
    "figure.dpi": 130, "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "grid.linestyle": "-",
})
SOURCE = "Source: NYC Open Data / NYPD Motor Vehicle Collisions - Crashes (h9gi-nx95), 2013-2025"

# 1. Absolute counts by mode
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(annual.yr, annual.ci, marker="o", lw=2.2, color="#d62728", label="Cyclists injured")
ax.plot(annual.yr, annual.pi, marker="o", lw=2.2, color="#1f77b4", label="Pedestrians injured")
ax.plot(annual.yr, annual.mi, marker="o", lw=2.2, color="#7f7f7f", label="Motorists injured")
for x, y in [(2019, annual.loc[annual.yr == 2019, "ci"].iloc[0]),
             (2025, annual.loc[annual.yr == 2025, "ci"].iloc[0])]:
    ax.annotate(f"{int(y):,}", (x, y), textcoords="offset points", xytext=(0, -16),
                ha="center", color="#d62728", fontweight="bold")
ax.set_title("People injured in NYC traffic crashes, by mode")
ax.set_ylabel("Annual injuries")
ax.set_xticks(annual.yr)
ax.tick_params(axis="x", rotation=45)
ax.legend(frameon=False)
ax.text(0, -0.22, SOURCE, transform=ax.transAxes, fontsize=7.5, color="#555")
fig.tight_layout()
fig.savefig(f"{OUT}/01_injuries_by_mode.png", bbox_inches="tight")
plt.close(fig)

# 2. Indexed trend
fig, ax = plt.subplots(figsize=(9, 5))
base = annual.yr == 2013
for col, label, color in [("ci", "Cyclists", "#d62728"), ("pi", "Pedestrians", "#1f77b4"),
                          ("mi", "Motorists", "#7f7f7f")]:
    ax.plot(annual.yr, 100 * annual[col] / annual.loc[base, col].iloc[0],
            marker="o", lw=2.2, color=color, label=label)
ax.axhline(100, color="black", lw=1, ls="--", alpha=0.6)
ax.set_title("Injuries indexed to 2013 = 100")
ax.set_ylabel("Index (2013 = 100)")
ax.set_xticks(annual.yr)
ax.tick_params(axis="x", rotation=45)
ax.legend(frameon=False)
ax.text(0, -0.22, SOURCE, transform=ax.transAxes, fontsize=7.5, color="#555")
fig.tight_layout()
fig.savefig(f"{OUT}/02_injuries_indexed.png", bbox_inches="tight")
plt.close(fig)

# 3. Cyclist share of injuries and deaths
fig, ax = plt.subplots(figsize=(9, 5))
ax.bar(annual.yr, annual.cyc_inj_share, color="#d62728", alpha=0.35, label="Share of all people injured")
ax.plot(annual.yr, annual.cyc_fat_share, marker="o", lw=2.2, color="#d62728",
        label="Share of all people killed")
for yr in (2013, 2025):
    r = annual[annual.yr == yr].iloc[0]
    ax.annotate(f"{r.cyc_inj_share:.1f}%", (yr, r.cyc_inj_share), textcoords="offset points",
                xytext=(0, 4), ha="center", fontsize=9, color="#d62728")
ax.set_title("Cyclists as a share of all NYC traffic crash casualties")
ax.set_ylabel("Percent")
ax.set_xticks(annual.yr)
ax.tick_params(axis="x", rotation=45)
ax.legend(frameon=False)
ax.text(0, -0.22, SOURCE, transform=ax.transAxes, fontsize=7.5, color="#555")
fig.tight_layout()
fig.savefig(f"{OUT}/03_cyclist_share.png", bbox_inches="tight")
plt.close(fig)

# 4. Fatality rate per 1000 injuries, 3-year rolling
fig, ax = plt.subplots(figsize=(9, 5))
for col, label, color in [("cyc_fatal_rate", "Cyclists", "#d62728"),
                          ("ped_fatal_rate", "Pedestrians", "#1f77b4"),
                          ("mot_fatal_rate", "Motorists", "#7f7f7f")]:
    ax.plot(annual.yr, annual[col].rolling(3).mean(), marker="o", lw=2.2, color=color, label=label)
ax.set_title("Deaths per 1,000 injuries (3-year rolling average)")
ax.set_ylabel("Deaths per 1,000 injuries")
ax.set_xticks(annual.yr)
ax.tick_params(axis="x", rotation=45)
ax.legend(frameon=False)
ax.text(0, -0.22, SOURCE + " | 2015 is first 3-year average", transform=ax.transAxes,
        fontsize=7.5, color="#555")
fig.tight_layout()
fig.savefig(f"{OUT}/04_fatality_rate.png", bbox_inches="tight")
plt.close(fig)

# 5. Reporting caveat
fig, ax = plt.subplots(figsize=(9, 5))
ax.bar(annual.yr, annual.crashes, color="#bbbbbb", label="Crashes reported")
ax.set_ylabel("Crashes reported")
ax2 = ax.twinx()
ax2.plot(annual.yr, annual.pct_no_injury, marker="o", lw=2.2, color="#ff7f0e",
         label="Share with nobody hurt")
ax2.set_ylabel("% of crashes with nobody injured or killed")
ax2.grid(False)
ax.set_title("Why crash counts can't be compared over time")
ax.set_xticks(annual.yr)
ax.tick_params(axis="x", rotation=45)
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, frameon=False, loc="lower left")
ax.text(0, -0.22, SOURCE, transform=ax.transAxes, fontsize=7.5, color="#555")
fig.tight_layout()
fig.savefig(f"{OUT}/05_reporting_change.png", bbox_inches="tight")
plt.close(fig)

# 6. H1 daily rate + borough change
fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
a = axes[0]
a.plot(window.yr, window.per_day, marker="o", lw=2.2, color="#d62728")
a.axvspan(2025.6, 2026.5, color="#ffd9d9", alpha=0.7)
a.annotate(f"2026 (Jan 1-Jun 11): {window.per_day.iloc[-1]:.1f}/day",
           (2026, window.per_day.iloc[-1]), textcoords="offset points", xytext=(-4, -28),
           ha="right", fontsize=8.5, color="#a00")
a.annotate(f"2013: {window.per_day.iloc[0]:.1f}/day", (2013, window.per_day.iloc[0]),
           textcoords="offset points", xytext=(8, -16), fontsize=8.5, color="#a00")
a.set_ylim(8.0, 13.4)
a.set_title("Cyclist injuries per day, Jan-Jun window")
a.set_ylabel("Injuries per day")
a.set_xticks(window.yr)
a.tick_params(axis="x", rotation=45)
b = axes[1]
colors = ["#d62728" if v > 0 else "#2ca02c" for v in borough.pct]
b.barh(borough.borough, borough.pct, color=colors)
b.axvline(0, color="black", lw=1)
for i, v in enumerate(borough.pct):
    b.text(v + (1.5 if v > 0 else -1.5), i, f"{v:+.0f}%", va="center",
           ha="left" if v > 0 else "right", fontsize=9)
b.set_xlim(-15, 60)
b.set_title("Change in avg annual cyclist injuries\n(2013-19 vs 2023-25)")
b.set_xlabel("% change")
fig.tight_layout()
fig.savefig(f"{OUT}/06_recent_rate_and_boroughs.png", bbox_inches="tight")
plt.close(fig)

print("Charts written to", OUT)
print(annual[["yr", "ci", "ck", "cyc_inj_share", "cyc_fat_share", "cyc_fatal_rate"]].round(2).to_string(index=False))
print(window.round(2).to_string(index=False))
print(trailing.round(2).to_string(index=False))
