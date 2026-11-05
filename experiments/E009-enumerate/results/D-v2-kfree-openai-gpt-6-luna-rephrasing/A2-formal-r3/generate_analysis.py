import json
import os

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


DATA = "data/crashes.parquet"
OUT = "out"
os.makedirs(OUT, exist_ok=True)

con = duckdb.connect()
query = """
WITH classified AS (
    SELECT
        CASE WHEN hour(crash_time) >= 19 OR hour(crash_time) < 7
             THEN 'Night (7pm–6:59am)' ELSE 'Day (7am–6:59pm)' END AS period,
        coalesce(number_of_persons_injured, 0) AS injured,
        coalesce(number_of_persons_killed, 0) AS killed
    FROM read_parquet(?)
)
SELECT period,
       count(*) AS crashes,
       count(*) FILTER (WHERE injured > 0 OR killed > 0) AS injury_or_fatal_crashes,
       sum(injured) AS persons_injured,
       sum(killed) AS persons_killed
FROM classified
GROUP BY period
"""
data = con.execute(query, [DATA]).fetchdf()
order = ["Day (7am–6:59pm)", "Night (7pm–6:59am)"]
data["period"] = pd.Categorical(data["period"], categories=order, ordered=True)
data = data.sort_values("period").reset_index(drop=True)
data["injury_or_fatal_crash_pct"] = 100 * data["injury_or_fatal_crashes"] / data["crashes"]
data["casualties"] = data["persons_injured"] + data["persons_killed"]
data["casualties_per_crash"] = data["casualties"] / data["crashes"]

plt.rcParams.update({"font.family": "DejaVu Sans", "axes.titleweight": "bold"})
colors = ["#4C78A8", "#E45756"]


def save_bar(option_id, values, column, title, ylabel, fmt, csv_columns):
    values[csv_columns].to_csv(f"{OUT}/values_{option_id}.csv", index=False)
    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    bars = ax.bar(values["period"].astype(str), values[column], color=colors, width=0.58)
    ax.set_title(title, loc="left", fontsize=15, pad=14)
    ax.set_ylabel(ylabel)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#D9DEE5", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", labelsize=10)
    ax.bar_label(bars, labels=[fmt.format(x) for x in values[column]], padding=4, fontsize=11)
    ax.margins(y=0.14)
    fig.text(0.01, 0.01, "NYC police-reported crashes, Jul 1, 2012–Jun 11, 2026. No adjustment for traffic volume or travel exposure.", fontsize=8, color="#555555")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(f"{OUT}/option_{option_id}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


save_bar(
    1, data, "crashes",
    "Police-reported crashes by time of day",
    "Crash count", "{:,.0f}",
    ["period", "crashes"],
)
save_bar(
    2, data, "injury_or_fatal_crash_pct",
    "Share of crashes with an injury or fatality",
    "Crashes with ≥1 person injured or killed (%)", "{:.1f}%",
    ["period", "crashes", "injury_or_fatal_crashes", "injury_or_fatal_crash_pct"],
)
save_bar(
    3, data, "casualties_per_crash",
    "People injured or killed per reported crash",
    "Injured + killed people per crash", "{:.3f}",
    ["period", "crashes", "persons_injured", "persons_killed", "casualties", "casualties_per_crash"],
)

print(data.to_string(index=False))
