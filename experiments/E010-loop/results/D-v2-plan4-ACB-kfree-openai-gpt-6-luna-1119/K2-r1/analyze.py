import csv
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
DATA = str(ROOT / "data" / "crashes.parquet")
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DAY_CASE = "CASE EXTRACT(ISODOW FROM crash_date) " + " ".join(
    f"WHEN {index} THEN '{day}'" for index, day in enumerate(WEEKDAYS, start=1)
) + " END"


def write_csv(path: Path, frame: pd.DataFrame) -> None:
    frame.to_csv(path, index=False, quoting=csv.QUOTE_MINIMAL)


def main() -> None:
    data_sql_path = DATA.replace("'", "''")
    con = duckdb.connect()
    con.execute(f"CREATE VIEW crashes AS SELECT crash_date FROM read_parquet('{data_sql_path}')")
    population_filter = "crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'"

    counts = con.execute(
        f"""
        SELECT {DAY_CASE} AS weekday, count(*) AS crash_rows
        FROM crashes
        WHERE {population_filter}
        GROUP BY weekday
        ORDER BY MIN(EXTRACT(ISODOW FROM crash_date))
        """
    ).df()
    counts["weekday"] = pd.Categorical(counts["weekday"], WEEKDAYS, ordered=True)
    counts = counts.sort_values("weekday").reset_index(drop=True)
    counts["weekday"] = counts["weekday"].astype(str)
    write_csv(OUT / "values_1.csv", counts)

    fig, ax = plt.subplots(figsize=(10, 5.7))
    bars = ax.bar(counts["weekday"], counts["crash_rows"], color="#2878B5")
    ax.bar_label(bars, labels=[f"{value:,}" for value in counts["crash_rows"]], padding=3, fontsize=8)
    fig.suptitle("NYC Police-Reported Crash Rows by Weekday (2013–2025)", y=0.985, fontsize=15)
    fig.text(
        0.5,
        0.925,
        "One row counted once by crash_date weekday; raw counts are not exposure-adjusted and reporting completeness is unverified",
        ha="center",
        fontsize=9,
    )
    ax.set_ylabel("Crash records")
    ax.set_xlabel("Weekday of crash_date")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout(rect=[0, 0, 1, 0.87])
    plt.savefig(OUT / "option_1.png", dpi=170, bbox_inches="tight")
    plt.close()

    annual = con.execute(
        f"""
        WITH daily AS (
            SELECT year(crash_date) AS year, {DAY_CASE} AS weekday,
                   count(*) AS crash_rows
            FROM crashes
            WHERE {population_filter}
            GROUP BY year, weekday
        ), yearly AS (
            SELECT year, sum(crash_rows) AS annual_crash_rows
            FROM daily GROUP BY year
        )
        SELECT daily.year, daily.weekday, daily.crash_rows,
               yearly.annual_crash_rows,
               100.0 * daily.crash_rows / yearly.annual_crash_rows AS share_pct
        FROM daily JOIN yearly USING (year)
        ORDER BY year, weekday
        """
    ).df()
    # Enforce a clear weekday ordering in the output and chart.
    annual["weekday"] = pd.Categorical(annual["weekday"], WEEKDAYS, ordered=True)
    annual = annual.sort_values(["year", "weekday"]).reset_index(drop=True)
    annual["weekday"] = annual["weekday"].astype(str)
    write_csv(OUT / "values_2.csv", annual)

    fig, ax = plt.subplots(figsize=(11, 6.2))
    for day in WEEKDAYS:
        subset = annual.loc[annual["weekday"] == day]
        ax.plot(subset["year"], subset["share_pct"], marker="o", linewidth=1.7, markersize=3.7, label=day)
    fig.suptitle("Annual Share of NYC Police-Reported Crash Rows by Weekday (2013–2025)", y=0.985, fontsize=15)
    fig.text(
        0.5,
        0.925,
        "Each point is weekday rows ÷ that year's rows; shares are not exposure-adjusted and reporting completeness is unverified",
        ha="center",
        fontsize=9,
    )
    ax.set_ylabel("Share of that year's crash records (%)")
    ax.set_xlabel("Year of crash_date")
    ax.set_xticks(range(2013, 2026))
    ax.tick_params(axis="x", labelrotation=45)
    ax.grid(alpha=0.25)
    ax.legend(ncol=4, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.18))
    fig.tight_layout(rect=[0, 0.05, 1, 0.87])
    plt.savefig(OUT / "option_2.png", dpi=170, bbox_inches="tight")
    plt.close()
    con.close()


if __name__ == "__main__":
    main()
