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

QUESTION ASKED: How are NYC crashes distributed across the days of the week, 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: mean number of police-reported crashes per calendar occurrence of each weekday over 2013-2025
denominator: number of calendar dates of each weekday in the complete calendar years 2013 through 2025 inclusive
grouping: weekday derived from crash_date, ordered Monday through Sunday
chart_type: bar chart
probability: 0.3
WRITTEN ANSWER:
The average was highest on Fridays at 499.7 crashes per calendar Friday and lowest on Sundays at 379.9 per calendar Sunday. This framing answers how frequently crashes occur on a typical calendar date of each weekday, by counting each police-reported crash row once and dividing each weekday's total by the number of those weekday dates in full calendar years 2013-2025. Friday averaged 499.7 crashes across 678 calendar Fridays, the highest rate, and Sunday averaged 379.9 across 678 calendar Sundays, the lowest; other weekday denominators were 678 Mondays, 679 Tuesdays, 679 Wednesdays, 678 Thursdays, and 678 Saturdays. This is defensible for comparing typical daily frequency because it accounts for weekday occurrence counts, but it does not show the cumulative crash burden or crashes never police-reported. The check found 0 missing dates, 0 missing weekdays, 0 tested sentinel dates, and 0 impossible typed dates among the 2,132,218 in-range rows, whose observed date limits span Jan 1-Dec 31 in all 13 years; all in-range rows were kept, while missing-date or out-of-range records fall outside the selected population and were not counted.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
weekday,crash_count,calendar_occurrences,mean_crashes_per_occurrence
Monday,304518,678,449.14159292035396
Tuesday,313488,679,461.69072164948454
Wednesday,311111,679,458.1899852724595
Thursday,318376,678,469.5811209439528
Friday,338800,678,499.70501474926255
Saturday,288381,678,425.3407079646018
Sunday,257544,678,379.85840707964604

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python out/data_check.py
# bash
python out/data_check.py
# bash
python out/data_check.py
# bash
python out/analyze.py
# bash
python -c "import csv,json,pathlib; p=pathlib.Path('out'); o=json.loads((p/'options.json').read_text()); plans=[json.loads((p/f'plan_{i}.json').read_text()) for i in (1,2)]; vals=[[r for r in csv.DictReader((p/f'values_{i}.csv').open())] for i in (1,2)]; assert len(o['options'])==2 and abs(sum(x['probability'] for x in o['options'])-1)<1e-9; assert sum(int(r['crash_count']) for r in vals[0])==2132218; assert sum(int(r['calendar_occurrences']) for r in vals[1])==4758; assert all((p/f'option_{i}.png').exists() for i in (1,2)); assert all('final_plan' in x and x['final_plan']['limitations'] for x in plans); print('JSON, plans, plotted data totals, probabilities, and chart files validated.')"
# bash
python -c "import csv,json,pathlib; p=pathlib.Path('out'); o=json.loads((p/'options.json').read_text()); plans=[json.loads((p/f'plan_{i}.json').read_text()) for i in (1,2)]; vals=[[r for r in csv.DictReader((p/f'values_{i}.csv').open())] for i in (1,2)]; assert len(o['options'])==2 and abs(sum(x['probability'] for x in o['options'])-1)<1e-9; assert sum(int(r['crash_count']) for r in vals[0])==2132218; assert sum(int(r['calendar_occurrences']) for r in vals[1])==4748; assert all((p/f'option_{i}.png').exists() for i in (1,2)); assert all('final_plan' in x and x['final_plan']['limitations'] for x in plans); print('JSON, plans, plotted data totals, probabilities, and chart files validated.')"
# bash
python -c "import csv,json,pathlib; p=pathlib.Path('out'); o=json.loads((p/'options.json').read_text()); plans=[json.loads((p/f'plan_{i}.json').read_text()) for i in (1,2)]; vals=[[r for r in csv.DictReader((p/f'values_{i}.csv').open())] for i in (1,2)]; assert len(o['options'])==2 and abs(sum(x['probability'] for x in o['options'])-1)<1e-9; assert sum(int(r['crash_count']) for r in vals[0])==2132218; assert sum(int(r['calendar_occurrences']) for r in vals[1])==4748; assert all((p/f'option_{i}.png').exists() for i in (1,2)); assert all('final_plan' in x and x['final_plan']['limitations'] for x in plans); assert all(len(x['interpretation'].split('. '))==4 for x in o['options']); print('Validated JSON, four-sentence interpretations, plans, plotted data totals, probabilities, and chart files.')"

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_DAYCOUNT: If per-day averages or 'X% fewer on <day>' comparisons are given, the arithmetic is right (e.g. Sunday has 24% fewer than the mean weekday, Friday 32% more) and unequal day counts (678/679) are handled or noted.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.