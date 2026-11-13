import duckdb
import matplotlib.pyplot as plt
import pandas as pd


SOURCE = "data/crashes.parquet"
YEARS = range(2013, 2026)

df = duckdb.sql(
    """
    SELECT
        year(crash_date) AS year,
        sum(number_of_motorist_killed) AS motorist_deaths,
        sum(number_of_cyclist_killed) AS cyclist_deaths
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
    """,
    params=[SOURCE],
).df()

expected_years = list(YEARS)
df = df.set_index("year").reindex(expected_years).rename_axis("year").reset_index()
df[["motorist_deaths", "cyclist_deaths"]] = df[["motorist_deaths", "cyclist_deaths"]].astype("int64")
df["cyclist_share_pct"] = (
    100 * df["cyclist_deaths"] / (df["cyclist_deaths"] + df["motorist_deaths"])
)
df.to_csv("out/values_1.csv", index=False)
df.to_csv("out/values_2.csv", index=False)

plt.figure(figsize=(10, 5.5))
plt.plot(df["year"], df["motorist_deaths"], marker="o", linewidth=2.2, label="Motorist deaths")
plt.plot(df["year"], df["cyclist_deaths"], marker="o", linewidth=2.2, label="Cyclist deaths")
plt.title("Annual reported motorist and cyclist deaths\nNYC crash reports, 2013–2025")
plt.xlabel("Crash year")
plt.ylabel("Reported deaths (count)")
plt.xticks(expected_years, rotation=45)
plt.grid(axis="y", alpha=0.25)
plt.legend(frameon=False)
plt.figtext(
    0.01,
    0.01,
    "Reported crash-level counts, not exposure-adjusted rates. Full-year date boundaries observed; within-year completeness unverified.",
    ha="left",
    fontsize=8,
)
plt.tight_layout(rect=(0, 0.06, 1, 1))
plt.savefig("out/option_1.png", dpi=180, bbox_inches="tight")
plt.close()

plt.figure(figsize=(10, 5.5))
plt.plot(df["year"], df["cyclist_share_pct"], marker="o", linewidth=2.2, color="#2a788e")
plt.title("Cyclist share of motorist-plus-cyclist deaths\nNYC crash reports, 2013–2025")
plt.xlabel("Crash year")
plt.ylabel("Cyclist deaths / (cyclist + motorist deaths), %")
plt.xticks(expected_years, rotation=45)
plt.ylim(bottom=0)
plt.grid(axis="y", alpha=0.25)
plt.figtext(
    0.01,
    0.01,
    "Excludes pedestrian deaths; not an exposure-adjusted risk measure. Full-year date boundaries observed; within-year completeness unverified.",
    ha="left",
    fontsize=8,
)
plt.tight_layout(rect=(0, 0.06, 1, 1))
plt.savefig("out/option_2.png", dpi=180, bbox_inches="tight")
plt.close()

print(df.to_string(index=False))
