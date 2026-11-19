from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent
PARQUET = ROOT.parent / "data" / "crashes.parquet"

query = """
SELECT
    year(crash_date) AS year,
    count(*) AS crash_rows,
    sum(number_of_motorist_killed) AS motorist_deaths
FROM read_parquet(?)
WHERE crash_date >= make_date(2013, 1, 1)
  AND crash_date < make_date(2026, 1, 1)
GROUP BY 1
ORDER BY 1
"""
values = duckdb.sql(query, params=[str(PARQUET)]).df()
values["deaths_per_crash"] = values["motorist_deaths"] / values["crash_rows"]

# Framing 1: annual motorist-death count.
count_values = values[["year", "motorist_deaths"]]
count_values.to_csv(ROOT / "values_1.csv", index=False)
fig, ax = plt.subplots(figsize=(10, 5.6))
ax.plot(count_values["year"], count_values["motorist_deaths"], marker="o", linewidth=2, color="#1f77b4")
ax.set_title("Annual motorist deaths recorded in police-reported NYC crashes")
ax.set_xlabel("Crash year")
ax.set_ylabel("Recorded motorist deaths (count)")
ax.set_xticks(count_values["year"])
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.3)
fig.text(0.5, 0.015, "Limitation: annual counts are not adjusted for miles driven; police-reported crashes only.", ha="center", fontsize=9)
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(ROOT / "option_1.png", dpi=180)
plt.close(fig)

# Framing 2: annual recorded motorist deaths per reported crash row.
rate_values = values[["year", "motorist_deaths", "crash_rows", "deaths_per_crash"]]
rate_values.to_csv(ROOT / "values_2.csv", index=False)
fig, ax = plt.subplots(figsize=(10, 5.6))
ax.plot(rate_values["year"], rate_values["deaths_per_crash"], marker="o", linewidth=2, color="#d95f02")
ax.set_title("Recorded motorist deaths per police-reported NYC crash")
ax.set_xlabel("Crash year")
ax.set_ylabel("Motorist deaths per crash row")
ax.set_xticks(rate_values["year"])
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.3)
fig.text(0.5, 0.015, "Limitation: crash-normalized, not miles-driven risk; police-reported crashes only.", ha="center", fontsize=9)
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(ROOT / "option_2.png", dpi=180)
plt.close(fig)

print(count_values.to_string(index=False))
print(rate_values.to_string(index=False))
