import csv
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

con = duckdb.connect()
source = f"read_parquet('{DATA.as_posix()}')"
rows = con.execute(
    f"""
    SELECT year(crash_date) AS year,
           isodow(crash_date) AS weekday_num,
           count(*) AS crash_rows
    FROM {source}
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year, weekday_num
    ORDER BY year, weekday_num
    """
).df()
rows["weekday"] = rows["weekday_num"].map(dict(enumerate(WEEKDAYS, start=1)))

# Framing 1: raw pooled counts.
pooled = (
    rows.groupby(["weekday_num", "weekday"], as_index=False)["crash_rows"]
    .sum()
    .sort_values("weekday_num")
)
pooled.to_csv(OUT / "values_1.csv", index=False)
fig, ax = plt.subplots(figsize=(10, 5.6))
bars = ax.bar(pooled["weekday"], pooled["crash_rows"], color="#3973ac")
ax.bar_label(bars, labels=[f"{v:,.0f}" for v in pooled["crash_rows"]], padding=3, fontsize=9)
ax.set_title("NYC Police-Reported Crash Rows by Weekday\nAll crashes dated 2013–2025", loc="left", weight="bold")
ax.set_ylabel("Crash rows")
ax.set_xlabel("")
ax.tick_params(axis="x", rotation=20)
ax.spines[["top", "right"]].set_visible(False)
fig.text(0.01, 0.01, "Counts are police-reported records, not exposure-adjusted crash risk.", fontsize=9, color="#555555")
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Framing 2: pooled share of all included rows.
pooled["share_percent"] = pooled["crash_rows"] / pooled["crash_rows"].sum() * 100
pooled[["weekday_num", "weekday", "crash_rows", "share_percent"]].to_csv(OUT / "values_2.csv", index=False)
fig, ax = plt.subplots(figsize=(10, 5.6))
bars = ax.bar(pooled["weekday"], pooled["share_percent"], color="#25877a")
ax.bar_label(bars, labels=[f"{v:.1f}%" for v in pooled["share_percent"]], padding=3, fontsize=9)
ax.set_title("Share of NYC Police-Reported Crash Rows by Weekday\nAll crashes dated 2013–2025", loc="left", weight="bold")
ax.set_ylabel("Share of all crash rows (%)")
ax.set_xlabel("")
ax.tick_params(axis="x", rotation=20)
ax.spines[["top", "right"]].set_visible(False)
fig.text(0.01, 0.01, "Denominator: all included crash rows; this is not an exposure-adjusted risk measure.", fontsize=9, color="#555555")
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Framing 3: each year's weekday composition, normalized within year.
annual = rows.copy()
annual["year_rows"] = annual.groupby("year")["crash_rows"].transform("sum")
annual["share_percent"] = annual["crash_rows"] / annual["year_rows"] * 100
annual["weekday"] = pd.Categorical(annual["weekday"], categories=WEEKDAYS, ordered=True)
annual = annual.sort_values(["year", "weekday_num"])
annual[["year", "weekday", "crash_rows", "year_rows", "share_percent"]].to_csv(OUT / "values_3.csv", index=False)
matrix = annual.pivot(index="year", columns="weekday", values="share_percent").reindex(columns=WEEKDAYS)
fig, ax = plt.subplots(figsize=(11, 7))
image = ax.imshow(matrix.to_numpy(), cmap="YlGnBu", aspect="auto", vmin=matrix.to_numpy().min(), vmax=matrix.to_numpy().max())
ax.set_xticks(range(len(WEEKDAYS)), WEEKDAYS, rotation=25, ha="right")
ax.set_yticks(range(len(matrix.index)), matrix.index.astype(int))
ax.set_title("Weekday Share of NYC Police-Reported Crash Rows by Year\nAll crashes dated 2013–2025; each row sums to 100%", loc="left", weight="bold")
ax.set_xlabel("")
ax.set_ylabel("Crash year")
colorbar = fig.colorbar(image, ax=ax, pad=0.02)
colorbar.set_label("Share of that year's crash rows (%)")
for i in range(matrix.shape[0]):
    for j in range(matrix.shape[1]):
        value = matrix.iloc[i, j]
        ax.text(j, i, f"{value:.1f}", ha="center", va="center", fontsize=8,
                color="white" if value > np.nanmean(matrix.to_numpy()) else "#222222")
fig.text(0.01, 0.01, "Annual row counts change; 2019 to 2020 fell by 98,568, so shares are not risk rates.", fontsize=9, color="#555555")
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(OUT / "option_3.png", dpi=180, bbox_inches="tight")
plt.close(fig)

print("created three values files and charts")
