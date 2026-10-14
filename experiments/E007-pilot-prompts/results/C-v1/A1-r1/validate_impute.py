import numpy as np
import pandas as pd
import duckdb
from scipy.spatial import cKDTree
from collections import Counter

PARQUET = "data/crashes.parquet"

df = duckdb.connect().execute(f"""
    SELECT crash_date, borough, latitude, longitude, on_street_name,
           number_of_pedestrians_injured, number_of_pedestrians_killed
    FROM '{PARQUET}'
""").df()

df["year"] = pd.to_datetime(df["crash_date"]).dt.year
df["is_bk"] = df["borough"] == "BROOKLYN"

lab = df[df["borough"].notna() & df["latitude"].notna() & df["longitude"].notna()].copy()
print("labeled with coords:", len(lab))

# ---- Test 1: kNN imputation accuracy on masked labeled rows (with coords) ----
rng = np.random.default_rng(0)
idx = rng.choice(len(lab), size=min(120_000, len(lab)), replace=False)
tree = cKDTree(lab[["latitude", "longitude"]].to_numpy())
pred_all, true_all = [], []
for i in idx:
    dist, nb = tree.query(lab[["latitude", "longitude"]].to_numpy()[i], k=6)
    # drop self (first neighbor)
    nb = nb[1:]
    votes = lab["borough"].to_numpy()[nb]
    pred_all.append(Counter(votes).most_common(1)[0][0])
    true_all.append(lab["borough"].to_numpy()[i])
pred_all = np.array(pred_all)
true_all = np.array(true_all)
acc = (pred_all == true_all).mean()
print(f"kNN(k=5) accuracy (all masked labeled rows): {acc:.4f}")

# accuracy restricted to pedestrian-injury rows
mask_ped = (lab.loc[idx, "number_of_pedestrians_injured"].to_numpy() > 0) | (
    lab.loc[idx, "number_of_pedestrians_killed"].to_numpy() > 0
)
print(f"kNN accuracy on pedestrian-injury rows (n={mask_ped.sum()}): {(pred_all[mask_ped]==true_all[mask_ped]).mean():.4f}")

# Brooklyn-specific: precision / recall of predicted BROOKLYN
bk_true = true_all == "BROOKLYN"
bk_pred = pred_all == "BROOKLYN"
tp = (bk_true & bk_pred).sum()
print(f"Brooklyn recall: {tp/max(bk_true.sum(),1):.4f}  precision: {tp/max(bk_pred.sum(),1):.4f}  "
      f"(Brooklyn share in sample: {bk_true.mean():.4f}, predicted share: {bk_pred.mean():.4f})")

# ---- Test 2: street-name imputation for rows WITHOUT coords ----
noloc = df[df["borough"].notna() & df["latitude"].isna() & df["on_street_name"].notna()].copy()
withloc = df[df["borough"].notna() & df["latitude"].notna() & df["on_street_name"].notna()]
street_map = (
    withloc.groupby("on_street_name")["borough"]
    .agg(n="size", mode=lambda s: Counter(s).most_common(1)[0][0],
         share=lambda s: Counter(s).most_common(1)[0][1] / len(s))
    .reset_index()
)
usable = street_map[street_map["n"] >= 10]
usable_map = dict(zip(usable["on_street_name"], usable["mode"]))
pred2 = noloc["on_street_name"].map(usable_map)
ok = pred2.notna()
print(f"street imputation coverage (no-coord labeled rows): {ok.mean():.4f}")
print(f"street imputation accuracy where covered: {(pred2[ok]==noloc.loc[ok,'borough']).mean():.4f} (n={ok.sum()})")
# restrict to pedestrian rows
ok_ped = ok & ((noloc["number_of_pedestrians_injured"] > 0) | (noloc["number_of_pedestrians_killed"] > 0))
if ok_ped.sum():
    print(f"street imputation accuracy, pedestrian rows: {(pred2[ok_ped]==noloc.loc[ok_ped,'borough']).mean():.4f} (n={ok_ped.sum()})")
