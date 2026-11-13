from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
DATA = ROOT / "data" / "crashes.parquet"
conn = duckdb.connect()
conn.execute(f"CREATE VIEW crashes AS SELECT * FROM read_parquet('{str(DATA).replace(chr(39), chr(39) * 2)}')")

query = """
    SELECT year(crash_date) AS year,
           sum(number_of_pedestrians_injured) AS pedestrians_injured,
           sum(number_of_pedestrians_killed) AS pedestrians_killed,
           sum(number_of_pedestrians_injured + number_of_pedestrians_killed) AS casualties
    FROM crashes
    WHERE upper(trim(borough)) = 'BROOKLYN'
      AND crash_date >= DATE '2013-01-01'
      AND number_of_pedestrians_injured IS NOT NULL
      AND number_of_pedestrians_killed IS NOT NULL
    GROUP BY year(crash_date)
    ORDER BY year
"""
df = conn.execute(query).df()
file_end = conn.execute("SELECT max(crash_date) FROM crashes").fetchone()[0]
for column in ["pedestrians_injured", "pedestrians_killed", "casualties"]:
    df[column] = df[column].astype("int64")
df["coverage"] = df["year"].apply(lambda y: "partial" if y == file_end.year else "full")
df["period_end"] = df["year"].apply(lambda y: str(file_end) if y == file_end.year else f"{y}-12-31")

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})

# Option 1: annual total pedestrian casualties, with the partial endpoint clearly marked.
option1 = df[["year", "casualties", "pedestrians_injured", "pedestrians_killed", "coverage", "period_end"]].copy()
option1 = option1.rename(columns={"casualties": "value"})
option1.to_csv(OUT / "values_1.csv", index=False)
fig, ax = plt.subplots(figsize=(10.5, 5.6))
colors = ["#177E89" if c == "full" else "#E58A36" for c in option1["coverage"]]
bars = ax.bar(option1["year"].astype(str), option1["value"], color=colors, width=0.72)
for bar, coverage in zip(bars, option1["coverage"]):
    if coverage == "partial":
        bar.set_hatch("///")
        bar.set_edgecolor("#8A4B10")
        bar.set_linewidth(1.1)
ax.set_title("People reported injured or killed as pedestrians in Brooklyn crashes\nPolice-reported crashes, annual count; 2026 through June 11 only", loc="left", fontsize=11, pad=12)
fig.suptitle("Brooklyn pedestrian injuries and deaths, 2013–2026", x=0.125, y=0.985, ha="left", fontsize=16, fontweight="bold")
ax.set_ylabel("Pedestrians injured or killed")
ax.set_xlabel("Crash year")
ax.grid(axis="y", color="#D9DEE2", linewidth=0.8)
ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)
ax.text(0.01, -0.20, "Annual counts are not adjusted for walking exposure. Hatched 2026 bar is incomplete.", transform=ax.transAxes, fontsize=9, color="#4B5563")
ax.annotate("2026 through Jun 11", xy=(len(option1) - 1, option1.iloc[-1]["value"]), xytext=(-76, 18), textcoords="offset points", fontsize=9, color="#8A4B10", arrowprops={"arrowstyle": "-", "color": "#8A4B10"})
fig.tight_layout(rect=[0, 0.04, 1, 0.94])
fig.savefig(OUT / "option_1.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# Option 2: annual pedestrian deaths, emphasizing the most severe safety outcome.
option2 = df[["year", "pedestrians_killed", "coverage", "period_end"]].copy()
option2 = option2.rename(columns={"pedestrians_killed": "value"})
option2.to_csv(OUT / "values_2.csv", index=False)
fig, ax = plt.subplots(figsize=(10.5, 5.6))
full = option2[option2["coverage"] == "full"]
partial = option2[option2["coverage"] == "partial"]
ax.plot(full["year"], full["value"], color="#B13B4A", marker="o", linewidth=2.5, markersize=5.5)
if not partial.empty:
    ax.scatter(partial["year"], partial["value"], color="#E58A36", marker="D", s=62, zorder=4, edgecolor="#8A4B10", linewidth=0.8)
    ax.annotate("2026 through Jun 11", xy=(partial.iloc[0]["year"], partial.iloc[0]["value"]), xytext=(-95, 18), textcoords="offset points", fontsize=9, color="#8A4B10", arrowprops={"arrowstyle": "-", "color": "#8A4B10"})
ax.set_title("Pedestrians killed in Brooklyn police-reported crashes\nAnnual deaths; 2026 through June 11 only", loc="left", fontsize=11, pad=12)
fig.suptitle("Brooklyn pedestrian deaths, 2013–2026", x=0.125, y=0.985, ha="left", fontsize=16, fontweight="bold")
ax.set_ylabel("Pedestrians killed")
ax.set_xlabel("Crash year")
ax.set_xticks(option2["year"])
ax.set_ylim(bottom=0)
ax.grid(axis="y", color="#D9DEE2", linewidth=0.8)
ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)
ax.text(0.01, -0.20, "Annual counts are not adjusted for walking exposure. The 2026 point is incomplete and is not connected to the full-year trend.", transform=ax.transAxes, fontsize=9, color="#4B5563")
fig.tight_layout(rect=[0, 0.04, 1, 0.94])
fig.savefig(OUT / "option_2.png", dpi=180, bbox_inches="tight")
plt.close(fig)
