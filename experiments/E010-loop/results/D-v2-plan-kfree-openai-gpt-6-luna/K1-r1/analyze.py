from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "crashes.parquet"

annual = duckdb.sql(
    """
    SELECT EXTRACT(YEAR FROM crash_date)::INT AS year,
           SUM(number_of_pedestrians_killed)::BIGINT AS pedestrians_killed
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
    """,
    params=[str(DATA)],
).df()

years = list(range(2013, 2026))
annual = (
    annual.set_index("year")
    .reindex(years, fill_value=0)
    .rename_axis("year")
    .reset_index()
)
annual["pedestrians_killed"] = annual["pedestrians_killed"].astype("int64")

limitation = (
    "Police-reported crashes and recorded fatalities only; observed date endpoints span each year, "
    "but reporting completeness is unverified."
)

for option_id, chart_type in ((1, "bar"), (2, "line")):
    values_path = OUT / f"values_{option_id}.csv"
    annual.to_csv(values_path, index=False)

    fig, ax = plt.subplots(figsize=(10, 6))
    if chart_type == "bar":
        bars = ax.bar(annual["year"], annual["pedestrians_killed"], color="#2878B5", width=0.72)
        ax.bar_label(bars, labels=[f"{v:,}" for v in annual["pedestrians_killed"]], padding=3, fontsize=8)
    else:
        ax.plot(
            annual["year"],
            annual["pedestrians_killed"],
            color="#2878B5",
            marker="o",
            linewidth=2,
            markersize=5,
        )
        for year, value in zip(annual["year"], annual["pedestrians_killed"]):
            ax.annotate(f"{value:,}", (year, value), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=8)

    ax.set_title(
        "Pedestrians killed per year in NYC police-reported motor vehicle crashes\n"
        "Annual number of pedestrian fatalities, 2013–2025",
        fontsize=13,
        pad=14,
    )
    ax.set_xlabel("Year")
    ax.set_ylabel("Pedestrians killed (people)")
    ax.set_xticks(years)
    ax.tick_params(axis="x", rotation=45)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{int(value):,}"))
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", alpha=0.25)
    fig.text(0.5, 0.015, f"Limitation: {limitation}", ha="center", va="bottom", fontsize=8, wrap=True)
    fig.tight_layout(rect=(0, 0.055, 1, 1))
    fig.savefig(OUT / f"option_{option_id}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
