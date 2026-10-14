import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import os

os.makedirs("out", exist_ok=True)

con = duckdb.connect()
df = con.execute("""
    SELECT year, sum(number_of_pedestrians_killed)::INT AS pedestrians_killed
    FROM (
        SELECT CAST(strftime(crash_date, '%Y') AS INT) AS year,
               number_of_pedestrians_killed
        FROM read_parquet('data/crashes.parquet')
        WHERE EXTRACT(YEAR FROM crash_date) BETWEEN 2013 AND 2025
    )
    GROUP BY year
    ORDER BY year
""").df()

df.to_csv("out/values.csv", index=False)

plt.figure(figsize=(9, 5))
plt.bar(df["year"], df["pedestrians_killed"], color="steelblue")
plt.xlabel("Year")
plt.ylabel("Pedestrians killed")
plt.title("Pedestrians killed in NYC motor vehicle crashes, 2013–2025")
plt.xticks(df["year"], rotation=45)
for x, y in zip(df["year"], df["pedestrians_killed"]):
    plt.text(x, y + 1, str(y), ha="center", fontsize=8)
plt.tight_layout()
plt.savefig("out/initial.png", dpi=120)
print(df.to_string(index=False))
