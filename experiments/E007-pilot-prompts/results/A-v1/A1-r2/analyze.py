import numpy as np
import pandas as pd
import duckdb
from scipy.spatial import cKDTree
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# ---------------------------------------------------------------- load
con = duckdb.connect()
df = con.execute("""
    SELECT crash_date, borough, zip_code, latitude, longitude,
           number_of_persons_injured, number_of_persons_killed,
           number_of_pedestrians_injured AS ped_inj,
           number_of_pedestrians_killed AS ped_killed
    FROM read_parquet('./data/crashes.parquet')
""").df()

df["year"] = pd.to_datetime(df["crash_date"]).dt.year
df["ped_inj"] = df["ped_inj"].fillna(0).astype(int)
df["ped_killed"] = df["ped_killed"].fillna(0).astype(int)

# ------------------------------------------------- impute missing borough
has_boro = df["borough"].notna().values
has_geo = df["latitude"].notna().values & df["longitude"].notna().values
train = df[has_boro & has_geo]
test_idx = np.where(~has_boro & has_geo)[0]
print(f"rows={len(df):,} labeled+geo={len(train):,} to impute={len(test_idx):,} "
      f"unfixable(no geo)={int((~has_boro & ~has_geo).sum()):,}")

tree = cKDTree(train[["latitude", "longitude"]].values)
pts = df.loc[test_idx, ["latitude", "longitude"]].values
dist, nn = tree.query(pts, k=5, workers=-1)
train_boro = train["borough"].values
imputed = np.empty(len(test_idx), dtype=object)
for i in range(len(test_idx)):
    labels, counts = np.unique(train_boro[nn[i]], return_counts=True)
    imputed[i] = labels[np.argmax(counts)]
# distance sanity: flag how far the nearest label was
print("nearest-labeled distance (deg): median=%.5f p95=%.5f max=%.5f"
      % (np.median(dist[:, 0]), np.percentile(dist[:, 0], 95), dist[:, 0].max()))
far = dist[:, 0] > 0.02
imputed = imputed.astype(object)
imputed[far] = None
print(f"far-from-any-labeled (>~2km, left unassigned): {far.sum():,}")
print("imputed borough mix:", pd.Series(imputed).dropna().value_counts().to_dict())

# validation: hide labels of 20k labeled rows and predict from the rest
rng = np.random.default_rng(0)
val_pos = np.where(has_boro & has_geo)[0]
keep = rng.choice(val_pos, size=20000, replace=False)
mask = np.ones(len(df), bool)
mask[keep] = False
train_v = df[has_boro & has_geo & mask]
tv = cKDTree(train_v[["latitude", "longitude"]].values)
d_v, nn_v = tv.query(df.loc[keep, ["latitude", "longitude"]].values, k=1, workers=-1)
pred = train_v["borough"].values[nn_v]
acc = (pred == df.loc[keep, "borough"].values).mean()
print(f"kNN borough imputation accuracy on held-out labeled rows: {acc:.3f}")

df.loc[test_idx, "borough"] = imputed

# ------------------------------------------------- yearly Brooklyn metrics
full = df[df["year"].between(2013, 2025)].copy()   # drop 2012 (starts 7/1) & 2026 (partial)
bk = full[full["borough"] == "BROOKLYN"]
ny = full

tbl = bk.groupby("year").agg(
    bk_crashes=("ped_inj", "size"),
    bk_ped_injured=("ped_inj", "sum"),
    bk_ped_killed=("ped_killed", "sum"),
).reset_index()
city = ny.groupby("year").agg(
    nyc_ped_injured=("ped_inj", "sum"),
    nyc_ped_killed=("ped_killed", "sum"),
).reset_index()
tbl = tbl.merge(city, on="year")
tbl["bk_share_of_nyc_injuries_pct"] = 100 * tbl.bk_ped_injured / tbl.nyc_ped_injured
tbl["bk_injured_per_1000_crashes"] = 1000 * tbl.bk_ped_injured / tbl.bk_crashes

print(tbl.to_string(index=False))

v2013 = int(tbl.loc[tbl.year == 2013, "bk_ped_injured"].iloc[0])
v2025 = int(tbl.loc[tbl.year == 2025, "bk_ped_injured"].iloc[0])
v2021 = int(tbl.loc[tbl.year == 2021, "bk_ped_injured"].iloc[0])
k2013 = int(tbl.loc[tbl.year == 2013, "bk_ped_killed"].iloc[0])
k2025 = int(tbl.loc[tbl.year == 2025, "bk_ped_killed"].iloc[0])
k_avg1315 = tbl.loc[tbl.year.between(2013, 2015), "bk_ped_killed"].mean()
k_avg2325 = tbl.loc[tbl.year.between(2023, 2025), "bk_ped_killed"].mean()
print("\n2013 injuries %d -> 2025 %d (%.1f%%)" % (v2013, v2025, 100 * (v2025 - v2013) / v2013))
print("2021 injuries %d -> 2025 %d (%.1f%%)" % (v2021, v2025, 100 * (v2025 - v2021) / v2021))
print("deaths 2013 %d -> 2025 %d; avg 13-15 %.1f vs avg 23-25 %.1f"
      % (k2013, k2025, k_avg1315, k_avg2325))
