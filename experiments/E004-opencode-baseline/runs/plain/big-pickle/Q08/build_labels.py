"""Rebuild labels: fast, positionally-correct labelling of each crash."""

import duckdb
import pandas as pd
import numpy as np

con = duckdb.connect()
con.execute("SET threads=4")
df = con.sql("SELECT * FROM './data/crashes.parquet'").df()
NC = len(df)
VCOLS = [f"vehicle_type_code{i}" for i in range(1, 6)]
df["year"] = df.crash_date.dt.year
df["year_month"] = df.crash_date.dt.to_period("M").astype(str)


def mode_codes(s: pd.Series) -> np.ndarray:
    """Return int codes for normalised vehicle mode."""
    t = s.astype(str).str.upper().str.replace(r"[^A-Z0-9]", "", regex=True)
    t = t.replace("NAN", "").replace("UNKNOWNNAN", "")
    electric = t.str.contains(
        "EBIKE|EBIK|EBI|ESCOOT|EMOPED|EUNICYCLE|ESKA|E350", regex=True
    ) | (t.str.startswith("E") & t.str.contains("BIKE|SCOOT|MOPED|UNICYCLE|SKATE", regex=True))
    kick = t.str.contains("SCOOT|SEGWA|SEG|KICKSCOOT|PUSHSC", regex=True)
    moped = t.str.contains("MOPED|MOTORSCOOT", regex=True)
    dirt = t.str.contains("DIRTBIKE|MINIBIKE|DARTBIKE|MOTOCROSS", regex=True)
    motor = t.str.contains("MOTORCYCLE|MOTORBIKE|MOTOBIKE", regex=True)
    bike = t.str.contains("BICYC|BIKE|BICY|CITIBIKE", regex=True)

    MODES = ["motor_vehicle/other", "unknown", "bicycle", "motorcycle", "e_bike",
             "e_scooter", "moped", "kick_scooter", "dirt_bike", "other_electric", "e_moped"]
    c = np.full(len(t), 0, dtype=np.int8)  # default motor_vehicle/other
    c[s.isna().values | t.isin(["UNKNOWN", ""]).values] = 1
    c[((~electric) & bike).values] = 2
    c[((~electric) & motor).values] = 3
    c[(electric & bike).values] = 4
    c[(electric & kick).values] = 5
    c[((~electric) & moped).values] = 6
    c[((~electric) & kick).values] = 7
    c[((~electric) & dirt).values] = 8
    c[electric.values] = 9
    c[(electric & moped).values] = 10
    return c, MODES


# melt: row i  ->  crash i // 5   (value_vars in order, no sorting)
slot_codes = np.empty((NC, 5), dtype=np.int8)
for j, col in enumerate(VCOLS):
    slot_codes[:, j], MODES = mode_codes(df[col])
assert NC * 5 == slot_codes.size

flat = slot_codes.reshape(-1)
crash_ix = np.repeat(np.arange(NC, dtype=np.int64), 5)

for k, m in enumerate(MODES):
    df[f"n_{m}"] = np.bincount(crash_ix, weights=(flat == k), minlength=NC).astype(np.int16)

EB = ["e_bike", "e_scooter", "e_moped"]
df["ebike_any"] = df[[f"n_{m}" for m in EB]].sum(axis=1) > 0
df["ebike_prim"] = np.isin(slot_codes[:, 0], [4, 5, 10])
df["bicycle_any"] = df.n_bicycle > 0
df["n_vehicles"] = slot_codes.shape[1]
df["pdo"] = (df.number_of_persons_injured == 0) & (df.number_of_persons_killed == 0)

print("=== VALIDATION ===")
print("rows:", NC, "| unique ids:", df.collision_id.nunique())
print("e-bike-family vehicle slots :", int(df[[f"n_{m}" for m in EB]].to_numpy().sum()))
print("crashes w/ >=1 e-bike       :", int(df.ebike_any.sum()))
print("crashes w/ e-bike in slot 1 :", int(df.ebike_prim.sum()))
print("crashes w/ >=1 pedal bike   :", int(df.bicycle_any.sum()))
print("crashes w/ >=1 motorcycle   :", int((df.n_motorcycle > 0).sum()))
print("vehicles per crash (mean)   :", round((slot_codes != 0).sum() / NC, 3))

print("\n=== per-year: e-bike / pedal-bike crashes ===")
yr = df.groupby("year").agg(all_crashes=("collision_id", "size"),
                            ebike=("ebike_any", "sum"),
                            bicycle=("bicycle_any", "sum"))
yr["ebike_share_pct"] = (100 * yr.ebike / yr.all_crashes).round(2)
yr["all_bike_share_pct"] = (100 * (yr.ebike + yr.bicycle) / yr.all_crashes).round(2)
print(yr.to_string())

df.to_parquet("./out/_crashes_labelled.parquet")
np.save("./out/_slot_codes.npy", slot_codes)
with open("./out/_modes.txt", "w") as f:
    f.write("\n".join(MODES))
print("\nsaved")
