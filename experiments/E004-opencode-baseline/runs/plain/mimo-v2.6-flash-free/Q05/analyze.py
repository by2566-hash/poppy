#!/usr/bin/env python3
"""NYC motor vehicle collisions: how dangerous is a street?

Usage:
  python3 analyze.py                       # citywide charts + street_stats.csv
  python3 analyze.py --street "BROADWAY"   # + a per-street report chart
  python3 analyze.py --street "FLATBUSH AVENUE" --borough BROOKLYN
"""
import argparse
import difflib
import re
from pathlib import Path

import duckdb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

DATA = Path("data/crashes.parquet")
OUT = Path("out")

# ---------------------------------------------------------------- normalization
ABBR = {
    "AVE": "AVENUE", "AV": "AVENUE", "AVEN": "AVENUE",
    "ST": "STREET", "STR": "STREET",
    "RD": "ROAD", "BLVD": "BOULEVARD", "PKWY": "PARKWAY", "PIKE": "PIKE",
    "EXPY": "EXPRESSWAY", "EXPWY": "EXPRESSWAY", "EXPRESSWY": "EXPRESSWAY",
    "DR": "DRIVE", "PL": "PLACE", "LN": "LANE", "CT": "COURT",
    "TER": "TERRACE", "PLZ": "PLAZA", "HWY": "HIGHWAY", "CIR": "CIRCLE",
    "SQ": "SQUARE", "TRL": "TRAIL", "RR": "RAILROAD", "RDWY": "ROADWAY",
}
DIR_FIRST = {"E": "EAST", "W": "WEST", "N": "NORTH", "S": "SOUTH"}
ORDINAL = re.compile(r"^(\d+)(ST|ND|RD|TH)$")


