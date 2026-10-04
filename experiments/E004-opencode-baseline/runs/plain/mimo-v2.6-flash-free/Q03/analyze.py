"""Which NYC borough is the most dangerous? Analysis of Motor Vehicle Collisions."""

import numpy as np
import pandas as pd
import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.spatial import cKDTree

plt.rcParams.update({
    "figure.dpi": 130, "savefig.dpi": 160, "font.size": 10,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "grid.linestyle": ":",
})

DATA = "./data/crashes.parquet"
OUT = "./out"

# 2020 U.S. Census populations (external reference, used only for per-capita rates)
POP = {
    "BROOKLYN": 2_736_074, "QUEENS": 2_405_464, "MANHATTAN": 1_694_251,
    "BRONX": 1_472_654, "STATEN ISLAND": 495_747,
}

# ---------------------------------------------------------------- load
con = duckdb.connect()
df = con.sql(f"""
    SELECT crash_date, borough, latitude, longitude, on_street_name, cross_street_name,
           number_of_persons_injured AS injured,
           number_of_persons_killed AS killed
    FROM '{DATA}'
""").df()
print(f"rows: {len(df):,}  |  {df.crash_date.min()} .. {df.crash_date.max()}")
print(f"borough missing: {df.borough.isna().sum():,} ({df.borough.isna().mean()*100:.1f}%)")

NYC = (df.latitude.between(40.4, 40.95) & df.longitude.between(-74.3, -73.6)).fillna(False)
labeled = df.borough.notna() & NYC
candidate = df.borough.isna() & NYC
print(f"stage 1 (coordinates) applicable to {candidate.sum():,} missing-borough rows")

# ---------------------------------- stage 1: nearest-neighbour in lat/lon
xy_l = df.loc[labeled, ["longitude", "latitude"]].to_numpy()
lab_l = df.loc[labeled, "borough"].to_numpy()
tree = cKDTree(xy_l)

# holdout validation: hide 5% of labeled rows, predict from the rest
rng = np.random.default_rng(0)
hold = rng.random(len(xy_l)) < 0.05
tree_h = cKDTree(xy_l[~hold])
d_h, i_h = tree_h.query(xy_l[hold], k=1)
acc_h = (lab_l[~hold][i_h] == lab_l[hold]).mean()
# k=5 vote: flag the ambiguous border cases
d5, i5 = tree_h.query(xy_l[hold], k=5)
votes = lab_l[~hold][i5]
pred5 = pd.DataFrame(votes).mode(axis=1)[0].to_numpy()
ambig = (votes != votes[:, [0]]).any(axis=1)
print(f"holdout NN accuracy: {acc_h:.3%} | where the 5 nearest neighbours disagree "
      f"({ambig.mean():.2%} of rows): {(pred5[ambig] == lab_l[hold][ambig]).mean():.1%}")

xy_c = df.loc[candidate, ["longitude", "latitude"]].to_numpy()
d_c, i_c = tree.query(xy_c, k=1)
stage1 = pd.Series(lab_l[i_c], index=df.index[candidate])
stage1[d_c > 0.01] = np.nan          # ~1 km: reject distant guesses
stage1 = stage1.reindex(df.index)
print(f"stage 1 assigned: {stage1.notna().sum():,}")

# ------------------------ stage 2: street name (validated by holdout test)
df["street"] = df.on_street_name.str.upper().str.strip()
df["cross"] = df.cross_street_name.str.upper().str.strip()
lab_any = df.borough.notna()

def street_map(keys, boro):
    t = pd.DataFrame({"k": keys, "b": boro}).dropna()
    return t.groupby("k")["b"].agg(
        n="size", top=lambda s: s.value_counts().index[0],
        share=lambda s: s.value_counts().iloc[0] / len(s))

k_sc = df["street"] + " @ " + df["cross"]
m_sc = street_map(k_sc[lab_any], df.loc[lab_any, "borough"])
m_s = street_map(df["street"][lab_any], df.loc[lab_any, "borough"])

