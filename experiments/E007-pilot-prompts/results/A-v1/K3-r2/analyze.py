import duckdb
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

con = duckdb.connect()
q = """
SELECT EXTRACT(YEAR FROM crash_date)::INT AS year,
       SUM(number_of_motorist_killed)::INT AS motorist_killed,
       SUM(number_of_cyclist_killed)::INT  AS cyclist_killed
FROM './data/crashes.parquet'
WHERE crash_date BETWEEN DATE '2013-01-01' AND DATE '2025-12-31'
GROUP BY 1
ORDER BY 1
"""
df = con.sql(q).df()
all_years = pd.DataFrame({"year": range(2013, 2026)})
df = all_years.merge(df, on="year", how="left").fillna(0)
df["motorist_killed"] = df["motorist_killed"].astype(int)
df["cyclist_killed"] = df["cyclist_killed"].astype(int)
df.to_csv("./out/values.csv", index=False)
print(df.to_string(index=False))

x = df["year"].values
w = 0.4
fig, ax = plt.subplots(figsize=(13, 7))
ax.bar(x - w/2, df["motorist_killed"], width=w, label="Motorist deaths", color="#1f77b4")
ax.bar(x + w/2, df["cyclist_killed"], width=w, label="Cyclist deaths", color="#ff7f0e")
for xi, m, c in zip(x, df["motorist_killed"], df["cyclist_killed"]):
    ax.text(xi - w/2, m + 1, str(m), ha="center", va="bottom", fontsize=8, color="#1f77b4")
    ax.text(xi + w/2, c + 1, str(c), ha="center", va="bottom", fontsize=8, color="#ff7f0e")
ax.set_xticks(x)
ax.set_xticklabels(x, rotation=45)
ax.set_ylabel("Deaths")
ax.set_xlabel("Year")
ax.set_title("NYC crash deaths: motorists vs cyclists, 2013-2025")
ax.legend()
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig("./out/initial.png", dpi=150)
print("saved")
