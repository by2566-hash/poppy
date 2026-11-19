import csv
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "crashes.parquet"
START_YEAR = 2013
END_YEAR = 2025

OPTIONS = {
    1: {
        "column": "number_of_pedestrians_injured",
        "value_column": "pedestrians_injured",
        "metric": "Annual pedestrians injured",
        "title": "Pedestrians injured in police-reported Brooklyn crashes",
        "color": "#147D83",
        "ylabel": "Pedestrians injured (count)",
    },
    2: {
        "column": "number_of_pedestrians_killed",
        "value_column": "pedestrians_killed",
        "metric": "Annual pedestrians killed",
        "title": "Pedestrians killed in police-reported Brooklyn crashes",
        "color": "#B4443C",
        "ylabel": "Pedestrians killed (count)",
    },
    3: {
        "column": "number_of_pedestrians_injured + number_of_pedestrians_killed",
        "value_column": "pedestrian_casualties",
        "metric": "Annual pedestrians injured or killed",
        "title": "Pedestrians injured or killed in police-reported Brooklyn crashes",
        "color": "#6653A3",
        "ylabel": "Pedestrian casualties (count)",
    },
}


def write_csv(path, fieldnames, rows):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    con = duckdb.connect()
    for option_id, spec in OPTIONS.items():
        if option_id == 3:
            measure = (
                "SUM(number_of_pedestrians_injured + number_of_pedestrians_killed)"
            )
        else:
            measure = f"SUM({spec['column']})"
        result = con.execute(
            f"""
            SELECT YEAR(crash_date) AS year, {measure} AS value
            FROM read_parquet(?)
            WHERE lower(trim(borough)) = 'brooklyn'
              AND crash_date >= DATE '{START_YEAR}-01-01'
              AND crash_date < DATE '{END_YEAR + 1}-01-01'
              AND {spec['column'] if option_id != 3 else 'number_of_pedestrians_injured'} IS NOT NULL
              {"AND number_of_pedestrians_killed IS NOT NULL" if option_id == 3 else ""}
            GROUP BY YEAR(crash_date)
            ORDER BY year
            """,
            [str(DATA)],
        ).fetchdf()
        result["year"] = result["year"].astype(int)
        result["value"] = result["value"].astype(int)
        result = result[(result["year"] >= START_YEAR) & (result["year"] <= END_YEAR)]
        if result["year"].tolist() != list(range(START_YEAR, END_YEAR + 1)):
            raise ValueError(f"Option {option_id} did not return all planned years")

        value_path = OUT / f"values_{option_id}.csv"
        write_csv(
            value_path,
            ["year", spec["value_column"]],
            [
                {"year": int(row.year), spec["value_column"]: int(row.value)}
                for row in result.itertuples(index=False)
            ],
        )

        plt.rcParams.update(
            {
                "font.family": "DejaVu Sans",
                "axes.spines.top": False,
                "axes.spines.right": False,
                "axes.titleweight": "bold",
            }
        )
        fig, ax = plt.subplots(figsize=(11.5, 6.4))
        fig.subplots_adjust(left=0.09, right=0.93, bottom=0.16, top=0.79)
        fig.patch.set_facecolor("#FBFAF7")
        ax.set_facecolor("#FBFAF7")
        ax.plot(
            result["year"],
            result["value"],
            color=spec["color"],
            linewidth=3,
            marker="o",
            markersize=5.5,
            markerfacecolor="#FBFAF7",
            markeredgewidth=2,
        )
        ax.fill_between(result["year"], result["value"], color=spec["color"], alpha=0.08)
        ax.set_xlim(2012.7, 2025.3)
        ax.set_xticks(list(range(START_YEAR, END_YEAR + 1)))
        ax.tick_params(axis="x", labelrotation=0, labelsize=9)
        ax.set_ylabel(spec["ylabel"], fontsize=11, labelpad=10)
        ax.set_xlabel("Crash year", fontsize=11, labelpad=10)
        ax.grid(axis="y", color="#D9D7D0", linewidth=0.8)
        ax.set_axisbelow(True)
        ax.spines["left"].set_color("#B9B7B0")
        ax.spines["bottom"].set_color("#B9B7B0")
        ax.set_ylim(bottom=0)
        final = result.iloc[-1]
        ax.annotate(
            f"{int(final.value):,}",
            (int(final.year), int(final.value)),
            xytext=(8, 0),
            textcoords="offset points",
            color=spec["color"],
            fontweight="bold",
            fontsize=10,
            va="center",
        )
        fig.text(
            0.09,
            0.95,
            spec["title"],
            ha="left",
            va="top",
            fontsize=16,
            fontweight="bold",
            color="#242424",
        )
        fig.text(
            0.09,
            0.885,
            "Annual count, 2013–2025. Not exposure-adjusted; borough-unassigned crashes are excluded, and partial 2026 is omitted.",
            ha="left",
            va="top",
            fontsize=9.5,
            color="#55534D",
        )
        fig.text(
            0.09,
            0.025,
            "Source: NYC police-reported motor vehicle crashes. Each point sums the recorded pedestrian count for crashes assigned to Brooklyn.",
            fontsize=8.5,
            color="#55534D",
        )
        fig.savefig(OUT / f"option_{option_id}.png", dpi=180, bbox_inches="tight")
        plt.close(fig)


if __name__ == "__main__":
    main()
