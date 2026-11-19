import csv
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "crashes.parquet"
START_YEAR = 2013
END_YEAR = 2025

con = duckdb.connect()
annual = con.execute(
    """
    SELECT
        year(crash_date) AS year,
        count(*) AS crash_rows,
        sum(number_of_motorist_killed) AS motorist_deaths,
        count(*) FILTER (WHERE number_of_motorist_killed > 0) AS crashes_with_motorist_death
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year(crash_date)
    ORDER BY year(crash_date)
    """,
    [str(DATA)],
).fetchall()

if [row[0] for row in annual] != list(range(START_YEAR, END_YEAR + 1)):
    raise ValueError("The planned period must have one annual value for every year 2013–2025")

framings = [
    {
        "id": 1,
        "measure": "motorist_deaths",
        "value_header": "motorist_deaths",
        "title": "Motorist deaths recorded in NYC crashes, 2013–2025",
        "ylabel": "Recorded motorist deaths",
    },
    {
        "id": 2,
        "measure": "crashes_with_motorist_death",
        "value_header": "crashes_with_motorist_death",
        "title": "NYC crashes with a motorist death, 2013–2025",
        "ylabel": "Crash rows with ≥1 motorist death",
    },
]

for framing in framings:
    values_path = OUT / f"values_{framing['id']}.csv"
    with values_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["year", framing["value_header"]])
        for year, crash_rows, motorist_deaths, fatal_crash_rows in annual:
            value = motorist_deaths if framing["id"] == 1 else fatal_crash_rows
            writer.writerow([year, int(value)])

    years = [row[0] for row in annual]
    values = [int(row[2] if framing["id"] == 1 else row[3]) for row in annual]
    fig, ax = plt.subplots(figsize=(10, 5.8))
    ax.plot(years, values, marker="o", linewidth=2, color="#176B87")
    ax.set_title(framing["title"], fontsize=14, pad=18)
    ax.text(
        0.5,
        1.01,
        "Annual counts from police-reported NYC crash rows; no miles-driven exposure for per-mile risk",
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=9,
        color="#555555",
    )
    ax.set_xlabel("Crash year")
    ax.set_ylabel(framing["ylabel"])
    ax.set_ylim(bottom=0)
    ax.set_xticks(years)
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / f"option_{framing['id']}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
