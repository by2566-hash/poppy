import csv
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


OUT = Path("./out")
DATA = "./data/crashes.parquet"


def build_values(frame: pd.DataFrame, option: int) -> pd.DataFrame:
    frame = frame.copy()
    frame["year"] = pd.to_datetime(frame["crash_date"]).dt.year
    frame = frame[frame["year"].between(2013, 2025)]
    frame = frame[frame["number_of_motorist_killed"].notna()]
    frame = frame[frame["number_of_motorist_killed"] >= 0]
    frame["year"] = frame["year"].astype(int)

    annual = frame.groupby("year", as_index=False).agg(
        crashes=("number_of_motorist_killed", "size"),
        motorist_deaths=("number_of_motorist_killed", "sum"),
        fatal_motorist_crashes=("number_of_motorist_killed", lambda s: int((s > 0).sum())),
    )
    years = pd.DataFrame({"year": range(2013, 2026)})
    annual = years.merge(annual, on="year", how="left").fillna(0)

    if option == 1:
        metric = "Motorists killed (count)"
        numerator = annual["motorist_deaths"]
        denominator = ["None (count)"] * len(annual)
        value = numerator
    elif option == 2:
        metric = "Crashes with a motorist killed (% of reported crashes)"
        numerator = annual["fatal_motorist_crashes"]
        denominator = annual["crashes"]
        value = numerator / denominator * 100
    else:
        metric = "Motorist deaths per 1,000 reported crashes"
        numerator = annual["motorist_deaths"]
        denominator = annual["crashes"]
        value = numerator / denominator * 1000

    return pd.DataFrame(
        {
            "year": annual["year"],
            "metric": metric,
            "numerator": numerator,
            "denominator": denominator,
            "value": value,
            "crashes_in_population": annual["crashes"],
        }
    )


def chart(values: pd.DataFrame, option: int, y_label: str, subtitle: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(values["year"], values["value"], marker="o", linewidth=2, color="#176B87")
    ax.set_xticks(values["year"])
    ax.tick_params(axis="x", rotation=45)
    ax.set_xlabel("Crash year")
    ax.set_ylabel(y_label)
    ax.grid(axis="y", alpha=0.25)
    ax.set_title(
        {
            1: "Annual motorist deaths in police-reported NYC crashes",
            2: "Share of police-reported NYC crashes with a motorist killed",
            3: "Motorist deaths per 1,000 police-reported NYC crashes",
        }[option],
        loc="left",
        fontsize=14,
        weight="bold",
        pad=28,
    )
    ax.text(0, 1.015, subtitle, transform=ax.transAxes, fontsize=9, va="bottom", color="#555555")
    fig.tight_layout()
    fig.savefig(OUT / f"option_{option}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


con = duckdb.connect()
source = con.execute(
    "SELECT crash_date, number_of_motorist_killed FROM read_parquet(?)",
    [DATA],
).fetchdf()

settings = {
    1: ("Motorists killed", "Counts are not adjusted for miles driven; the file contains no travel-exposure denominator."),
    2: ("Crashes with a motorist killed (%)", "Crash share is not risk per mile; the file contains no travel-exposure denominator."),
    3: ("Motorist deaths per 1,000 crashes", "Crash-normalized deaths are not risk per mile; the file contains no travel-exposure denominator."),
}

for option in (1, 2, 3):
    values = build_values(source, option)
    values.to_csv(OUT / f"values_{option}.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    ylabel, limitation = settings[option]
    chart(values, option, ylabel, limitation)

print("Created option_1–3.png and values_1–3.csv")
