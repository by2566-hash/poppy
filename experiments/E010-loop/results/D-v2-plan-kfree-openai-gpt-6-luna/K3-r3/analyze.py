from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "crashes.parquet"
OUT = ROOT / "out"


def load_annual_counts():
    con = duckdb.connect()
    df = con.execute(
        """
        SELECT EXTRACT(YEAR FROM crash_date)::INTEGER AS year,
               SUM(number_of_cyclist_killed)::BIGINT AS cyclist_deaths,
               SUM(number_of_motorist_killed)::BIGINT AS motorist_deaths
        FROM read_parquet(?)
        WHERE crash_date >= DATE '2013-01-01'
          AND crash_date < DATE '2026-01-01'
        GROUP BY year
        ORDER BY year
        """,
        [str(DATA)],
    ).df()
    con.close()
    return df


def option_1(counts):
    values = counts[["year", "cyclist_deaths", "motorist_deaths"]]
    values.to_csv(OUT / "values_1.csv", index=False)

    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    ax.plot(values["year"], values["motorist_deaths"], marker="o", linewidth=2.2, label="Motorist deaths", color="#d55e00")
    ax.plot(values["year"], values["cyclist_deaths"], marker="o", linewidth=2.2, label="Cyclist deaths", color="#0072b2")
    ax.set_title("Annual reported cyclist and motorist deaths in NYC, 2013–2025", loc="left", fontsize=14, weight="bold", pad=16)
    ax.text(0, 1.02, "Counts summed across police-reported crashes; counts, not exposure-adjusted rates. Full-year date spans observed.", transform=ax.transAxes, fontsize=9, color="#555555", va="bottom")
    ax.set_xlabel("Crash year")
    ax.set_ylabel("Reported deaths")
    ax.set_xticks(values["year"])
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", color="#dddddd", linewidth=0.7)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, ncol=2, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def option_2(counts):
    values = counts[["year", "cyclist_deaths", "motorist_deaths"]].copy()
    values["motorist_minus_cyclist_deaths"] = values["motorist_deaths"] - values["cyclist_deaths"]
    values.to_csv(OUT / "values_2.csv", index=False)

    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    bars = ax.bar(values["year"], values["motorist_minus_cyclist_deaths"], color="#7b3294", width=0.72)
    ax.axhline(0, color="#333333", linewidth=0.9)
    ax.set_title("Annual motorist-minus-cyclist death gap in NYC, 2013–2025", loc="left", fontsize=14, weight="bold", pad=16)
    ax.text(0, 1.02, "Difference in reported death counts across police-reported crashes; not an exposure-adjusted rate. Full-year date spans observed.", transform=ax.transAxes, fontsize=9, color="#555555", va="bottom")
    ax.set_xlabel("Crash year")
    ax.set_ylabel("Motorist deaths minus cyclist deaths")
    ax.set_xticks(values["year"])
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", color="#dddddd", linewidth=0.7)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    for bar, gap in zip(bars, values["motorist_minus_cyclist_deaths"]):
        ax.annotate(f"{gap:+,}", (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 3 if gap >= 0 else -12), textcoords="offset points",
                    ha="center", va="bottom" if gap >= 0 else "top", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def main():
    counts = load_annual_counts()
    option_1(counts)
    option_2(counts)


if __name__ == "__main__":
    main()
