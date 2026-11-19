from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


OUT = Path("out")
con = duckdb.connect()
base = """
    SELECT year(crash_date) AS year,
           CASE WHEN crash_time = TIME '00:00:00' THEN 'Midnight / possible default'
                WHEN crash_time < TIME '06:00:00' OR crash_time >= TIME '20:00:00' THEN 'Night'
                ELSE 'Day' END AS time_group,
           number_of_persons_injured AS injured,
           number_of_persons_killed AS killed
    FROM read_parquet('data/crashes.parquet')
    WHERE year(crash_date) BETWEEN 2013 AND 2025
      AND crash_time IS NOT NULL
      AND number_of_persons_injured IS NOT NULL
      AND number_of_persons_killed IS NOT NULL
"""

injury_share = con.execute(
    f"""
    SELECT year, time_group,
           count(*) AS eligible_crashes,
           sum(CASE WHEN injured + killed > 0 THEN 1 ELSE 0 END) AS crashes_with_injury_or_death,
           100.0 * sum(CASE WHEN injured + killed > 0 THEN 1 ELSE 0 END) / count(*) AS injury_or_death_crash_share_pct
    FROM ({base})
    GROUP BY year, time_group
    ORDER BY year, CASE time_group WHEN 'Day' THEN 1 WHEN 'Night' THEN 2 ELSE 3 END
    """
).fetchdf()
injury_share.to_csv(OUT / "values_1.csv", index=False, float_format="%.6f")

casualty_rate = con.execute(
    f"""
    SELECT year, time_group,
           count(*) AS eligible_crashes,
           sum(injured) AS persons_injured,
           sum(killed) AS persons_killed,
           sum(injured + killed) AS injured_plus_killed_people,
           100.0 * sum(injured + killed) / count(*) AS injured_plus_killed_per_100_crashes
    FROM ({base})
    GROUP BY year, time_group
    ORDER BY year, CASE time_group WHEN 'Day' THEN 1 WHEN 'Night' THEN 2 ELSE 3 END
    """
).fetchdf()
casualty_rate.to_csv(OUT / "values_2.csv", index=False, float_format="%.6f")

colors = {"Day": "#2471A3", "Night": "#C0392B", "Midnight / possible default": "#777777"}
styles = {"Day": "-", "Night": "-", "Midnight / possible default": "--"}


def draw_chart(data, y_column, ylabel, title, subtitle, output, y_format):
    fig, ax = plt.subplots(figsize=(12, 6.8))
    for group in ("Day", "Night", "Midnight / possible default"):
        part = data[data["time_group"] == group]
        ax.plot(
            part["year"], part[y_column], marker="o", markersize=4.5,
            linewidth=2, linestyle=styles[group], color=colors[group], label=group,
        )
    ax.set_title(title, loc="left", fontsize=15, weight="bold", pad=26)
    ax.text(0, 1.015, subtitle, transform=ax.transAxes, fontsize=9.5, color="#444444", va="bottom")
    ax.set_xlabel("Calendar year")
    ax.set_ylabel(ylabel)
    ax.set_ylim(bottom=0)
    ax.set_xticks(sorted(data["year"].unique()))
    ax.tick_params(axis="x", rotation=45)
    ax.yaxis.set_major_formatter(y_format)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False, ncol=3, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / output, dpi=180, bbox_inches="tight")
    plt.close(fig)


from matplotlib.ticker import FuncFormatter

draw_chart(
    injury_share, "injury_or_death_crash_share_pct", "Crashes with injury or death (%)",
    "Share of injury-or-death crashes among NYC police-reported crashes, 2013–2025",
    "Eligible crashes with known person-injury and death counts; night = 20:00–23:59 and 00:01–05:59, day = 06:00–19:59. 00:00 isolated as possible default; not a per-trip risk measure.",
    "option_1.png", FuncFormatter(lambda value, _: f"{value:.0f}%"),
)
draw_chart(
    casualty_rate, "injured_plus_killed_per_100_crashes", "Injured + killed people per 100 crashes",
    "Injured and killed people per 100 NYC police-reported crashes, 2013–2025",
    "Eligible crashes with known person-injury and death counts; night = 20:00–23:59 and 00:01–05:59, day = 06:00–19:59. 00:00 isolated as possible default; no traffic-exposure denominator.",
    "option_2.png", FuncFormatter(lambda value, _: f"{value:.1f}"),
)
