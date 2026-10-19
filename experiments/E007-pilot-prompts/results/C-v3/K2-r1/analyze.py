import duckdb
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

os.makedirs("out", exist_ok=True)

con = duckdb.connect()

# Inspect schema and date range first
print(con.execute("DESCRIBE SELECT * FROM 'data/crashes.parquet'").fetchdf())
print(con.execute("""
    SELECT MIN(crash_date) AS min_d, MAX(crash_date) AS max_d, COUNT(*) AS n
    FROM 'data/crashes.parquet'
""").fetchdf())

# Crashes by day of week (2013-2025). Exclude any rows outside 2013-2025 if present.
df = con.execute("""
    SELECT
        DAYNAME(crash_date) AS day_of_week,
        DAYOFWEEK(crash_date) AS dow_num,
        COUNT(*) AS crashes
    FROM 'data/crashes.parquet'
    WHERE crash_date IS NOT NULL AND YEAR(crash_date) BETWEEN 2013 AND 2025
    GROUP BY 1, 2
""").fetchdf()

nulls = con.execute("""
    SELECT COUNT(*) AS n_null
    FROM 'data/crashes.parquet'
    WHERE crash_date IS NULL AND TRUE
""").fetchdf().loc[0, "n_null"]
print("Rows with NULL crash_date (all years):", nulls)

# DAYNAME returns full names (e.g. 'Monday'); order Mon..Sun
order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
df["day_of_week"] = pd.Categorical(df["day_of_week"], categories=order, ordered=True)
df = df.sort_values("day_of_week").reset_index(drop=True)

total = df["crashes"].sum()
df["pct"] = df["crashes"] / total * 100

# Average per day over the period: count how many of each weekday exist in 2013-2025
cal = con.execute("""
    WITH RECURSIVE d AS (
        SELECT DATE '2013-01-01' AS dt
        UNION ALL
        SELECT dt + INTERVAL 1 DAY FROM d WHERE dt < DATE '2025-12-31'
    )
    SELECT
        DAYNAME(dt) AS day_of_week,
        COUNT(*) AS n_days
    FROM d
    GROUP BY 1
""").fetchdf()
df = df.merge(cal, on="day_of_week", how="left")
df["avg_per_day"] = df["crashes"] / df["n_days"]
df = df.drop(columns=["n_days"])

print(df)
print("Total dated crashes 2013-2025:", total)

df.to_csv("out/values.csv", index=False)

fig, ax = plt.subplots(figsize=(9, 5.5))
colors = ["#4C72B0"]*5 + ["#DD8452"]*2
bars = ax.bar(df["day_of_week"].astype(str), df["crashes"], color=colors)
for b, v, p in zip(bars, df["crashes"], df["pct"]):
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+ df["crashes"].max()*0.01,
            f"{v:,}\n({p:.1f}%)", ha="center", va="bottom", fontsize=9)
ax.set_title(f"NYC police-reported motor vehicle crashes by day of week, 2013–2025\n(n = {total:,}; weekend days in orange)")
ax.set_ylabel("Number of crashes")
ax.set_ylim(0, df["crashes"].max()*1.18)
ax.spines[["top","right"]].set_visible(False)
plt.tight_layout()
plt.savefig("out/initial.png", dpi=120)
print("Saved out/initial.png and out/values.csv")
