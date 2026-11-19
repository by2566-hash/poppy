from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter


ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "crashes.parquet"

con = duckdb.connect()
df = con.execute(
    """SELECT CAST(crash_date AS VARCHAR) AS crash_date,
              CAST(crash_time AS VARCHAR) AS crash_time,
              number_of_persons_injured,
              number_of_persons_killed
       FROM read_parquet(?)""",
    [str(DATA)],
).fetchdf()
df["date"] = pd.to_datetime(df["crash_date"], errors="coerce")
df["time"] = pd.to_datetime(df["crash_time"], format="mixed", errors="coerce")
df["injured"] = pd.to_numeric(df["number_of_persons_injured"], errors="coerce")
df["killed"] = pd.to_numeric(df["number_of_persons_killed"], errors="coerce")

# The dataset's observed calendar range (2012–2026) is the plan's year scope.
base = df[df["date"].notna() & df["time"].notna()].copy()
base["period"] = base["time"].dt.hour.map(
    lambda hour: "Night" if hour >= 20 or hour < 6 else "Day"
)
base["period"] = pd.Categorical(base["period"], categories=["Night", "Day"], ordered=True)

plans = {
    1: {
        "columns": ["injured", "killed"],
        "kind": "share_injury_or_death",
        "title": "Share of complete-case crashes with injury or death",
        "population": "NYC police-reported motor-vehicle crashes, 2012–2026",
        "unit": "Percent of crashes",
        "subtitle": "Night = 8pm–5:59am; day = 6am–7:59pm. Crash severity only; no traffic exposure. 2012 and 2026 are partial years.",
        "color": "#285f8f",
    },
    2: {
        "columns": ["injured", "killed"],
        "kind": "mean_casualties",
        "title": "Mean people injured or killed per complete-case crash",
        "population": "NYC police-reported motor-vehicle crashes, 2012–2026",
        "unit": "People per crash",
        "subtitle": "Night = 8pm–5:59am; day = 6am–7:59pm. Casualties per crash, not per trip; no traffic exposure. 2012 and 2026 are partial years.",
        "color": "#8a4d19",
    },
    3: {
        "columns": ["killed"],
        "kind": "share_fatal",
        "title": "Share of complete-case crashes with a death",
        "population": "NYC police-reported motor-vehicle crashes, 2012–2026",
        "unit": "Percent of crashes",
        "subtitle": "Night = 8pm–5:59am; day = 6am–7:59pm. Fatal-crash involvement only; no traffic exposure. 2012 and 2026 are partial years.",
        "color": "#793945",
    },
}

for option_id, plan in plans.items():
    eligible = base.copy()
    for column in plan["columns"]:
        eligible = eligible[eligible[column].notna() & (eligible[column] >= 0)]

    records = []
    for period in ["Night", "Day"]:
        part = eligible[eligible["period"] == period]
        crashes = len(part)
        if plan["kind"] == "share_injury_or_death":
            numerator = int(((part["injured"] + part["killed"]) > 0).sum())
            value = numerator / crashes * 100 if crashes else float("nan")
            metric = "crashes_with_injury_or_death_share"
        elif plan["kind"] == "mean_casualties":
            numerator = int((part["injured"] + part["killed"]).sum())
            value = numerator / crashes if crashes else float("nan")
            metric = "injured_plus_killed_people_per_crash"
        else:
            numerator = int((part["killed"] > 0).sum())
            value = numerator / crashes * 100 if crashes else float("nan")
            metric = "crashes_with_death_share"
        records.append(
            {
                "period": period,
                "metric": metric,
                "numerator": numerator,
                "denominator_crashes": crashes,
                "value": value,
                "unit": plan["unit"],
            }
        )
    values = pd.DataFrame(records)
    values.to_csv(OUT / f"values_{option_id}.csv", index=False, float_format="%.8f")

    fig, ax = plt.subplots(figsize=(8.2, 5.3))
    heights = values["value"]
    bars = ax.bar(values["period"].astype(str), heights, color=plan["color"], width=0.56)
    ax.set_ylabel(plan["unit"])
    if plan["unit"].startswith("Percent"):
        ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:g}%"))
    ax.set_title(f"{plan['title']}\n{plan['population']}", fontsize=14, pad=16)
    ax.grid(axis="y", color="#d9d9d9", linewidth=0.7)
    ax.set_axisbelow(True)
    for bar, height in zip(bars, heights):
        label = f"{height:.2f}%" if plan["unit"].startswith("Percent") else f"{height:.3f}"
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), label,
                ha="center", va="bottom", fontsize=11, fontweight="bold")
    fig.text(0.5, 0.025, plan["subtitle"], ha="center", va="bottom", fontsize=8.3, wrap=True)
    fig.tight_layout(rect=(0, 0.10, 1, 1))
    fig.savefig(OUT / f"option_{option_id}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

print("Saved three plotted datasets and charts.")
