"""Build gold_readings.json: for each dev question, every reading the scorer may match, keyed by name, with
the DuckDB query that produced it (independent SQL, same window as gold_pilot.py), plus the written standard
the grader applies: the question's trap-sheet items (SCORING.md §4) and, for insufficient questions, the
required statement. Readings are added only when a run produced one that a human judged legitimate (plan §4).

  ~/.poppy/venv/bin/python experiments/E007-pilot-prompts/gold_readings.py
"""
import json, duckdb
from pathlib import Path
HERE = Path(__file__).resolve().parent
P = HERE.parents[1] / "data" / "processed" / "nyc_crashes.parquet"
W = "year(crash_date) BETWEEN 2013 AND 2025"
BK = "upper(borough)='BROOKLYN'"
DN = "CASE WHEN hour(crash_time) BETWEEN 6 AND 17 THEN 'day' ELSE 'night' END"

# name -> (key kind, SQL). First column is the key; the others are the gold columns. kind: year | weekday (0 = Sunday) | period | hour
READINGS = {
 "K1": {"ped_killed_by_year": ("year", f"SELECT year(crash_date) k, sum(number_of_pedestrians_killed) pedestrians_killed FROM '{P}' WHERE {W} GROUP BY 1 ORDER BY 1")},
 "K2": {"crashes_by_weekday": ("weekday", f"SELECT dayofweek(crash_date) k, count(*) crashes FROM '{P}' WHERE {W} GROUP BY 1 ORDER BY 1")},
 "K3": {"motorist_cyclist_killed_by_year": ("year", f"SELECT year(crash_date) k, sum(number_of_motorist_killed) motorist_killed, sum(number_of_cyclist_killed) cyclist_killed FROM '{P}' WHERE {W} GROUP BY 1 ORDER BY 1")},
 "A1": {"brooklyn_ped_injured_killed_by_year": ("year", f"SELECT year(crash_date) k, sum(number_of_pedestrians_injured) pedestrians_injured, sum(number_of_pedestrians_killed) pedestrians_killed FROM '{P}' WHERE {W} AND {BK} GROUP BY 1 ORDER BY 1"),
        "brooklyn_crashes_by_year": ("year", f"SELECT year(crash_date) k, count(*) crashes FROM '{P}' WHERE {W} AND {BK} GROUP BY 1 ORDER BY 1")},
 "A2": {"day_night_06_17": ("period", f"SELECT {DN} k, count(*) crashes, sum(number_of_persons_killed) killed, sum(number_of_persons_injured) injured FROM '{P}' WHERE {W} GROUP BY 1 ORDER BY 1"),
        "by_hour": ("hour", f"SELECT hour(crash_time) k, count(*) crashes, sum(number_of_persons_killed) killed, sum(number_of_persons_injured) injured FROM '{P}' WHERE {W} GROUP BY 1 ORDER BY 1")},
 "I1": {"motorist_killed_by_year": ("year", f"SELECT year(crash_date) k, sum(number_of_motorist_killed) motorist_killed FROM '{P}' WHERE {W} GROUP BY 1 ORDER BY 1"),
        "crashes_and_all_killed_by_year": ("year", f"SELECT year(crash_date) k, count(*) crashes, sum(number_of_persons_killed) persons_killed FROM '{P}' WHERE {W} GROUP BY 1 ORDER BY 1")},
}

