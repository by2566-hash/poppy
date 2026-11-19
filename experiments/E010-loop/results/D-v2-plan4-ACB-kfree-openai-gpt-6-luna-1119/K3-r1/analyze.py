import csv

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


con = duckdb.connect()
data = con.execute(
    """
    SELECT
        year(crash_date)::INTEGER AS year,
        sum(number_of_motorist_killed)::BIGINT AS motorist_deaths,
        sum(number_of_cyclist_killed)::BIGINT AS cyclist_deaths
    FROM read_parquet('data/crashes.parquet')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year(crash_date)
    ORDER BY year(crash_date)
    """
).fetchdf()

data["combined_deaths"] = data["motorist_deaths"] + data["cyclist_deaths"]
data["motorist_share_pct"] = 100 * data["motorist_deaths"] / data["combined_deaths"]
data["cyclist_share_pct"] = 100 * data["cyclist_deaths"] / data["combined_deaths"]

data[["year", "motorist_deaths", "cyclist_deaths"]].to_csv(
    "out/values_1.csv", index=False, quoting=csv.QUOTE_MINIMAL
)
data[["year", "combined_deaths", "motorist_share_pct", "cyclist_share_pct"]].to_csv(
    "out/values_2.csv", index=False, quoting=csv.QUOTE_MINIMAL
)

plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})

fig, ax = plt.subplots(figsize=(10, 5.8))
ax.plot(data["year"], data["motorist_deaths"], marker="o", linewidth=2.3,
        color="#315a9b", label="Motorist deaths")
ax.plot(data["year"], data["cyclist_deaths"], marker="o", linewidth=2.3,
        color="#d17425", label="Cyclist deaths")
ax.set_title("Annual reported motorist and cyclist deaths in police-reported NYC crashes (2013–2025)",
             loc="left", fontsize=13, weight="bold", pad=13)
ax.set_xlabel("Calendar year")
ax.set_ylabel("Reported deaths (sum of killed-person counts)")
ax.set_xticks(data["year"])
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", color="#dddddd", linewidth=0.7)
ax.legend(frameon=False, ncol=2, loc="upper right")
fig.text(0.01, 0.01,
         "Counts from NYC police-reported motor-vehicle crashes; these are not exposure-adjusted risks and show only the motorist/cyclist categories.",
         ha="left", va="bottom", fontsize=8, color="#555555")
fig.tight_layout(rect=(0, 0.055, 1, 1))
fig.savefig("out/option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 5.8))
ax.bar(data["year"], data["motorist_share_pct"], color="#315a9b", width=0.72,
       label="Motorist share")
ax.bar(data["year"], data["cyclist_share_pct"], bottom=data["motorist_share_pct"],
       color="#d17425", width=0.72, label="Cyclist share")
ax.set_title("Motorist and cyclist shares of their combined reported deaths in NYC crashes (2013–2025)",
             loc="left", fontsize=13, weight="bold", pad=13)
ax.set_xlabel("Calendar year")
ax.set_ylabel("Share of motorist + cyclist deaths")
ax.set_ylim(0, 100)
ax.set_yticks(range(0, 101, 20), labels=[f"{v}%" for v in range(0, 101, 20)])
ax.set_xticks(data["year"])
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", color="#dddddd", linewidth=0.7)
ax.set_axisbelow(True)
ax.legend(frameon=False, ncol=2, loc="upper right")
fig.text(0.01, 0.01,
         "Percentages use only motorist and cyclist deaths; pedestrian and other road-user deaths are outside this denominator.",
         ha="left", va="bottom", fontsize=8, color="#555555")
fig.tight_layout(rect=(0, 0.055, 1, 1))
fig.savefig("out/option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)