print("max/min injury year:", int(tbl.bk_ped_injured.max()), int(tbl.bk_ped_injured.min()))

# ---------------------------------------------------------------- chart
out = tbl.copy()
out.to_csv("./out/values.csv", index=False)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.edgecolor": "#444444",
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})

fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(11, 8.5), sharex=True,
    gridspec_kw={"height_ratios": [1.45, 1], "hspace": 0.12},
)

years = out["year"].values
colors = ["#9ec5d8"] * len(years)
colors[int(np.where(years == 2013)[0][0])] = "#1f4e79"
colors[int(np.where(years == 2025)[0][0])] = "#c0392b"

bars = ax1.bar(years, out.bk_ped_injured, width=0.72, color=colors, zorder=3)
ax1.set_title("Pedestrians injured in Brooklyn crashes",
              fontsize=14, fontweight="bold", loc="left", pad=8)
ax1.yaxis.set_major_locator(MaxNLocator(nbins=6))
ax1.grid(axis="y", color="#dddddd", lw=0.8, zorder=0)
ax1.set_axisbelow(True)
for s in ["top", "right"]:
    ax1.spines[s].set_visible(False)

for x, v in zip(years, out.bk_ped_injured):
    ax1.text(x, v + 40, f"{v:,}", ha="center", va="bottom",
             fontsize=8.5, color="#333333")

i13, i21, i25 = (int(np.where(years == y)[0][0]) for y in (2013, 2021, 2025))
ax1.annotate("", xy=(2025, out.bk_ped_injured[i25] + 330),
             xytext=(2013, out.bk_ped_injured[i13] + 330),
             arrowprops=dict(arrowstyle="->", color="#1f4e79", lw=1.6))
ax1.text(2019, out.bk_ped_injured.max() + 400,
         f"down {100*(out.bk_ped_injured[i25]-out.bk_ped_injured[i13])/out.bk_ped_injured[i13]:.0f}% vs 2013",
         ha="center", fontsize=11, color="#1f4e79", fontweight="bold")

ax2.plot(years, out.bk_ped_killed, color="#c0392b", lw=2.2, marker="o",
         ms=7, zorder=3, label="Pedestrians killed")
ax2.axhline(out.bk_ped_killed.mean(), color="#888888", ls="--", lw=1.2,
            label=f"13-year average ({out.bk_ped_killed.mean():.0f})")
ax2.set_title("Pedestrians killed in Brooklyn crashes",
              fontsize=14, fontweight="bold", loc="left", pad=8)
ax2.set_ylabel("Killed")
ax2.grid(axis="y", color="#dddddd", lw=0.8, zorder=0)
ax2.set_axisbelow(True)
for s in ["top", "right"]:
    ax2.spines[s].set_visible(False)
for x, v in zip(years, out.bk_ped_killed):
    ax2.annotate(f"{v}", (x, v), textcoords="offset points", xytext=(0, 9),
                 ha="center", fontsize=8.5, color="#c0392b")
ax2.legend(frameon=False, fontsize=10, loc="upper right", ncol=2)
ax2.set_xticks(years)
ax2.set_xticklabels([str(y) for y in years], fontsize=10)
ax2.set_ylim(0, max(out.bk_ped_killed) * 1.35)

fig.suptitle(
    "Brooklyn streets got safer for walkers after 2013 — then the gains stalled",
    fontsize=17, fontweight="bold", x=0.012, ha="left", y=0.985)
fig.text(0.012, 0.938,
         "Pedestrian injuries have fallen sharply since 2013, but they have climbed every year "
         "since 2021, and deaths remain near their long-run average.",
         fontsize=11.5, color="#333333", ha="left")
fig.text(0.012, 0.012,
         "Source: NYPD Motor Vehicle Collisions (one row per crash), years 2013–2025; 2012 and 2026 "
         "excluded (partial years). Borough missing on ~30% of records and imputed from coordinates "
         f"by 5-nearest-neighbor lookup (validated accuracy {acc:.0%}).",
         fontsize=8.5, color="#666666", ha="left")

fig.subplots_adjust(top=0.86, bottom=0.09, left=0.075, right=0.975)
fig.savefig("./out/initial.png", dpi=160)
print("saved ./out/initial.png and ./out/values.csv")
