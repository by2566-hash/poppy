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

QUESTION ASKED: How do motorist and cyclist deaths compare year by year in NYC, 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: For each calendar year, the share of the combined motorist and cyclist death count attributable to motorists and to cyclists, calculated separately
denominator: For each year, the sum of number_of_motorist_killed and number_of_cyclist_killed; the two displayed group shares sum to 100% when this denominator is positive
grouping: Calendar year and road-user group (motorist, cyclist)
chart_type: 100% stacked bar chart by year
probability: 0.25
WRITTEN ANSWER:
Among motorist-plus-cyclist deaths, the motorist share was 72.6%–90.9% by year and the cyclist share was 9.1%–27.4%; in 2025 the shares were 77.9% and 22.1%, respectively. For each crash year from 2013 through 2025, the chart divides each group's summed deaths by that year's combined motorist-and-cyclist death total; motorist shares range from 72.6% to 90.9% and cyclist shares from 9.1% to 27.4% (77.9% and 22.1% in 2025). A 100%-stacked bar is defensible for comparing this within-year composition while making explicit that each year's two shares total 100%. Because the denominator excludes pedestrians and other road users, this does not show either group's share of all traffic deaths or a risk rate. The final plan retains all 2,132,218 crashes with dates in 2013–2025: both summed death columns have 0 missing values and the selected rows have 0 missing/default dates; the date filter excludes null or out-of-range dates (not counted separately in this scoped check), observed date extents span Jan–Dec in every year, and no outcome rows were dropped or imputed.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,road_user,deaths,combined_deaths_denominator,share_percent
2013,Cyclist,11,121,9.0909
2013,Motorist,110,121,90.9091
2014,Cyclist,20,129,15.5039
2014,Motorist,109,129,84.4961
2015,Cyclist,15,110,13.6364
2015,Motorist,95,110,86.3636
2016,Cyclist,18,90,20.0000
2016,Motorist,72,90,80.0000
2017,Cyclist,27,134,20.1493
2017,Motorist,107,134,79.8507
2018,Cyclist,10,108,9.2593
2018,Motorist,98,108,90.7407
2019,Cyclist,31,113,27.4336
2019,Motorist,82,113,72.5664
2020,Cyclist,29,168,17.2619
2020,Motorist,139,168,82.7381
2021,Cyclist,19,153,12.4183
2021,Motorist,134,153,87.5817
2022,Cyclist,19,135,14.0741
2022,Motorist,116,135,85.9259
2023,Cyclist,31,154,20.1299
2023,Motorist,123,154,79.8701
2024,Cyclist,24,135,17.7778
2024,Motorist,111,135,82.2222
2025,Cyclist,23,104,22.1154
2025,Motorist,81,104,77.8846

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
pwd && ls
# bash
ls
# bash
python3 out/data_check.py
# bash
python3 out/analyze.py
# bash
python3 out/analyze.py && python3 -c 'import csv, json, os; from pathlib import Path; opts=json.load(open("out/options.json")); assert [o["id"] for o in opts["options"]] == [1,2]; assert abs(sum(o["probability"] for o in opts["options"])-1)<1e-9; plans=[json.load(open(f"out/plan_{i}.json")) for i in (1,2)]; assert all(p["status"]=="final" and p["limitations"] for p in plans); assert all(Path(f"out/option_{i}.png").stat().st_size>0 for i in (1,2)); rows1=list(csv.DictReader(open("out/values_1.csv"))); rows2=list(csv.DictReader(open("out/values_2.csv"))); assert len(rows1)==26 and len(rows2)==26; assert {r["year"] for r in rows1}=={str(y) for y in range(2013,2026)}; assert {r["year"] for r in rows2}=={str(y) for y in range(2013,2026)}; assert all(float(r["share_percent"])>=0 for r in rows2); print("validated plans, JSON, 13-year values, and charts")'

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR15: Claims about cyclist deaths changing sharply (e.g. 'tripled') are qualified by the small counts (10 → 31).
- tr_TR03: The output does not claim that motorist + cyclist deaths are all deaths (pedestrians and unclassified deaths exist).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.