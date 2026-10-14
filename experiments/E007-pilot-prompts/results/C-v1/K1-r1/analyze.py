import duckdb
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

os.makedirs("out", exist_ok=True)

con = duckdb.connect()
df = con.sql("""
    SELECT YEAR(crash_date)::INT AS year,
           SUM(number_of_pedestrians_killed)::INT AS pedestrians_killed
    FROM './data/crashes.parquet'
    WHERE YEAR(crash_date) BETWEEN 2013 AND 2025
    GROUP BY 1
    ORDER BY 1
""").df()

df.to_csv("out/values.csv", index=False)
print(df.to_string(index=False))
print("Total 2013-2025:", df.pedestrians_killed.sum())

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(df.year, df.pedestrians_killed, color="#C0392B", edgecolor="black", width=0.75)

mean = df.pedestrians_killed.mean()
ax.axhline(mean, ls="--", lw=1.5, color="#2C3E50",
           label=f"Mean: {mean:.0f} deaths/year")

for b, v in zip(bars, df.pedestrians_killed):
    ax.text(b.get_x() + b.get_width() / 2, v + 2, str(v),
            ha="center", va="bottom", fontsize=9, fontweight="bold")

ax.set_title("Pedestrians Killed in NYC Motor Vehicle Crashes by Year, 2013–2025",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Year")
ax.set_ylabel("Pedestrians killed")
ax.set_xticks(df.year)
ax.set_ylim(0, max(df.pedestrians_killed) * 1.18)
ax.legend()
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig("out/initial.png", dpi=150)
print("Saved out/initial.png and out/values.csv")