def norm_street(s):
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return None
    s = str(s).upper().strip()
    s = re.sub(r"\(.*?\)", " ", s)          # drop "(BQE)"-style parentheticals
    s = re.sub(r"^\d{5}\s+", "", s)         # drop stray ZIP-code prefixes
    s = re.sub(r"[.,'#]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    if not s:
        return None
    out = []
    for i, tok in enumerate(s.split(" ")):
        m = ORDINAL.match(tok)
        if m:
            tok = m.group(1)
        if i == 0 and tok == "ST":
            tok = "SAINT"                    # ST NICHOLAS AVENUE == SAINT NICHOLAS AVENUE
        elif i == 0 and tok in DIR_FIRST:
            tok = DIR_FIRST[tok]             # E 42 ST == EAST 42 STREET
        elif tok in ABBR:
            tok = ABBR[tok]
        out.append(tok)
    return " ".join(out)


# ---------------------------------------------------------------- load / build
def load() -> pd.DataFrame:
    df = duckdb.connect().execute(
        f"SELECT * FROM '{DATA.as_posix()}'"
    ).df()
    df["street"] = df["on_street_name"].map(norm_street)
    df["cross"] = df["cross_street_name"].map(norm_street)
    df["year"] = pd.to_datetime(df["crash_date"]).dt.year
    df["hour"] = pd.to_datetime(
        df["crash_time"].astype(str), format="%H:%M:%S", errors="coerce"
    ).dt.hour
    df["injured_any"] = (
        df["number_of_persons_injured"].fillna(0)
        + df["number_of_persons_killed"].fillna(0)
    ) > 0
    df["vru"] = (
        df["number_of_pedestrians_injured"].fillna(0)
        + df["number_of_pedestrians_killed"].fillna(0)
        + df["number_of_cyclist_injured"].fillna(0)
        + df["number_of_cyclist_killed"].fillna(0)
    )
    df["vru_crash"] = df["vru"] > 0
    return df


def street_stats(df: pd.DataFrame) -> pd.DataFrame:
    s = df.dropna(subset=["street"])
    g = s.groupby("street")
    st = pd.DataFrame({
        "crashes": g.size(),
        "injured": g["number_of_persons_injured"].sum(),
        "killed": g["number_of_persons_killed"].sum(),
        "ped_cyc_cas": g["vru"].sum(),
        "inj_or_fatal_crashes": g["injured_any"].sum(),
        "vru_crash_share": g["vru_crash"].mean(),
    })
    st["crashes_per_year"] = st["crashes"] / 13.95
    st["pct_crashes_with_injury_or_death"] = 100 * st["inj_or_fatal_crashes"] / st["crashes"]
    st["fatalities_per_1000_crashes"] = 1000 * st["killed"] / st["crashes"]
    st["ped_cyc_share_pct"] = 100 * st["vru_crash_share"]
    br = (
        s.dropna(subset=["borough"])
        .groupby(["street", "borough"]).size().rename("n").reset_index()
        .sort_values("n", ascending=False)
        .groupby("street").agg(boroughs=("borough", lambda x: ", ".join(x[:3])),
                               main_borough=("borough", "first"))
    )
    st = st.join(br)
    eligible = st["crashes"] >= 100
    st["volume_pctile"] = st["crashes"].rank(pct=True) * 100
    st["severity_pctile"] = st.loc[eligible, "pct_crashes_with_injury_or_death"].rank(pct=True) * 100
    return st.sort_values("crashes", ascending=False)


# ---------------------------------------------------------------- citywide charts
def citywide_charts(df: pd.DataFrame, st: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))

    full = df[df["year"].between(2013, 2025)]
    yr = full.groupby("year").agg(
        crashes=("collision_id", "size"),
        injured=("number_of_persons_injured", "sum"),
        killed=("number_of_persons_killed", "sum"),
    )
    ax = axes[0]
    ax.bar(yr.index, yr["crashes"], color="#4C78A8")
    ax.set_title("NYC crashes per year (2013–2025)")
    ax.set_ylabel("crashes")
    ax2 = ax.twinx()
    ax2.plot(yr.index, yr["killed"], color="#E45756", marker="o", lw=2, label="people killed")
    ax2.set_ylabel("people killed", color="#E45756")
    ax2.set_ylim(0, 1.15 * yr["killed"].max())
    ax.set_xticks(yr.index[::2])

    top = st[st["crashes"] >= 100].nlargest(20, "crashes")
    ax = axes[1]
    ax.barh(top.index[::-1], top["crashes"][::-1], color="#72B7B2")
    ax.set_title("Top 20 streets by total crashes")
    ax.set_xlabel("crashes, 2012-07 → 2026-06")

    m = st[st["crashes"] >= 300].copy()
    ax = axes[2]
    sc = ax.scatter(m["crashes_per_year"], m["pct_crashes_with_injury_or_death"],
                    c=m["fatalities_per_1000_crashes"], s=28, cmap="YlOrRd",
                    alpha=.75, vmax=30)
    ax.set_xscale("log")
    ax.set_xlabel("crashes per year (log scale)")
    ax.set_ylabel("% of crashes with injury or death")
    ax.set_title("Volume vs. severity (streets ≥300 crashes)")
    labels = list(m.nlargest(4, "crashes").index)
    labels += [i for i in m.nlargest(2, "fatalities_per_1000_crashes").index
               if i not in labels]
    labels += [i for i in ["FULTON STREET", "QUEENS BOULEVARD", "LINDEN BOULEVARD"]
               if i in m.index and i not in labels]
    labels = labels[:8]
    spread = [8, -12, 20, -24, 32, -36, 44, -48]
    xmax = m["crashes_per_year"].max()
    for k, name in enumerate(labels):
        x = m.loc[name, "crashes_per_year"]
        y = m.loc[name, "pct_crashes_with_injury_or_death"]
        right = x > 0.45 * xmax
        ax.annotate(name, (x, y), fontsize=7,
                    xytext=(-6, spread[k]) if right else (6, spread[k]),
                    textcoords="offset points",
                    ha="right" if right else "left",
                    arrowprops=dict(arrowstyle="-", lw=.5, color="0.35"))
    plt.colorbar(sc, ax=ax, label="fatalities per 1000 crashes")

    fig.tight_layout()
    fig.savefig(OUT / "citywide_overview.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------- per-street report
def street_report(df: pd.DataFrame, st: pd.DataFrame, query: str, borough: str | None) -> str:
    raw = query.upper().strip()
    q = norm_street(raw) or raw
    if q in st.index:
        name = q
    else:
        cands = [i for i in st.index if q in i or i in q]
        if not cands:
            cands = difflib.get_close_matches(q, st.index, n=8, cutoff=0.6)
        if not cands:
            print(f"No street matches {query!r}. Try e.g.: {', '.join(st.head(8).index)}")
            return ""
        if len(cands) > 1:
            print(f"Multiple matches for {query!r}: " + ", ".join(cands[:10]))
        name = max(cands[:10], key=lambda c: st.loc[c, "crashes"])

    sub = df[df["street"] == name]
    scoped = False
    if borough:
        b = sub[sub["borough"].str.upper() == borough.upper()]
        if len(b):
            sub, scoped = b, True
        else:
            print(f"Warning: no {name} crashes with borough={borough!r}; using all boroughs.")
    if not len(sub):
        print(f"No crashes found for {name!r}.")
        return ""

    row = st.loc[name]
    n, inj, kil = len(sub), int(sub["number_of_persons_injured"].sum()), int(sub["number_of_persons_killed"].sum())
    vru = int(sub["vru"].sum())
    vol_pct = row["volume_pctile"]
    sev = 100 * sub["injured_any"].sum() / n
    per_year = n / 13.95
    med_sev = st.loc[st["crashes"] >= 100, "pct_crashes_with_injury_or_death"].median()

    main_b = str(row.get("main_borough", "n/a"))
    if scoped:
        scope = main_b if main_b.upper() == borough.upper() else f"{main_b}, {borough.upper()} only"
    else:
        scope = f"{main_b}, all boroughs"
    print(f"\n{'=' * 70}\n{name}  ({scope})\n{'=' * 70}")
    print(f"Crashes (2012-07 → 2026-06): {n:,}   ~{per_year:.1f}/year")
    print(f"People injured: {inj:,}   People killed: {kil:,}   "
          f"ped/cyclist casualties: {vru:,}")
    print(f"Crashes with injury or death: {sev:.1f}%  "
          f"(median street with 100+ crashes: {med_sev:.1f}%)")
    print(f"Volume percentile vs all named streets: {vol_pct:.0f}th")
    sev_pct = row["severity_pctile"]
    print("Severity percentile vs streets with 100+ crashes: "
          + ("n/a (too few crashes)" if pd.isna(sev_pct) else f"{sev_pct:.0f}th"))

    pairs = (
        sub.dropna(subset=["cross"])
        .groupby("cross").size().sort_values(ascending=False).head(8)
    )
    print("\nMost-crashed intersections:")
    for c, v in pairs.items():
        print(f"  {name} & {c:<30} {v:,} crashes")

    fac = sub["contributing_factor_vehicle_1"].fillna("Unspecified")
    fac = fac[~fac.str.upper().isin(["UNSPECIFIED", "1"])]
    if len(fac):
        print("\nTop listed contributing factors:")
        for f, v in fac.value_counts().head(6).items():
            print(f"  {f:<45} {v:,}")

    slug = re.sub(r"[^A-Z0-9]+", "_", name).strip("_").lower()
    path = OUT / f"street_{slug}.png"

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    full = sub[sub["year"].between(2013, 2025)]
    yr = full.groupby("year").size().reindex(range(2013, 2026), fill_value=0)
    city = (df[df["year"].between(2013, 2025)].groupby("year").size()
            .reindex(range(2013, 2026), fill_value=0))
    ax = axes[0, 0]
    ax.bar(yr.index, yr.values, color="#4C78A8", label=name.title())
    ax.set_title("Crashes per year on this street")
    ax.set_ylabel("crashes")
    ax3 = ax.twinx()
    ax3.plot(city.index, 100 * yr.values / city.values, color="#E45756", lw=2,
             label="% of all NYC crashes")
    ax3.set_ylabel("% of all citywide crashes", color="#E45756")
    ax.set_xticks(yr.index[::3])

    ax = axes[0, 1]
    hrs = sub["hour"].value_counts().reindex(range(24), fill_value=0)
    cityh = df["hour"].value_counts(normalize=True).reindex(range(24), fill_value=0) * len(sub)
    ax.bar(hrs.index, hrs.values, color="#4C78A8", label="this street")
    ax.plot(cityh.index, cityh.values, color="#E45756", lw=2, label="citywide pattern")
    ax.set_title("Time of day")
    ax.set_xlabel("hour of day")
    ax.legend(fontsize=8)

    ax = axes[1, 0]
    ax.barh(pairs.index[::-1], pairs.values[::-1], color="#72B7B2")
    ax.set_title("Worst intersections (crash count)")
    ax.set_xlabel("crashes")

    ax = axes[1, 1]
    facv = sub["contributing_factor_vehicle_1"].fillna("Unspecified")
    facv = facv[~facv.str.upper().isin(["UNSPECIFIED", "1"])]
    fv = facv.value_counts().head(8)[::-1] if len(facv) else pd.Series(dtype=int)
    ax.barh([str(x)[:38] for x in fv.index], fv.values, color="#F58518")
    ax.set_title("Top contributing factors")
    ax.set_xlabel("crashes")

    fig.suptitle(
        f"{name} — {n:,} crashes, {inj:,} injured, {kil:,} killed "
        f"({sev:.1f}% of crashes caused injury or death)",
        fontsize=13, fontweight="bold",
    )
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"\nSaved chart: {path}")
    return path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--street", help="street name to report on")
    ap.add_argument("--borough", help="limit the report to one borough")
    args = ap.parse_args()

    OUT.mkdir(exist_ok=True)
    df = load()
    st = street_stats(df)
    st.to_csv(OUT / "street_stats.csv")

    citywide_charts(df, st)
    print(f"Wrote {OUT / 'street_stats.csv'} ({len(st):,} distinct street names), "
          f"{OUT / 'citywide_overview.png'}")
    if args.street:
        street_report(df, st, args.street, args.borough)
    else:
        print("\nTop 15 streets by crashes:")
        print(st.head(15)[["crashes", "injured", "killed",
                           "pct_crashes_with_injury_or_death"]].round(1).to_string())


if __name__ == "__main__":
    main()
