import os
import duckdb
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.makedirs("./out", exist_ok=True)
SRC = "./data/crashes.parquet"

con = duckdb.connect()

distinct_days = con.sql(
    f"SELECT COUNT(DISTINCT crash_date) FROM '{SRC}'"
).fetchone()[0]

hourly = con.sql(f"""
    SELECT
        date_part('hour', crash_time)::INT                       AS hour,
        COUNT(*)                                                 AS crashes,
        SUM(number_of_persons_injured)                           AS persons_injured,
        SUM(number_of_persons_killed)                            AS persons_killed,
        COUNT(*) FILTER (WHERE number_of_persons_injured > 0)    AS crashes_with_injury,
        COUNT(*) FILTER (WHERE number_of_persons_killed > 0)     AS fatal_crashes
    FROM '{SRC}'
    GROUP BY 1
    ORDER BY 1
""").df()

hourly["crashes"] = hourly["crashes"].astype(int)
hourly["persons_injured"] = hourly["persons_injured"].astype(int)
hourly["persons_killed"] = hourly["persons_killed"].astype(int)
hourly["inj_per_100_crashes"] = 100 * hourly["persons_injured"] / hourly["crashes"]
hourly["deaths_per_1000_crashes"] = 1000 * hourly["persons_killed"] / hourly["crashes"]
hourly["pct_crashes_with_injury"] = 100 * hourly["crashes_with_injury"] / hourly["crashes"]

# Time bands: night = 9pm-5:59am (the hours when crash counts are low but severity is high)
def band(h):
    if 6 <= h <= 9:
        return "Morning rush (6-9:59)"
    if 10 <= h <= 15:
        return "Midday (10am-3:59)"
    if 16 <= h <= 20:
        return "Evening (4-8:59)"
    return "Night (9pm-5:59)"

hourly["band"] = hourly["hour"].map(band)

bands = (
    hourly.groupby("band", as_index=False)
    .agg(
        hours=("hour", "nunique"),
        crashes=("crashes", "sum"),
        persons_injured=("persons_injured", "sum"),
        persons_killed=("persons_killed", "sum"),
        crashes_with_injury=("crashes_with_injury", "sum"),
        fatal_crashes=("fatal_crashes", "sum"),
    )
)
bands["crashes_per_day"] = bands["crashes"] / distinct_days
bands["inj_per_100_crashes"] = 100 * bands["persons_injured"] / bands["crashes"]
bands["deaths_per_1000_crashes"] = 1000 * bands["persons_killed"] / bands["crashes"]
bands["pct_crashes_with_injury"] = 100 * bands["crashes_with_injury"] / bands["crashes"]
bands["share_of_all_crashes_pct"] = 100 * bands["crashes"] / bands["crashes"].sum()

order = [
    "Morning rush (6-9:59)",
    "Midday (10am-3:59)",
    "Evening (4-8:59)",
    "Night (9pm-5:59)",
]
bands["ord"] = bands["band"].map({b: i for i, b in enumerate(order)})
bands = bands.sort_values("ord").drop(columns="ord").reset_index(drop=True)

# Day vs night two-way summary for the headline number
day = bands[bands["band"] != "Night (9pm-5:59)"].sum(numeric_only=True)
night = bands[bands["band"] == "Night (9pm-5:59)"].sum(numeric_only=True)

summary = pd.DataFrame(
    [
        {
            "period": "Day (6am-8:59pm)",
            "hours_per_day": 15,
            "crashes": int(day["crashes"]),
            "persons_injured": int(day["persons_injured"]),
            "persons_killed": int(day["persons_killed"]),
            "inj_per_100_crashes": 100 * day["persons_injured"] / day["crashes"],
            "deaths_per_1000_crashes": 1000 * day["persons_killed"] / day["crashes"],
            "pct_crashes_with_injury": 100 * day["crashes_with_injury"] / day["crashes"],
        },
        {
            "period": "Night (9pm-5:59am)",
            "hours_per_day": 9,
            "crashes": int(night["crashes"]),
            "persons_injured": int(night["persons_injured"]),
            "persons_killed": int(night["persons_killed"]),
            "inj_per_100_crashes": 100 * night["persons_injured"] / night["crashes"],
            "deaths_per_1000_crashes": 1000 * night["persons_killed"] / night["crashes"],
            "pct_crashes_with_injury": 100 * night["crashes_with_injury"] / night["crashes"],
        },
    ]
)
summary["crashes_per_day"] = summary["crashes"] / distinct_days
summary["deaths_per_year"] = summary["persons_killed"] / (distinct_days / 365.25)

# hourly CSV (main plotted data), plus band and summary blocks
hourly_out = hourly[
    [
        "hour",
        "band",
        "crashes",
        "persons_injured",
        "persons_killed",
        "crashes_with_injury",
        "fatal_crashes",
        "inj_per_100_crashes",
        "deaths_per_1000_crashes",
        "pct_crashes_with_injury",
    ]
].copy()
hourly_out.to_csv("./out/values.csv", index=False)
bands.to_csv("./out/values_by_time_of_day.csv", index=False)
summary.to_csv("./out/values_day_night.csv", index=False)

