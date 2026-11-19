import csv
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"

df = duckdb.connect().execute(
    """
    SELECT year(crash_date) AS year,
           count(*) AS crash_rows,
           sum(number_of_motorist_killed) AS motorist_deaths
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year(crash_date)
    ORDER BY year
    """,
    [str(DATA)],
).df()
df["year"] = df["year"].astype(int)
df["crash_rows"] = df["crash_rows"].astype("int64")
df["motorist_deaths"] = df["motorist_deaths"].astype("int64")
df["deaths_per_100000_crashes"] = df["motorist_deaths"] / df["crash_rows"] * 100000


def save_line_chart(column, ylabel, title, filename):
    fig, ax = plt.subplots(figsize=(10, 5.8))
    ax.plot(df["year"], df[column], marker="o", linewidth=2, color="#176B87")
    ax.set_xticks(df["year"])
    ax.tick_params(axis="x", rotation=45)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Crash year")
    ax.grid(axis="y", alpha=0.25)
    ax.set_title(title, loc="left", fontsize=14, weight="bold", pad=26)
    fig.text(
        0.125,
        0.92,
        "Police-reported NYC crashes, 2013–2025. Miles driven are unavailable; this is not a per-mile risk measure.",
        ha="left",
        fontsize=9,
        color="#444444",
    )
    fig.tight_layout(rect=(0, 0.02, 1, 0.89))
    fig.savefig(OUT / filename, dpi=180, bbox_inches="tight")
    plt.close(fig)


df[["year", "crash_rows", "motorist_deaths"]].to_csv(
    OUT / "values_1.csv", index=False, quoting=csv.QUOTE_MINIMAL
)
df[["year", "crash_rows", "motorist_deaths", "deaths_per_100000_crashes"]].to_csv(
    OUT / "values_2.csv", index=False, float_format="%.6f", quoting=csv.QUOTE_MINIMAL
)

save_line_chart(
    "motorist_deaths",
    "Recorded motorist deaths (count)",
    "Annual recorded motorist deaths in police-reported NYC crashes",
    "option_1.png",
)
save_line_chart(
    "deaths_per_100000_crashes",
    "Recorded motorist deaths per 100,000 crash rows",
    "Recorded motorist deaths per 100,000 police-reported NYC crashes",
    "option_2.png",
)
