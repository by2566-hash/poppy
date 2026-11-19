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
metric: Annual cyclist deaths divided by annual motorist deaths, expressed as cyclist deaths per 100 motorist deaths
denominator: Annual sum of number_of_motorist_killed; the comparison is normalized to the motorist death count and is undefined if that count is zero
grouping: Calendar year
chart_type: Line chart
probability: 0.3
WRITTEN ANSWER:
Cyclist deaths ranged from 10.0 per 100 motorist deaths in 2013 to 37.8 in 2019, and were 28.4 per 100 in 2025. The metric is the annual sum of recorded cyclist deaths divided by the annual sum of recorded motorist deaths, multiplied by 100, for all NYC police-reported crashes dated in each calendar year; it ranged from 10.0 in 2013 to 37.8 in 2019 and was 28.4 in 2025. This is a defensible relative-count comparison, but because its denominator is motorist deaths rather than cyclist or motorist exposure, it does not show either group's risk or death rate. The plan uses all in-window dated rows and excludes undated or out-of-window crashes by its date filter; among the 2,132,218 included rows, both fatality columns have 0 missing values and there are 0 checked date sentinels, so no included rows are dropped or counted differently, and all 13 years have full observed calendar-year coverage. The included crash-row count rose from 203,742 in 2013 to 231,564 in 2018, then declined to 85,546 in 2025; although this ratio is not divided by crash rows, those varying row totals and unknown road-user exposure prevent treating it as a risk rate.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,cyclist_deaths_per_100_motorist_deaths,cyclist_deaths,motorist_deaths
2013,10.0000,11,110
2014,18.3486,20,109
2015,15.7895,15,95
2016,25.0000,18,72
2017,25.2336,27,107
2018,10.2041,10,98
2019,37.8049,31,82
2020,20.8633,29,139
2021,14.1791,19,134
2022,16.3793,19,116
2023,25.2033,31,123
2024,21.6216,24,111
2025,28.3951,23,81

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python out/data_check.py
# bash
python out/data_check.py
# bash
python out/analyze.py
# bash
python -c "import json; from pathlib import Path; root=Path('out'); [json.loads((root/f'plan_{i}.json').read_text()) for i in (1,2)]; data=json.loads((root/'options.json').read_text()); assert len(data['options']) == 2; assert abs(sum(x['probability'] for x in data['options'])-1) < 1e-9; assert all((root/f'{name}').exists() for name in ['check_1.csv','check_2.csv','values_1.csv','values_2.csv','option_1.png','option_2.png']); print('JSON valid; outputs present; probabilities sum to 1.')"

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