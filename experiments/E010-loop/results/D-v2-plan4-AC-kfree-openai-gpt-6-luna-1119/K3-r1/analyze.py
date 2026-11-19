import csv
import duckdb
import matplotlib.pyplot as plt
import numpy as np


SOURCE = "data/crashes.parquet"
YEARS = list(range(2013, 2026))
con = duckdb.connect()
annual = con.execute(
    f"""SELECT year(crash_date) AS year,
               sum(number_of_motorist_killed)::BIGINT AS motorist_deaths,
               sum(number_of_cyclist_killed)::BIGINT AS cyclist_deaths
        FROM read_parquet('{SOURCE}')
        WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
          AND number_of_motorist_killed IS NOT NULL
          AND number_of_cyclist_killed IS NOT NULL
        GROUP BY year ORDER BY year"""
).fetchall()
rows = {int(year): (int(motorist), int(cyclist)) for year, motorist, cyclist in annual}
if set(rows) != set(YEARS):
    raise ValueError(f"Unexpected annual coverage: {sorted(rows)}")

# Option 1: absolute annual counts, by road-user group.
with open("out/values_1.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["year", "road_user_group", "deaths"])
    for year in YEARS:
        motorist, cyclist = rows[year]
        writer.writerow([year, "Motorist", motorist])
        writer.writerow([year, "Cyclist", cyclist])

fig, ax = plt.subplots(figsize=(13, 6.5))
x = np.arange(len(YEARS))
width = 0.38
motorist_values = [rows[year][0] for year in YEARS]
cyclist_values = [rows[year][1] for year in YEARS]
ax.bar(x - width / 2, motorist_values, width, label="Motorist", color="#2463A6")
ax.bar(x + width / 2, cyclist_values, width, label="Cyclist", color="#E07832")
ax.set_title("Annual motorist and cyclist deaths\nNYC police-reported motor vehicle crashes, 2013–2025", loc="left", weight="bold")
ax.set_ylabel("Reported deaths (count)")
ax.set_xticks(x, YEARS, rotation=45)
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)
ax.legend(frameon=False, ncol=2, loc="upper right")
fig.text(0.01, 0.015, "Annual sums of the corresponding death-count fields; file dates span Jan 1–Dec 31 in each year. Counts are not adjusted for population or travel exposure.", fontsize=9)
fig.tight_layout(rect=(0, 0.055, 1, 1))
fig.savefig("out/option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Option 2: each group's share of that year's combined motorist and cyclist deaths.
share_rows = []
with open("out/values_2.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["year", "motorist_deaths", "cyclist_deaths", "combined_motorist_cyclist_deaths", "motorist_share_percent", "cyclist_share_percent"])
    for year in YEARS:
        motorist, cyclist = rows[year]
        combined = motorist + cyclist
        if combined == 0:
            motorist_share = cyclist_share = 0.0
        else:
            motorist_share = motorist / combined * 100
            cyclist_share = cyclist / combined * 100
        writer.writerow([year, motorist, cyclist, combined, f"{motorist_share:.6f}", f"{cyclist_share:.6f}"])
        share_rows.append((motorist_share, cyclist_share))

fig, ax = plt.subplots(figsize=(13, 6.5))
motorist_shares = [pair[0] for pair in share_rows]
cyclist_shares = [pair[1] for pair in share_rows]
ax.bar(x, motorist_shares, label="Motorist", color="#2463A6")
ax.bar(x, cyclist_shares, bottom=motorist_shares, label="Cyclist", color="#E07832")
ax.set_title("Share of motorist-plus-cyclist deaths by year\nNYC police-reported motor vehicle crashes, 2013–2025", loc="left", weight="bold")
ax.set_ylabel("Share of the two groups' combined deaths (%)")
ax.set_ylim(0, 100)
ax.set_xticks(x, YEARS, rotation=45)
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)
ax.legend(frameon=False, ncol=1, loc="upper left", bbox_to_anchor=(1.01, 1.0))
fig.text(0.01, 0.015, "Each bar is normalized to 100% of that year's motorist and cyclist deaths; this composition does not show annual volume or exposure-adjusted risk.", fontsize=9)
fig.tight_layout(rect=(0, 0.055, 0.86, 1))
fig.savefig("out/option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)

print("Saved annual values and charts for both final plans.")
