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
metric: Brooklyn crashes with at least one pedestrian injured or killed per 10,000 Brooklyn crashes
denominator: All reported Brooklyn motor-vehicle crashes in the same year
grouping: Brooklyn crash year, 2013–2025
chart_type: Line chart
probability: 0.25
WRITTEN ANSWER:
Pedestrian-casualty crashes increased from 744 to 1138 per 10,000 Brooklyn crashes between 2013 and 2025 (+53.0%), indicating a worse share-based measure. This answers whether pedestrian-casualty crashes form a larger or smaller share of reported Brooklyn crashes: the rate went from 744 per 10,000 in 2013 to 1138 in 2025 (+53.0%). It is defensible as a within-dataset comparison of pedestrian-harm crashes against the volume of all reported crashes, but is not a measure of pedestrian exposure or risk per trip. It does not show how many victims were harmed in each crash, and the denominator's changes can affect the rate. The analysis uses only Brooklyn records in complete years 2013–2025; it excludes 659,713 rows with NULL borough (30.9% of all crashes dated 2013–2025) and 0 Brooklyn rows with a NULL pedestrian injury/death count (0.0% of Brooklyn rows dated 2013–2025); 2026 is excluded as partial, with 9,700 Brooklyn rows (2.0% of Brooklyn rows from 2013 onward in the file) through June 11, 2026, while 2012 is outside the requested period.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,pedestrian_casualty_crashes,brooklyn_crashes,pedestrian_casualty_crashes_per_10000
2013,3498,47024,743.8755
2014,3234,47761,677.1215
2015,2962,50851,582.4861
2016,2797,47464,589.2887
2017,2550,44915,567.7391
2018,2697,47313,570.0336
2019,2623,44479,589.7165
2020,1724,25473,676.7950
2021,1856,25174,737.2686
2022,2185,23369,934.9994
2023,2310,22890,1009.1743
2024,2576,22785,1130.5684
2025,2766,24303,1138.1311

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
pwd && ls
# bash
ls
# bash
python3 -c "import duckdb, pandas, matplotlib; print('duckdb', duckdb.__version__, 'pandas', pandas.__version__, 'matplotlib', matplotlib.__version__)"
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='./data/crashes.parquet'; print(c.execute(f\"DESCRIBE SELECT * FROM read_parquet('{p}')\").fetchdf().to_string(index=False)); print(c.execute(f\"SELECT COUNT(*) n, MIN(crash_date) start, MAX(crash_date) end, COUNT(DISTINCT borough) boroughs FROM read_parquet('{p}')\").fetchdf().to_string(index=False)); print(c.execute(f\"SELECT strftime(crash_date, '%Y') yr, COUNT(*) n FROM read_parquet('{p}') GROUP BY yr ORDER BY yr\").fetchdf().to_string(index=False))"
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='./data/crashes.parquet'; q=f\"SELECT COUNT(*) AS n, MIN(crash_date) AS first_date, MAX(crash_date) AS last_date, COUNT(*) FILTER (WHERE borough='BROOKLYN') AS brooklyn_caps, COUNT(*) FILTER (WHERE borough IS NULL) AS borough_nulls FROM read_parquet('{p}')\"; print(c.execute(q).fetchdf().to_string(index=False)); q=f\"SELECT year(crash_date) AS yr, COUNT(*) AS crashes, COUNT(*) FILTER (WHERE number_of_pedestrians_injured IS NULL OR number_of_pedestrians_killed IS NULL) AS ped_null_rows, SUM(number_of_pedestrians_injured) AS ped_inj, SUM(number_of_pedestrians_killed) AS ped_killed, COUNT(*) FILTER (WHERE borough='BROOKLYN') AS brooklyn_crashes, COUNT(*) FILTER (WHERE borough='BROOKLYN' AND (number_of_pedestrians_injured IS NULL OR number_of_pedestrians_killed IS NULL)) AS brooklyn_ped_null_rows, SUM(number_of_pedestrians_injured) FILTER (WHERE borough='BROOKLYN') AS b_inj, SUM(number_of_pedestrians_killed) FILTER (WHERE borough='BROOKLYN') AS b_killed FROM read_parquet('{p}') GROUP BY yr ORDER BY yr\"; print(c.execute(q).fetchdf().to_string(index=False))"
# bash
python3 generate_options.py
# bash
python3 generate_options.py
# bash
python3 generate_options.py
# bash
python3 -c "import json, pathlib, pandas as pd; p=pathlib.Path('out'); obj=json.loads((p/'options.json').read_text()); assert abs(sum(o['probability'] for o in obj['options'])-1)<1e-9; assert len(obj['options'])==3; assert all((p/f'option_{i}.png').is_file() and (p/f'values_{i}.csv').is_file() for i in (1,2,3)); d1=pd.read_csv(p/'values_1.csv'); d2=pd.read_csv(p/'values_2.csv'); d3=pd.read_csv(p/'values_3.csv'); assert int(d1.iloc[0].pedestrian_casualties)==3671 and int(d1.iloc[-1].pedestrian_casualties)==2874; assert int(d2.iloc[0].pedestrian_fatalities)==30 and int(d2.iloc[-1].pedestrian_fatalities)==39; assert round(d3.iloc[0].pedestrian_casualty_crashes_per_10000)==744 and round(d3.iloc[-1].pedestrian_casualty_crashes_per_10000)==1138; print('validated: JSON parses; probabilities sum to 1; all six chart/data files exist; reported endpoints match CSV values')"

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
- tr_TR01: If a per-reported-crash rate spanning 2020 is shown, the output says that the number of recorded crashes changes sharply around 2020 and that this affects comparing the per-crash rate across years (naming the cause, the 2020 recording change, is not required: it is not in the data or the dictionary).
- tr_TR15: Claims about pedestrian deaths changing are qualified by the small counts (about 30–39 per year).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.