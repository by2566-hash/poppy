import csv
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
SOURCE = str(ROOT / "data" / "crashes.parquet").replace("'", "''")


def main():
    con = duckdb.connect()
    annual = con.execute(
        f"""
        SELECT EXTRACT(YEAR FROM crash_date)::INTEGER AS year,
               COUNT(*)::BIGINT AS crash_rows,
               SUM(number_of_motorist_killed)::BIGINT AS motorist_deaths,
               SUM(number_of_cyclist_killed)::BIGINT AS cyclist_deaths
        FROM read_parquet('{SOURCE}')
        WHERE crash_date >= DATE '2013-01-01'
          AND crash_date < DATE '2026-01-01'
        GROUP BY year
        ORDER BY year
        """
    ).fetchall()

    records = []
    for year, crash_rows, motorist_deaths, cyclist_deaths in annual:
        for road_user, deaths in (
            ("Motorist", motorist_deaths),
            ("Cyclist", cyclist_deaths),
        ):
            records.append(
                {
                    "year": year,
                    "road_user": road_user,
                    "deaths": deaths,
                    "crash_rows": crash_rows,
                    "deaths_per_1000_crashes": deaths * 1000.0 / crash_rows,
                }
            )

    for option_id, metric_column, metric_label, title_metric, file_name in (
        (1, "deaths", "Recorded deaths", "Recorded deaths", "option_1.png"),
        (
            2,
            "deaths_per_1000_crashes",
            "Deaths per 1,000 crash rows",
            "Deaths per 1,000 reported crashes",
            "option_2.png",
        ),
    ):
        values_path = OUT / f"values_{option_id}.csv"
        with values_path.open("w", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=("year", "road_user", "metric", "deaths", "crash_rows"),
            )
            writer.writeheader()
            for row in records:
                writer.writerow(
                    {
                        "year": row["year"],
                        "road_user": row["road_user"],
                        "metric": row[metric_column],
                        "deaths": row["deaths"],
                        "crash_rows": row["crash_rows"],
                    }
                )

        fig, ax = plt.subplots(figsize=(10.5, 6.0))
        for road_user, color, marker in (
            ("Motorist", "#2369a1", "o"),
            ("Cyclist", "#d46a27", "s"),
        ):
            subset = [row for row in records if row["road_user"] == road_user]
            ax.plot(
                [row["year"] for row in subset],
                [row[metric_column] for row in subset],
                label=road_user,
                color=color,
                marker=marker,
                linewidth=2,
                markersize=4.5,
            )
        ax.set_title(
            f"{title_metric} by road-user type\n"
            "Police-reported NYC motor vehicle crashes, 2013–2025",
            loc="left",
            fontsize=14,
            fontweight="bold",
        )
        ax.set_xlabel("Calendar year")
        ax.set_ylabel(metric_label)
        ax.set_xticks([row[0] for row in annual])
        ax.grid(axis="y", alpha=0.25)
        ax.legend(frameon=False, ncol=2, loc="upper left")
        if option_id == 1:
            footnote = (
                "Complete calendar years; recorded killed-column totals. "
                "Counts do not adjust for motorist/cyclist exposure."
            )
        else:
            footnote = (
                "Annual deaths divided by all reported crash rows; not an exposure- or risk-adjusted rate."
            )
        fig.tight_layout(rect=(0, 0.09, 1, 1))
        fig.text(0.01, 0.025, footnote, fontsize=9, color="#555555")
        fig.savefig(OUT / file_name, dpi=180, bbox_inches="tight")
        plt.close(fig)


if __name__ == "__main__":
    main()
