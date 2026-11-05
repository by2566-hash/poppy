"""Check collected F2 A2 runs (no grader): structure, PNGs, CSVs; each values cell recomputed by a direct DuckDB query
under the run's own night definition and window (the A2 gold rows use 2013-2025 and day = 06-17, which no run used)."""
import os
from pathlib import Path as _P
os.chdir(_P(__file__).resolve().parents[3])   # repo root: every path below is relative to it

import json, csv, sys, re
from pathlib import Path
import duckdb, matplotlib.image as mpimg
R = Path("experiments/E009-enumerate/results/D-v2-kfree-openai-gpt-6-luna-rephrasing"); PQ = "data/processed/nyc_crashes.parquet"
span = duckdb.sql(f"SELECT min(crash_date), max(crash_date), max(crash_date)-min(crash_date)+1, count(*) FROM '{PQ}'").fetchone()
print("data window", span[0], "to", span[1], "=", span[2], "calendar dates;", span[3], "rows")
nul = duckdb.sql(f"SELECT year(crash_date) y, count(*) FILTER (WHERE number_of_persons_killed IS NULL), count(*) FILTER (WHERE number_of_persons_injured IS NULL), count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) FROM '{PQ}' GROUP BY 1 HAVING count(*) FILTER (WHERE number_of_persons_killed IS NULL) > 0 ORDER BY 1").fetchall()
print("rows with NULL persons_killed / persons_injured / pedestrians_killed, by year:", nul)
def q(day_end):   # day = 06:00 .. day_end:59
    return duckdb.sql(f"""SELECT CASE WHEN hour(crash_time) BETWEEN 6 AND {day_end} THEN 'day' ELSE 'night' END p,
      count(*) crashes,
      count(*) FILTER (WHERE number_of_persons_injured > 0 OR number_of_persons_killed > 0) harm_any,
      count(*) FILTER (WHERE number_of_persons_injured IS NOT NULL AND number_of_persons_killed IS NOT NULL) complete_both,
      count(*) FILTER (WHERE number_of_persons_injured IS NOT NULL AND number_of_persons_killed IS NOT NULL AND (number_of_persons_injured > 0 OR number_of_persons_killed > 0)) harm_complete,
      count(*) FILTER (WHERE number_of_persons_injured IS NOT NULL) known_inj, count(*) FILTER (WHERE number_of_persons_injured > 0) inj_crash,
      count(*) FILTER (WHERE number_of_persons_killed IS NOT NULL) known_kil, count(*) FILTER (WHERE number_of_persons_killed > 0) fatal,
      count(*) FILTER (WHERE number_of_pedestrians_injured > 0 OR number_of_pedestrians_killed > 0) ped_cas, count(*) FILTER (WHERE number_of_pedestrians_killed > 0) ped_fatal,
      sum(number_of_pedestrians_injured) ped_inj, sum(number_of_pedestrians_killed) ped_kil
      FROM '{PQ}' GROUP BY 1""").df().set_index("p")
D = span[2]
exp = {   # run -> option -> {column: (day, night)}
 "A2-casual-r1": (18, {1: lambda t: {"hours_per_date": (13, 11), "date_span_days": (D, D), "observed_clock_hours": (13*D, 11*D),
                        "crashes_with_recorded_injury_or_death": tuple(t.harm_any), "crashes_with_recorded_injury_or_death_per_clock_hour": (t.harm_any.day/(13*D), t.harm_any.night/(11*D))},
                       2: lambda t: {"crashes_with_complete_injury_and_fatality_counts": tuple(t.complete_both), "crashes_recording_any_injury_or_death": tuple(t.harm_complete),
                        "share_with_injury_or_death_pct": tuple(100*t.harm_complete/t.complete_both)}}),
 "A2-casual-r2": (19, {1: lambda t: {"crashes": tuple(t.crashes), "calendar_days": (D, D), "hours_per_day": (14, 10), "observed_clock_hours": (14*D, 10*D),
                        "crashes_per_clock_hour": (t.crashes.day/(14*D), t.crashes.night/(10*D))},
                       2: lambda t: {"crashes_with_known_injury_count": tuple(t.known_inj), "crashes_with_injury": tuple(t.inj_crash), "injury_crash_percent": tuple(100*t.inj_crash/t.known_inj)},
                       3: lambda t: {"crashes_with_known_killed_count": tuple(t.known_kil), "fatal_crashes": tuple(t.fatal), "fatal_crashes_per_1000": tuple(1000*t.fatal/t.known_kil)}}),
 "A2-casual-r3": (19, {1: lambda t: {"crashes": tuple(t.crashes), "calendar_days": (D, D), "hours_per_daypart": (14, 10), "observed_clock_hours": (14*D, 10*D),
                        "crashes_per_clock_hour": (t.crashes.day/(14*D), t.crashes.night/(10*D))},
                       2: lambda t: {"crashes": tuple(t.crashes), "casualty_crashes": tuple(t.harm_any), "fatal_crashes": tuple(t.fatal),
                        "casualty_crashes_per_1000": tuple(1000*t.harm_any/t.crashes), "fatal_crashes_per_1000": tuple(1000*t.fatal/t.crashes)},
                       3: lambda t: {"crashes": tuple(t.crashes), "pedestrian_casualty_crashes": tuple(t.ped_cas), "pedestrian_fatal_crashes": tuple(t.ped_fatal),
                        "pedestrian_injuries": tuple(t.ped_inj), "pedestrian_deaths": tuple(t.ped_kil),
                        "pedestrian_casualty_crashes_per_1000": tuple(1000*t.ped_cas/t.crashes), "pedestrian_fatal_crashes_per_1000": tuple(1000*t.ped_fatal/t.crashes)}}),
}
for run, (day_end, opts_exp) in exp.items():
    d = R / run; t = q(day_end).reindex(["day", "night"]); opts = json.load(open(d / "out/options.json"))["options"]
    files = sorted(p.name for p in (d / "out").iterdir() if p.name != "options.json")
    expect = sorted(f"{s}_{o['id']}.{e}" for o in opts for s, e in (("option", "png"), ("values", "csv")))
    print(f"{run} (day 06:00-{day_end}:59): files match ids {files == expect}; prob sum {sum(o['probability'] for o in opts):.2f}")
    for o in opts:
        miss = [k for k in ("metric", "denominator", "grouping", "chart_type", "reason", "answer", "interpretation", "probability") if o.get(k) in (None, "")]
        img = mpimg.imread(d / "out" / f"option_{o['id']}.png"); rows = list(csv.DictReader(open(d / "out" / f"values_{o['id']}.csv")))
        e = opts_exp[o["id"]](t); probs = []; unchecked = []
        for i, r in enumerate(rows):
            for c, v in r.items():
                if c == "period": continue
                if c not in e: unchecked.append(c); continue
                ref = float(e[c][i])
                if abs(float(v) - ref) > 1e-4 * max(1, abs(ref)): probs.append((r["period"], c, v, round(ref, 6)))
        print(f"  o{o['id']} p={o['probability']} png {img.shape[1]}x{img.shape[0]} rows={len(rows)} missing={miss} unchecked={sorted(set(unchecked))} value problems={probs}")
