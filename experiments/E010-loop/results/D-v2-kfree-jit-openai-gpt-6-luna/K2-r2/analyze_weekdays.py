import json
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)

db = duckdb.connect()
df = db.execute(
    """
    SELECT
        strftime(crash_date, '%A') AS weekday,
        isodow(crash_date) AS weekday_num,
        COUNT(*) AS crash_count,
        COUNT(DISTINCT crash_date) AS date_count
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY weekday, weekday_num
    ORDER BY weekday_num
    """,
    [str(ROOT / "data" / "crashes.parquet")],
).df()

df["share_percent"] = 100 * df["crash_count"] / df["crash_count"].sum()
df["avg_crashes_per_date"] = df["crash_count"] / df["date_count"]
df.to_csv(OUT / "values_1.csv", index=False)
df.to_csv(OUT / "values_2.csv", index=False)

plt.rcParams.update({"font.size": 10, "axes.titleweight": "bold"})

fig, ax = plt.subplots(figsize=(9, 5.2))
bars = ax.bar(df["weekday"], df["crash_count"], color="#3977a8")
ax.bar_label(bars, labels=[f"{v:,.0f}" for v in df["crash_count"]], padding=3, fontsize=8)
ax.set_title("NYC police-reported crashes by weekday, 2013–2025")
ax.set_xlabel("Day of week")
ax.set_ylabel("Crashes over the full period")
ax.set_ylim(0, df["crash_count"].max() * 1.13)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "option_1.png", dpi=180)
plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 5.2))
bars = ax.bar(df["weekday"], df["avg_crashes_per_date"], color="#548b58")
ax.bar_label(bars, labels=[f"{v:,.1f}" for v in df["avg_crashes_per_date"]], padding=3, fontsize=8)
ax.set_title("Average NYC police-reported crashes per weekday date, 2013–2025")
ax.set_xlabel("Day of week")
ax.set_ylabel("Average crashes per calendar date")
ax.set_ylim(0, df["avg_crashes_per_date"].max() * 1.13)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "option_2.png", dpi=180)
plt.close(fig)

total = int(df["crash_count"].sum())
top = df.loc[df["crash_count"].idxmax()]
bottom = df.loc[df["crash_count"].idxmin()]
top_avg = df.loc[df["avg_crashes_per_date"].idxmax()]
bottom_avg = df.loc[df["avg_crashes_per_date"].idxmin()]

options = {
    "options": [
        {
            "id": 1,
            "metric": "Number of police-reported crashes",
            "denominator": "No denominator; total crash count within 2013–2025",
            "grouping": "Day of week, pooling all dates from 2013-01-01 through 2025-12-31",
            "chart_type": "Bar chart",
            "reason": "Period totals directly show how the observed crash burden is distributed across weekdays.",
            "probability": 0.55,
            "answer": f"Of {total:,} crashes in 2013–2025, Friday had the most ({int(top['crash_count']):,}; {top['share_percent']:.1f}%) and Sunday the fewest ({int(bottom['crash_count']):,}; {bottom['share_percent']:.1f}%).",
            "interpretation": "This answers how the total number of recorded NYC crashes is distributed across weekdays over the full period; Friday is highest and Sunday lowest. Totals are an intuitive measure of the observed burden, but this framing does not adjust for the number of calendar dates of each weekday or for traffic exposure.",
        },
        {
            "id": 2,
            "metric": "Average number of police-reported crashes per calendar date",
            "denominator": "Number of dates of each weekday in 2013–2025",
            "grouping": "Day of week",
            "chart_type": "Bar chart",
            "reason": "A per-date average makes weekday comparisons less sensitive to the slightly unequal number of weekday dates in the period.",
            "probability": 0.45,
            "answer": f"On an average date, Friday had the most crashes ({top_avg['avg_crashes_per_date']:,.1f}) and Sunday the fewest ({bottom_avg['avg_crashes_per_date']:,.1f}).",
            "interpretation": "This answers how many recorded crashes occurred on a typical date for each weekday, accounting for the count of dates of that weekday in the 13-year period. Friday remains highest and Sunday lowest after that calendar adjustment; the average does not adjust for how much or how many people travel on each weekday.",
        },
    ]
}
(OUT / "options.json").write_text(json.dumps(options, indent=2) + "\n")
