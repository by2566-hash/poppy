import csv

import duckdb
import matplotlib.pyplot as plt


DATA = "data/crashes.parquet"
START_YEAR = 2013
END_YEAR = 2025

con = duckdb.connect()
rows = con.execute(
    f"""SELECT year(crash_date) AS year,
               sum(number_of_pedestrians_killed)::BIGINT AS pedestrians_killed
        FROM read_parquet('{DATA}')
        WHERE crash_date >= DATE '{START_YEAR}-01-01'
          AND crash_date < DATE '{END_YEAR + 1}-01-01'
        GROUP BY year
        ORDER BY year"""
).fetchall()

with open("out/values_1.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["year", "pedestrians_killed"])
    writer.writerows(rows)

years = [row[0] for row in rows]
values = [row[1] for row in rows]
fig, ax = plt.subplots(figsize=(11, 6))
ax.plot(years, values, marker="o", linewidth=2, color="#205493")
ax.set_xticks(years)
ax.set_xticklabels(years, rotation=45, ha="right")
ax.set_ylabel("Pedestrians killed (people)")
ax.set_xlabel("Crash year")
ax.set_title(
    "Pedestrians killed per year in police-reported NYC motor vehicle crashes\n"
    "Annual total; all crashes with a date in 2013–2025"
)
fig.text(
    0.5,
    0.015,
    "Limitation: counts fatalities recorded in police-reported crashes; unreported crashes are not represented.",
    ha="center",
    fontsize=9,
)
ax.grid(axis="y", alpha=0.25)
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig("out/option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)
