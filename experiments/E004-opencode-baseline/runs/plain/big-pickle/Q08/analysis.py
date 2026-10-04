"""Analysis: are e-bikes making NYC streets more dangerous?"""

import duckdb
import pandas as pd
import numpy as np

con = duckdb.connect()
con.execute("SET threads=4")
df = con.sql("SELECT * FROM './data/crashes.parquet'").df()
VCOLS = [f"vehicle_type_code{i}" for i in range(1, 6)]

df["year"] = df.crash_date.dt.year
df["year_month"] = df.crash_date.dt.to_period("M").astype(str)


def classify(s: pd.Series) -> pd.Series:
    """Map a raw vehicle_type_code to a normalised mode category."""
    t = s.astype(str).str.upper().str.replace(r"[^A-Z0-9]", "", regex=True)
    t = t.str.replace(r"UNKNOWNNAN|NAN", "", regex=True)
    out = pd.Series(pd.NA, index=s.index, dtype=object)

    electric = t.str.contains("EBIKE|EBIK|EBI|ESCOOT|ESCOOTER|EMOPED|EUNICYCLE|ESKA|E350", regex=True) | (
        t.str.startswith("E") & t.str.contains("BIKE|SCOOT|MOPED|UNICYCLE|SKATE", regex=True)
    )
    # gas/bike-family base categories
    kick = t.str.contains("SCOOT|SEGWA|SEG|KICKSCOOT|PUSHSC", regex=True)
    moped = t.str.contains("MOPED", regex=True) | t.str.contains("MOTORSCOOT", regex=True)
    dirt = t.str.contains("DIRTBIKE|MINIBIKE|DARTBIKE|MOTOCROSS", regex=True)
    motor = t.str.contains("MOTORCYCLE|MOTORBIKE|MOTOBIKE|MOTOR", regex=True)
    bike = t.str.contains("BICYC|BIKE|BICY|CITIBIKE", regex=True)

    out[electric] = "other_electric"
    out[electric & kick] = "e_scooter"
    out[electric & moped] = "e_moped"
    out[electric & bike] = "e_bike"

    out[(~electric) & kick] = "kick_scooter"
    out[(~electric) & moped] = "moped"
    out[(~electric) & dirt] = "dirt_bike"
    out[(~electric) & motor] = "motorcycle"
    out[(~electric) & bike] = "bicycle"

    out = out.fillna("motor_vehicle/other")
    out[s.astype(str).str.upper().isin(["UNKNOWN", ""])] = "unknown"
    return out


veh_long = df.melt(
    id_vars=[c for c in df.columns if c not in VCOLS],
    value_vars=VCOLS,
    value_name="vtype_raw",
)
veh_long["mode"] = classify(veh_long.vtype_raw)

print("=== vehicle-mode frequency (all vehicle slots, 2012-2026) ===")
print(veh_long["mode"].value_counts().to_string())

# sanity: raw totals for the electric family
raw = pd.concat([df[c] for c in VCOLS]).astype(str).str.upper()
fam = raw[raw.str.contains("BIKE|SCOOT|MOPED", regex=True)]
print("\nraw slots mentioning BIKE/SCOOT/MOPED:", len(fam))
print(fam.value_counts().head(25).to_string())

prim = classify(df.vehicle_type_code1)
any_ = veh_long.groupby("collision_id")["mode"].apply(set)

print("\n=== primary (slot 1) vs any-vehicle involvement ===")
print(f"{'mode':<20}{'primary':>10}{'any':>10}{'any/prim':>10}")
for m in ["e_bike", "e_scooter", "e_moped", "other_electric", "bicycle", "moped",
          "kick_scooter", "motorcycle", "dirt_bike"]:
    p = int((prim == m).sum())
    a = int(any_.apply(lambda s: m in s).sum())
    print(f"{m:<20}{p:>10,}{a:>10,}{(a/p if p else float('nan')):>10.2f}")

EBIKE_FAMILY = {"e_bike", "e_scooter", "e_moped"}
df["ebike_any"] = any_.apply(lambda s: bool(s & EBIKE_FAMILY)).values
df["bicycle_any"] = any_.apply(lambda s: "bicycle" in s).values
df["ebike_prim"] = prim.isin(EBIKE_FAMILY).values

df.to_parquet("./out/_crashes_labelled.parquet")
print("\nwrote labelled crash table:", len(df), "rows")
