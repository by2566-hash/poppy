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
metric: Annual cyclist share and complementary motorist share of combined motorist and cyclist deaths
denominator: For each year, summed motorist deaths plus summed cyclist deaths
grouping: Calendar year of crash_date and fatality category: motorist or cyclist
chart_type: 100% stacked bar chart
probability: 0.35
WRITTEN ANSWER:
Cyclists made up 9.1%-27.4% of the combined motorist-and-cyclist deaths each year, with the highest share in 2019; motorists remained the larger share in every year. This answers how the year-by-year balance compares by showing each group's share of the combined annual sums of motorist-killed and cyclist-killed fields for police-reported NYC crashes dated 2013-2025 inclusive; each 100% bar uses only those two fatality categories. Cyclists' share ranged from 9.1% in 2013 to 27.4% in 2019, while the motorist share was larger each year, so this is a defensible view of changing composition. It leaves the absolute annual burden, deaths among pedestrians, and exposure-adjusted risk unanswered because shares normalize only by the combined motorist-and-cyclist total. The date filter leaves out crashes outside 2013-2025 or without an in-range date; within the selected 2,132,218 rows (85,546-231,564 per year), the check found zero missing values in either death field each year and observed Jan 1-Dec 31 dates in every year, so all selected rows are retained, although full reporting completeness cannot be verified.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,motorist_deaths,cyclist_deaths,combined_motorist_cyclist_deaths,motorist_share,cyclist_share
2013,110,11,121,0.9090909090909091,0.09090909090909091
2014,109,20,129,0.8449612403100775,0.15503875968992248
2015,95,15,110,0.8636363636363636,0.13636363636363635
2016,72,18,90,0.8,0.2
2017,107,27,134,0.7985074626865671,0.20149253731343283
2018,98,10,108,0.9074074074074074,0.09259259259259259
2019,82,31,113,0.7256637168141593,0.2743362831858407
2020,139,29,168,0.8273809523809523,0.17261904761904762
2021,134,19,153,0.8758169934640523,0.12418300653594772
2022,116,19,135,0.8592592592592593,0.14074074074074075
2023,123,31,154,0.7987012987012987,0.2012987012987013
2024,111,24,135,0.8222222222222222,0.17777777777777778
2025,81,23,104,0.7788461538461539,0.22115384615384615

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python3 out/data_check.py
# bash
python3 out/data_check.py
# bash
python3 out/analyze.py
# bash
python3 out/analyze.py
# bash
python3 -c "import json; p=json.load(open('out/options.json')); assert len(p['options'])==2; assert abs(sum(x['probability'] for x in p['options'])-1)<1e-12; print('JSON valid; option probabilities sum to 1.0')"
# bash
python3 -c "import json; from pathlib import Path; root=Path('out'); [json.loads((root/f'plan_{i}.json').read_text()) for i in (1,2)]; required=['data_check.py','analyze.py','check_1.csv','check_2.csv','option_1.png','option_2.png','values_1.csv','values_2.csv','options.json']; missing=[name for name in required if not (root/name).exists()]; assert not missing, missing; print('Plans parse; all requested check, chart, values, and options files exist.')"

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