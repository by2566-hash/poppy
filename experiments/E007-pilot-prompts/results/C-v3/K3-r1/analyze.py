import duckdb
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

con = duckdb.connect()

df = con.sql("""
SELECT EXTRACT(YEAR FROM crash_date)::INT AS year,
       SUM(number_of_motorist_killed)::BIGINT  AS motorist_killed,
       SUM(number_of_cyclist_killed)::BIGINT   AS cyclist_killed,
       SUM(number_of_pedestrians_killed)::BIGINT AS pedestrian_killed,
       SUM(number_of_persons_killed)::BIGINT   AS total_killed,
       COUNT(*) AS crashes
FROM './data/crashes.parquet'
WHERE EXTRACT(YEAR FROM crash_date) BETWEEN 2013 AND 2025
GROUP BY 1
ORDER BY 1
""").df()

out = df[["year", "motorist_killed", "cyclist_killed"]].copy()
out.to_csv("./out/values.csv", index=False)

# sanity checks
dup = con.sql("""SELECT COUNT(*) - COUNT(DISTINCT collision_id) FROM './data/crashes.parquet'""").fetchone()[0]
years = sorted(df["year"].tolist())
print("duplicate collision_ids:", dup)
print("years:", years)
print(out.to_string(index=False))
print("sums:", out[["motorist_killed", "cyclist_killed"]].sum().to_dict())

fig, ax = plt.subplots(figsize=(12, 6.5))
x = range(len(out))
w = 0.4
b1 = ax.bar([i - w / 2 for i in x], out["motorist_killed"], w, label="Motorist deaths", color="#1f77b4")
b2 = ax.bar([i + w / 2 for i in x], out["cyclist_killed"], w, label="Cyclist deaths", color="#ff7f0e")

for bars in (b1, b2):
    for b in bars:
        ax.annotate(f"{int(b.get_height())}", (b.get_x() + b.get_width() / 2, b.get_height()),
                    ha="center", va="bottom", fontsize=8)

ax.set_xticks(list(x))
ax.set_xticklabels(out["year"], rotation=0)
ax.set_xlabel("Year")
ax.set_ylabel("People killed")
ax.set_title("NYC motor vehicle deaths by year, 2013–2025:\nmotorists vs cyclists")
ax.set_ylim(0, max(out["motorist_killed"]) * 1.15)
ax.legend()
ax.grid(axis="y", alpha=0.3)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig("./out/initial.png", dpi=150)
print("saved")
