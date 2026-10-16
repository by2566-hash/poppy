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
python3 -c "import duckdb, pandas, matplotlib; print(duckdb.__version__, pandas.__version__, matplotlib.__version__)"

python3 -c "
import duckdb
con = duckdb.connect()
print(con.sql(\"DESCRIBE SELECT * FROM 'data/crashes.parquet'\").df().to_string())
print(con.sql(\"SELECT MIN(crash_date), MAX(crash_date), COUNT(*) FROM 'data/crashes.parquet'\").df().to_string())
"

mkdir -p out && cat > /tmp/ped_deaths.py << 'EOF'
import duckdb
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

con = duckdb.connect()
df = con.sql("""
    SELECT YEAR(crash_date) AS year,
           SUM(number_of_pedestrians_killed)::INT AS pedestrians_killed
    FROM 'data/crashes.parquet'
    WHERE crash_date BETWEEN DATE '2013-01-01' AND DATE '2025-12-31'
    GROUP BY 1
    ORDER BY 1
""").df()

full = pd.DataFrame({"year": range(2013, 2026)})
df = full.merge(df, on="year", how="left").fillna(0)
df["pedestrians_killed"] = df["pedestrians_killed"].astype(int)
df.to_csv("out/values.csv", index=False)
print(df.to_string(index=False))
print("Total:", df.pedestrians_killed.sum())

plt.figure(figsize=(11, 6))
bars = plt.bar(df.year, df.pedestrians_killed, color="#c0392b", width=0.75)
for b, v in zip(bars, df.pedestrians_killed):
    plt.text(b.get_x() + b.get_width()/2, v + 3, str(v), ha="center", va="bottom", fontsize=9)
plt.title("Pedestrians Killed in NYC Motor Vehicle Crashes, 2013–2025")
plt.xlabel("Year")
plt.ylabel("Pedestrians killed")
plt.xticks(df.year)
plt.ylim(0, df.pedestrians_killed.max() * 1.15)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("out/initial.png", dpi=130)
EOF
python3 /tmp/ped_deaths.py

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
Pedestrian deaths in NYC fell from a 13-year high of 176 in 2013 to 119 in 2025, averaging ~130 per year (1,690 total). The series trends down overall, with a low of 101 in 2020 (pandemic) and a recent low of 107 in 2023, then 124 in 2024 and 119 in 2025.

Reviewer's issues:
1. Written answer: "a low of 101 in 2020 (pandemic)" attributes the 2020 drop to the pandemic, a causal claim the crash data itself cannot support; it should be dropped or marked as outside the data.

Instructions:
- Go through the issues one by one. For each, either fix it, or check it and keep the original if the reviewer was wrong, or state that it cannot be addressed with this data.
- Change nothing the reviewer did not flag: same data, filters, numbers, chart type and wording of the written answer, unless fixing an issue requires it.
- Write and run the revised code yourself. Save the chart to ./out/revised.png and the plotted data to ./out/revised_values.csv, even if only the written answer changes.
- When finished, reply in exactly this format, with one line per issue in the reviewer's numbering:
CHANGES:
1. <fixed | kept | cannot address>: <what you changed, or why you kept it or could not address it>
2. ...
ANSWER: <the revised short written answer, based on the numbers you computed>
