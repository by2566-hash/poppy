import json
from pathlib import Path

import duckdb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
YEARS = (2013, 2025)
con = duckdb.connect()
plans = {i: json.loads((OUT / f"plan_{i}.json").read_text()) for i in (1, 2, 3)}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titleweight": "bold",
    "axes.titlesize": 17,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
})


def annual_data(column):
    return con.execute(
        f"""SELECT year(crash_date)::INTEGER AS year,
                   sum({column})::BIGINT AS total,
                   count(*)::BIGINT AS eligible_brooklyn_crash_records
            FROM read_parquet('{DATA.as_posix()}')
            WHERE upper(trim(borough)) = 'BROOKLYN'
              AND crash_date >= DATE '2013-01-01'
              AND crash_date < DATE '2026-01-01'
              AND {column} IS NOT NULL
            GROUP BY year ORDER BY year"""
    ).df()


def draw_chart(option_id, df, metric_col, title, subtitle, y_label, color,
               as_rate=False):
    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    fig.subplots_adjust(left=0.095, right=0.975, top=0.79, bottom=0.18)
    years = df["year"].tolist()
    vals = df[metric_col].astype(float).tolist()
    ax.plot(years, vals, color=color, linewidth=2.8, marker="o", markersize=5.5)
    ax.fill_between(years, vals, 0, color=color, alpha=0.09)
    ax.set_title(title, loc="left", pad=22)
    ax.text(0, 1.012, subtitle, transform=ax.transAxes, ha="left", va="bottom",
            color="#505a65", fontsize=9.4)
    ax.set_ylabel(y_label, color="#303943")
    # The annual x-axis ticks are self-labeled by year; omit an axis label to
    # leave room for the source/coverage footnote below the plot.
    ax.set_xticks(years)
    ax.tick_params(axis="x", rotation=0, length=0, pad=7)
    ax.tick_params(axis="y", length=0, pad=7)
    ax.grid(axis="y", color="#dce2e8", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.margins(x=0.035, y=0.16)
    if as_rate:
        ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.1f}"))
    else:
        ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    first, last = vals[0], vals[-1]
    pct = (last / first - 1) * 100 if first else float("nan")
    label_fmt = (lambda v: f"{v:,.1f}") if as_rate else (lambda v: f"{v:,.0f}")
    ax.annotate(f"2013  {label_fmt(first)}", (years[0], first), xytext=(8, 11),
                textcoords="offset points", color=color, fontsize=9, fontweight="bold")
    ax.annotate(f"2025  {label_fmt(last)}\n{pct:+.1f}% vs 2013",
                (years[-1], last), xytext=(-8, 12), textcoords="offset points",
                ha="right", color=color, fontsize=9, fontweight="bold")
    fig.text(0.01, 0.012,
             "Source: NYC police-reported motor vehicle crashes. 2026 omitted because the file covers only Jan 1–Jun 11.",
             ha="left", color="#626d78", fontsize=8)
    fig.savefig(OUT / f"option_{option_id}.png", dpi=180, facecolor="white")
    plt.close(fig)


injuries = annual_data("number_of_pedestrians_injured")
deaths = annual_data("number_of_pedestrians_killed")

injuries.to_csv(OUT / "values_1.csv", index=False)
draw_chart(
    1, injuries, "total",
    "Pedestrians injured in police-reported Brooklyn crashes",
    "Annual people injured · 2013–2025 · counts do not account for walking exposure",
    "Pedestrians injured", "#1769aa",
)

deaths.to_csv(OUT / "values_2.csv", index=False)
draw_chart(
    2, deaths, "total",
    "Pedestrians killed in police-reported Brooklyn crashes",
    "Annual people killed · 2013–2025 · counts do not account for walking exposure",
    "Pedestrians killed", "#b23a48",
)

rate = injuries.copy()
rate["injuries_per_1000_crash_records"] = (
    rate["total"] * 1000 / rate["eligible_brooklyn_crash_records"]
)
rate = rate.rename(columns={"total": "pedestrians_injured"})
rate.to_csv(OUT / "values_3.csv", index=False)
draw_chart(
    3, rate, "injuries_per_1000_crash_records",
    "Pedestrian injuries per 1,000 reported Brooklyn crashes",
    "Annual rate · 2013–2025 · denominator is crash records, not pedestrian trips",
    "Pedestrians injured per 1,000 crash records", "#17806b", as_rate=True,
)
