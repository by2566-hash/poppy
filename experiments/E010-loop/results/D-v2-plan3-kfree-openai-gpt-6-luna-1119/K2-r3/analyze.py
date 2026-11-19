from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
SOURCE = str(ROOT / "data" / "crashes.parquet").replace("'", "''")
START = "2013-01-01"
END = "2025-12-31"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

con = duckdb.connect()

# Option 1: pooled crash-row count and share by weekday.
pooled = con.execute(
    f"""
    SELECT isodow(crash_date) AS weekday_num, count(*) AS crash_rows
    FROM read_parquet('{SOURCE}')
    WHERE crash_date >= DATE '{START}' AND crash_date <= DATE '{END}'
    GROUP BY weekday_num
    ORDER BY weekday_num
    """
).df()
pooled["weekday"] = pooled["weekday_num"].map(lambda n: WEEKDAYS[int(n) - 1])
pooled["share_pct"] = pooled["crash_rows"] / pooled["crash_rows"].sum() * 100
pooled = pooled[["weekday", "crash_rows", "share_pct"]]
pooled["share_pct"] = pooled["share_pct"].round(4)
pooled.to_csv(OUT / "values_1.csv", index=False)

fig, ax = plt.subplots(figsize=(10, 5.8))
bars = ax.bar(pooled["weekday"], pooled["share_pct"], color="#337ab7")
ax.bar_label(bars, labels=[f"{v:.1f}%" for v in pooled["share_pct"]], padding=3, fontsize=9)
ax.set_ylabel("Share of qualifying crash rows (%)")
ax.set_xlabel("Weekday of crash_date")
ax.set_title("Share of police-reported NYC crash rows by weekday, 2013–2025")
ax.text(
    0.5,
    -0.22,
    "Police-reported rows only; higher-volume years receive more weight, and date bounds do not prove complete daily reporting.",
    ha="center",
    va="top",
    transform=ax.transAxes,
    fontsize=9,
)
ax.set_ylim(0, max(pooled["share_pct"]) * 1.15)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Option 2: within-year weekday shares, then equal-weight the 13 years.
annual = con.execute(
    f"""
    WITH by_weekday AS (
        SELECT year(crash_date) AS yr,
               isodow(crash_date) AS weekday_num,
               count(*) AS weekday_rows
        FROM read_parquet('{SOURCE}')
        WHERE crash_date >= DATE '{START}' AND crash_date <= DATE '{END}'
        GROUP BY yr, weekday_num
    ),
    year_totals AS (
        SELECT yr, sum(weekday_rows) AS year_rows
        FROM by_weekday
        GROUP BY yr
    )
    SELECT b.yr, b.weekday_num,
           b.weekday_rows::DOUBLE / t.year_rows AS annual_share
    FROM by_weekday b
    JOIN year_totals t USING (yr)
    ORDER BY b.yr, b.weekday_num
    """
).df()
annual["weekday"] = annual["weekday_num"].map(lambda n: WEEKDAYS[int(n) - 1])
summary = (
    annual.groupby("weekday", sort=False)["annual_share"]
    .agg(mean_annual_share="mean", min_annual_share="min", max_annual_share="max", years="count")
    .reindex(WEEKDAYS)
    .reset_index()
)
for col in ["mean_annual_share", "min_annual_share", "max_annual_share"]:
    summary[col] *= 100
summary = summary.rename(columns={"index": "weekday"})
summary[["mean_annual_share", "min_annual_share", "max_annual_share"]] = summary[
    ["mean_annual_share", "min_annual_share", "max_annual_share"]
].round(4)
summary.to_csv(OUT / "values_2.csv", index=False)

fig, ax = plt.subplots(figsize=(10, 5.8))
bars = ax.bar(summary["weekday"], summary["mean_annual_share"], color="#5a8f69")
ax.bar_label(bars, labels=[f"{v:.1f}%" for v in summary["mean_annual_share"]], padding=3, fontsize=9)
ax.set_ylabel("Mean annual share (%)")
ax.set_xlabel("Weekday of crash_date")
ax.set_title("Equal-year mean annual weekday share of police-reported NYC crashes, 2013–2025")
ax.text(
    0.5,
    -0.22,
    "Each calendar year's weekday shares are normalized within year, then the 13 years are equally weighted; date bounds do not prove complete daily reporting.",
    ha="center",
    va="top",
    transform=ax.transAxes,
    fontsize=9,
)
ax.set_ylim(0, max(summary["mean_annual_share"]) * 1.15)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)
