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

DATA FACTS (pinned snapshot):
- The file covers 2012-07-01 to 2026-06-11; 2013-2025 are complete calendar years; 2026 is partial (to June 11).
- borough is NULL for about 20-38% of crashes in every year (TR05): a borough filter silently drops them.
- number_of_persons_killed is NULL in most May-2026 and all June-2026 rows (TR08); 2013-2025 killed counts have no NULLs.
- crash_time has no NULL rows. Reported crash counts fall sharply in 2020 (TR01): per-reported-crash rates spanning 2020 need a caveat.
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: How are NYC crashes distributed across the days of the week, 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Share of all police-reported crashes
denominator: All 2,132,218 crashes dated 2013–2025
grouping: Weekday (Monday through Sunday)
chart_type: Pie chart
probability: 0.32
WRITTEN ANSWER:
Friday accounted for the largest share, 15.89% of crashes, while Sunday accounted for the smallest, 12.08%.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
weekday,crash_count,share_pct
Monday,304518,14.281748
Tuesday,313488,14.702437
Wednesday,311111,14.590956
Thursday,318376,14.931681
Friday,338800,15.889557
Saturday,288381,13.524930
Sunday,257544,12.078690

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python3 -c "import duckdb; print(duckdb.query(\"select min(crash_date), max(crash_date), count(*) from read_parquet('data/crashes.parquet')\").fetchall())"
# bash
python3 -c "import duckdb; print(duckdb.query(\"select year(crash_date) yr, min(crash_date), max(crash_date), count(*) from read_parquet('data/crashes.parquet') where crash_date >= date '2013-01-01' and crash_date < date '2026-01-01' group by 1 order by 1\").df().to_string(index=False))"
# bash
ls -la
# bash
python3 _make_weekday_outputs.py
# bash
ls -l out
# bash
python3 -c "import json; p='out/options.json'; d=json.load(open(p)); assert len(d['options'])==3; assert abs(sum(o['probability'] for o in d['options'])-1)<1e-9; print('valid JSON; probability sum =', sum(o['probability'] for o in d['options']))"

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR01: If counts are pooled over 2013–2025, the output says that pre-2020 years dominate or that crash reporting changed in 2020.
- tr_DAYCOUNT: If per-day averages or 'X% fewer on <day>' comparisons are given, the arithmetic is right (e.g. Sunday has 24% fewer than the mean weekday, Friday 32% more) and unequal day counts (678/679) are handled or noted.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.