# The written standard per question (from SCORING.md §4). Each trap item is a PASS/FAIL question for the grader.
STANDARD = {
 "K1": {"type": "clear", "traps": [
   {"id": "TR07", "item": "The output does not present the open-data death counts as the official NYC toll (reporting them as counts in this dataset is fine).", "note": "open-data deaths differ from official counts (2025: 229 here vs 205 NYC DOT)"},
   {"id": "CAUSAL", "item": "The output makes no causal attribution (e.g. 'because of the pandemic') that the data cannot support.", "note": "causal asides fail criterion 6"}]},
 "K2": {"type": "clear", "traps": [
   {"id": "TR01", "item": "If counts are pooled over 2013–2025, the output says that pre-2020 years dominate or that crash reporting changed in 2020.", "note": "crashes 211,486 in 2019 → 110,558 in 2021 → 85,546 in 2025"},
   {"id": "DAYCOUNT", "item": "If per-day averages or 'X% fewer on <day>' comparisons are given, the arithmetic is right (e.g. Sunday has 24% fewer than the mean weekday, Friday 32% more) and unequal day counts (678/679) are handled or noted.", "note": "Tue and Wed occur 679 times, other days 678"}]},
 "K3": {"type": "clear", "traps": [
   {"id": "TR15", "item": "Claims about cyclist deaths changing sharply (e.g. 'tripled') are qualified by the small counts (10 → 31).", "note": "small numbers"},
   {"id": "TR03", "item": "The output does not claim that motorist + cyclist deaths are all deaths (pedestrians and unclassified deaths exist).", "note": "residual 6–20 deaths per year outside the three mode columns, 2021–2025"}]},
 "A1": {"type": "ambiguous", "traps": [
   {"id": "TR05", "item": "If a borough filter (borough = 'BROOKLYN') is used, the output discloses that crashes with no borough recorded (19.9–38.1% per year) are excluded.", "note": "undisclosed borough filter fails"},
   {"id": "TR11", "item": "The output does not call Brooklyn 'safer' or 'less safe' from counts alone without saying that there is no pedestrian exposure measure.", "note": "counts are not risk"},
   {"id": "TR01", "item": "If a per-crash rate spanning 2020 is shown, the output caveats the 2020 change in crash recording.", "note": "per-crash denominators collapse after 2020"},
   {"id": "TR15", "item": "Claims about pedestrian deaths changing are qualified by the small counts (about 30–39 per year).", "note": "small numbers"}]},
 "A2": {"type": "ambiguous", "traps": [
   {"id": "TR11", "item": "Severity per crash (deaths or injuries per crash) is described as such, not as the risk of being on the street at night (no traffic volume by hour exists).", "note": "no exposure"},
   {"id": "TR08", "item": "The analysis window is 2013–2025, or 2026 rows (killed count NULL in 87.8% of May-2026 and 100% of June-2026 rows) are excluded or handled, and sums are NULL-safe.", "note": "a window including 2026 biases fatality rates low"},
   {"id": "NIGHTDEF", "item": "The definition of 'night' (hours) is stated.", "note": "the cut is one of several defensible ones"}]},
 "I1": {"type": "insufficient", "required_statement": "Per-mile (per vehicle-mile) risk cannot be determined from this data because it has no vehicle-miles or traffic volume.", "traps": [
   {"id": "TR01", "item": "If a per-reported-crash rate spanning 2020 is shown, the output caveats the 2020 change in crash recording (fewer minor crashes reported).", "note": "per-crash denominators collapse after 2020"},
   {"id": "PERMILE", "item": "A per-reported-crash rate, if shown, is not presented as a substitute for per-mile risk.", "note": "per-crash is not per-mile"},
   {"id": "VMT", "item": "No vehicle-miles figure is imported, assumed or estimated from outside the data.", "note": "any VMT number is unsourced"}]},
}

if __name__ == "__main__":
    con = duckdb.connect()
    out = {}
    for q, rd in READINGS.items():
        out[q] = dict(STANDARD[q]); out[q]["readings"] = {}
        for name, (kind, sql) in rd.items():
            cur = con.execute(sql); cols = [d[0] for d in cur.description]
            rows = [[r[0] if isinstance(r[0], str) else int(r[0])] + [float(x) if x is not None else None for x in r[1:]] for r in cur.fetchall()]
            out[q]["readings"][name] = {"key_kind": kind, "columns": cols[1:], "rows": rows, "query": sql.replace(str(P), "<parquet>"), "source": "gold_readings.py, audit 2026-10-21 window"}
            print(q, name, len(rows), rows[:2])
    (HERE / "gold_readings.json").write_text(json.dumps(out, indent=1))
