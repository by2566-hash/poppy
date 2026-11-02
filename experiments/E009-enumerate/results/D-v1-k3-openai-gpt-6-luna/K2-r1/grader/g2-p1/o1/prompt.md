You are grading ONE output of a data-analysis agent against a written standard. The chart is attached as an image.
Judge from the materials below only. Do not fix anything, do not redo the analysis. For each item answer PASS or FAIL
(NA if the item does not apply to this output) and quote the sentence, number or chart element that decides it.
Be strict: a limitation that matters but is not stated is a FAIL on the item that asks for it.
If the QUESTION TYPE is "insufficient", the data cannot answer the question as asked; the appropriate output states that
(required_statement) and shows a measure the data does support. Do not FAIL c1 or c2 merely because the measure is not the
one the question named (e.g. not per mile); FAIL them only if the output pretends to answer the unanswerable question.

QUESTION ASKED: K2
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Crash-record count
denominator: None; absolute number of crash records
grouping: Weekday across 2013–2025
chart_type: Bar chart
probability: 0.45
WRITTEN ANSWER:
Friday had the most recorded crashes (338,800), while Sunday had the fewest (257,544) among 2,132,218 crashes dated 2013–2025.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
weekday,crashes,share_percent
Monday,304518,14.281747926337736
Tuesday,313488,14.702436617644162
Wednesday,311111,14.590956459423943
Thursday,318376,14.931681469718386
Friday,338800,15.889557259154552
Saturday,288381,13.524930377663072
Sunday,257544,12.078689890058145

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python3 -c "import duckdb, pandas, matplotlib; print('duckdb',duckdb.__version__,'pandas',pandas.__version__,'matplotlib',matplotlib.__version__)"
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(\"SELECT min(crash_date), max(crash_date), count(*), count_if(crash_date IS NULL) FROM read_parquet(?)\",[p]).fetchall()); print(c.execute(\"SELECT strftime(crash_date, '%A') weekday, count(*) n FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY CASE weekday WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3 WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6 ELSE 7 END\",[p]).fetchall())"
# bash
python3 -c "import duckdb; c=duckdb.connect(); print(c.execute(\"SELECT year(crash_date), min(crash_date), max(crash_date), count(*) FROM read_parquet('data/crashes.parquet') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1\").fetchall())"
# bash
python3 out/.generate_options.py
# bash
python3 -c "import json, pandas as pd; from pathlib import Path; p=Path('out'); opts=json.loads((p/'options.json').read_text())['options']; a=pd.read_csv(p/'values_1.csv'); b=pd.read_csv(p/'values_2.csv'); c=pd.read_csv(p/'values_3.csv'); assert a.crashes.sum()==2132218 and len(a)==7; assert abs(b.share_percent.sum()-100)<1e-9; assert len(c)==91 and c.groupby('year').size().eq(7).all(); assert len(opts)==3 and abs(sum(x['probability'] for x in opts)-1)<1e-9; assert all((p/f'option_{i}.png').read_bytes()[:8]==b'\x89PNG\r\n\x1a\n' and (p/f'values_{i}.csv').exists() for i in (1,2,3)); print('Validated: totals, percentages, 13 years × 7 weekdays, JSON probabilities, and all three PNG/CSV pairs.')"

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