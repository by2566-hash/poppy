import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

SRC = "./data/crashes.parquet"
con = duckdb.connect()

# Census Vintage 2024 borough populations (July 2024), via NYC DCP
POP = {
    "BROOKLYN": 2617631,
    "QUEENS": 2316841,
    "MANHATTAN": 1660664,
    "BRONX": 1384724,
    "STATEN ISLAND": 498212,
}
TITLE = {"BROOKLYN": "Brooklyn", "QUEENS": "Queens", "MANHATTAN": "Manhattan",
         "BRONX": "Bronx", "STATEN ISLAND": "Staten Island"}

COL = {"BROOKLYN": "#4C72B0", "QUEENS": "#DD8452", "MANHATTAN": "#55A868",
       "BRONX": "#C44E52", "STATEN ISLAND": "#8172B3"}


def fetch(sql):
    return con.execute(sql).df()


# ---------------------------------------------------------------- recent window
recent = fetch(f"""
    SELECT borough,
           count(*) / 5.0                        AS crashes_yr,
           sum(number_of_persons_killed) / 5.0  AS deaths_yr,
           sum(number_of_persons_injured) / 5.0 AS injuries_yr,
           sum(number_of_pedestrians_killed) / 5.0 AS ped_deaths_yr,
           sum(number_of_cyclist_killed) / 5.0    AS cyc_deaths_yr,
           sum(number_of_motorist_killed) / 5.0   AS mot_deaths_yr
    FROM read_parquet('{SRC}')
    WHERE borough IS NOT NULL
      AND crash_date BETWEEN DATE '2021-01-01' AND DATE '2025-12-31'
    GROUP BY 1
""")
recent["pop"] = recent["borough"].map(POP)
recent["crashes_100k"] = 1e5 * recent["crashes_yr"] / recent["pop"]
recent["deaths_100k"] = 1e5 * recent["deaths_yr"] / recent["pop"]
recent["injuries_100k"] = 1e5 * recent["injuries_yr"] / recent["pop"]
recent["deaths_per_1k"] = 1000 * recent["deaths_yr"] / recent["crashes_yr"]
recent["vuln_100k"] = 1e5 * (recent["ped_deaths_yr"] + recent["cyc_deaths_yr"]) / recent["pop"]

# risk index: share of city harm / share of city population
recent["pop_share"] = 100 * recent["pop"] / recent["pop"].sum()
recent["crash_share"] = 100 * recent["crashes_yr"] / recent["crashes_yr"].sum()
recent["death_share"] = 100 * recent["deaths_yr"] / recent["deaths_yr"].sum()
recent["risk_crash"] = recent["crash_share"] / recent["pop_share"]
recent["risk_death"] = recent["death_share"] / recent["pop_share"]

recent = recent.sort_values("crashes_100k", ascending=False).reset_index(drop=True)
print("=== Per-capita scorecard, 2021-2025 avg ===")
print(recent[["borough", "crashes_100k", "deaths_100k", "injuries_100k",
              "deaths_per_1k", "vuln_100k", "risk_crash", "risk_death"]]
      .rename(columns=TITLE).round(2).to_string(index=False))

# ---------------------------------------------------------------------- figure 1
metrics = [
    ("crashes_100k",  "Crashes\nper 100k residents",   "Crashes per 100,000 residents"),
    ("deaths_100k",   "Deaths\nper 100k residents",   "Deaths per 100,000 residents"),
    ("vuln_100k",     "Ped+cyclist deaths\nper 100k", "Pedestrian + cyclist deaths\nper 100,000 residents"),
    ("deaths_per_1k", "Deaths per 1,000\ncrashes",   "Deaths per 1,000 crashes\n(crash severity)"),
]

fig, axes = plt.subplots(1, 4, figsize=(17, 5.4))
for ax, (col, xlabel, title) in zip(axes, metrics):
    d = recent.sort_values(col, ascending=True)
    vals = d[col].values
    colors = [COL[b] for b in d["borough"]]
    bars = ax.barh([TITLE[b] for b in d["borough"]], vals, color=colors, edgecolor="white")
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_title(title, fontsize=11, weight="bold")
    ax.grid(axis="x", alpha=0.25, linewidth=0.6)
    ax.set_axisbelow(True)
    span = max(vals)
    for b, v in zip(bars, vals):
        ax.text(v + span * 0.015, b.get_y() + b.get_height() / 2,
                f"{v:,.2f}" if v < 100 else f"{v:,.0f}",
                va="center", fontsize=9, weight="bold", color="#333")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_xlim(0, span * 1.20)
    ax.tick_params(labelsize=9)

fig.suptitle("Which NYC borough is the most dangerous?  Five lenses, 2021\u20132025 average",
             fontsize=15, weight="bold", y=1.02)
