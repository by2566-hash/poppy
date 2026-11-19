import duckdb
import matplotlib.pyplot as plt
import pandas as pd


START = "2013-01-01"
STOP = "2026-01-01"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

con = duckdb.connect()
con.execute(
    "CREATE VIEW crashes AS "
    "SELECT crash_date FROM read_parquet('data/crashes.parquet')"
)

# Option 1: pooled crash counts and percentage of all selected crash records.
pooled = con.execute(
    "SELECT isodow(crash_date) AS weekday_number, count(*) AS crash_count "
    "FROM crashes WHERE crash_date >= ? AND crash_date < ? "
    "GROUP BY weekday_number ORDER BY weekday_number",
    [START, STOP],
).df()
pooled = pd.DataFrame({"weekday_number": range(1, 8)}).merge(
    pooled, on="weekday_number", how="left"
)
pooled["crash_count"] = pooled["crash_count"].fillna(0).astype("int64")
pooled["weekday"] = [WEEKDAYS[number - 1] for number in pooled["weekday_number"]]
total = int(pooled["crash_count"].sum())
pooled["share_percent"] = pooled["crash_count"] / total * 100
pooled[["weekday", "crash_count", "share_percent"]].to_csv(
    "out/values_1.csv", index=False, float_format="%.6f"
)

fig, ax = plt.subplots(figsize=(10, 5.7))
bars = ax.bar(pooled["weekday"], pooled["crash_count"], color="#2878B5")
ax.set_title(
    "Police-reported crash counts by weekday\nNYC, 2013–2025",
    fontsize=15,
    pad=36,
)
ax.text(
    0.5,
    1.015,
    "All 2,132,218 dated crash records; event data cannot verify coverage on every date",
    transform=ax.transAxes,
    ha="center",
    va="bottom",
    fontsize=9,
    color="#444444",
)
ax.set_ylabel("Number of crashes")
ax.set_xlabel("Day of week (Monday–Sunday)")
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)
ax.tick_params(axis="x", rotation=20)
for bar, share in zip(bars, pooled["share_percent"]):
    ax.annotate(
        f"{share:.1f}%",
        (bar.get_x() + bar.get_width() / 2, bar.get_height()),
        xytext=(0, 3),
        textcoords="offset points",
        ha="center",
        fontsize=8,
    )
fig.tight_layout()
fig.savefig("out/option_1.png", dpi=160, bbox_inches="tight")
plt.close(fig)

# Option 2: within-year weekday shares, with each calendar year its own denominator.
annual = con.execute(
    "SELECT year(crash_date) AS year, isodow(crash_date) AS weekday_number, "
    "count(*) AS crash_count "
    "FROM crashes WHERE crash_date >= ? AND crash_date < ? "
    "GROUP BY year, weekday_number ORDER BY year, weekday_number",
    [START, STOP],
).df()
years = list(range(2013, 2026))
full_index = pd.MultiIndex.from_product(
    [years, range(1, 8)], names=["year", "weekday_number"]
)
annual = (
    annual.set_index(["year", "weekday_number"])
    .reindex(full_index, fill_value=0)
    .reset_index()
)
annual["crash_count"] = annual["crash_count"].astype("int64")
annual["year_total"] = annual.groupby("year")["crash_count"].transform("sum")
annual["share_percent"] = annual["crash_count"] / annual["year_total"] * 100
annual["weekday"] = [WEEKDAYS[number - 1] for number in annual["weekday_number"]]
annual[["year", "weekday", "crash_count", "year_total", "share_percent"]].to_csv(
    "out/values_2.csv", index=False, float_format="%.6f"
)

fig, ax = plt.subplots(figsize=(11, 6.2))
for weekday in WEEKDAYS:
    subset = annual[annual["weekday"] == weekday]
    ax.plot(
        subset["year"],
        subset["share_percent"],
        marker="o",
        linewidth=1.8,
        markersize=4,
        label=weekday,
    )
ax.set_title(
    "Weekday share of police-reported crashes within each year\nNYC, 2013–2025",
    fontsize=15,
    pad=36,
)
ax.text(
    0.5,
    1.015,
    "Each year's denominator is its dated crash records; event data cannot verify coverage on every date",
    transform=ax.transAxes,
    ha="center",
    va="bottom",
    fontsize=9,
    color="#444444",
)
ax.set_xlabel("Calendar year")
ax.set_ylabel("Share of that year's recorded crashes (%)")
ax.set_xticks(years)
ax.grid(alpha=0.25)
ax.legend(ncol=4, frameon=False, loc="best")
fig.tight_layout()
fig.savefig("out/option_2.png", dpi=160, bbox_inches="tight")
plt.close(fig)

print("Pooled population:", total)
print(pooled[["weekday", "crash_count", "share_percent"]].to_string(index=False))
print("Annual values rows:", len(annual), "years:", annual["year"].nunique())
