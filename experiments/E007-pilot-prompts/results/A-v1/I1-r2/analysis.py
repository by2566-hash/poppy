import duckdb
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

con = duckdb.connect()
df = con.sql("""
SELECT year(crash_date) AS year,
       count(*) AS reported_crashes,
       sum(CASE WHEN number_of_persons_injured > 0 THEN 1 ELSE 0 END) AS injury_crashes,
       sum(number_of_persons_injured) AS persons_injured,
       sum(number_of_persons_killed) AS persons_killed,
       sum(number_of_motorist_killed) AS motorist_killed,
       sum(number_of_motorist_injured) AS motorist_injured
FROM './data/crashes.parquet'
WHERE year(crash_date) BETWEEN 2013 AND 2025
GROUP BY 1 ORDER BY 1
""").df()

df["motorist_killed_per_1000_injury_crashes"] = df.motorist_killed / df.injury_crashes * 1000
df["motorist_killed_per_1000_crashes"] = df.motorist_killed / df.reported_crashes * 1000
df["motorist_killed_per_100k_motorist_injured"] = df.motorist_killed / df.motorist_injured * 100000

df.to_csv("./out/values.csv", index=False)

a = df[df.year == 2013].iloc[0]
b = df[df.year == 2025].iloc[0]

fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(10.5, 8.5), sharex=True,
    gridspec_kw={"height_ratios": [1, 1.15], "hspace": 0.14}
)

ax1.bar(df.year, df.motorist_killed, color="#c0392b", width=0.7, label="Motorists killed")
for x, v in zip(df.year, df.motorist_killed):
    ax1.text(x, v + 3, str(int(v)), ha="center", va="bottom", fontsize=8.5, color="#333333")
ax1.annotate(f"2013: {int(a.motorist_killed)}\n2025: {int(b.motorist_killed)}  (-26%)",
             xy=(2025, b.motorist_killed), xytext=(2021.4, 145),
             arrowprops=dict(arrowstyle="->", color="#333333"), fontsize=9.5, color="#333333")
ax1.set_ylabel("Motorists killed per year")
ax1.set_title("NYC motorist deaths fell 26% (110 \u2192 81), and risk per unit of driving exposure fell too",
              fontsize=12, loc="left", pad=10)
ax1.grid(axis="y", alpha=0.3)
ax1.set_axisbelow(True)
ax1.set_ylim(0, 165)

ax2.plot(df.year, df.motorist_killed_per_1000_injury_crashes, marker="o", lw=2.4,
         color="#2c5f9e", label="per 1,000 injury crashes (exposure proxy)")
ax2.plot(df.year, df.motorist_killed_per_1000_crashes, marker="s", lw=1.8, ls="--",
         color="#7f8c8d", label="per 1,000 all reported crashes")
for x, v in zip(df.year, df.motorist_killed_per_1000_injury_crashes):
    ax2.annotate(f"{v:.2f}", (x, v), textcoords="offset points", xytext=(0, 8),
                 ha="center", fontsize=8, color="#2c5f9e")
ax2.set_ylabel("Motorists killed per 1,000 crashes")
ax2.set_xlabel("Year")
ax2.set_title("Crash file has no vehicle-miles-traveled; injury-involved crashes (stable reporting) used as proxy for miles driven",
              fontsize=10, loc="left", pad=8, color="#444444")
ax2.grid(alpha=0.3)
ax2.set_axisbelow(True)
ax2.set_xticks(df.year)
ax2.set_xticklabels(df.year, rotation=45)
ax2.legend(loc="upper left", fontsize=9, framealpha=0.9)
ax2.annotate(f"{a.motorist_killed_per_1000_injury_crashes:.2f} \u2192 "
             f"{b.motorist_killed_per_1000_injury_crashes:.2f}  (-21%)",
             xy=(2025, b.motorist_killed_per_1000_injury_crashes),
             xytext=(2020.6, 1.55), fontsize=9.5, color="#2c5f9e",
             arrowprops=dict(arrowstyle="->", color="#2c5f9e"))
ax2.annotate("post-2020 collapse in minor-crash\nreporting inflates the all-crash rate",
             xy=(2022.0, df.loc[df.year == 2022, "motorist_killed_per_1000_crashes"].iloc[0]),
             xytext=(2016.4, 1.35), fontsize=8.5, color="#7f8c8d",
             arrowprops=dict(arrowstyle="->", color="#7f8c8d"))

fig.text(0.01, 0.012,
         "Source: NYPD motor-vehicle collisions, ./data/crashes.parquet (full years 2013-2025). "
         "True per-mile risk requires VMT, which this file does not contain.",
         fontsize=8, color="#666666")
fig.subplots_adjust(bottom=0.11)
fig.savefig("./out/initial.png", dpi=150)
print(df.to_string(index=False))
print("\n2013->2025 motorist deaths: %d -> %d (%.1f%%)" % (
    a.motorist_killed, b.motorist_killed,
    (b.motorist_killed / a.motorist_killed - 1) * 100))
print("deaths per 1000 injury crashes: %.3f -> %.3f (%.1f%%)" % (
    a.motorist_killed_per_1000_injury_crashes, b.motorist_killed_per_1000_injury_crashes,
    (b.motorist_killed_per_1000_injury_crashes / a.motorist_killed_per_1000_injury_crashes - 1) * 100))
print("deaths per 1000 reported crashes: %.3f -> %.3f (%.1f%%)" % (
    a.motorist_killed_per_1000_crashes, b.motorist_killed_per_1000_crashes,
    (b.motorist_killed_per_1000_crashes / a.motorist_killed_per_1000_crashes - 1) * 100))
print("injury crashes: %d -> %d (%.1f%%)" % (
    a.injury_crashes, b.injury_crashes,
    (b.injury_crashes / a.injury_crashes - 1) * 100))
print("all reported crashes: %d -> %d (%.1f%%)" % (
    a.reported_crashes, b.reported_crashes,
    (b.reported_crashes / a.reported_crashes - 1) * 100))
