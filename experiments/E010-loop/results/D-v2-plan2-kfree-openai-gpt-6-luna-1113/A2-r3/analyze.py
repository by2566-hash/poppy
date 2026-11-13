from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
YEAR_START, YEAR_END = 2013, 2025
PERIODS = ["Day", "Night"]
COLS_BY_OPTION = {
    1: ["number_of_persons_injured", "number_of_persons_killed"],
    2: ["number_of_persons_injured", "number_of_persons_killed"],
    3: ["number_of_pedestrians_injured", "number_of_pedestrians_killed"],
}
CHART_TITLES = {
    1: "Total casualties per 100 NYC reported crashes",
    2: "Reported crashes involving injury or death",
    3: "Pedestrian casualties per 100 NYC reported crashes",
}
SUBTITLES = {
    1: "NYC motor-vehicle crashes, complete calendar years 2013–2025",
    2: "Share of NYC motor-vehicle crashes, complete calendar years 2013–2025",
    3: "NYC motor-vehicle crashes, complete calendar years 2013–2025",
}
NOTES = {
    1: "Per-crash measure; no traffic exposure is available. Midnight records are retained.",
    2: "Among reported crashes, not per trip or vehicle-mile. Midnight records are retained.",
    3: "No pedestrian exposure measure is available. Midnight records are retained.",
}
Y_LABELS = {
    1: "Persons injured or killed per 100 crashes",
    2: "Crashes with ≥1 person injured or killed (%)",
    3: "Pedestrians injured or killed per 100 crashes",
}


for option_id, outcome_columns in COLS_BY_OPTION.items():
    selected_columns = ["crash_date", "crash_time", *outcome_columns]
    projection = ", ".join(f'"{column}"' for column in selected_columns)
    data = duckdb.connect().execute(
        f"SELECT {projection} FROM read_parquet(?)", [str(ROOT / "data" / "crashes.parquet")]
    ).fetchdf()

    data["year"] = pd.to_datetime(data["crash_date"]).dt.year
    data = data.loc[data["year"].between(YEAR_START, YEAR_END)].copy()
    data = data.loc[data["crash_time"].notna() & data[outcome_columns].notna().all(axis=1)].copy()
    data["hour"] = data["crash_time"].map(lambda value: value.hour)
    data["period"] = data["hour"].map(lambda hour: "Night" if hour >= 20 or hour < 6 else "Day")

    if option_id == 2:
        data["event"] = (data[outcome_columns[0]] > 0) | (data[outcome_columns[1]] > 0)
        measure_label = "crashes with injury/death"
    else:
        data["event"] = data[outcome_columns[0]] + data[outcome_columns[1]]
        measure_label = "casualties"

    records = []
    for period in PERIODS:
        group = data.loc[data["period"] == period]
        denominator = len(group)
        outcome_total = group["event"].sum()
        value = (100 * outcome_total / denominator) if denominator else float("nan")
        records.append(
            {
                "period": period,
                "crashes_in_denominator": denominator,
                "outcome_measure": measure_label,
                "outcome_total": int(outcome_total),
                "metric_value": value,
            }
        )

    values = pd.DataFrame(records)
    values.to_csv(OUT / f"values_{option_id}.csv", index=False, float_format="%.6f")

    fig, ax = plt.subplots(figsize=(8.4, 5.1))
    colors = ["#3572A5", "#D05A47"]
    bars = ax.bar(values["period"], values["metric_value"], color=colors, width=0.58)
    for bar, value in zip(bars, values["metric_value"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.2f}%" if option_id == 2 else f"{value:.2f}",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )
    ax.set_title(CHART_TITLES[option_id], loc="left", fontsize=15, fontweight="bold", pad=25)
    ax.text(
        0,
        1.015,
        SUBTITLES[option_id] + " · Night 8 p.m.–5:59 a.m.; day 6 a.m.–7:59 p.m.",
        transform=ax.transAxes,
        fontsize=9,
        color="#555555",
    )
    ax.set_ylabel(Y_LABELS[option_id])
    ax.set_xlabel("")
    ax.grid(axis="y", color="#dddddd", linewidth=0.7)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(0, -0.19, NOTES[option_id], transform=ax.transAxes, fontsize=8.7, color="#555555")
    fig.tight_layout()
    fig.savefig(OUT / f"option_{option_id}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
