from pathlib import Path
import json

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


OUT = Path("out")
OUT.mkdir(exist_ok=True)
DATA = "data/crashes.parquet"
START_YEAR = 2013
END_YEAR = 2025  # 2026 is partial in the supplied file.

query = f"""
SELECT
    year(crash_date) AS year,
    sum(coalesce(number_of_pedestrians_injured, 0))::BIGINT AS pedestrians_injured,
    sum(coalesce(number_of_pedestrians_killed, 0))::BIGINT AS pedestrians_killed,
    count(*)::BIGINT AS all_reported_crashes,
    sum(CASE WHEN coalesce(number_of_pedestrians_injured, 0) > 0
                  OR coalesce(number_of_pedestrians_killed, 0) > 0
             THEN 1 ELSE 0 END)::BIGINT AS crashes_with_pedestrian_harm
FROM read_parquet('{DATA}')
WHERE upper(trim(borough)) = 'BROOKLYN'
  AND crash_date >= DATE '{START_YEAR}-01-01'
  AND crash_date < DATE '{END_YEAR + 1}-01-01'
GROUP BY 1
ORDER BY 1
"""
df = duckdb.connect().execute(query).fetchdf()
expected_years = list(range(START_YEAR, END_YEAR + 1))
assert df["year"].astype(int).tolist() == expected_years
df["pedestrian_harm_share_percent"] = (
    100 * df["crashes_with_pedestrian_harm"] / df["all_reported_crashes"]
)


plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 17,
    "axes.titleweight": "bold",
    "axes.labelsize": 10,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def make_line_chart(option_id, title, subtitle, column, ylabel, color,
                    number_format, filename, highlight_year=2025):
    fig, ax = plt.subplots(figsize=(10, 5.6))
    x = df["year"].astype(int)
    y = df[column]
    ax.plot(x, y, color=color, linewidth=3, marker="o", markersize=5)
    ax.fill_between(x, y, 0, color=color, alpha=0.08)
    ax.set_title(title, loc="left", pad=19)
    ax.text(0, 1.015, subtitle, transform=ax.transAxes, ha="left",
            va="bottom", color="#4b5563", fontsize=10)
    ax.set_ylabel(ylabel, color="#374151")
    ax.set_xticks(x)
    ax.set_xticklabels([str(year) for year in x], rotation=0)
    ax.set_xlim(2012.7, 2025.5)
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", color="#d1d5db", linewidth=0.8)
    ax.grid(axis="x", visible=False)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#9ca3af")
    ax.tick_params(axis="y", length=0, pad=7, colors="#4b5563")
    ax.tick_params(axis="x", length=0, pad=8, colors="#4b5563")
    for year in (2013, highlight_year):
        row = df.loc[df["year"] == year].iloc[0]
        value = row[column]
        ax.annotate(number_format(value), (year, value),
                    xytext=(0, 12 if year == 2013 else -23),
                    textcoords="offset points", ha="center", fontsize=10,
                    fontweight="bold", color=color)
    fig.text(0.01, 0.018,
             "Source: NYC Police-Reported Motor Vehicle Collisions; Brooklyn borough; calendar years 2013–2025. "
             "2026 excluded because year-to-date.",
             ha="left", fontsize=8, color="#6b7280")
    fig.tight_layout(rect=(0, 0.055, 1, 0.98))
    fig.savefig(OUT / filename, dpi=180, bbox_inches="tight")
    plt.close(fig)


make_line_chart(
    1,
    "Brooklyn pedestrian injuries remain below 2013",
    "People reported injured in crashes, by year",
    "pedestrians_injured", "Pedestrians injured", "#176b87",
    lambda value: f"{int(value):,}", "option_1.png")
make_line_chart(
    2,
    "Brooklyn pedestrian deaths have not fallen since 2013",
    "People reported killed in crashes, by year",
    "pedestrians_killed", "Pedestrians killed", "#b33b36",
    lambda value: f"{int(value):,}", "option_2.png")
make_line_chart(
    3,
    "Pedestrian-harm crashes make up a larger share in Brooklyn",
    "Crashes with a pedestrian injured or killed, as a share of all reported crashes",
    "pedestrian_harm_share_percent", "Share of reported crashes (%)", "#8a5a14",
    lambda value: f"{value:.1f}%", "option_3.png")


