import numpy as np
import pandas as pd
import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

PARQUET = "./data/crashes.parquet"
OUT = Path("./out")
OUT.mkdir(exist_ok=True)

NIGHT_HOURS = {22, 23, 0, 1, 2, 3, 4, 5}

con = duckdb.connect()
rows = con.execute(f"""
    SELECT year(crash_date) AS yr, month(crash_date) AS mo, dayofweek(crash_date) AS dow,
           hour(crash_time) AS h,
           number_of_persons_injured AS inj, number_of_persons_killed AS kil,
           number_of_pedestrians_killed AS pedk,
           (contributing_factor_vehicle_1 = 'Alcohol Involvement') AS alc
    FROM '{PARQUET}'
    WHERE number_of_persons_injured IS NOT NULL
      AND number_of_persons_killed IS NOT NULL
""").df()

assert rows["inj"].notna().all() and rows["kil"].notna().all()
rows["band"] = np.where(rows["h"].isin(NIGHT_HOURS), "night", "day")


def summarize(df):
    n = len(df)
    if n == 0:
        return dict(crashes=0, persons_injured=0, persons_killed=0,
                    injuries_per_1000_crashes=np.nan, deaths_per_100000_crashes=np.nan,
                    pct_crashes_with_injury_or_death=np.nan, pct_alcohol_factor=np.nan)
    inj, kil = int(df["inj"].sum()), int(df["kil"].sum())
    return dict(
        crashes=n,
        persons_injured=inj,
        persons_killed=kil,
        injuries_per_1000_crashes=inj / n * 1000,
        deaths_per_100000_crashes=kil / n * 100000,
        pct_crashes_with_injury_or_death=100.0 * ((df["inj"] > 0) | (df["kil"] > 0)).sum() / n,
        pct_alcohol_factor=100.0 * df["alc"].mean(),
    )


records = []
for h in range(24):
    records.append({"slice": "hour", "label": f"{h:02d}:00-{h:02d}:59", **summarize(rows[rows["h"] == h])})
for name, mask in [("night", rows["band"] == "night"), ("day", rows["band"] == "day")]:
    records.append({"slice": "band", "label": name, **summarize(rows[mask])})
records.append({"slice": "band", "label": "all", **summarize(rows)})

rows["era"] = pd.cut(rows["yr"], bins=[2011, 2015, 2019, 2022, 2026],
                     labels=["2012-2015", "2016-2019", "2020-2022", "2023-2026"])
rows["dow_band"] = np.where(rows["dow"].isin([0, 6]), "weekend", "weekday")
for era, sub in rows.groupby("era", observed=True):
    for band in ["night", "day"]:
        records.append({"slice": "era", "label": f"{era}_{band}",
                        **summarize(sub[sub["band"] == band])})
for d, sub in rows.groupby("dow_band"):
    for band in ["night", "day"]:
        records.append({"slice": "daytype", "label": f"{d}_{band}",
                        **summarize(sub[sub["band"] == band])})

vals = pd.DataFrame(records)
vals.to_csv(OUT / "values.csv", index=False, float_format="%.2f")

hourly = vals[vals["slice"] == "hour"].copy()
band = vals[vals["slice"] == "band"].set_index("label")
night, day, allh = band.loc["night"], band.loc["day"], band.loc["all"]

fig = plt.figure(figsize=(13, 9))
gs = fig.add_gridspec(2, 2, height_ratios=[1, 1], hspace=0.42, wspace=0.22)

