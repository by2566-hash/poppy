import json
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


OUT = Path("out")
OUT.mkdir(exist_ok=True)

annual = duckdb.connect().execute(
    """
    SELECT
        EXTRACT(YEAR FROM crash_date)::INTEGER AS year,
        SUM(COALESCE(number_of_motorist_killed, 0))::INTEGER AS motorist_deaths,
        COUNT(*)::INTEGER AS reported_crashes,
        COUNT_IF(COALESCE(number_of_motorist_killed, 0) > 0)::INTEGER AS crashes_with_motorist_death
    FROM read_parquet('data/crashes.parquet')
    WHERE EXTRACT(YEAR FROM crash_date) BETWEEN 2013 AND 2025
    GROUP BY year
    ORDER BY year
    """
).df()

years = list(range(2013, 2026))
assert annual["year"].tolist() == years
annual["motorist_deaths_per_1000_crashes"] = (
    annual["motorist_deaths"] / annual["reported_crashes"] * 1000
)


def finish_chart(fig, path):
    fig.text(
        0.5,
        0.015,
        "Crash records contain no vehicle-miles-traveled measure; this is not per-mile risk.",
        ha="center",
        fontsize=8,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


# Option 1: annual count of motorist deaths.
values1 = annual[["year", "motorist_deaths"]]
values1.to_csv(OUT / "values_1.csv", index=False)
fig, ax = plt.subplots(figsize=(9, 4.8))
ax.plot(values1["year"], values1["motorist_deaths"], marker="o", linewidth=2.2, color="#1f77b4")
ax.set(title="Motorist deaths in reported NYC crashes", xlabel="Crash year", ylabel="Motorist deaths (people)")
ax.set_xticks(years)
ax.grid(axis="y", alpha=0.25)
ax.annotate("2013: 110", (2013, 110), xytext=(7, 10), textcoords="offset points", fontsize=8)
ax.annotate("2025: 81", (2025, 81), xytext=(-48, 10), textcoords="offset points", fontsize=8)
finish_chart(fig, OUT / "option_1.png")

# Option 2: annual count of crashes in which at least one motorist died.
values2 = annual[["year", "crashes_with_motorist_death"]]
values2.to_csv(OUT / "values_2.csv", index=False)
fig, ax = plt.subplots(figsize=(9, 4.8))
ax.bar(values2["year"], values2["crashes_with_motorist_death"], color="#d97732", width=0.72)
ax.set(title="Reported crashes with at least one motorist death", xlabel="Crash year", ylabel="Crashes with a motorist death")
ax.set_xticks(years, labels=[str(year) for year in years], rotation=45)
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)
finish_chart(fig, OUT / "option_2.png")

# Option 3: motorist deaths per 1,000 reported crash records.
values3 = annual[["year", "motorist_deaths", "reported_crashes", "motorist_deaths_per_1000_crashes"]]
values3.to_csv(OUT / "values_3.csv", index=False, float_format="%.6f")
fig, ax = plt.subplots(figsize=(9, 4.8))
ax.plot(
    values3["year"],
    values3["motorist_deaths_per_1000_crashes"],
    marker="o",
    linewidth=2.2,
    color="#25855a",
)
ax.set(title="Motorist deaths per 1,000 reported crashes", xlabel="Crash year", ylabel="Deaths per 1,000 crash records")
ax.set_xticks(years)
ax.grid(axis="y", alpha=0.25)
finish_chart(fig, OUT / "option_3.png")


v1_2013 = int(annual.loc[annual.year == 2013, "motorist_deaths"].iloc[0])
v1_2025 = int(annual.loc[annual.year == 2025, "motorist_deaths"].iloc[0])
v2_2013 = int(annual.loc[annual.year == 2013, "crashes_with_motorist_death"].iloc[0])
v2_2025 = int(annual.loc[annual.year == 2025, "crashes_with_motorist_death"].iloc[0])
v3_2013 = float(annual.loc[annual.year == 2013, "motorist_deaths_per_1000_crashes"].iloc[0])
v3_2025 = float(annual.loc[annual.year == 2025, "motorist_deaths_per_1000_crashes"].iloc[0])

options = {
    "options": [
        {
            "id": 1,
            "metric": "Annual count of motorist deaths",
            "denominator": "None (count)",
            "grouping": "Crash year",
            "chart_type": "Line chart",
            "reason": "A count directly shows how many motorists died in crashes each year without introducing an unavailable exposure estimate.",
            "probability": 0.38,
            "answer": f"This crash data cannot establish deaths per mile because it contains no miles-driven denominator. Recorded motorist deaths went from {v1_2013} in 2013 to {v1_2025} in 2025, a lower annual count in 2025.",
        },
        {
            "id": 2,
            "metric": "Number of crashes with at least one motorist death",
            "denominator": "None (count of crash records meeting the condition)",
            "grouping": "Crash year",
            "chart_type": "Bar chart",
            "reason": "Counting fatal crashes rather than individual deaths avoids letting crashes with multiple motorist deaths count as multiple fatal events.",
            "probability": 0.32,
            "answer": f"This crash data cannot establish deaths per mile because it contains no miles-driven denominator. Crashes with at least one motorist death declined from {v2_2013} in 2013 to {v2_2025} in 2025.",
        },
        {
            "id": 3,
            "metric": "Motorist deaths per 1,000 reported crashes",
            "denominator": "All police-reported crash records in the year",
            "grouping": "Crash year",
            "chart_type": "Line chart",
            "reason": "Scaling deaths by the number of reported crashes offers a crash-volume-adjusted comparison that the available columns support.",
            "probability": 0.30,
            "answer": f"This crash data cannot establish deaths per mile because it contains no miles-driven denominator. Motorist deaths per 1,000 reported crashes rose from {v3_2013:.3f} in 2013 to {v3_2025:.3f} in 2025.",
        },
    ]
}
(OUT / "options.json").write_text(json.dumps(options, indent=2) + "\n", encoding="utf-8")