values1 = df[["year", "pedestrians_injured"]]
values2 = df[["year", "pedestrians_killed"]]
values3 = df[["year", "crashes_with_pedestrian_harm", "all_reported_crashes",
              "pedestrian_harm_share_percent"]]
values1.to_csv(OUT / "values_1.csv", index=False)
values2.to_csv(OUT / "values_2.csv", index=False)
values3.to_csv(OUT / "values_3.csv", index=False, float_format="%.4f")


start, end = df.iloc[0], df.iloc[-1]
injury_change = (end.pedestrians_injured / start.pedestrians_injured - 1) * 100
death_change = (end.pedestrians_killed / start.pedestrians_killed - 1) * 100
share_change = end.pedestrian_harm_share_percent - start.pedestrian_harm_share_percent
options = {
    "options": [
        {
            "id": 1,
            "metric": "Annual number of pedestrians injured",
            "denominator": "None; annual count of pedestrians reported injured (pedestrians killed reported separately)",
            "grouping": "Calendar year, Brooklyn, 2013–2025",
            "chart_type": "Line chart",
            "reason": "Injury counts show the annual nonfatal harm burden directly and are easy to compare across years.",
            "probability": 0.35,
            "answer": f"The file cannot establish whether risk per walking trip improved; it shows reported pedestrian injuries fell {abs(injury_change):.1f}%, from {int(start.pedestrians_injured):,} in 2013 to {int(end.pedestrians_injured):,} in 2025, after rising from the 2020 low."
            ,
            "interpretation": "This framing answers whether the annual number of pedestrians injured has declined: it was lower in 2025 than in 2013, after rising from a 2020 low. Counts are a direct measure of nonfatal harm and provide a clear year-to-year trend. It does not measure risk per walking trip or explain changes in pedestrian exposure."
        },
        {
            "id": 2,
            "metric": "Annual number of pedestrians killed",
            "denominator": "None; annual count of pedestrians reported killed",
            "grouping": "Calendar year, Brooklyn, 2013–2025",
            "chart_type": "Line chart",
            "reason": "Fatalities isolate the most severe pedestrian outcome, which can move differently from injuries.",
            "probability": 0.30,
            "answer": f"The file cannot establish whether risk per walking trip improved; reported pedestrian deaths rose {death_change:.1f}%, from {int(start.pedestrians_killed)} in 2013 to {int(end.pedestrians_killed)} in 2025."
            ,
            "interpretation": "This framing answers the question for the most severe outcome: the 2025 death count exceeded 2013, despite substantial year-to-year variation. Fatalities are a distinct and consequential safety outcome, so it is defensible to examine them separately. The count does not show pedestrian risk per trip or whether the trend reflects changes in walking volume."
        },
        {
            "id": 3,
            "metric": "Share of reported Brooklyn crashes with a pedestrian injured or killed",
            "denominator": "All police-reported motor vehicle crashes with Brooklyn recorded as borough",
            "grouping": "Calendar year, Brooklyn, 2013–2025",
            "chart_type": "Line chart",
            "reason": "The share places pedestrian-harm crashes in the context of all reported crashes, rather than showing counts alone.",
            "probability": 0.35,
            "answer": f"The file cannot establish whether risk per walking trip improved; pedestrian-harm crashes rose from {start.pedestrian_harm_share_percent:.1f}% of reported Brooklyn crashes in 2013 to {end.pedestrian_harm_share_percent:.1f}% in 2025 (+{share_change:.1f} percentage points)."
            ,
            "interpretation": "This framing answers whether pedestrian-injury-or-death crashes became a larger part of Brooklyn's reported crash record: their share rose from 2013 to 2025. It is a defensible relative measure when the overall number of recorded crashes changes substantially. It is not a pedestrian exposure rate and misses pedestrian-involved crashes with no reported pedestrian injury or death."
        }
    ]
}
assert abs(sum(option["probability"] for option in options["options"]) - 1) < 1e-9
(OUT / "options.json").write_text(json.dumps(options, indent=2) + "\n")

print(df.to_string(index=False))
print(f"2013–2025 injury change: {injury_change:.1f}%")
print(f"2013–2025 death change: {death_change:.1f}%")
print(f"2013–2025 harm-share change: {share_change:.2f} percentage points")
