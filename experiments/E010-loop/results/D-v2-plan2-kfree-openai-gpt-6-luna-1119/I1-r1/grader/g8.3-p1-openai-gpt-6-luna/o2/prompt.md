You are grading ONE output of a data-analysis agent against a written standard. The chart is attached as an image.
Judge from the materials below only. Do not fix anything, do not redo the analysis. For each item answer PASS or FAIL
(NA if the item does not apply to this output) and quote the sentence, number or chart element that decides it.
Be strict: a limitation that matters but is not stated is a FAIL on the item that asks for it.
If the QUESTION TYPE is "insufficient", the data cannot answer the question as asked; the appropriate output states that
(required_statement) and shows a measure the data does support. Do not FAIL c1 or c2 merely because the measure is not the
one the question named (e.g. not per mile); FAIL them only if the output pretends to answer the unanswerable question.
Rules that follow from the written standard (SCORING.md section 4):
- The DECLARED FRAMING fields are part of the output: a definition given there (e.g. which hours count as night) counts as stated.
- c6 FAILs whenever a disclosure item below (TR.., NIGHTDEF, ...) FAILs: an undisclosed exclusion or an uncaveated denominator is a
  limitation that matters, and an exposure disclaimer does not make up for it. c6 also FAILs when a superlative or comparison in the
  prose (largest, smallest, peak, doubled) is contradicted by the values table.
- Do not invent limitations: rely on DATA FACTS for what is partial, missing or NULL.
- c5: a y-axis that does not start at zero is not a distortion on a line chart when the axis is labelled; on a bar chart it is a FAIL.
- NA, not PASS, when the claim or element an item is about is absent from the output (e.g. no claim that deaths changed sharply);
  PASS means the claim is present and handled.
- A disclaimer whose wording can reasonably be read as a conclusion from the data is judged by that reading: "per-trip risk
  is not greater", or a substitute measure offered as the answer ("so this crash-based proxy did not fall" under a per-mile
  question), FAILS unsupported_claim (and PERMILE where it applies); "does not establish" or "this is not per-mile risk" passes.
- Where an item asks for a qualification or disclosure, wording in the WRITTEN ANSWER or the DECLARED FRAMING counts, in any
  phrasing (it need not say "in this dataset" literally); text that appears only inside the chart image (title, footnote, source
  note) does not satisfy it on its own.
- The official-count part of unsupported_claim concerns death counts presented as the official city toll: on a question with a
  TR07 item it FAILs exactly when TR07 FAILs; elsewhere a count or share computed from this data is not an official-count claim.

DATA FACTS (pinned snapshot):
- The file covers 2012-07-01 to 2026-06-11; 2013-2025 are complete calendar years; 2026 is partial (to June 11).
- borough is NULL for about 20-38% of crashes in every year (TR05): a borough filter silently drops them.
- number_of_persons_killed is NULL in most May-2026 and all June-2026 rows (TR08); 2013-2025 killed counts have no NULLs.
- crash_time has no NULL rows. Reported crash counts (the number of crash records) fall sharply in 2020 (TR01), so a per-reported-crash rate (deaths or injuries divided by reported crashes) compared across years spanning 2020 needs a caveat. Counts of deaths or injuries by year do NOT need it (they are not affected by the reporting change), and a comparison between groups within one pooled window (e.g. day vs night) does not either (decided 2026-11-04; g5 wording after g4 failed c6 on plain death counts).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: Did the risk of a motorist being killed per mile driven in NYC decline from 2013 to 2025? Make a chart and answer based on this crash data.
QUESTION TYPE: insufficient
DECLARED FRAMING:
metric: 100 times the number of crashes with number_of_motorist_killed greater than zero, divided by all eligible crashes in the calendar year.
denominator: All police-reported NYC motor-vehicle crashes with crash_date in that calendar year; each crash counted once.
grouping: Calendar year of crash_date, 2013–2025 inclusive.
chart_type: Line chart
probability: 0.45
WRITTEN ANSWER:
The share of crashes involving a motorist death rose from 0.0501% in 2013 to 0.0877% in 2025, but this is not a per-mile risk measure. For each calendar year from 2013 through 2025, this plots 100 times crashes with at least one recorded motorist death divided by all police-reported NYC motor-vehicle crashes, counting each crash once; the share rose from 102/203,742 (0.0501%) in 2013 to 75/85,546 (0.0877%) in 2025. This is a defensible within-reported-crash frequency measure, but it does not establish whether deaths per mile or an individual motorist's risk changed because miles driven and the population of motorists are not in the file. Data checks found no missing or impossible negative motorist-killed fields (0/203,742 crashes in 2013 and 0/85,546 in 2025, and zero in every intervening year), and each year had dates spanning January 1 through December 31 including 2025. Consequently all in-range crashes were included in the denominators, with none excluded or assigned to an unknown category.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,crashes,crashes_with_motorist_death,crashes_with_motorist_death_pct
2013,203742,102,0.05006331536943782
2014,206046,99,0.048047523368568185
2015,217708,89,0.04088044536718908
2016,229833,63,0.027411207267885814
2017,231007,100,0.043288731510300556
2018,231564,97,0.0418890673852585
2019,211486,77,0.036409029439300945
2020,112918,126,0.11158539825359996
2021,110558,126,0.11396732936558186
2022,103887,107,0.1029965250705093
2023,96607,114,0.11800387135507778
2024,91316,98,0.10731963730342985
2025,85546,75,0.08767212961447642

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python3 -c 'import duckdb, csv, json; from pathlib import Path
base=Path("data/crashes.parquet"); out=Path("out"); con=duckdb.connect()
q="""SELECT EXTRACT(YEAR FROM crash_date)::INTEGER AS yr, COUNT(*) AS candidate_rows, COUNT(*) FILTER (WHERE number_of_motorist_killed IS NULL) AS motorist_killed_missing, COUNT(*) FILTER (WHERE number_of_motorist_killed IS NOT NULL) AS motorist_killed_recorded, MIN(crash_date) AS first_date, MAX(crash_date) AS last_date FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY yr ORDER BY yr"""
rows=con.execute(q,[str(base)]).fetchall(); facts=[]
for y,n,miss,recorded,first,last in rows:
 facts.extend([(f"{y} candidate dated crash rows",n),(f"{y} plan-population rows with recorded motorist-killed field",recorded),(f"{y} rows with missing motorist-killed field among candidate dated crashes",miss),(f"{y} earliest observed crash_date",str(first)),(f"{y} latest observed crash_date",str(last))])
