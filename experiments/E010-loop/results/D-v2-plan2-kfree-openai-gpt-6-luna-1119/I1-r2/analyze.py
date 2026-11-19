import duckdb
import matplotlib.pyplot as plt


SOURCE = "data/crashes.parquet"
START_YEAR = 2013
END_YEAR = 2025

con = duckdb.connect()
rows = con.execute(
    f"""
    SELECT year(crash_date) AS year,
           count(*) AS crash_rows,
           sum(number_of_motorist_killed) AS motorist_deaths,
           count(*) FILTER (WHERE number_of_motorist_killed > 0) AS
               crashes_with_motorist_death
    FROM read_parquet('{SOURCE}')
    WHERE crash_date >= DATE '{START_YEAR}-01-01'
      AND crash_date < DATE '{END_YEAR + 1}-01-01'
    GROUP BY year
    ORDER BY year
    """
).fetchall()

years = [int(row[0]) for row in rows]
crash_rows = [int(row[1]) for row in rows]
motorist_deaths = [int(row[2]) for row in rows]
fatal_crash_rows = [int(row[3]) for row in rows]
per_1000_crashes = [1000 * fatal / total for fatal, total in zip(fatal_crash_rows, crash_rows)]

with open("out/values_1.csv", "w") as file:
    file.write("year,motorist_deaths\n")
    for year, deaths in zip(years, motorist_deaths):
        file.write(f"{year},{deaths}\n")

with open("out/values_2.csv", "w") as file:
    file.write("year,crashes_with_motorist_death,all_crash_rows,crashes_with_motorist_death_per_1000_crashes\n")
    for year, fatal, total, rate in zip(years, fatal_crash_rows, crash_rows, per_1000_crashes):
        file.write(f"{year},{fatal},{total},{rate:.6f}\n")

plt.figure(figsize=(10, 5.8))
plt.plot(years, motorist_deaths, marker="o", linewidth=2, color="#1769aa")
plt.xticks(years, rotation=45)
plt.ylabel("Recorded motorist deaths")
plt.xlabel("Crash year")
plt.title(
    "Annual recorded motorist deaths in NYC police-reported crashes\n"
    "All reported crashes dated 2013–2025; counts, not exposure-adjusted rates",
    fontsize=13,
)
plt.grid(axis="y", alpha=0.25)
plt.tight_layout()
plt.savefig("out/option_1.png", dpi=160)
plt.close()

plt.figure(figsize=(10, 5.8))
plt.plot(years, per_1000_crashes, marker="o", linewidth=2, color="#a23b72")
plt.xticks(years, rotation=45)
plt.ylabel("Crashes with ≥1 motorist death per 1,000 crashes")
plt.xlabel("Crash year")
plt.title(
    "Motorist-fatality crashes per 1,000 NYC police-reported crashes\n"
    "All reported crashes dated 2013–2025; not a per-mile risk measure",
    fontsize=13,
)
plt.grid(axis="y", alpha=0.25)
plt.tight_layout()
plt.savefig("out/option_2.png", dpi=160)
plt.close()

print("Wrote annual death counts, crash-based ratios, and charts.")
