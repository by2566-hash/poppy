import csv
import duckdb
import matplotlib.pyplot as plt


DATA = "./data/crashes.parquet"
START = "2013-01-01"
END = "2026-01-01"

con = duckdb.connect()
annual = con.execute(
    f"""SELECT YEAR(crash_date) AS year,
               COUNT(*) AS reported_crashes,
               SUM(number_of_motorist_killed) AS motorist_deaths
        FROM read_parquet('{DATA}')
        WHERE crash_date >= DATE '{START}' AND crash_date < DATE '{END}'
        GROUP BY YEAR(crash_date)
        ORDER BY year"""
).fetchdf()
annual["motorist_deaths_per_1000_crashes"] = annual["motorist_deaths"] / annual["reported_crashes"] * 1000

with open("./out/values_1.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["year", "motorist_deaths"])
    writer.writerows((int(row.year), int(row.motorist_deaths)) for row in annual.itertuples())

fig, ax = plt.subplots(figsize=(10, 5.8))
ax.plot(annual["year"], annual["motorist_deaths"], marker="o", linewidth=2, color="#176B87")
ax.set_title("Annual motorist deaths recorded in NYC police-reported crashes, 2013–2025", pad=22)
ax.text(0.5, 1.015, "Crash records have no miles-driven denominator; full-year reporting is not independently verified",
        transform=ax.transAxes, ha="center", va="bottom", fontsize=9, color="#555555")
ax.set_xlabel("Calendar year of crash")
ax.set_ylabel("Motorist deaths recorded")
ax.set_xticks(annual["year"])
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig("./out/option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

with open("./out/values_2.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["year", "motorist_deaths", "reported_crashes", "motorist_deaths_per_1000_crashes"])
    writer.writerows((int(row.year), int(row.motorist_deaths), int(row.reported_crashes), f"{row.motorist_deaths_per_1000_crashes:.6f}") for row in annual.itertuples())

fig, ax = plt.subplots(figsize=(10, 5.8))
ax.plot(annual["year"], annual["motorist_deaths_per_1000_crashes"], marker="o", linewidth=2, color="#A34A28")
ax.set_title("Motorist deaths per 1,000 NYC police-reported crashes, 2013–2025", pad=22)
ax.text(0.5, 1.015, "This is a per-crash measure, not risk per mile; full-year reporting is not independently verified",
        transform=ax.transAxes, ha="center", va="bottom", fontsize=9, color="#555555")
ax.set_xlabel("Calendar year of crash")
ax.set_ylabel("Motorist deaths per 1,000 reported crashes")
ax.set_xticks(annual["year"])
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig("./out/option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)