fig.text(0.5, -0.04,
         "Each panel ranks the boroughs differently \u2014 the winner depends entirely on how "
         "\u201cdangerous\u201d is defined.\nCrashes with no recorded borough are excluded "
         "(24% of rows). Population: U.S. Census Vintage 2024 (July 2024).",
         ha="center", fontsize=9.5, color="#555")
fig.tight_layout()
fig.savefig("./out/borough_scorecard.png", dpi=160, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------------- figure 2
trend = fetch(f"""
    SELECT year(crash_date) AS year, borough, count(*) AS crashes,
           sum(number_of_persons_killed) AS deaths
    FROM read_parquet('{SRC}')
    WHERE borough IS NOT NULL
      AND crash_date BETWEEN DATE '2016-01-01' AND DATE '2025-12-31'
    GROUP BY 1, 2
""")
sev = fetch(f"""
    SELECT year(crash_date) AS year, count(*) AS crashes,
           sum(number_of_persons_killed) AS deaths
    FROM read_parquet('{SRC}')
    WHERE borough IS NOT NULL
      AND crash_date BETWEEN DATE '2016-01-01' AND DATE '2025-12-31'
    GROUP BY 1 ORDER BY 1
""")
sev["deaths_per_1k"] = 1000 * sev["deaths"] / sev["crashes"]

fig, axes = plt.subplots(1, 3, figsize=(17, 4.8))

# (a) crashes vs deaths, city-wide, indexed to 2016
ax = axes[0]
ax.plot(sev["year"], 100 * sev["crashes"] / sev["crashes"].iloc[0],
        marker="o", color="#C44E52", linewidth=2.4, label="Crashes")
ax.plot(sev["year"], 100 * sev["deaths"] / sev["deaths"].iloc[0],
        marker="s", color="#4C72B0", linewidth=2.4, label="Deaths")
ax.axhline(100, color="#999", linewidth=1, linestyle="--")
ax.set_title("(a) Crashes fell 55%, but deaths rose\nNYC motor vehicle deaths, 2016=100",
             fontsize=11, weight="bold")
ax.set_ylabel("Index (2016 = 100)", fontsize=9)
ax.legend(fontsize=9, frameon=False)
ax.grid(alpha=0.25, linewidth=0.6)
ax.set_axisbelow(True)

# (b) severity doubling
ax = axes[1]
ax.bar(sev["year"], sev["deaths_per_1k"], color="#55A868", edgecolor="white", width=0.7)
ax.set_title("(b) Each crash is now far more lethal\nDeaths per 1,000 reported crashes",
             fontsize=11, weight="bold")
ax.set_ylabel("Deaths per 1,000 crashes", fontsize=9)
for x, v in zip(sev["year"], sev["deaths_per_1k"]):
    ax.text(x, v + 0.05, f"{v:.2f}", ha="center", fontsize=8, color="#333")
ax.set_ylim(0, sev["deaths_per_1k"].max() * 1.2)
ax.grid(axis="y", alpha=0.25, linewidth=0.6)
ax.set_axisbelow(True)

# (c) risk index
ax = axes[2]
d = recent.sort_values("risk_crash")
x = np.arange(len(d))
ax.bar(x - 0.19, d["risk_crash"], 0.36, label="Crash rate", color="#4C72B0", edgecolor="white")
ax.bar(x + 0.19, d["risk_death"], 0.36, label="Death rate", color="#C44E52", edgecolor="white")
ax.axhline(1.0, color="#333", linewidth=1.4, linestyle="--", label="City average")
ax.set_xticks(x)
ax.set_xticklabels([TITLE[b] for b in d["borough"]], fontsize=9, rotation=20, ha="right")
ax.set_title("(c) Risk index: borough share of harm\n\u00f7 its share of NYC population",
             fontsize=11, weight="bold")
ax.set_ylabel("Index (1.0 = city average)", fontsize=9)
ax.legend(fontsize=8.5, frameon=False)
ax.grid(axis="y", alpha=0.25, linewidth=0.6)
ax.set_axisbelow(True)

for ax in axes:
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

fig.suptitle("Brooklyn carries the city's road-death burden \u2014 and the risk is worsening",
             fontsize=14, weight="bold", y=1.04)
fig.text(0.5, -0.10,
         "Panel (c): >1.0 means a borough's share of harm exceeds its share of NYC population. "
         "Brooklyn and the Bronx sit above average;\nStaten Island well below. "
         "Crash counts exclude rows with no recorded borough.",
         ha="center", fontsize=9, color="#555")
fig.tight_layout()
fig.savefig("./out/borough_trend_risk.png", dpi=160, bbox_inches="tight")
plt.close(fig)

print("\nwrote ./out/borough_scorecard.png and ./out/borough_trend_risk.png")