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
df.to_csv("./out/revised_values.csv", index=False)
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
fig.savefig("./out/revised.png", dpi=150)
print("saved ./out/revised.png")
