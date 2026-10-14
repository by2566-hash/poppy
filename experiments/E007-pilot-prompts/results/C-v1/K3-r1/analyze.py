import os

import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.makedirs("./out", exist_ok=True)

con = duckdb.connect()
df = con.sql("""
    SELECT EXTRACT(YEAR FROM crash_date)::INT AS year,
           SUM(number_of_motorist_killed)::INT AS motorist_killed,
           SUM(number_of_cyclist_killed)::INT  AS cyclist_killed
    FROM './data/crashes.parquet'
    WHERE EXTRACT(YEAR FROM crash_date) BETWEEN 2013 AND 2025
    GROUP BY 1
    ORDER BY 1
""").df()

df.to_csv("./out/values.csv", index=False)
print(df.to_string(index=False))

x = df["year"].to_numpy()
w = 0.4
fig, ax = plt.subplots(figsize=(12, 6.5))
b1 = ax.bar(x - w / 2, df["motorist_killed"], w, label="Motorist deaths", color="#c0392b")
b2 = ax.bar(x + w / 2, df["cyclist_killed"], w, label="Cyclist deaths", color="#2980b9")
ax.bar_label(b1, padding=2, fontsize=8)
ax.bar_label(b2, padding=2, fontsize=8)

ax.set_title("NYC crash deaths by road user type, 2013-2025")
ax.set_xlabel("Year")
ax.set_ylabel("People killed")
ax.set_xticks(x)
ax.set_ylim(0, max(df["motorist_killed"]) * 1.15)
ax.legend()
ax.grid(axis="y", alpha=0.3)

mot_avg = df["motorist_killed"].mean()
cyc_avg = df["cyclist_killed"].mean()
ax.annotate(
    f"Mean motorist: {mot_avg:.0f}/yr\nMean cyclist: {cyc_avg:.0f}/yr",
    xy=(0.02, 0.95), xycoords="axes fraction", va="top", fontsize=9,
    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8),
)

fig.tight_layout()
fig.savefig("./out/initial.png", dpi=150)
print("saved ./out/initial.png")
