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
metric: Average number of police-reported crash records per calendar date
denominator: Calendar dates of each weekday during 2013–2025 (678 or 679 dates)
grouping: Day of week
chart_type: Vertical bar chart
probability: 0.5
WRITTEN ANSWER:
A Friday averaged 499.7 crash records, the highest daily average, while a Sunday averaged 379.9, the lowest, across 2013–2025. This framing answers how the average number of recorded crashes on a date differs by weekday, while accounting for the slight differences in weekday-date counts in the 13-year period. Fridays remain highest and Sundays lowest on this per-date measure. It does not measure crash risk per trip or explain whether the pattern reflects differences in travel volume.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
weekday_num,weekday,crashes,calendar_dates,share_pct,avg_crashes_per_date
1,Monday,304518,678,14.281748,449.141593
2,Tuesday,313488,679,14.702437,461.690722
3,Wednesday,311111,679,14.590956,458.189985
4,Thursday,318376,678,14.931681,469.581121
5,Friday,338800,678,15.889557,499.705015
6,Saturday,288381,678,13.524930,425.340708
7,Sunday,257544,678,12.078690,379.858407

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls -la && ls -la data
# bash
python3 -c "import duckdb; p='data/crashes.parquet'; c=duckdb.connect(); print(c.execute('describe select * from read_parquet(?)',[p]).fetchdf().to_string(index=False)); print(c.execute('select count(*) n, min(crash_date) min_date, max(crash_date) max_date from read_parquet(?)',[p]).fetchdf().to_string(index=False))"
# bash
python3 out/create_outputs.py
# bash
python3 -c "import json, pathlib, pandas as pd; p=pathlib.Path('out'); o=json.loads((p/'options.json').read_text()); assert abs(sum(x['probability'] for x in o['options'])-1)<1e-9; assert len(o['options'])==2; v1=pd.read_csv(p/'values_1.csv'); v2=pd.read_csv(p/'values_2.csv'); assert v1['crashes'].sum()==2132218; assert v1.loc[v1.crashes.idxmax(),'weekday']=='Friday' and v1.loc[v1.crashes.idxmin(),'weekday']=='Sunday'; assert v2.loc[v2.avg_crashes_per_date.idxmax(),'weekday']=='Friday' and v2.loc[v2.avg_crashes_per_date.idxmin(),'weekday']=='Sunday'; print('JSON valid; probability sum:',sum(x['probability'] for x in o['options'])); print('Files:', sorted(x.name for x in p.iterdir()))"

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