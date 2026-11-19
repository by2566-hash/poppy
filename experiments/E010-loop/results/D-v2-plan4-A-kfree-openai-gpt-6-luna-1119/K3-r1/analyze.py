from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
PARQUET = ROOT / "data" / "crashes.parquet"
path_sql = str(PARQUET).replace("'", "''")

annual = duckdb.sql(
    f"""
    SELECT EXTRACT(YEAR FROM crash_date)::INTEGER AS year,
           SUM(number_of_motorist_killed)::BIGINT AS motorist_deaths,
           SUM(number_of_cyclist_killed)::BIGINT AS cyclist_deaths
    FROM read_parquet('{path_sql}')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
    """
).df()

expected_years = list(range(2013, 2026))
assert annual["year"].tolist() == expected_years
assert annual[["motorist_deaths", "cyclist_deaths"]].notna().all().all()

# Framing 1: annual counts, grouped bars.
count_values = annual.copy()
count_values.to_csv(OUT / "values_1.csv", index=False)
years = count_values["year"].to_numpy()
x = np.arange(len(years))
width = 0.39
fig, ax = plt.subplots(figsize=(12.5, 6.6))
ax.bar(x - width / 2, count_values["motorist_deaths"], width, label="Motorist deaths", color="#276FBF")
ax.bar(x + width / 2, count_values["cyclist_deaths"], width, label="Cyclist deaths", color="#F28E2B")
ax.set_title("Annual recorded motorist and cyclist deaths in NYC\nPolice-reported motor vehicle crashes, 2013–2025", loc="left", fontsize=14, weight="bold")
ax.set_ylabel("Recorded deaths (count)")
ax.set_xlabel("Calendar year")
ax.set_xticks(x, years)
ax.grid(axis="y", color="#dddddd", linewidth=0.7)
ax.set_axisbelow(True)
ax.legend(frameon=False, ncols=2, loc="upper right")
fig.text(0.125, 0.015, "Counts are not adjusted for the number of people or amount of travel in each road-user group.", fontsize=9, color="#555555")
fig.tight_layout(rect=(0, 0.045, 1, 1))
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Framing 2: the two groups' shares of their combined annual recorded deaths.
share_values = annual.copy()
share_values["combined_motorist_cyclist_deaths"] = share_values["motorist_deaths"] + share_values["cyclist_deaths"]
share_values["motorist_share"] = share_values["motorist_deaths"] / share_values["combined_motorist_cyclist_deaths"]
share_values["cyclist_share"] = share_values["cyclist_deaths"] / share_values["combined_motorist_cyclist_deaths"]
share_values.to_csv(OUT / "values_2.csv", index=False)

fig, ax = plt.subplots(figsize=(12.5, 6.6))
motorist_pct = 100 * share_values["motorist_share"].to_numpy()
cyclist_pct = 100 * share_values["cyclist_share"].to_numpy()
ax.bar(x, motorist_pct, label="Motorist share", color="#276FBF")
ax.bar(x, cyclist_pct, bottom=motorist_pct, label="Cyclist share", color="#F28E2B")
ax.set_title("Motorist and cyclist shares of their combined deaths in NYC\nPolice-reported motor vehicle crashes, by calendar year, 2013–2025", loc="left", fontsize=14, weight="bold")
ax.set_ylabel("Share of motorist + cyclist deaths (%)")
ax.set_xlabel("Calendar year")
ax.set_xticks(x, years)
ax.set_ylim(0, 100)
ax.grid(axis="y", color="#dddddd", linewidth=0.7)
ax.set_axisbelow(True)
ax.legend(frameon=False, ncols=2, loc="upper right")
fig.text(0.125, 0.015, "Denominator includes only motorist and cyclist deaths; shares are not exposure-adjusted risk rates.", fontsize=9, color="#555555")
fig.tight_layout(rect=(0, 0.045, 1, 1))
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)

print("Annual values:")
print(share_values.to_string(index=False))
