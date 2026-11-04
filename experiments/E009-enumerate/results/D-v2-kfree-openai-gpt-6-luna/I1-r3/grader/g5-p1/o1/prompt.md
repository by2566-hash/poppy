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
- crash_time has no NULL rows. Reported crash counts (the number of crash records) fall sharply in 2020 (TR01), so a per-reported-crash rate (deaths or injuries divided by reported crashes) compared across years spanning 2020 needs a caveat. Counts of deaths or injuries by year do NOT need it (they are not affected by the reporting change), and a comparison between groups within one pooled window (e.g. day vs night) does not either (decided 2026-11-04; g5 wording after g4 failed c6 on plain death counts).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: Did the risk of a motorist being killed per mile driven in NYC decline from 2013 to 2025? Make a chart and answer based on this crash data.
QUESTION TYPE: insufficient
DECLARED FRAMING:
metric: Annual count of motorists killed
denominator: None (count)
grouping: Calendar year
chart_type: Line chart
probability: 0.25
WRITTEN ANSWER:
Reported motorist deaths fell from 110 in 2013 to 81 in 2025, but these counts cannot establish whether deaths per mile driven declined. This framing answers whether the annual number of motorists killed in recorded NYC crashes changed, and shows 110 deaths in 2013 versus 81 in 2025, with substantial year-to-year variation. An annual count is a defensible measure of the recorded toll, but it leaves unanswered the per-mile risk question because miles driven are not in this dataset.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,motorist_deaths
2013,110
2014,109
2015,95
2016,72
2017,107
2018,98
2019,82
2020,139
2021,134
2022,116
2023,123
2024,111
2025,81

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
pwd && ls
# bash
ls
# bash
python3 -c "import duckdb; p='data/crashes.parquet'; print(duckdb.query(f\"DESCRIBE SELECT * FROM read_parquet('{p}')\").df().to_string(index=False)); print(duckdb.query(f\"SELECT min(crash_date), max(crash_date), count(*) FROM read_parquet('{p}')\").df().to_string(index=False))"
# bash
ls out
# bash
python3 -c "import duckdb; p='data/crashes.parquet'; q=\"SELECT year(crash_date) AS year, count(*) AS crashes, sum(coalesce(number_of_motorist_killed,0)) AS motorist_deaths, count(*) FILTER (WHERE coalesce(number_of_motorist_killed,0)>0) AS fatal_crashes, sum(coalesce(number_of_motorist_killed,0))*1000.0/count(*) AS deaths_per_1000_crashes, count(*) FILTER (WHERE coalesce(number_of_motorist_killed,0)>0)*100000.0/count(*) AS fatal_crashes_per_100k FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1\"; print(duckdb.execute(q,[p]).df().to_string(index=False))"
# bash
python3 out/_generate.py
# bash
python3 -c "import duckdb,json,pathlib; p='data/crashes.parquet'; print(duckdb.query(\"SELECT year(crash_date) y, min(crash_date) start_date, max(crash_date) end_date, count(*) n FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1\",[p]).df().to_string(index=False)); d=json.loads(pathlib.Path('out/options.json').read_text()); print('probability_sum=',sum(x['probability'] for x in d['options'])); print('json_valid options=',len(d['options']))"
# bash
python3 -c "import duckdb,json,pathlib; p='data/crashes.parquet'; print(duckdb.execute(\"SELECT year(crash_date) y, min(crash_date) start_date, max(crash_date) end_date, count(*) n FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1\",[p]).df().to_string(index=False)); d=json.loads(pathlib.Path('out/options.json').read_text()); print('probability_sum=',sum(x['probability'] for x in d['options'])); print('json_valid options=',len(d['options']))"

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