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
metric: Annual recorded motorist deaths per 1,000 police-reported NYC crashes
denominator: All eligible police-reported NYC crashes in each crash year, scaled to 1,000 crashes
grouping: Crash year
chart_type: Line chart
probability: 0.3
WRITTEN ANSWER:
The data cannot establish per-mile risk; recorded motorist deaths per 1,000 crashes increased from 0.54 in 2013 to 0.95 in 2025, despite falling from their 2023 high of 1.27. This framing answers how motorist deaths per reported crash volume changed: the value increased from 0.54 per 1,000 crashes in 2013 to 0.95 in 2025, with a 2023 high of 1.27. It is a defensible normalization that counts multiple deaths in a crash, unlike a share that gives each fatal crash equal weight. It still leaves per-mile risk unanswered because crash counts do not measure miles driven. The check found 2,132,218 crashes in 2013–2025, with observed dates spanning Jan 1–Dec 31 in every year including 2025, and zero missing dates, missing motorist-killed values, or negative counts; zero-death crashes (99.95% in 2013 and 99.91% in 2025) stayed in the crash denominator, and no rows were excluded.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,metric,numerator,denominator,value,crashes_in_population
2013,"Motorist deaths per 1,000 reported crashes",110,203742,0.5398984990821726,203742
2014,"Motorist deaths per 1,000 reported crashes",109,206046,0.5290080855731244,206046
2015,"Motorist deaths per 1,000 reported crashes",95,217708,0.43636430448123176,217708
2016,"Motorist deaths per 1,000 reported crashes",72,229833,0.31327094020440927,229833
2017,"Motorist deaths per 1,000 reported crashes",107,231007,0.46318942716021594,231007
2018,"Motorist deaths per 1,000 reported crashes",98,231564,0.4232091344077663,231564
2019,"Motorist deaths per 1,000 reported crashes",82,211486,0.3877325213016464,211486
2020,"Motorist deaths per 1,000 reported crashes",139,112918,1.2309817743849518,112918
2021,"Motorist deaths per 1,000 reported crashes",134,110558,1.212033502776823,110558
2022,"Motorist deaths per 1,000 reported crashes",116,103887,1.1165978418858953,103887
2023,"Motorist deaths per 1,000 reported crashes",123,96607,1.273199664620576,96607
2024,"Motorist deaths per 1,000 reported crashes",111,91316,1.2155591572123177,91316
2025,"Motorist deaths per 1,000 reported crashes",81,85546,0.9468589998363454,85546

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python -c 'import duckdb, csv, os
con=duckdb.connect()
path="./data/crashes.parquet"
os.makedirs("./out", exist_ok=True)
# Scoped eligibility check: only crash_date and number_of_motorist_killed; outcome values are checked, never aggregated.
base=con.execute("SELECT crash_date, number_of_motorist_killed FROM read_parquet(?)", [path]).fetchdf()
rows=[]
missing_dates=int(base.crash_date.isna().sum())
rows.append(("rows_with_missing_crash_date_unassignable_to_year", missing_dates))
df=base[base.crash_date.notna()].copy()
df["year"]=df.crash_date.dt.year
df=df[df.year.between(2013,2025)]
rows.append(("eligible_rows_with_date_in_2013_2025", len(df)))
for y in range(2013,2026):
 d=df[df.year.eq(y)]
 rows.append((f"eligible_crashes_{y}",len(d)))
 rows.append((f"first_crash_date_{y}", str(d.crash_date.min().date()) if len(d) else "no rows"))
 rows.append((f"last_crash_date_{y}", str(d.crash_date.max().date()) if len(d) else "no rows"))
 rows.append((f"motorist_killed_missing_{y}",int(d.number_of_motorist_killed.isna().sum())))
 rows.append((f"motorist_killed_negative_impossible_{y}",int((d.number_of_motorist_killed.lt(0).fillna(False)).sum())))
 rows.append((f"motorist_killed_zero_{y}",int((d.number_of_motorist_killed.eq(0).fillna(False)).sum())))
for i in (1,2,3):
 with open(f"./out/check_{i}.csv","w",newline="") as f:
  w=csv.writer(f); w.writerow(["fact","value"]); w.writerows(rows)
print("Wrote scoped row-quality and coverage checks to out/check_1.csv, out/check_2.csv, out/check_3.csv")'
# bash
python ./out/analyze.py
# bash
python -c 'import json, csv, math
from pathlib import Path
opts=json.loads(Path("./out/options.json").read_text())["options"]
assert len(opts)==3 and abs(sum(o["probability"] for o in opts)-1)<1e-12
for i,o in enumerate(opts,1):
 rows=list(csv.DictReader(open(f"./out/values_{i}.csv")))
 assert len(rows)==13 and rows[0]["year"]=="2013" and rows[-1]["year"]=="2025"
 if i==1:
  assert int(rows[0]["value"])==110 and int(rows[-1]["value"])==81
 elif i==2:
  assert math.isclose(float(rows[0]["value"]),0.05006331536943782) and math.isclose(float(rows[-1]["value"]),0.08767212961447642)
 else:
  assert math.isclose(float(rows[0]["value"]),0.5398984990821726) and math.isclose(float(rows[-1]["value"]),0.9468589998363454)
 assert Path(f"./out/option_{i}.png").is_file()
print("JSON is valid; probabilities sum to 1; each chart and 2013–2025 values file agrees with the option summaries.")'

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR01: If a per-reported-crash rate spanning 2020 is shown, the output caveats the 2020 change in crash recording (fewer minor crashes reported).
- tr_PERMILE: A per-reported-crash rate, if shown, is not presented as a substitute for per-mile risk.
- tr_VMT: No vehicle-miles figure is imported, assumed or estimated from outside the data.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence
- required_statement: PASS if the output states, in its own words: Per-mile (per vehicle-mile) risk cannot be determined from this data because it has no vehicle-miles or traffic volume.

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.