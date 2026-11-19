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
metric: Annual share of combined motorist-plus-cyclist deaths attributable to motorists and to cyclists
denominator: For each calendar year, the sum of motorist and cyclist deaths across crashes with both death counts present
grouping: Calendar year of crash_date, with separate motorist and cyclist shares
chart_type: 100% stacked bar chart
probability: 0.35
WRITTEN ANSWER:
Motorists accounted for 72.6%–90.9% of combined motorist-and-cyclist deaths each year, while cyclists accounted for 9.1%–27.4%; the cyclist share was highest in 2019 (27.4%) and lowest in 2013 (9.1%). This framing answers the year-by-year relative mix by dividing each category's summed death count by the combined motorist-plus-cyclist count for that same calendar year; cyclist shares ranged from 9.1% in 2013 to 27.4% in 2019, and motorist shares ranged from 72.6% to 90.9%. It is defensible for comparing the composition of these two recorded categories, but its denominator excludes pedestrians and other possible road users and it does not compare risk or exposure. The population is police-reported crash records dated 2013–2025 with both death fields present, grouped by full calendar year. The check found 2,132,218 in-period crash rows, no missing death values in either field and no missing crash dates (zero rows excluded by the complete-pair rule), no default-like dates, and complete January-to-December coverage in each year, so none of these in-period rows were dropped or counted differently because of the checks.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,road_user,deaths,denominator,share,share_percent
2013,motorist,110,121,0.9090909090909091,90.9090909090909
2014,motorist,109,129,0.8449612403100775,84.49612403100775
2015,motorist,95,110,0.8636363636363636,86.36363636363636
2016,motorist,72,90,0.8,80.0
2017,motorist,107,134,0.7985074626865671,79.8507462686567
2018,motorist,98,108,0.9074074074074074,90.74074074074075
2019,motorist,82,113,0.7256637168141593,72.56637168141593
2020,motorist,139,168,0.8273809523809523,82.73809523809523
2021,motorist,134,153,0.8758169934640523,87.58169934640523
2022,motorist,116,135,0.8592592592592593,85.92592592592592
2023,motorist,123,154,0.7987012987012987,79.87012987012987
2024,motorist,111,135,0.8222222222222222,82.22222222222221
2025,motorist,81,104,0.7788461538461539,77.88461538461539
2013,cyclist,11,121,0.09090909090909091,9.090909090909092
2014,cyclist,20,129,0.15503875968992248,15.503875968992247
2015,cyclist,15,110,0.13636363636363635,13.636363636363635
2016,cyclist,18,90,0.2,20.0
2017,cyclist,27,134,0.20149253731343283,20.149253731343283
2018,cyclist,10,108,0.09259259259259259,9.25925925925926
2019,cyclist,31,113,0.2743362831858407,27.43362831858407
2020,cyclist,29,168,0.17261904761904762,17.261904761904763
2021,cyclist,19,153,0.12418300653594772,12.418300653594772
2022,cyclist,19,135,0.14074074074074075,14.074074074074074
2023,cyclist,31,154,0.2012987012987013,20.12987012987013
2024,cyclist,24,135,0.17777777777777778,17.77777777777778
2025,cyclist,23,104,0.22115384615384615,22.115384615384613

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python3 -c "import duckdb,pandas,matplotlib; print('duckdb',duckdb.__version__); print('pandas',pandas.__version__); print('matplotlib',matplotlib.__version__)"
# bash
ls -la
# bash
python3 out/check_data.py
# bash
python3 out/check_data.py
# bash
python3 out/analyze.py
# bash
python3 out/check_data.py
# bash
python3 -c "import json,csv,pathlib; p=pathlib.Path('out'); x=json.loads((p/'options.json').read_text()); assert len(x['options'])==2; assert abs(sum(o['probability'] for o in x['options'])-1)<1e-9; plans=[json.loads((p/f'plan_{i}.json').read_text()) for i in (1,2)]; assert all(v['stage']=='final plan' for v in plans); assert all((p/f'option_{i}.png').is_file() and (p/f'values_{i}.csv').is_file() and (p/f'check_{i}.csv').is_file() for i in (1,2)); print('JSON, final plans, chart/value/check files validated; probabilities sum to', sum(o['probability'] for o in x['options']))"

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