ax = fig.add_subplot(gs[0, :])
x = np.arange(24)
colors = ["#c0392b" if h in NIGHT_HOURS else "#34495e" for h in range(24)]
ax.bar(x, hourly["crashes"], color=colors, width=0.78, zorder=3)
ax.axvspan(-0.5, 5.5, color="#f6d55c", alpha=0.25, zorder=0)
ax.axvspan(21.5, 23.5, color="#f6d55c", alpha=0.25, zorder=0)
ax.text(2.5, hourly["crashes"].max() * 0.92, "NIGHT  10 p.m.–5:59 a.m.",
        ha="center", fontsize=10, color="#8a6d0b", fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels([f"{h}" for h in range(24)])
ax.set_xlabel("Hour crash was reported (local clock time)")
ax.set_ylabel("Crashes per hour")
peak_h = int(hourly["crashes"].idxmax())
ax.set_title("A. Where NYC's crashes happen: overwhelmingly in the daytime\n"
             f"({night['crashes']/allh['crashes']*100:.0f}% of crashes fall in the 8-hour night window; "
             f"busiest hour is {peak_h}:00–{peak_h}:59)", fontsize=11, loc="left")
ax.grid(axis="y", alpha=0.3, zorder=0)

ax2 = fig.add_subplot(gs[1, 0])
ax2.plot(x, hourly["injuries_per_1000_crashes"], marker="o", ms=5, lw=2, color="#2c6fbb", zorder=3)
ax2.axvspan(-0.5, 5.5, color="#f6d55c", alpha=0.25, zorder=0)
ax2.axvspan(21.5, 23.5, color="#f6d55c", alpha=0.25, zorder=0)
ax2.set_xticks(x[::2])
ax2.set_xticklabels([f"{h}" for h in range(24)][::2])
ax2.set_xlabel("Hour crash was reported")
ax2.set_ylabel("People injured per 1,000 crashes")
ax2.set_ylim(0, 480)
ax2.set_title("B. A night crash tends to injure more people\n"
              f"injured per 1,000 crashes: night {night['injuries_per_1000_crashes']:.0f} vs "
              f"day {day['injuries_per_1000_crashes']:.0f}", fontsize=10, loc="left")
ax2.grid(alpha=0.3, zorder=0)

ax3 = fig.add_subplot(gs[1, 1])
ax3.plot(x, hourly["deaths_per_100000_crashes"], marker="o", ms=5, lw=2, color="#c0392b", zorder=3)
ax3.axvspan(-0.5, 5.5, color="#f6d55c", alpha=0.25, zorder=0)
ax3.axvspan(21.5, 23.5, color="#f6d55c", alpha=0.25, zorder=0)
ax3.set_xticks(x[::2])
ax3.set_xticklabels([f"{h}" for h in range(24)][::2])
ax3.set_xlabel("Hour crash was reported")
ax3.set_ylabel("People killed per 100,000 crashes")
ax3.set_title("C. The deadliest crashes are pre-dawn: a 4 a.m. crash is ~7x\n"
              f"as likely to kill as a 4 p.m. crash (night {night['deaths_per_100000_crashes']:.0f} vs "
              f"day {day['deaths_per_100000_crashes']:.0f} deaths/100,000 crashes)", fontsize=10, loc="left")
ax3.grid(alpha=0.3, zorder=0)

fig.suptitle("NYC streets are quieter at night — and far more lethal per crash",
             fontsize=15, fontweight="bold", x=0.01, ha="left", y=0.985)
fig.text(0.01, 0.015,
         "Source: NYPD motor-vehicle collisions, 2012-07-01 to 2026-06-11 (2.26M crashes with complete injury/fatality counts). "
         "Rates are per crash recorded, not per mile driven.\n"
         "Counts of crashes cannot measure risk per trip: the file holds no traffic-volume data. "
         "Yellow bands mark 10 p.m.–5:59 a.m. by clock time (actual darkness varies by season).",
         fontsize=8.5, color="#444444")
fig.subplots_adjust(top=0.86, bottom=0.10)
fig.savefig(OUT / "initial.png", dpi=150)

print(vals[vals["slice"].isin(["hour", "band"])].to_string(index=False))
print()
print(night.to_dict())
print(day.to_dict())
print(f"night crash share {night['crashes']/allh['crashes']*100:.1f}%, "
      f"night death share {night['persons_killed']/allh['persons_killed']*100:.1f}%")
