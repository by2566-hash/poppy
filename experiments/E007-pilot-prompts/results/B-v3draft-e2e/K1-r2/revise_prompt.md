Revise an analysis based on a reviewer's numbered issues.

Question:
How many pedestrians were killed in NYC motor vehicle crashes each year from 2013 to 2025?

Data description:
Data file: ./data/crashes.parquet (one row per police-reported motor vehicle crash in New York City; read it with DuckDB or pandas).
Columns: crash_date (DATE), crash_time (TIME), borough (VARCHAR, may be NULL), zip_code, latitude, longitude,
on_street_name, cross_street_name, number_of_persons_injured (INT), number_of_persons_killed (INT),
number_of_pedestrians_injured, number_of_pedestrians_killed, number_of_cyclist_injured, number_of_cyclist_killed,
number_of_motorist_injured, number_of_motorist_killed, contributing_factor_vehicle_1 ... contributing_factor_vehicle_5 (VARCHAR),
collision_id (BIGINT), vehicle_type_code1 ... vehicle_type_code5 (VARCHAR).
Python 3 with duckdb, pandas and matplotlib is available.

Current code:
# file: analyze.py
import os
import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.makedirs("./out", exist_ok=True)

con = duckdb.connect()
df = con.sql("""
    SELECT year(crash_date) AS year,
           SUM(number_of_pedestrians_killed)::INT AS pedestrians_killed
    FROM './data/crashes.parquet'
    WHERE crash_date IS NOT NULL
      AND year(crash_date) BETWEEN 2013 AND 2025
    GROUP BY 1
    ORDER BY 1
""").df()

full = list(range(2013, 2026))
df = df.set_index("year").reindex(full).fillna(0).astype(int).reset_index()
df.columns = ["year", "pedestrians_killed"]
df.to_csv("./out/values.csv", index=False)
print(df.to_string(index=False))
print("Total:", int(df.pedestrians_killed.sum()))

fig, ax = plt.subplots(figsize=(12, 6.5))
bars = ax.bar(df.year, df.pedestrians_killed, color="#c0392b", edgecolor="black", linewidth=0.6)
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Pedestrians killed", fontsize=12)
ax.set_title("Pedestrians killed in NYC motor vehicle crashes, 2013-2025", fontsize=14)
ax.set_xticks(full)
ax.set_xticklabels([str(y) for y in full], rotation=45, ha="right")
ax.set_ylim(0, max(df.pedestrians_killed) * 1.15)
ax.grid(axis="y", alpha=0.3)

mean_v = df.pedestrians_killed.mean()
ax.axhline(mean_v, color="#2c3e50", linestyle="--", linewidth=1.2,
           label=f"Mean 2013-2025 = {mean_v:.0f}")
for b, v in zip(bars, df.pedestrians_killed):
    ax.annotate(str(v), (b.get_x() + b.get_width() / 2, b.get_height()),
                textcoords="offset points", xytext=(0, 3), ha="center", fontsize=9)
ax.legend(loc="upper right", fontsize=10)
fig.tight_layout()
fig.savefig("./out/initial.png", dpi=150)
print("saved ./out/initial.png")


Current plotted values (values.csv):
year,pedestrians_killed
2013,176
2014,133
2015,133
2016,149
2017,127
2018,123
2019,131
2020,101
2021,132
2022,135
2023,107
2024,124
2025,119


Current written answer:
Pedestrian deaths in NYC fell from a 13-year high of 176 in 2013 to 119 in 2025, averaging 130 per year (1,690 total). After the 2013 peak, deaths settled into a 101-149 band — the low was 101 in 2020 (pandemic driving) and 107 in 2023, with a slight rebound to 135 in 2022; the last three years (2023-2025: 107, 124, 119) are all below average.

Reviewer's issues:
1. Written answer: the parenthetical "(pandemic driving)" attributes the 2020 low to a cause. The data file (crash records with dates, locations, injuries/fatalities) contains no information about why deaths were lower, so this causal claim is unsupported by the allowed data. It should be removed or rephrased as a neutral note not asserted from the data (e.g., drop the parenthetical).

Instructions:
- Go through the issues one by one. For each, either fix it, or check it and keep the original if the reviewer was wrong, or state that it cannot be addressed with this data.
- Change nothing the reviewer did not flag: same data, filters, numbers, chart type and wording of the written answer, unless fixing an issue requires it.
- Write and run the revised code yourself. Save the chart to ./out/revised.png and the plotted data to ./out/revised_values.csv, even if only the written answer changes.
- When finished, reply in exactly this format, with one line per issue in the reviewer's numbering:
CHANGES:
1. <fixed | kept | cannot address>: <what you changed, or why you kept it or could not address it>
2. ...
ANSWER: <the revised short written answer, based on the numbers you computed>
