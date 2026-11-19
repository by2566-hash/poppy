from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

con = duckdb.connect()
parquet_path = str(DATA).replace("'", "''")
con.execute(f"CREATE VIEW crashes AS SELECT crash_date FROM read_parquet('{parquet_path}')")

# Only crash_date is needed: each row is one crash, and weekday/year come from its date.
weekday_sql = """
    SELECT EXTRACT(isodow FROM crash_date)::INTEGER AS weekday_num,
           count(*)::BIGINT AS crash_count
    FROM crashes
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY weekday_num ORDER BY weekday_num
"""
total_by_weekday = con.execute(weekday_sql).fetchdf()
total_by_weekday["weekday"] = total_by_weekday["weekday_num"].map(lambda n: WEEKDAYS[n - 1])
total_by_weekday["share_of_period_pct"] = (
    total_by_weekday["crash_count"] / total_by_weekday["crash_count"].sum() * 100
)
total_by_weekday[["weekday", "crash_count", "share_of_period_pct"]].to_csv(
    OUT / "values_1.csv", index=False, float_format="%.4f"
)

year_weekday = con.execute(
    """
    SELECT year(crash_date)::INTEGER AS year,
           EXTRACT(isodow FROM crash_date)::INTEGER AS weekday_num,
           count(*)::BIGINT AS crash_count
    FROM crashes
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY year, weekday_num ORDER BY year, weekday_num
    """
).fetchdf()
year_weekday["weekday"] = year_weekday["weekday_num"].map(lambda n: WEEKDAYS[n - 1])
year_weekday["year_total"] = year_weekday.groupby("year")["crash_count"].transform("sum")
year_weekday["share_of_year_pct"] = year_weekday["crash_count"] / year_weekday["year_total"] * 100
year_weekday[["year", "weekday", "crash_count", "year_total", "share_of_year_pct"]].to_csv(
    OUT / "values_2.csv", index=False, float_format="%.4f"
)
con.close()

plt.rcParams.update({"font.size": 10, "axes.titlesize": 15, "axes.labelsize": 11})

# Framing 1: pooled crash-record counts by weekday.
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(total_by_weekday["weekday"], total_by_weekday["crash_count"], color="#176B87")
ax.bar_label(bars, labels=[f"{int(v):,}" for v in total_by_weekday["crash_count"]], padding=3, fontsize=9)
ax.set_title("NYC police-reported motor vehicle crashes by weekday, 2013–2025", pad=36)
ax.text(
    0.5, 1.025,
    "One row per crash; excludes 136,969 dated records outside 2013–2025. Not adjusted for traffic exposure.",
    transform=ax.transAxes, ha="center", va="bottom", fontsize=9, color="#444444",
)
ax.set_xlabel("Weekday of crash")
ax.set_ylabel("Police-reported crashes")
ax.set_ylim(0, total_by_weekday["crash_count"].max() * 1.12)
ax.grid(axis="y", alpha=0.22)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Framing 2: yearly weekday shares reveal how weekday composition varies by year.
fig, ax = plt.subplots(figsize=(11, 6.5))
for weekday in WEEKDAYS:
    series = year_weekday[year_weekday["weekday"] == weekday]
    ax.plot(series["year"], series["share_of_year_pct"], marker="o", linewidth=1.8, markersize=4, label=weekday)
ax.set_title("Share of NYC police-reported motor vehicle crashes by weekday within each year, 2013–2025", pad=36)
ax.text(
    0.5, 1.025,
    "Each year's crashes are the denominator; all years have full date coverage. Shares are not exposure-adjusted.",
    transform=ax.transAxes, ha="center", va="bottom", fontsize=9, color="#444444",
)
ax.set_xlabel("Calendar year")
ax.set_ylabel("Share of that year's crashes (%)")
ax.set_xticks(range(2013, 2026))
ax.set_ylim(bottom=0)
ax.grid(alpha=0.22)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(title="Weekday", ncols=2, frameon=False, loc="center left", bbox_to_anchor=(1.01, 0.5))
fig.tight_layout()
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)
