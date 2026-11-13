import duckdb
import matplotlib.pyplot as plt
import pandas as pd


con = duckdb.connect()
values = con.execute(
    """
    SELECT
        EXTRACT(YEAR FROM crash_date)::INTEGER AS year,
        SUM(number_of_pedestrians_killed)::BIGINT AS pedestrians_killed
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
    """,
    ["./data/crashes.parquet"],
).df()
values["year"] = values["year"].astype(int)
values["pedestrians_killed"] = values["pedestrians_killed"].astype("int64")
values.to_csv("./out/values_1.csv", index=False)

fig, ax = plt.subplots(figsize=(11, 6.4))
ax.bar(values["year"].astype(str), values["pedestrians_killed"], color="#1f6b8a")
ax.set_title(
    "Pedestrians killed each year in NYC police-reported motor vehicle crashes\n"
    "Annual count of pedestrians killed · crashes dated 2013–2025",
    loc="left",
    fontsize=15,
    pad=18,
)
ax.set_xlabel("Calendar year of crash")
ax.set_ylabel("Pedestrians killed (people)")
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)
ax.text(
    0,
    -0.19,
    "Limitation: police-reported crashes only; observed date bounds span each year, but reporting completeness is not established.",
    transform=ax.transAxes,
    fontsize=9,
    color="#444444",
)
fig.tight_layout()
fig.savefig("./out/option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)
