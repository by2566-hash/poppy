from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
data_path = str(DATA).replace("'", "''")
con = duckdb.connect()
con.execute(
    "CREATE VIEW crashes AS SELECT crash_date, number_of_motorist_killed "
    f"FROM read_parquet('{data_path}')"
)

annual = con.execute(
    """
    SELECT year(crash_date) AS year,
           sum(number_of_motorist_killed)::BIGINT AS motorists_killed,
           count(*) FILTER (WHERE number_of_motorist_killed > 0)::BIGINT AS crashes_with_motorist_killed
    FROM crashes
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
    """
).df()

measure_defs = {
    1: (
        "motorists_killed",
        "motorists killed",
        "Annual number of motorists recorded killed in police-reported NYC crashes",
        "Motorists recorded killed in police-reported NYC crashes",
        "Annual count of motorists, 2013–2025",
    ),
    2: (
        "crashes_with_motorist_killed",
        "crashes with motorist killed",
        "Annual number of police-reported NYC crashes with at least one motorist recorded killed",
        "Crashes with at least one motorist recorded killed in NYC",
        "Annual crash-event count, 2013–2025",
    ),
}

for option_id, (column, value_label, metric_title, chart_title, y_label) in measure_defs.items():
    plotted = annual[["year", column]].rename(columns={column: "value"})
    plotted.insert(1, "metric", value_label)
    plotted.to_csv(OUT / f"values_{option_id}.csv", index=False)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    if option_id == 1:
        ax.plot(plotted["year"], plotted["value"], marker="o", linewidth=2, color="#16697A")
    else:
        ax.bar(plotted["year"], plotted["value"], color="#489FB5", width=0.72)
    ax.set_title(f"{metric_title}\nNYC crashes, calendar years 2013–2025", loc="left", fontsize=13, weight="bold", pad=18)
    ax.text(
        0,
        1.015,
        "Limitation: no vehicle-miles traveled are recorded; this is not a per-mile risk rate.",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=9,
        color="#444444",
    )
    ax.set_xlabel("Calendar year of crash")
    ax.set_ylabel(y_label)
    ax.set_xticks(plotted["year"])
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / f"option_{option_id}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
