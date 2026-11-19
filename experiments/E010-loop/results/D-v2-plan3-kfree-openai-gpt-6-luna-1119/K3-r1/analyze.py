import duckdb
import matplotlib.pyplot as plt
import numpy as np


SOURCE = "data/crashes.parquet"
YEARS = list(range(2013, 2026))

con = duckdb.connect()
data = con.execute(
    """
    SELECT
        CAST(year(crash_date) AS INTEGER) AS year,
        sum(number_of_motorist_killed)::BIGINT AS motorist_deaths,
        sum(number_of_cyclist_killed)::BIGINT AS cyclist_deaths
    FROM read_parquet(?)
    WHERE year(crash_date) BETWEEN 2013 AND 2025
    GROUP BY year
    ORDER BY year
    """,
    [SOURCE],
).df()
data = data.set_index("year").reindex(YEARS, fill_value=0).rename_axis("year").reset_index()
data["combined_motorist_cyclist_deaths"] = data["motorist_deaths"] + data["cyclist_deaths"]
data["motorist_share_pct"] = np.where(
    data["combined_motorist_cyclist_deaths"] > 0,
    100 * data["motorist_deaths"] / data["combined_motorist_cyclist_deaths"],
    np.nan,
)
data["cyclist_share_pct"] = np.where(
    data["combined_motorist_cyclist_deaths"] > 0,
    100 * data["cyclist_deaths"] / data["combined_motorist_cyclist_deaths"],
    np.nan,
)

# Option 1: annual counts of recorded deaths by road-user category.
data.to_csv("out/values_1.csv", index=False)
fig, ax = plt.subplots(figsize=(12, 6.6))
x = np.arange(len(data))
width = 0.38
ax.bar(x - width / 2, data["motorist_deaths"], width, label="Motorist", color="#3366a8")
ax.bar(x + width / 2, data["cyclist_deaths"], width, label="Cyclist", color="#e28e2c")
ax.set_xticks(x, data["year"], rotation=45)
ax.set_ylabel("Recorded deaths (sum of killed-person column)")
ax.set_title(
    "Annual motorist and cyclist deaths in police-reported NYC crashes\n2013–2025"
)
ax.legend(frameon=False, ncol=2, loc="upper right")
ax.grid(axis="y", alpha=0.22)
ax.set_axisbelow(True)
fig.text(
    0.5,
    0.015,
    "Limitation: counts are not exposure-adjusted; the number of crash records differs substantially by year.",
    ha="center",
    fontsize=9,
)
fig.tight_layout(rect=(0, 0.045, 1, 1))
fig.savefig("out/option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Option 2: each year's combined motorist-plus-cyclist deaths sum to 100%.
data.to_csv("out/values_2.csv", index=False)
fig, ax = plt.subplots(figsize=(12, 6.6))
motorist = data["motorist_share_pct"].fillna(0)
cyclist = data["cyclist_share_pct"].fillna(0)
ax.bar(x, motorist, label="Motorist", color="#3366a8")
ax.bar(x, cyclist, bottom=motorist, label="Cyclist", color="#e28e2c")
ax.set_xticks(x, data["year"], rotation=45)
ax.set_ylim(0, 100)
ax.set_ylabel("Share of motorist + cyclist deaths (%)")
ax.set_title(
    "Composition of motorist and cyclist deaths in police-reported NYC crashes\n2013–2025"
)
ax.legend(frameon=False, ncol=2, loc="upper right")
ax.grid(axis="y", alpha=0.22)
ax.set_axisbelow(True)
fig.text(
    0.5,
    0.015,
    "Limitation: denominator includes only recorded motorist and cyclist deaths; shares do not show absolute counts or exposure-adjusted risk.",
    ha="center",
    fontsize=9,
)
fig.tight_layout(rect=(0, 0.045, 1, 1))
fig.savefig("out/option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)
