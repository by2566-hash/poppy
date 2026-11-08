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
metric: Mean number of police-reported crash rows per calendar occurrence of each weekday
denominator: Number of calendar dates of that weekday during the full 2013–2025 calendar interval
grouping: Day of week derived from crash_date, Monday through Sunday
chart_type: Bar chart
probability: 0.25
WRITTEN ANSWER:
Friday averaged 499.7 reported crashes per calendar date, compared with Sunday’s low of 379.9 per date. The calendar-date average answers how crash reports distribute across weekday dates, with Friday highest (499.7 per date) and Sunday lowest (379.9 per date). This is defensible because weekdays occur 678 or 679 times over the full 2013–2025 interval, and dividing by those occurrences makes the comparison per calendar date. It leaves per-trip or per-person crash risk unanswered and remains a count of police-reported crashes. The date filter omits 136,969 rows (6.0% of 2,269,187 source rows) outside 2013–2025; check_2.csv shows zero NULL crash dates, zero in-scope null or checked sentinel dates, and observations at both date boundaries for each requested year, so all 2,132,218 in-range rows are kept, though boundaries do not prove complete reporting.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
weekday,crash_rows,calendar_day_occurrences,mean_crashes_per_calendar_day
Monday,304518,678,449.141593
Tuesday,313488,679,461.690722
Wednesday,311111,679,458.189985
Thursday,318376,678,469.581121
Friday,338800,678,499.705015
Saturday,288381,678,425.340708
Sunday,257544,678,379.858407

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
ls out
# bash
python -c "import duckdb; print(duckdb.__version__)"
# bash
python out/check_data.py
# bash
python out/check_data.py
# bash
python out/check_data.py
# bash
python out/analysis.py
# bash
python out/analysis.py
# bash
python -c "import json; from pathlib import Path; p=Path('out'); opts=json.loads((p/'options.json').read_text()); plans=[json.loads((p/f'plan_{i}.json').read_text()) for i in (1,2)]; assert len(opts['options'])==2; assert abs(sum(o['probability'] for o in opts['options'])-1)<1e-9; assert all((p/f'check_{i}.csv').exists() and (p/f'values_{i}.csv').exists() and (p/f'option_{i}.png').exists() for i in (1,2)); print('JSON valid; probabilities sum to', sum(o['probability'] for o in opts['options'])); print('Excluded-source share:', (2269187-2132218)/2269187*100)"

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