for y,n,miss,recorded,first,last in rows:
 if (first.month,first.day)!=(1,1) or (last.month,last.day)!=(12,31): facts.append((f"{y} observed date span does not reach both calendar-year boundaries (possible partial coverage)",f"first={first}; last={last}"))
facts.append(("plan years with no dated crash rows",", ".join(str(y) for y in range(2013,2026) if y not in {r[0] for r in rows}) or "none"))
facts.append(("crash_date missing among rows assignable to plan years",0))
for i in (1,2):
 with (out/f"check_{i}.csv").open("w",newline="") as f:
  w=csv.writer(f); w.writerow(["fact","value"]); w.writerows(facts)
print(json.dumps(facts,indent=2))'
# bash
python3 -c 'import duckdb, csv, json; from pathlib import Path
base=Path("data/crashes.parquet"); out=Path("out"); con=duckdb.connect()
q="""SELECT EXTRACT(YEAR FROM crash_date)::INTEGER AS yr, COUNT(*) AS candidate_rows, COUNT(*) FILTER (WHERE number_of_motorist_killed IS NULL) AS motorist_killed_missing, COUNT(*) FILTER (WHERE number_of_motorist_killed IS NOT NULL) AS motorist_killed_recorded, MIN(crash_date) AS first_date, MAX(crash_date) AS last_date FROM read_parquet(?) WHERE crash_date >= CAST(? AS DATE) AND crash_date < CAST(? AS DATE) GROUP BY yr ORDER BY yr"""
rows=con.execute(q,[str(base),"2013-01-01","2026-01-01"]).fetchall(); facts=[]
for y,n,miss,recorded,first,last in rows:
 facts.extend([(f"{y} candidate dated crash rows",n),(f"{y} plan-population rows with recorded motorist-killed field",recorded),(f"{y} rows with missing motorist-killed field among candidate dated crashes",miss),(f"{y} earliest observed crash_date",str(first)),(f"{y} latest observed crash_date",str(last))])
for y,n,miss,recorded,first,last in rows:
 if (first.month,first.day)!=(1,1) or (last.month,last.day)!=(12,31): facts.append((f"{y} observed date span does not reach both calendar-year boundaries (possible partial coverage)",f"first={first}; last={last}"))
facts.append(("plan years with no dated crash rows",", ".join(str(y) for y in range(2013,2026) if y not in {r[0] for r in rows}) or "none"))
facts.append(("crash_date missing among rows assignable to plan years",0))
for i in (1,2):
 with (out/f"check_{i}.csv").open("w",newline="") as f:
  w=csv.writer(f); w.writerow(["fact","value"]); w.writerows(facts)
print(json.dumps(facts,indent=2))'
# bash
python3 out/analyze.py
# bash
python3 -c 'import duckdb, csv; from pathlib import Path
con=duckdb.connect(); path=Path("data/crashes.parquet")
rows=con.execute("""SELECT EXTRACT(YEAR FROM crash_date)::INTEGER, COUNT(*) FILTER (WHERE number_of_motorist_killed < 0) FROM read_parquet(?) WHERE crash_date >= CAST(? AS DATE) AND crash_date < CAST(? AS DATE) GROUP BY 1 ORDER BY 1""",[str(path),"2013-01-01","2026-01-01"]).fetchall()
p=Path("out/check_2.csv")
with p.open("a",newline="") as f:
 w=csv.writer(f); w.writerows([(f"{year} plan-column impossible negative motorist-killed counts",count) for year,count in rows])
print(rows)'
# bash
python3 -c 'import json, csv; from pathlib import Path
out=Path("out"); options=json.loads((out/"options.json").read_text()); assert set(options)=={"options"} and len(options["options"])==2; assert abs(sum(x["probability"] for x in options["options"])-1)<1e-9
for i in (1,2):
 plan=json.loads((out/f"plan_{i}.json").read_text()); assert set(plan)=={"initial_plan","data_check","final_plan"}; assert (out/f"option_{i}.png").stat().st_size>0
 with (out/f"values_{i}.csv").open() as f: assert len(list(csv.DictReader(f)))==13
 with (out/f"check_{i}.csv").open() as f: assert set(csv.DictReader(f).fieldnames)=={"fact","value"}
print("Validated two options, plans, checks, 13 yearly values per chart, and non-empty chart files; probabilities sum to 1.")'

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR01: If a per-reported-crash rate spanning 2020 is shown, the output says that the number of recorded crashes changes sharply around 2020 and that this affects comparing the per-crash rate across years (naming the cause, the 2020 recording change, is not required: it is not in the data or the dictionary).
- tr_PERMILE: A per-reported-crash rate, if shown, is not presented as a substitute for per-mile risk.
- tr_VMT: No vehicle-miles figure is imported, assumed or estimated from outside the data.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence
- required_statement: PASS if the output states, in its own words: Per-mile (per vehicle-mile) risk cannot be determined from this data because it has no vehicle-miles or traffic volume.

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.