# ---------------- chart ----------------
fig, axes = plt.subplots(3, 1, figsize=(11, 11), sharex=True)

night_mask = (hourly["hour"] >= 21) | (hourly["hour"] <= 5)
colors = ["#4C78A8" if not n else "#22314e" for n in night_mask]

# Panel 1: crash volume
ax = axes[0]
ax.bar(hourly["hour"], hourly["crashes"] / 1000.0, color=colors, width=0.85)
ax.set_title(
    "1. Most crashes happen in daylight rush hour — volume, not danger",
    fontsize=12, loc="left", fontweight="bold",
)
ax.set_ylabel("Crashes (thousands)")
ax.text(0.995, 0.92, "dark bars / shaded region = night (9pm-5:59am)",
        transform=ax.transAxes, fontsize=9, ha="right", color="#22314e")

# Panel 2: deaths per 1,000 crashes
ax = axes[1]
ax.bar(hourly["hour"], hourly["deaths_per_1000_crashes"], color=colors, width=0.85)
avg = hourly["persons_killed"].sum() * 1000.0 / hourly["crashes"].sum()
ax.axhline(avg, color="#c44e52", ls="--", lw=1.5)
ax.text(0.01, 0.92, f"Citywide average: {avg:.2f} deaths per 1,000 crashes",
        transform=ax.transAxes, fontsize=9, color="#c44e52")
ax.set_title(
    "2. But each crash is far more lethal at night — deaths per 1,000 crashes",
    fontsize=12, loc="left", fontweight="bold",
)
ax.set_ylabel("Deaths per 1,000 crashes")
ax.set_ylim(0, hourly["deaths_per_1000_crashes"].max() * 1.25)

# annotate worst hours
worst = hourly.nlargest(3, "deaths_per_1000_crashes")
for _, r in worst.iterrows():
    ax.annotate(
        f"{int(r['hour']):02d}:00\n{r['deaths_per_1000_crashes']:.2f}",
        (r["hour"], r["deaths_per_1000_crashes"]),
        textcoords="offset points", xytext=(0, 6),
        ha="center", fontsize=8.5, color="#22314e", fontweight="bold",
    )

# Panel 3: injuries per 100 crashes
ax = axes[2]
ax.bar(hourly["hour"], hourly["inj_per_100_crashes"], color=colors, width=0.85)
avg_inj = hourly["persons_injured"].sum() * 100.0 / hourly["crashes"].sum()
ax.axhline(avg_inj, color="#c44e52", ls="--", lw=1.5)
ax.text(0.01, 0.92, f"Citywide average: {avg_inj:.1f} people injured per 100 crashes",
        transform=ax.transAxes, fontsize=9, color="#c44e52")
ax.set_title(
    "3. Injuries per crash also rise after dark",
    fontsize=12, loc="left", fontweight="bold",
)
ax.set_ylabel("People injured per 100 crashes")
ax.set_xlabel("Hour of day (crash time)")
ax.set_xticks(range(0, 24))
ax.set_xticklabels([f"{h:02d}" for h in range(0, 24)])
ax.set_xlim(-0.7, 23.7)

# night shading across all panels
for a in axes:
    a.axvspan(-0.7, 5.5, color="#22314e", alpha=0.07, zorder=0)
    a.axvspan(20.5, 23.7, color="#22314e", alpha=0.07, zorder=0)
    a.grid(axis="y", alpha=0.25)
    a.set_axisbelow(True)

fig.suptitle(
    "Are NYC's streets more dangerous at night?",
    fontsize=16, fontweight="bold", x=0.01, ha="left", y=0.985,
)
n = summary[summary["period"].str.startswith("Night")].iloc[0]
d = summary[summary["period"].str.startswith("Day")].iloc[0]
fig.text(
    0.01, 0.945,
    f"Night (9pm-6am): {n['deaths_per_1000_crashes']:.2f} deaths per 1,000 crashes vs "
    f"{d['deaths_per_1000_crashes']:.2f} in daytime  |  "
    f"{n['inj_per_100_crashes']:.1f} vs {d['inj_per_100_crashes']:.1f} injuries per 100 crashes  |  "
    f"{n['deaths_per_1000_crashes'] / d['deaths_per_1000_crashes']:.1f}x the death risk per crash",
    fontsize=11, color="#333333",
)
fig.text(
    0.01, 0.015,
    "Source: NYPD motor-vehicle collisions, Jul 2012-Jun 2026 (2,269,187 crashes). "
    "Severity rates are per crash reported, not per mile driven: exposure (traffic volume) is not in the data.",
    fontsize=8.5, color="#666666",
)
fig.tight_layout(rect=[0, 0.03, 1, 0.93])
fig.savefig("./out/initial.png", dpi=150)
print("saved ./out/initial.png")
print(summary.to_string(index=False))
print()
print(bands.to_string(index=False))
print()
print(hourly[["hour", "crashes", "deaths_per_1000_crashes", "inj_per_100_crashes"]].to_string(index=False))