stage2 = pd.Series(pd.NA, index=df.index, dtype="object")
for keys, m in [(k_sc, m_sc), (df["street"], m_s)]:
    top, share, n = keys.map(m["top"]), keys.map(m["share"]), keys.map(m["n"])
    fill = stage2.isna() & (share >= 0.90) & (n >= 3)
    stage2[fill] = top[fill]

rng = np.random.default_rng(3)
hold2 = lab_any & (rng.random(len(df)) < 0.05)
ok = stage2[hold2].notna()
print(f"stage 2 (street) holdout: coverage {ok.mean():.1%}, "
      f"accuracy {(stage2[hold2][ok] == df.loc[hold2, 'borough'][ok]).mean():.3%} ({ok.sum()} rows)")

df["borough_final"] = df.borough.fillna(stage1).fillna(stage2)
unresolved = df.borough_final.isna()
print(f"assigned total: {df.borough_final.notna().sum():,} "
      f"(given {(~df.borough.isna()).sum():,} + coords {stage1.notna().sum():,} "
      f"+ street {(stage2.notna() & df.borough.isna() & stage1.isna()).sum():,})")
print(f"unresolved: {unresolved.sum():,} ({unresolved.mean()*100:.1f}%) | "
      f"missing {df.loc[unresolved, 'killed'].sum()} of {df.killed.sum()} deaths")

# ------------------------------------------------- metrics
def metrics(frame):
    g = frame.groupby("borough_final").agg(
        crashes=("injured", "size"), injured=("injured", "sum"), killed=("killed", "sum")
    ).reset_index().rename(columns={"borough_final": "borough"})
    g["deaths_per_100k_crashes"] = g.killed / g.crashes * 1e5
    g["inj_per_1k_crashes"] = g.injured / g.crashes * 1e3
    g["pop"] = g.borough.map(POP)
    g["crashes_per_100k_pop"] = g.crashes / g["pop"] * 1e5
    g["deaths_per_100k_pop"] = g.killed / g["pop"] * 1e5
    g["share_city_crashes"] = g.crashes / g.crashes.sum() * 100
    g["share_city_deaths"] = g.killed / g.killed.sum() * 100
    return g.sort_values("crashes", ascending=False).reset_index(drop=True)

m_all = metrics(df[df.borough_final.notna()])
m_raw = metrics(df[df.borough.notna()])          # borough as given, no imputation
m_recent = metrics(df[(df.borough_final.notna()) & (df.crash_date >= "2019-01-01")])

cols = ["borough", "crashes", "injured", "killed", "deaths_per_100k_crashes",
        "inj_per_1k_crashes", "crashes_per_100k_pop", "deaths_per_100k_pop"]
m_all.to_csv(f"{OUT}/borough_metrics.csv", index=False)
print("\n=== ALL YEARS (borough as given + spatial imputation) ===")
print(m_all[cols].to_string(index=False, float_format=lambda v: f"{v:,.1f}"))
print("\n=== SENSITIVITY: borough as given (no imputation) ===")
print(m_raw[cols].to_string(index=False, float_format=lambda v: f"{v:,.1f}"))
print("\n=== 2019-2026 only ===")
print(m_recent[cols].to_string(index=False, float_format=lambda v: f"{v:,.1f}"))

# rankings under competing definitions
print("\n=== RANK 1 BY DEFINITION ===")
for c in ["crashes", "injured", "killed", "deaths_per_100k_crashes",
          "inj_per_1k_crashes", "crashes_per_100k_pop", "deaths_per_100k_pop"]:
    r = m_all.sort_values(c, ascending=False).iloc[0]
    print(f"  {c:26s} -> {r.borough} ({r[c]:,.2f})")

rate_cols = ["crashes", "injured", "killed", "deaths_per_100k_crashes",
             "inj_per_1k_crashes", "crashes_per_100k_pop", "deaths_per_100k_pop"]
ranks = m_all.set_index("borough")[rate_cols].rank(ascending=False)
print("\n=== AVERAGE RANK (1 = most dangerous on that metric) ===")
print(ranks.mean(axis=1).sort_values().round(2).to_string())

