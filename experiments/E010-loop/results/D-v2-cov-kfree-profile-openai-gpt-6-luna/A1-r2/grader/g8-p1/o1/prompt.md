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

QUESTION ASKED: Has road safety for pedestrians in Brooklyn gotten better since 2013? Make a chart suitable for a local news story and summarize the findings.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Annual pedestrian casualties (pedestrians injured plus pedestrians killed)
denominator: None; annual count
grouping: Crash year for Brooklyn crashes, 2013–2025
chart_type: Line chart
probability: 0.65
WRITTEN ANSWER:
Brooklyn's recorded pedestrian casualties fell from 3,671 in 2013 to 2,874 in 2025 (21.7% lower), despite pedestrian deaths rising from 30 to 39. This framing answers whether the annual count of pedestrians injured or killed in Brooklyn crashes is lower than in 2013. The chart shows casualties declined from 3,671 in 2013 to 2,874 in 2025, with a pronounced low in 2020 followed by increases through 2025. A count is a defensible measure of observed harm, but it does not adjust for how many people walked or measure risk per pedestrian trip. The Brooklyn filter omits other boroughs; borough is NULL for 659,713 of 2,132,218 rows (30.9%) in 2013–2025 and pedestrian count fields are complete, and only full years 2013–2025 are used (2012 and partial 2026 are excluded).

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,pedestrians_injured,pedestrians_killed,pedestrian_casualties
2013,3641,30,3671
2014,3349,42,3391
2015,3029,46,3075
2016,2917,20,2937
2017,2663,20,2683
2018,2785,23,2808
2019,2700,33,2733
2020,1781,17,1798
2021,1905,32,1937
2022,2275,23,2298
2023,2385,22,2407
2024,2645,31,2676
2025,2835,39,2874

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c "import duckdb, pandas, matplotlib; print('duckdb', duckdb.__version__, 'pandas', pandas.__version__, 'matplotlib', matplotlib.__version__)"
# bash
python -c "import duckdb; p='data/crashes.parquet'; q=\"SELECT EXTRACT(year FROM crash_date)::INT year, COUNT(*) rows, COUNT(*) FILTER (WHERE borough IS NULL) null_borough, COUNT(*) FILTER (WHERE borough='BROOKLYN') brooklyn_rows, SUM(number_of_pedestrians_injured) FILTER (WHERE borough='BROOKLYN') injured, SUM(number_of_pedestrians_killed) FILTER (WHERE borough='BROOKLYN') killed FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1\"; print(duckdb.query(q, [p]).df().to_string(index=False)); print('totals', duckdb.query(\"SELECT COUNT(*) rows, COUNT(*) FILTER (WHERE borough IS NULL) null_borough, COUNT(*) FILTER (WHERE borough='BROOKLYN') brooklyn_rows FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'\", [p]).df().to_string(index=False))"
# bash
python -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; q=\"SELECT EXTRACT(year FROM crash_date)::INT year, COUNT(*) rows, COUNT(*) FILTER (WHERE borough IS NULL) null_borough, COUNT(*) FILTER (WHERE borough='BROOKLYN') brooklyn_rows, SUM(number_of_pedestrians_injured) FILTER (WHERE borough='BROOKLYN') injured, SUM(number_of_pedestrians_killed) FILTER (WHERE borough='BROOKLYN') killed FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1\"; print(c.execute(q, [p]).df().to_string(index=False)); print('totals', c.execute(\"SELECT COUNT(*) rows, COUNT(*) FILTER (WHERE borough IS NULL) null_borough, COUNT(*) FILTER (WHERE borough='BROOKLYN') brooklyn_rows FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'\", [p]).df().to_string(index=False))"
# bash
python -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; q=\"SELECT EXTRACT(year FROM crash_date)::INT AS yr, COUNT(*) AS rows, COUNT(*) FILTER (WHERE borough IS NULL) AS null_borough, COUNT(*) FILTER (WHERE borough='BROOKLYN') AS brooklyn_rows, SUM(number_of_pedestrians_injured) FILTER (WHERE borough='BROOKLYN') AS injured, SUM(number_of_pedestrians_killed) FILTER (WHERE borough='BROOKLYN') AS killed FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1\"; print(c.execute(q, [p]).df().to_string(index=False)); print('totals', c.execute(\"SELECT COUNT(*) AS rows, COUNT(*) FILTER (WHERE borough IS NULL) AS null_borough, COUNT(*) FILTER (WHERE borough='BROOKLYN') AS brooklyn_rows FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'\", [p]).df().to_string(index=False))"
# bash
ls -la
# bash
python out/build_charts.py
# bash
python out/build_charts.py
# bash
python -c "import json, pathlib, pandas as pd; p=pathlib.Path('out'); x=json.loads((p/'options.json').read_text()); assert [o['id'] for o in x['options']]==[1,2]; assert abs(sum(o['probability'] for o in x['options'])-1)<1e-9; a=pd.read_csv(p/'values_1.csv'); b=pd.read_csv(p/'values_2.csv'); assert (a.iloc[[0,-1]]['pedestrian_casualties'].tolist()==[3671,2874]); assert b.iloc[[0,-1]]['pedestrian_deaths'].tolist()==[30,39]; assert all((p/f'option_{i}.png').stat().st_size for i in [1,2]); print('JSON valid; probabilities sum to 1; plotted endpoints match CSVs; charts exist.')"

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR05: If a borough filter (borough = 'BROOKLYN') is used, the output discloses that crashes with no borough recorded (19.9–38.1% per year) are excluded.
- tr_TR11: The output does not call Brooklyn 'safer' or 'less safe' from counts alone without saying that there is no pedestrian exposure measure.
- tr_TR01: If a per-crash rate spanning 2020 is shown, the output caveats the 2020 change in crash recording.
- tr_TR15: Claims about pedestrian deaths changing are qualified by the small counts (about 30–39 per year).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.