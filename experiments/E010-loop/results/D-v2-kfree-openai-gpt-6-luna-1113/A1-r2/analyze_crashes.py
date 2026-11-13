from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "data" / "crashes.parquet"
START_YEAR = 2013
END_YEAR = 2025  # Last complete calendar year in the supplied data.

con = duckdb.connect()
query = """
    SELECT
        year(crash_date)::INTEGER AS year,
        sum(coalesce(number_of_pedestrians_injured, 0))::BIGINT AS pedestrians_injured,
        sum(coalesce(number_of_pedestrians_killed, 0))::BIGINT AS pedestrians_killed
    FROM read_parquet(?)
    WHERE borough = 'BROOKLYN'
      AND crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
"""
df = con.execute(query, [str(DATA)]).fetchdf()
years = pd.DataFrame({"year": range(START_YEAR, END_YEAR + 1)})
df = years.merge(df, on="year", how="left").fillna(0)
df[["pedestrians_injured", "pedestrians_killed"]] = df[
    ["pedestrians_injured", "pedestrians_killed"]
].astype("int64")
df["pedestrian_casualties"] = df["pedestrians_injured"] + df["pedestrians_killed"]

series = [
    (1, "pedestrians_injured", "Pedestrians injured", "People injured", "#176B87"),
    (2, "pedestrians_killed", "Pedestrians killed", "People killed", "#B33A3A"),
    (3, "pedestrian_casualties", "Pedestrian casualties", "People injured or killed", "#6C5B7B"),
]

print(df.to_string(index=False))
print("Year-over-year baseline comparisons:")
for _, column, *_ in series:
    start = int(df.loc[df.year == START_YEAR, column].iloc[0])
    end = int(df.loc[df.year == END_YEAR, column].iloc[0])
    change = (end / start - 1) * 100 if start else float("nan")
    print(f"{column}: {start} in 2013; {end} in 2025; change {change:.1f}%")

for option_id, column, title, ylabel, color in series:
    values = df[["year", column]].rename(columns={column: "count"})
    values.to_csv(ROOT / f"values_{option_id}.csv", index=False)

    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    ax.plot(values["year"], values["count"], color=color, linewidth=2.8, marker="o", markersize=5)
    ax.fill_between(values["year"], values["count"], color=color, alpha=0.10)
    ax.set_title(f"Brooklyn: {title}, 2013–2025", loc="left", fontsize=16, weight="bold", pad=16)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Crash year")
    ax.set_xticks(values["year"])
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", color="#d9d9d9", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    for row in (values.iloc[0], values.iloc[-1]):
        ax.annotate(
            f"{int(row['count']):,}",
            (int(row["year"]), int(row["count"])),
            xytext=(0, 10),
            textcoords="offset points",
            ha="center",
            fontsize=10,
            weight="bold",
            color=color,
        )
    fig.text(
        0.01,
        0.015,
        "Pedestrian counts in police-reported crashes; not adjusted for pedestrian traffic or population. 2026 omitted (partial year).",
        fontsize=8.5,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(ROOT / f"option_{option_id}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
