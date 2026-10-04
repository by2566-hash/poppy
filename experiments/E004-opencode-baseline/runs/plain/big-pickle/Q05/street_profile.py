"""
Street profile lookup. Run once a specific street is named:

    python3 street_profile.py "FLATBUSH AVENUE" --borough BROOKLYN

Reports where the street sits in the city-wide distribution for four
definitions of "dangerous", so the answer is relative, not absolute.
"""
import sys
import duckdb
import pandas as pd

con = duckdb.connect()
SRC = "'data/crashes.parquet'"

name = sys.argv[1]
borough = None
if "--borough" in sys.argv:
    borough = sys.argv[sys.argv.index("--borough") + 1].upper()

where = "trim(upper(coalesce(on_street_name,''))) = upper(?)"
params = [name]
if borough:
    where += " AND borough = ?"
    params.append(borough)

mine = con.sql(f"""
    WITH t AS (
        SELECT number_of_persons_killed k, number_of_persons_injured i,
               number_of_pedestrians_killed + number_of_pedestrians_injured pk,
               number_of_cyclist_killed + number_of_cyclist_injured ck,
               number_of_motorist_killed + number_of_motorist_injured mk
        FROM {SRC} WHERE {where}
    )
    SELECT count(*) crashes, sum(k) killed, sum(i) injured, sum(pk) peds, sum(ck) cyc, sum(mk) mots,
           1000.0*sum(k)/count(*) killed_1k, 1000.0*sum(pk)/count(*) ped_1k,
           1000.0*sum(ck)/count(*) cyc_1k, 1000.0*sum(i)/count(*) inj_1k
    FROM t
""", params=params).df().iloc[0]

# comparison pool: same street+borough universe, so ranks are like-for-like
pwhere = "trim(coalesce(on_street_name,'')) <> '' AND borough IS NOT NULL"
pparams = []
if borough:
    pwhere += " AND borough = ?"
    pparams.append(borough)

pool = con.sql(f"""
    WITH t AS (
        SELECT trim(upper(on_street_name)) st, borough b,
               number_of_persons_killed k, number_of_persons_injured i,
               number_of_pedestrians_killed + number_of_pedestrians_injured pk,
               number_of_cyclist_killed + number_of_cyclist_injured ck
        FROM {SRC} WHERE {pwhere}
    )
    SELECT st, b, count(*) n, 1000.0*sum(k)/count(*) killed_1k,
           1000.0*sum(pk)/count(*) ped_1k, 1000.0*sum(ck)/count(*) cyc_1k
    FROM t GROUP BY 1,2 HAVING count(*) >= 100
""", params=pparams).df()


def pct_rank(val, col):
    return round(100.0 * (pool[col] <= val).mean(), 1)


print(f"\n=== {name}" + (f" ({borough})" if borough else " — all boroughs") + " ===")
print(f"police-reported crashes (2012-07..2026-06): {mine.crashes:,.0f}")
print(f"people killed {mine.killed:,.0f} | injured {mine.injured:,.0f} | "
      f"pedestrians hurt {mine.peds:,.0f} | cyclists hurt {mine.cyc:,.0f} | motorists hurt {mine.mots:,.0f}")
print("\npercentile vs other streets (100 = most dangerous):")
for label, col, val in [
    ("crash volume",      None,        None),
    ("fatality rate",     "killed_1k", mine.killed_1k),
    ("pedestrian harm",   "ped_1k",    mine.ped_1k),
    ("cyclist harm",      "cyc_1k",    mine.cyc_1k),
]:
    if col is None:
        rank = 100.0 * (pool.n <= mine.crashes).mean()
    else:
        rank = pct_rank(val, col)
    print(f"  {label:18s} {rank:5.1f}")

print("\nCaveat: this counts only police-reported crashes (injury, death, or")
print(">=$1,000 damage). It is not a count of all crashes, and there is no")
print("traffic-volume denominator, so raw totals measure exposure, not risk.")