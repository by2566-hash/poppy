import os

import duckdb
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter


os.makedirs("out", exist_ok=True)
db = duckdb.connect()
data = db.execute(
    """
    SELECT
        year(crash_date) AS year,
        sum(coalesce(number_of_pedestrians_injured, 0))::BIGINT AS pedestrian_injured,
        sum(coalesce(number_of_pedestrians_killed, 0))::BIGINT AS pedestrian_killed,
        sum(coalesce(number_of_pedestrians_injured, 0)
            + coalesce(number_of_pedestrians_killed, 0))::BIGINT AS pedestrian_casualties,
        count(*)::BIGINT AS brooklyn_crashes,
        count(*) FILTER (
            WHERE coalesce(number_of_pedestrians_injured, 0)
                + coalesce(number_of_pedestrians_killed, 0) > 0
        )::BIGINT AS crashes_with_pedestrian_casualty
    FROM read_parquet('data/crashes.parquet')
    WHERE upper(borough) = 'BROOKLYN'
      AND year(crash_date) BETWEEN 2013 AND 2025
    GROUP BY 1
    ORDER BY 1
    """
).df()
data["pedestrian_casualty_crash_pct"] = (
    100 * data.crashes_with_pedestrian_casualty / data.brooklyn_crashes
)
assert list(data.year) == list(range(2013, 2026))

data[
    ["year", "pedestrian_injured", "pedestrian_killed", "pedestrian_casualties"]
].to_csv("out/values_1.csv", index=False)
data[["year", "pedestrian_killed"]].to_csv("out/values_2.csv", index=False)
data[
    [
        "year",
        "crashes_with_pedestrian_casualty",
        "brooklyn_crashes",
        "pedestrian_casualty_crash_pct",
    ]
].to_csv("out/values_3.csv", index=False)

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titleweight": "bold",
        "axes.titlesize": 16,
        "axes.labelsize": 11,
    }
)
years = data.year

fig, ax = plt.subplots(figsize=(10.5, 6.1))
ax.plot(years, data.pedestrian_casualties, color="#176b87", lw=3, marker="o", ms=5)
ax.fill_between(years, data.pedestrian_casualties, color="#176b87", alpha=0.10)
ax.set_title("Brooklyn pedestrian injuries and deaths fell—then climbed", loc="left", pad=17)
ax.text(
    0,
    1.015,
    "People hurt or killed in police-reported crashes | 2013–2025",
    transform=ax.transAxes,
    color="#555",
    fontsize=10,
)
ax.set_ylabel("Pedestrians injured or killed (people)")
ax.set_xlabel("Crash year")
ax.set_xticks(years)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v):,}"))
ax.grid(axis="y", alpha=0.22)
ax.annotate(
    f"{int(data.pedestrian_casualties.iloc[0]):,}",
    (2013, data.pedestrian_casualties.iloc[0]),
    xytext=(0, 12),
    textcoords="offset points",
    ha="center",
    fontweight="bold",
)
low = data.pedestrian_casualties.idxmin()
ax.annotate(
    f"2020 low: {int(data.loc[low, 'pedestrian_casualties']):,}",
    (int(data.loc[low, "year"]), data.loc[low, "pedestrian_casualties"]),
    xytext=(8, -23),
    textcoords="offset points",
    fontsize=9,
    color="#444",
)
ax.annotate(
    f"2025: {int(data.pedestrian_casualties.iloc[-1]):,}",
    (2025, data.pedestrian_casualties.iloc[-1]),
    xytext=(-7, 12),
    textcoords="offset points",
    ha="right",
    fontweight="bold",
)
fig.text(
    0.01,
    0.01,
    "Source: NYC police-reported motor vehicle crash records. Counts are not adjusted for pedestrian trips or exposure.",
    fontsize=8,
    color="#555",
)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig("out/option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(10.5, 6.1))
colors = ["#c74e4e" if y in (2013, 2025) else "#d9a09a" for y in years]
bars = ax.bar(years, data.pedestrian_killed, color=colors, width=0.72)
ax.set_title("Brooklyn pedestrian deaths remain above 2013", loc="left", pad=17)
ax.text(
    0,
    1.015,
    "Pedestrians killed in police-reported crashes | 2013–2025",
    transform=ax.transAxes,
    color="#555",
    fontsize=10,
)
ax.set_ylabel("Pedestrian deaths (people)")
ax.set_xlabel("Crash year")
ax.set_xticks(years)
ax.grid(axis="y", alpha=0.22)
ax.set_axisbelow(True)
ax.bar_label(bars, padding=3, fontsize=9)
ax.set_ylim(0, max(data.pedestrian_killed) * 1.18)
fig.text(
    0.01,
    0.01,
    "Source: NYC police-reported motor vehicle crash records. Death counts are not rates per pedestrian trip.",
    fontsize=8,
    color="#555",
)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig("out/option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(10.5, 6.1))
ax.plot(
    years,
    data.pedestrian_casualty_crash_pct,
    color="#a64b26",
    lw=3,
    marker="o",
    ms=5,
)
ax.fill_between(years, data.pedestrian_casualty_crash_pct, color="#a64b26", alpha=0.10)
ax.set_title(
    "Pedestrian casualties make up a larger share of Brooklyn crashes", loc="left", pad=17
)
ax.text(
    0,
    1.015,
    "Brooklyn crash reports with a pedestrian injured or killed | 2013–2025",
    transform=ax.transAxes,
    color="#555",
    fontsize=10,
)
ax.set_ylabel("Share of all Brooklyn crash reports (%)")
ax.set_xlabel("Crash year")
ax.set_xticks(years)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
ax.grid(axis="y", alpha=0.22)
ax.annotate(
    f"{data.pedestrian_casualty_crash_pct.iloc[0]:.2f}%",
    (2013, data.pedestrian_casualty_crash_pct.iloc[0]),
    xytext=(4, -19),
    textcoords="offset points",
    ha="left",
    fontweight="bold",
)
ax.annotate(
    f"{data.pedestrian_casualty_crash_pct.iloc[-1]:.2f}%",
    (2025, data.pedestrian_casualty_crash_pct.iloc[-1]),
    xytext=(-4, 11),
    textcoords="offset points",
    ha="right",
    fontweight="bold",
)
fig.text(
    0.01,
    0.01,
    "Source: NYC police-reported motor vehicle crash records. This is a share of crashes, not pedestrian exposure-based risk.",
    fontsize=8,
    color="#555",
)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig("out/option_3.png", dpi=180, bbox_inches="tight")
plt.close(fig)

print(data.to_string(index=False))
print(
    "2013 to 2025 casualties change %:",
    (data.pedestrian_casualties.iloc[-1] / data.pedestrian_casualties.iloc[0] - 1) * 100,
)
print(
    "2013 to 2025 deaths change %:",
    (data.pedestrian_killed.iloc[-1] / data.pedestrian_killed.iloc[0] - 1) * 100,
)
print(
    "2013 to 2025 share relative change %:",
    (
        data.pedestrian_casualty_crash_pct.iloc[-1]
        / data.pedestrian_casualty_crash_pct.iloc[0]
        - 1
    )
    * 100,
)
