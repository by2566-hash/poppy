from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
PARQUET = (ROOT / "data" / "crashes.parquet").as_posix().replace("'", "''")


def main():
    con = duckdb.connect()
    data = con.execute(
        f"""
        SELECT year(crash_date) AS year,
               sum(number_of_motorist_killed)::BIGINT AS motorist_deaths,
               count(*)::BIGINT AS eligible_crashes,
               count(*) FILTER (WHERE number_of_motorist_killed > 0)::BIGINT
                   AS crashes_with_motorist_death
        FROM read_parquet('{PARQUET}')
        WHERE crash_date >= DATE '2013-01-01'
          AND crash_date < DATE '2026-01-01'
          AND number_of_motorist_killed IS NOT NULL
        GROUP BY year
        ORDER BY year
        """
    ).df()
    con.close()

    data["motorist_deaths_per_100k_crashes"] = (
        data["motorist_deaths"] / data["eligible_crashes"] * 100_000
    )
    data["share_crashes_with_motorist_death_pct"] = (
        data["crashes_with_motorist_death"] / data["eligible_crashes"] * 100
    )

    specs = [
        {
            "id": 1,
            "column": "motorist_deaths",
            "label": "Motorists killed",
            "title": "Motorists killed per calendar year\nNYC police-reported crashes with known motorist-death counts, 2013–2025",
            "filename": "option_1.png",
            "values": "values_1.csv",
            "format": "{:.0f}",
        },
        {
            "id": 2,
            "column": "motorist_deaths_per_100k_crashes",
            "label": "Motorist deaths per 100,000 reported crashes",
            "title": "Motorist deaths per 100,000 reported crashes\nNYC police-reported crashes with known motorist-death counts, 2013–2025",
            "filename": "option_2.png",
            "values": "values_2.csv",
            "format": "{:.2f}",
        },
        {
            "id": 3,
            "column": "share_crashes_with_motorist_death_pct",
            "label": "Crashes with at least one motorist killed (%)",
            "title": "Share of crashes with at least one motorist killed\nNYC police-reported crashes with known motorist-death counts, 2013–2025",
            "filename": "option_3.png",
            "values": "values_3.csv",
            "format": "{:.3f}%",
        },
    ]

    for spec in specs:
        plotted = pd.DataFrame({
            "year": data["year"],
            "value": data[spec["column"]],
            "motorist_deaths": data["motorist_deaths"],
            "eligible_crashes": data["eligible_crashes"],
            "crashes_with_motorist_death": data["crashes_with_motorist_death"],
        })
        plotted.to_csv(OUT / spec["values"], index=False, float_format="%.8f")

        fig, ax = plt.subplots(figsize=(10.5, 6.1))
        ax.plot(plotted["year"], plotted["value"], marker="o", linewidth=2.2, color="#176B87")
        ax.set_title(spec["title"], loc="left", fontsize=13, fontweight="bold", pad=16)
        ax.set_xlabel("Crash year")
        ax.set_ylabel(spec["label"])
        ax.set_xticks(plotted["year"])
        ax.tick_params(axis="x", rotation=45)
        ax.grid(axis="y", color="#d8e0e5", linewidth=0.8)
        ax.spines[["top", "right"]].set_visible(False)
        for year in (2013, 2025):
            row = plotted.loc[plotted["year"] == year].iloc[0]
            ax.annotate(
                spec["format"].format(row["value"]),
                (row["year"], row["value"]),
                xytext=(0, 10),
                textcoords="offset points",
                ha="center",
                fontsize=9,
                fontweight="bold",
            )
        fig.text(
            0.01,
            0.015,
            "Limitation: crash records contain no vehicle-miles-traveled exposure; this is not a per-mile risk.",
            fontsize=9,
            color="#4b5563",
        )
        fig.tight_layout(rect=(0, 0.05, 1, 1))
        fig.savefig(OUT / spec["filename"], dpi=180, bbox_inches="tight")
        plt.close(fig)


if __name__ == "__main__":
    main()
