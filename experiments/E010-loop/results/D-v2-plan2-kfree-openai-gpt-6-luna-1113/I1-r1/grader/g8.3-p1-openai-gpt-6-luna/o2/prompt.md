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
metric: Sum of motorists killed per 100,000 eligible NYC police-reported crashes
denominator: Dated 2013-2025 police-reported crash rows with nonmissing number_of_motorist_killed, within the same year, scaled to 100,000
grouping: Calendar year of crash_date, 2013-2025
chart_type: Line chart
probability: 0.43
WRITTEN ANSWER:
Motorist deaths per 100,000 reported crashes rose from 53.99 in 2013 to 94.69 in 2025, so this per-crash proxy did not decline and does not measure risk per mile. This framing answers whether the number of motorists killed relative to the volume of reported crashes declined: it sums motorist deaths and divides by same-year eligible crash rows, then scales to 100,000; the rate rose from 53.99 in 2013 to 94.69 in 2025. This is defensible as a crash-volume-adjusted comparison, and the denominator is explicitly eligible crash rows with known motorist-death counts. It leaves per-mile risk unanswered because crash counts are not miles driven and the file has no vehicle-miles-traveled exposure. The check found 2,132,218 dated crash rows in 2013-2025, 0 missing motorist-death counts and 0 missing crash dates, so no rows are dropped by the complete-case rule; all years have Jan 1-Dec 31 observed endpoints, and typed DATE values cannot contain empty strings or textual unknowns.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,value,motorist_deaths,eligible_crashes,crashes_with_motorist_death
2013,53.98984991,110,203742,102
2014,52.90080856,109,206046,99
2015,43.63643045,95,217708,89
2016,31.32709402,72,229833,63
2017,46.31894272,107,231007,100
2018,42.32091344,98,231564,97
2019,38.77325213,82,211486,77
2020,123.09817744,139,112918,126
2021,121.20335028,134,110558,126
2022,111.65978419,116,103887,107
2023,127.31996646,123,96607,114
2024,121.55591572,111,91316,98
2025,94.68589998,81,85546,75

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python3 out/data_check.py
# bash
python3 out/data_check.py
# bash
python3 out/analysis.py
# bash
python3 out/analysis.py
# bash
python3 -c "import json, pathlib; p=pathlib.Path('out'); o=json.loads((p/'options.json').read_text()); assert abs(sum(x['probability'] for x in o['options'])-1)<1e-12; assert all((p/f'option_{i}.png').exists() and (p/f'values_{i}.csv').exists() and (p/f'check_{i}.csv').exists() and (p/f'plan_{i}.json').exists() for i in (1,2,3)); [json.loads((p/f'plan_{i}.json').read_text()) for i in (1,2,3)]; print('JSON valid; probabilities sum to 1; all plans, checks, charts, and values exist.')"

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