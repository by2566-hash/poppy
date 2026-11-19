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
metric: Annual number of recorded motorist deaths and cyclist deaths per 1,000 police-reported crash rows, calculated as the relevant *_killed sum divided by the year's crash-row count and multiplied by 1,000
denominator: Count of all police-reported NYC motor vehicle crash rows in each calendar year (not people, trips, miles, or road-user exposure)
grouping: Calendar year, with two series: motorist deaths per 1,000 crashes and cyclist deaths per 1,000 crashes
chart_type: Two-series line chart
probability: 0.3
WRITTEN ANSWER:
This framing answers only part of the question: in 2023, the rates were 1.273 motorist deaths and 0.321 cyclist deaths per 1,000 reported crashes. This answers only part of the question by comparing the sum of each *_killed column divided by the annual count of all police-reported NYC crash rows and multiplied by 1,000, for crash dates in 2013–2025 inclusive, grouped by calendar year and road-user series; in 2023 the measures were 1.273 motorist deaths and 0.321 cyclist deaths per 1,000 crash rows. It is a defensible crash-volume-normalized measure, but it does not answer comparative individual risk because the data contain no motorist or cyclist exposure denominator. The largest neighboring-year denominator change was a decrease of 98,568 crash rows, from 211,486 in 2019 to 112,918 in 2020; a rise or fall in the per-crash measure across those years can result from that denominator shift and not from the death count, so compare the rates with that caution. All years are complete in the file, there are 0 NULL dates and 0 rows at the checked 1900/1970 date sentinels, and both killed columns have 0 missing rows in each year; I retained all eligible crashes in each denominator and no outcome values were omitted for missingness.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,road_user,metric,deaths,crash_rows
2013,Motorist,0.5398984990821726,110,203742
2013,Cyclist,0.05398984990821726,11,203742
2014,Motorist,0.5290080855731244,109,206046
2014,Cyclist,0.09706570377488521,20,206046
2015,Motorist,0.43636430448123176,95,217708
2015,Cyclist,0.06889962702335238,15,217708
2016,Motorist,0.31327094020440927,72,229833
2016,Cyclist,0.07831773505110232,18,229833
2017,Motorist,0.46318942716021594,107,231007
2017,Cyclist,0.11687957507781149,27,231007
2018,Motorist,0.4232091344077663,98,231564
2018,Cyclist,0.04318460555181289,10,231564
2019,Motorist,0.3877325213016464,82,211486
2019,Cyclist,0.14658180683354927,31,211486
2020,Motorist,1.2309817743849518,139,112918
2020,Cyclist,0.2568235356630475,29,112918
2021,Motorist,1.212033502776823,134,110558
2021,Cyclist,0.17185549666238537,19,110558
2022,Motorist,1.1165978418858953,116,103887
2022,Cyclist,0.182891025826138,19,103887
2023,Motorist,1.273199664620576,123,96607
2023,Cyclist,0.3208877203515273,31,96607
2024,Motorist,1.2155591572123177,111,91316
2024,Cyclist,0.26282360155942003,24,91316
2025,Motorist,0.9468589998363454,81,85546
2025,Cyclist,0.26886119748439435,23,85546

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
ls out
# bash
ls data
# bash
python out/data_check.py
# bash
python out/analyze.py
# bash
python out/analyze.py
# bash
python -c "import json,csv,pathlib; p=pathlib.Path('out'); o=json.loads((p/'options.json').read_text()); assert len(o['options'])==2; assert abs(sum(x['probability'] for x in o['options'])-1)<1e-9; [(lambda d: None)(list(csv.DictReader((p/f'values_{i}.csv').open()))) for i in (1,2)]; print('JSON valid; probabilities sum to 1; both values CSVs readable')"
# bash
python out/analyze.py
# bash
python -c "import csv,json,pathlib; p=pathlib.Path('out'); opts=json.loads((p/'options.json').read_text())['options']; assert [x['id'] for x in opts]==[1,2] and abs(sum(x['probability'] for x in opts)-1)<1e-9; [json.loads((p/f'plan_{i}.json').read_text()) for i in (1,2)]; checks=[list(csv.DictReader((p/f'check_{i}.csv').open())) for i in (1,2)]; assert len(checks[0])==len(checks[1])==68; rows={i:list(csv.DictReader((p/f'values_{i}.csv').open())) for i in (1,2)}; assert all(len(v)==26 and {r['year'] for r in v}=={str(y) for y in range(2013,2026)} for v in rows.values()); assert all((p/f'option_{i}.png').is_file() for i in (1,2)); print('Plans and options JSON parse; 13 years × 2 series in each values file; checks and charts present.')"

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