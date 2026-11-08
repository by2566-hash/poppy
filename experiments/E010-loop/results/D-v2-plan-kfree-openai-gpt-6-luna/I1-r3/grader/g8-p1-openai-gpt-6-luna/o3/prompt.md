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
metric: Annual share of crash records with number_of_motorist_killed greater than zero
denominator: All police-reported NYC crash records in that calendar year
grouping: Calendar year of crash_date
chart_type: line chart
probability: 0.3
WRITTEN ANSWER:
The share of crash reports with a motorist death rose from 0.0501% in 2013 to 0.0877% in 2025 (75.1%), not a decline; it does not measure per-mile risk. The per-mile risk question cannot be answered, but this chart shows the crash-level share with at least one motorist death rising from 0.0501% in 2013 to 0.0877% in 2025, with a low of 0.0274% in 2016 and a high of 0.1180% in 2023. This proportion is defensible when the question is whether a reported crash was fatal to a motorist, rather than how many motorists died across crashes. It leaves unanswered individual risk per mile because mileage and motorist exposure are absent. The check found 2,132,218 crash records in 2013–2025, with 0 NULL and 0 negative motorist-death values; zero-death crashes (2,130,945 records) were retained in the denominator and counted as no motorist-death crash, and observed dates span each calendar year's bounds, though that alone does not prove reporting completeness.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,crashes_with_motorist_death,crash_records,share_crashes_with_motorist_death_percent
2013,102,203742,0.050063
2014,99,206046,0.048048
2015,89,217708,0.040880
2016,63,229833,0.027411
2017,100,231007,0.043289
2018,97,231564,0.041889
2019,77,211486,0.036409
2020,126,112918,0.111585
2021,126,110558,0.113967
2022,107,103887,0.102997
2023,114,96607,0.118004
2024,98,91316,0.107320
2025,75,85546,0.087672

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls -la && ls -la data
# bash
python3 out/check_data.py
# bash
python3 out/check_data.py
# bash
python3 -c "print(sum([203640,205947,217619,229770,230907,231467,211409,112792,110432,103780,96493,91218,85471]))"
# bash
python3 out/analyze.py
# bash
python3 -c "print((1-81/110)*100); print(0.946859/0.539898-1); print(0.087672/0.050063-1)"
# bash
python3 -c "import json, pathlib; p=pathlib.Path('out'); o=json.loads((p/'options.json').read_text()); assert len(o['options'])==3; assert abs(sum(x['probability'] for x in o['options'])-1)<1e-9; assert all((p/f'option_{i}.png').is_file() and (p/f'values_{i}.csv').is_file() and json.loads((p/f'plan_{i}.json').read_text())['status']=='final plan' for i in range(1,4)); print('JSON valid; probabilities sum to', sum(x['probability'] for x in o['options']), '; all final plans, charts, and values files present.')"

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