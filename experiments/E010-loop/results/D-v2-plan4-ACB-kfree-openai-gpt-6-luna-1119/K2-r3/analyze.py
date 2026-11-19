from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

con = duckdb.connect()
source = str(DATA).replace("'", "''")

# Final plan 1: pooled number of crash rows by weekday.
pooled = con.execute(
    f"""
    SELECT isodow(crash_date) AS weekday_number, COUNT(*) AS crash_rows
    FROM read_parquet('{source}')
    WHERE crash_date BETWEEN DATE '2013-01-01' AND DATE '2025-12-31'
    GROUP BY weekday_number
    ORDER BY weekday_number
    """
).df()
pooled["weekday"] = pooled["weekday_number"].map(lambda n: WEEKDAYS[int(n) - 1])
pooled = pooled[["weekday", "crash_rows"]]
pooled.to_csv(OUT / "values_1.csv", index=False)

fig, ax = plt.subplots(figsize=(10, 5.8))
bars = ax.bar(pooled["weekday"], pooled["crash_rows"], color="#2463a6")
ax.set_title("Police-reported crash rows by weekday, NYC, 2013–2025", fontsize=15, pad=18)
ax.text(0.5, 1.015, "All 2,132,218 crash records; complete calendar years. Counts are not exposure-adjusted.",
        transform=ax.transAxes, ha="center", va="bottom", fontsize=9, color="#444444")
ax.set_ylabel("Crash rows")
ax.set_xlabel("Day of week of crash_date")
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)
ax.bar_label(bars, labels=[f"{int(v):,}" for v in pooled["crash_rows"]], padding=3, fontsize=9)
fig.tight_layout()
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Final plan 2: annual weekday shares, averaged equally over the 13 years.
annual = con.execute(
    f"""
    WITH weekday_counts AS (
        SELECT YEAR(crash_date) AS year, isodow(crash_date) AS weekday_number,
               COUNT(*) AS crash_rows
        FROM read_parquet('{source}')
        WHERE crash_date BETWEEN DATE '2013-01-01' AND DATE '2025-12-31'
        GROUP BY year, weekday_number
    ),
    annual_totals AS (
        SELECT year, SUM(crash_rows) AS year_rows
        FROM weekday_counts
        GROUP BY year
    )
    SELECT w.weekday_number,
           AVG(100.0 * w.crash_rows / t.year_rows) AS mean_annual_share_percent
    FROM weekday_counts w
    JOIN annual_totals t USING (year)
    GROUP BY w.weekday_number
    ORDER BY w.weekday_number
    """
).df()
annual["weekday"] = annual["weekday_number"].map(lambda n: WEEKDAYS[int(n) - 1])
annual["years_averaged"] = 13
annual = annual[["weekday", "mean_annual_share_percent", "years_averaged"]]
annual.to_csv(OUT / "values_2.csv", index=False, float_format="%.6f")

fig, ax = plt.subplots(figsize=(10, 5.8))
bars = ax.bar(annual["weekday"], annual["mean_annual_share_percent"], color="#23866b")
ax.set_title("Mean annual share of NYC crash rows by weekday, 2013–2025", fontsize=15, pad=18)
ax.text(0.5, 1.015, "Each of 13 complete years weighted equally; annual shares use all crash records and are not exposure-adjusted.",
        transform=ax.transAxes, ha="center", va="bottom", fontsize=9, color="#444444")
ax.set_ylabel("Mean annual share of crash rows (%)")
ax.set_xlabel("Day of week of crash_date")
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)
ax.bar_label(bars, labels=[f"{v:.2f}%" for v in annual["mean_annual_share_percent"]], padding=3, fontsize=9)
fig.tight_layout()
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)

print("Pooled crash rows by weekday:")
print(pooled.to_string(index=False))
print("\nMean annual percentage by weekday:")
print(annual.to_string(index=False))
