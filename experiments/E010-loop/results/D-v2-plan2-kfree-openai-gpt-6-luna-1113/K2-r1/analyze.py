from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
PARQUET = ROOT / "data" / "crashes.parquet"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def load_daily_counts():
    con = duckdb.connect()
    return con.execute(
        """
        SELECT
            year(crash_date) AS year,
            strftime(crash_date, '%A') AS weekday,
            COUNT(*) AS crashes
        FROM read_parquet(?)
        WHERE crash_date BETWEEN DATE '2013-01-01' AND DATE '2025-12-31'
        GROUP BY year, weekday
        ORDER BY year, weekday
        """,
        [str(PARQUET)],
    ).fetchdf()


def make_pooled_count_chart(daily):
    values = (
        daily.groupby("weekday", as_index=False)["crashes"].sum()
        .set_index("weekday")
        .reindex(WEEKDAYS)
        .reset_index()
    )
    values.to_csv(OUT / "values_1.csv", index=False)

    fig, ax = plt.subplots(figsize=(10, 5.7))
    bars = ax.bar(values["weekday"], values["crashes"], color="#2c78a8")
    ax.bar_label(bars, labels=[f"{int(x):,}" for x in values["crashes"]], padding=3, fontsize=9)
    ax.set_title("Police-reported NYC crash counts by weekday, 2013–2025", pad=30, fontsize=15)
    ax.text(
        0.5,
        1.015,
        "Pooled counts are not exposure-adjusted and can conceal year-to-year changes.",
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=9,
        color="#444444",
    )
    ax.set_xlabel("Day of week (from crash date)")
    ax.set_ylabel("Number of reported crashes")
    ax.tick_params(axis="x", rotation=20)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def make_annual_share_chart(daily):
    annual = daily.copy()
    annual["year_total"] = annual.groupby("year")["crashes"].transform("sum")
    annual["share_percent"] = annual["crashes"] / annual["year_total"] * 100
    annual = annual.sort_values(["year", "weekday"], key=lambda col: col.map({d: i for i, d in enumerate(WEEKDAYS)}) if col.name == "weekday" else col)
    annual[["year", "weekday", "crashes", "year_total", "share_percent"]].to_csv(
        OUT / "values_2.csv", index=False, float_format="%.6f"
    )

    pivot = annual.pivot(index="year", columns="weekday", values="share_percent").reindex(columns=WEEKDAYS)
    fig, ax = plt.subplots(figsize=(11, 6.2))
    colors = ["#2c78a8", "#e18727", "#3b9b68", "#c64b4b", "#7b61a8", "#4c9da6", "#a8774e"]
    for weekday, color in zip(WEEKDAYS, colors):
        ax.plot(pivot.index, pivot[weekday], marker="o", markersize=3.5, linewidth=1.7, label=weekday, color=color)
    ax.set_title("Weekday share of NYC crashes within each year, 2013–2025", pad=30, fontsize=15)
    ax.text(
        0.5,
        1.015,
        "Each year's denominator is that year's reported crashes; shares are not exposure-adjusted.",
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=9,
        color="#444444",
    )
    ax.set_xlabel("Crash year")
    ax.set_ylabel("Share of that year's reported crashes (%)")
    ax.set_xticks(list(range(2013, 2026)))
    ax.tick_params(axis="x", rotation=35)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(title="Day of week", ncol=4, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.2))
    fig.tight_layout()
    fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    data = load_daily_counts()
    make_pooled_count_chart(data)
    make_annual_share_chart(data)
