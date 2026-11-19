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
metric: Annual sum of number_of_motorist_killed divided by the number of police-reported crash rows, multiplied by 1,000.
denominator: All NYC police-reported crash rows dated in the same calendar year; scaled per 1,000 crash rows.
grouping: Calendar year of crash_date, 2013-2025 inclusive.
chart_type: Line chart
probability: 0.7
WRITTEN ANSWER:
This file cannot establish per-mile risk; instead, recorded motorist deaths per 1,000 reported crash rows were 0.540 in 2013 and 0.947 in 2025, reaching 1.273 in 2023. Per-mile risk cannot be determined because miles driven is absent; this chart instead shows the annual sum of number_of_motorist_killed divided by all NYC police-reported crash rows dated in that year, multiplied by 1,000, grouped by crash year from 2013 through 2025. The value was 0.540 deaths per 1,000 reported crashes in 2013, peaked at 1.273 in 2023, and was 0.947 in 2025; this is a defensible deaths-per-reported-crash measure, not risk per mile or per journey. Annual denominator rows rose from 203,742 in 2013 to 231,564 in 2018, then generally contracted to 85,546 in 2025, including a sharp drop to 112,918 in 2020; because the number of reported crash rows per year changes substantially, this rate compares deaths per recorded crash rather than changes in travel exposure. The check found no missing crash dates or motorist-death values among 2,132,218 planned rows (0 of 2,132,218 death values missing) and observed January 1-December 31 spans in every year, so all dated rows were retained with no missing-value exclusions; records outside 2013-2025 are out of scope, and the date spans do not prove complete crash capture.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,motorist_deaths,reported_crashes,deaths_per_1000_reported_crashes
2013,110,203742,0.5398984990821726
2014,109,206046,0.5290080855731244
2015,95,217708,0.43636430448123176
2016,72,229833,0.31327094020440927
2017,107,231007,0.46318942716021594
2018,98,231564,0.4232091344077663
2019,82,211486,0.3877325213016464
2020,139,112918,1.2309817743849518
2021,134,110558,1.212033502776823
2022,116,103887,1.1165978418858953
2023,123,96607,1.273199664620576
2024,111,91316,1.2155591572123177
2025,81,85546,0.9468589998363454

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python3 out/check_data.py
# bash
python3 out/analyze.py
# bash
ls out
# bash
python3 -c 'import json,csv,pathlib; p=pathlib.Path("out"); files=[p/"plan_1.json",p/"plan_2.json",p/"options.json"]; [json.loads(f.read_text()) for f in files]; o=json.loads((p/"options.json").read_text()); assert len(o["options"])==2; assert abs(sum(x["probability"] for x in o["options"])-1)<1e-9; rows1=list(csv.DictReader((p/"values_1.csv").open())); rows2=list(csv.DictReader((p/"values_2.csv").open())); assert len(rows1)==len(rows2)==13; assert rows1[0]=={"year":"2013","motorist_deaths":"110"}; assert rows1[-1]=={"year":"2025","motorist_deaths":"81"}; assert rows2[0]["reported_crashes"]=="203742" and rows2[-1]["reported_crashes"]=="85546"; print("JSON valid; options, years, key values, and probabilities verified")'

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