# ------------------------------------------------- charts
order = list(m_all.borough)
COLORS = {"BROOKLYN": "#1f4e79", "QUEENS": "#2e75b6", "MANHATTAN": "#7f7f7f",
          "BRONX": "#c00000", "STATEN ISLAND": "#ed7d31"}
c = [COLORS[b] for b in order]

# 1. absolute totals
fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
for ax, col, title in zip(axes, ["crashes", "injured", "killed"],
                          ["Crashes", "Persons injured", "Persons killed"]):
    v = m_all[col]
    ax.bar(order, v, color=c)
    ax.set_title(title)
    ax.tick_params(axis="x", rotation=35)
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    for x, val in enumerate(v):
        ax.text(x, val, f"{val:,}", ha="center", va="bottom", fontsize=8)
    ax.set_ylim(0, v.max() * 1.15)
fig.suptitle("NYC collisions by borough, 2012-07 to 2026-06 (total harm)", y=1.02, fontsize=12)
fig.text(0.5, -0.04, "Borough assigned for 95.6% of records (4.4% left unassigned); "
         "city totals for these panels exclude unassigned records", ha="center", fontsize=8, color="0.4")
fig.tight_layout()
fig.savefig(f"{OUT}/borough_totals.png", bbox_inches="tight")
plt.close(fig)

# 2. rates: severity vs per-capita exposure
fig, axes = plt.subplots(2, 2, figsize=(11, 7.6))
panels = [
    ("deaths_per_100k_crashes", "Deaths per 100,000 crashes", "Severity per crash"),
    ("inj_per_1k_crashes", "Injured per 1,000 crashes", "Injuries per crash"),
    ("crashes_per_100k_pop", "Crashes per 100,000 residents", "Exposure (2012-2026)"),
    ("deaths_per_100k_pop", "Deaths per 100,000 residents", "Lethality per resident"),
]
for ax, (col, ylab, title) in zip(axes.flat, panels):
    v = m_all[col]
    ax.bar(order, v, color=c)
    ax.set_title(title)
    ax.set_ylabel(ylab)
    ax.tick_params(axis="x", rotation=35)
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{x:,.1f}" if abs(x) < 100 else f"{x:,.0f}"))
    for x, val in enumerate(v):
        ax.text(x, val, f"{val:,.1f}", ha="center", va="bottom", fontsize=8)
    ax.set_ylim(0, v.max() * 1.18)
fig.suptitle("Danger by borough: severity and population-adjusted rates", y=1.0, fontsize=12)
fig.tight_layout()
fig.savefig(f"{OUT}/borough_rates.png", bbox_inches="tight")
plt.close(fig)

# 3. annual fatalities per 100k residents (trend)
yr = (df[df.borough_final.notna()].assign(y=lambda d: d.crash_date.dt.year)
      .query("2013 <= y <= 2025")
      .groupby(["y", "borough_final"]).killed.sum().reset_index())
yr["rate"] = yr.apply(lambda r: r.killed / POP[r.borough_final] * 1e5, axis=1)
fig, ax = plt.subplots(figsize=(10, 5))
for b in order:
    s = yr[yr.borough_final == b].set_index("y").rate.reindex(range(2013, 2026))
    ax.plot(s.index, s.values, lw=1, alpha=0.45, color=COLORS[b], marker="o", ms=3)
    ax.plot(s.index, s.rolling(3, min_periods=1).mean(), lw=2.4, color=COLORS[b], label=b)
ax.set_ylabel("Deaths per 100,000 residents (per year)")
ax.set_xlabel("Year")
ax.set_title("Annual traffic deaths per 100k residents by borough\n"
             "(thin lines = actual year, bold = 3-year moving average)")
ax.legend(frameon=False, ncol=3, fontsize=9)
fig.tight_layout()
fig.savefig(f"{OUT}/borough_fatality_trend.png", bbox_inches="tight")
plt.close(fig)

print("\nsaved: borough_totals.png, borough_rates.png, borough_fatality_trend.png, borough_metrics.csv")
