import duckdb
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

con = duckdb.connect()
df = con.sql("""
    SELECT EXTRACT(YEAR FROM crash_date)::INT AS year,
           SUM(number_of_motorist_killed)::INT AS motorist_killed,
           SUM(number_of_cyclist_killed)::INT  AS cyclist_killed
    FROM './data/crashes.parquet'
    WHERE crash_date BETWEEN DATE '2013-01-01' AND DATE '2025-12-31'
      AND EXTRACT(YEAR FROM crash_date) BETWEEN 2013 AND 2025
    GROUP BY 1
    ORDER BY 1
""").df()

all_years = pd.DataFrame({"year": range(2013, 2026)})
df = all_years.merge(df, on="year", how="left").fillna(0)
df[["motorist_killed", "cyclist_killed"]] = df[["motorist_killed", "cyclist_killed"]].astype(int)
df["total_killed"] = df["motorist_killed"] + df["cyclist_killed"]
df["ratio_motorist_to_cyclist"] = (df["motorist_killed"] / df["cyclist_killed"].replace(0, pd.NA)).round(1)

df.to_csv("./out/values.csv", index=False)
print(df.to_string(index=False))

fig, ax = plt.subplots(figsize=(12, 7))
x = df["year"]
w = 0.38
b1 = ax.bar(x - w/2, df["motorist_killed"], w, label="Motorist deaths", color="#1f77b4")
b2 = ax.bar(x + w/2, df["cyclist_killed"], w, label="Cyclist deaths", color="#ff7f0e")

for bars in (b1, b2):
    for r in bars:
        h = r.get_height()
        ax.annotate(f"{int(h)}", (r.get_x() + r.get_width()/2, h), ha="center", va="bottom",
                    fontsize=8, xytext=(0, 2), textcoords="offset points")

ax.set_title("NYC Motorist vs. Cyclist Deaths by Year, 2013-2025", fontsize=15, fontweight="bold")
ax.set_xlabel("Year")
ax.set_ylabel("Deaths (police-reported)")
ax.set_xticks(x)
ax.set_xticklabels([str(y) for y in x], rotation=45)
ax.legend()
ax.grid(axis="y", alpha=0.3)
ax.set_axisbelow(True)

tot_m = df["motorist_killed"].sum()
tot_c = df["cyclist_killed"].sum()
ax.text(0.99, 0.97, f"13-yr totals: motorist {tot_m}, cyclist {tot_c}\nratio {tot_m/tot_c:.1f} : 1",
        transform=ax.transAxes, ha="right", va="top", fontsize=10,
        bbox=dict(boxstyle="round", fc="white", ec="gray", alpha=0.9))

fig.tight_layout()
fig.savefig("./out/initial.png", dpi=150)
print("\nsaved ./out/initial.png and ./out/values.csv")
