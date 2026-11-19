from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
PARQUET = ROOT / "data" / "crashes.parquet"
parquet_path = str(PARQUET).replace("'", "''")
con = duckdb.connect()
con.execute(f"CREATE VIEW crashes AS SELECT * FROM read_parquet('{parquet_path}')")

base_filter = """UPPER(TRIM(borough)) = 'BROOKLYN'
                 AND crash_date >= DATE '2013-01-01'
                 AND crash_date < DATE '2026-01-01'
                 AND number_of_pedestrians_injured IS NOT NULL
                 AND number_of_pedestrians_killed IS NOT NULL"""

series = {
    1: {
        "sql": f"""SELECT YEAR(crash_date) AS year,
                           SUM(number_of_pedestrians_injured + number_of_pedestrians_killed)
                             AS pedestrian_casualties
                    FROM crashes WHERE {base_filter}
                    GROUP BY year ORDER BY year""",
        "title": "Pedestrians injured or killed in Brooklyn motor-vehicle crashes",
        "subtitle": "Annual recorded casualties, 2013–2025 · counts, not exposure-adjusted risk; 2026 partial year omitted",
        "ylabel": "Pedestrian casualties recorded",
        "column": "pedestrian_casualties",
        "color": "#135D8C",
        "filename": "Pedestrian casualties",
    },
    2: {
        "sql": f"""SELECT YEAR(crash_date) AS year, COUNT(*) AS casualty_crashes
                    FROM crashes WHERE {base_filter}
                      AND (number_of_pedestrians_injured > 0
                           OR number_of_pedestrians_killed > 0)
                    GROUP BY year ORDER BY year""",
        "title": "Brooklyn crashes with a recorded pedestrian injury or death",
        "subtitle": "One count per police-reported crash record, 2013–2025 · not exposure-adjusted risk; 2026 partial year omitted",
        "ylabel": "Crashes with a pedestrian casualty",
        "column": "casualty_crashes",
        "color": "#B34A34",
        "filename": "Crashes with pedestrian casualties",
    },
    3: {
        "sql": """SELECT YEAR(crash_date) AS year,
                           SUM(number_of_pedestrians_killed) AS pedestrian_deaths
                    FROM crashes
                    WHERE UPPER(TRIM(borough)) = 'BROOKLYN'
                      AND crash_date >= DATE '2013-01-01'
                      AND crash_date < DATE '2026-01-01'
                      AND number_of_pedestrians_killed IS NOT NULL
                    GROUP BY year ORDER BY year""",
        "title": "Pedestrian deaths recorded in Brooklyn motor-vehicle crashes",
        "subtitle": "Annual recorded deaths, 2013–2025 · counts, not exposure-adjusted risk; 2026 partial year omitted",
        "ylabel": "Pedestrian deaths recorded",
        "column": "pedestrian_deaths",
        "color": "#76518A",
        "filename": "Pedestrian deaths",
    },
}

for plan_id, spec in series.items():
    data = con.execute(spec["sql"]).df()
    data["year"] = data["year"].astype(int)
    data[spec["column"]] = data[spec["column"]].astype("int64")
    data.to_csv(OUT / f"values_{plan_id}.csv", index=False)

    fig, ax = plt.subplots(figsize=(10.5, 5.8), layout="constrained")
    ax.plot(data["year"], data[spec["column"]], color=spec["color"], linewidth=2.8,
            marker="o", markersize=5.5)
    ax.fill_between(data["year"], data[spec["column"]], color=spec["color"], alpha=0.08)
    ax.annotate(f"{data.iloc[0][spec['column']]:,}",
                (data.iloc[0]["year"], data.iloc[0][spec["column"]]),
                xytext=(5, 10), textcoords="offset points", color=spec["color"],
                fontsize=9, fontweight="bold")
    ax.annotate(f"{data.iloc[-1][spec['column']]:,}",
                (data.iloc[-1]["year"], data.iloc[-1][spec["column"]]),
                xytext=(-5, 10), textcoords="offset points", ha="right",
                color=spec["color"], fontsize=9, fontweight="bold")
    ax.set_title(spec["title"], loc="left", fontsize=15, fontweight="bold", pad=30)
    ax.text(0, 1.015, spec["subtitle"], transform=ax.transAxes, ha="left",
            va="bottom", fontsize=9, color="#555555")
    ax.set_xlabel("Crash year")
    ax.set_ylabel(spec["ylabel"])
    ax.set_xticks(data["year"])
    ax.tick_params(axis="x", rotation=45)
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", color="#D9DEE3", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(OUT / f"option_{plan_id}.png", dpi=180, facecolor="white")
    plt.close(fig)

con.close()
