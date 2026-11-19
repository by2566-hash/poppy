from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DATA = (ROOT / "data" / "crashes.parquet").as_posix().replace("'", "''")


def main() -> None:
    con = duckdb.connect()
    annual = con.execute(
        f"""
        SELECT EXTRACT(YEAR FROM crash_date)::INTEGER AS year,
               SUM(number_of_motorist_killed)::BIGINT AS motorist_deaths,
               SUM(number_of_cyclist_killed)::BIGINT AS cyclist_deaths
        FROM read_parquet('{DATA}')
        WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
        GROUP BY year
        ORDER BY year
        """
    ).df()
    con.close()
    annual = annual.set_index("year").reindex(range(2013, 2026)).rename_axis("year").reset_index()
    annual[["motorist_deaths", "cyclist_deaths"]] = annual[
        ["motorist_deaths", "cyclist_deaths"]
    ].fillna(0).astype("int64")
    annual["combined_motorist_cyclist_deaths"] = (
        annual["motorist_deaths"] + annual["cyclist_deaths"]
    )
    denominator = annual["combined_motorist_cyclist_deaths"].replace(0, np.nan)
    annual["motorist_share_pct"] = annual["motorist_deaths"] / denominator * 100
    annual["cyclist_share_pct"] = annual["cyclist_deaths"] / denominator * 100

    # Option 1: annual absolute reported death counts.
    values1 = annual[["year", "motorist_deaths", "cyclist_deaths"]].copy()
    values1.to_csv(OUT / "values_1.csv", index=False)
    fig, ax = plt.subplots(figsize=(10, 5.8))
    ax.plot(annual["year"], annual["motorist_deaths"], marker="o", linewidth=2.3,
            color="#285f9e", label="Motorist deaths")
    ax.plot(annual["year"], annual["cyclist_deaths"], marker="o", linewidth=2.3,
            color="#d17c19", label="Cyclist deaths")
    ax.set_title("Annual reported motorist and cyclist deaths in NYC crashes\nAll police-reported NYC motor vehicle crashes, 2013–2025",
                 loc="left", fontsize=14, fontweight="bold", pad=16)
    fig.text(0.125, 0.91,
             "Counts, not rates; date endpoints span full years, but daily completeness is not verified.",
             fontsize=9, color="#555555")
    ax.set_xlabel("Crash year")
    ax.set_ylabel("Reported deaths (count)")
    ax.set_xticks(annual["year"])
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", color="#dddddd", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, ncol=2, loc="upper left")
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # Option 2: annual composition of the combined motorist/cyclist death total.
    values2 = annual[[
        "year", "motorist_deaths", "cyclist_deaths",
        "combined_motorist_cyclist_deaths", "motorist_share_pct", "cyclist_share_pct",
    ]].copy()
    values2.to_csv(OUT / "values_2.csv", index=False)
    fig, ax = plt.subplots(figsize=(10, 5.8))
    ax.bar(annual["year"], annual["motorist_share_pct"], width=0.72,
           color="#285f9e", label="Motorist share")
    ax.bar(annual["year"], annual["cyclist_share_pct"], width=0.72,
           bottom=annual["motorist_share_pct"], color="#d17c19", label="Cyclist share")
    ax.set_title("Share of combined motorist and cyclist deaths in NYC crashes\nAll police-reported NYC motor vehicle crashes, 2013–2025",
                 loc="left", fontsize=14, fontweight="bold", pad=16)
    fig.text(0.125, 0.91,
             "Within these two types only; shares are not risk rates, and daily completeness is not verified.",
             fontsize=9, color="#555555")
    ax.set_xlabel("Crash year")
    ax.set_ylabel("Share of motorist + cyclist deaths (%)")
    ax.set_ylim(0, 100)
    ax.set_xticks(annual["year"])
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", color="#dddddd", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, ncol=2, loc="upper left")
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
