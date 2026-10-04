"""Q: are e-bikes making the streets more dangerous?  Part 2: trends + reporting artifact."""

import duckdb
import pandas as pd

pd.set_option("display.width", 200)

df = pd.read_parquet("./out/_crashes_labelled.parquet")
df["partial_year"] = df.year.isin([2012, 2026])

FULL = df[~df.partial_year]
print("=== 1. e-bike-family crashes per year (any vehicle slot) ===")
yr = df.groupby("year").agg(
    all_crashes=("collision_id", "size"),
    ebike=("ebike_any", "sum"),
    ebike_primary=("ebike_prim", "sum"),
    bicycle=("bicycle_any", "sum"),
)
yr["ebike_share_pct"] = 100 * yr.ebike / yr.all_crashes
yr["bicycle_share_pct"] = 100 * yr.bicycle / yr.all_crashes
print(yr.round(2).to_string())

print("\n=== 2. annualised (partial years 2012 & 2026 scaled) ===")
ann = yr.copy()
frac = df.groupby("year").size()
ann.loc[2012] *= 365 / (pd.Timestamp("2012-12-31") - pd.Timestamp("2012-07-01")).days
ann.loc[2026] *= 365 / (pd.Timestamp("2026-06-11") - pd.Timestamp("2026-01-01")).days + 1
print("2012 raw", yr.loc[2012, "ebike"], "-> annualised", round(ann.loc[2012, "ebike"]))
print("2026 raw", yr.loc[2026, "ebike"], "-> annualised", round(ann.loc[2026, "ebike"]))
print(f"\ne-bike crashes 2013={yr.loc[2013,'ebike']:,}  2025={yr.loc[2025,'ebike']:,} "
      f"-> {yr.loc[2025,'ebike']/yr.loc[2013,'ebike']:.1f}x")
print(f"pedal-bike     2013={yr.loc[2013,'bicycle']:,}  2025={yr.loc[2025,'bicycle']:,} "
      f"-> {yr.loc[2025,'bicycle']/yr.loc[2013,'bicycle']:.2f}x")
print(f"all crashes    2013={yr.loc[2013,'all_crashes']:,}  2025={yr.loc[2025,'all_crashes']:,} "
      f"-> {yr.loc[2025,'all_crashes']/yr.loc[2013,'all_crashes']:.2f}x")

print("\n=== 3. is the total-crash decline real, or a reporting artifact? ===")
df["pdo"] = (df.number_of_persons_injured == 0) & (df.number_of_persons_killed == 0)
rep = df.groupby("year").agg(
    all_crashes=("collision_id", "size"),
    pdo_only=("pdo", "sum"),
    with_injury_or_fatal=("pdo", lambda s: (~s).sum()),
)
rep["pdo_pct"] = 100 * rep.pdo_only / rep.all_crashes
idx = rep.index
print(rep.to_string())
print("\nindex vs 2016 (=100):")
print((100 * rep / rep.loc[2016]).round(1).to_string())

print("\n=== 4. monthly e-bike share, to locate the inflection ===")
mo = df[~df.partial_year].groupby("year_month").agg(
    all_crashes=("collision_id", "size"), ebike=("ebike_any", "sum"))
mo["share_pct"] = 100 * mo.ebike / mo.all_crashes
print(mo[mo.index >= "2019-01"].round(2).to_string())

df.to_parquet("./out/_crashes_labelled.parquet")
