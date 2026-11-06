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
metric: Annual number of pedestrians injured or killed
denominator: None; absolute count of people
grouping: Calendar year, Brooklyn
chart_type: Line chart
probability: 0.5
WRITTEN ANSWER:
Brooklyn recorded 2,874 pedestrian injuries and deaths in 2025, 22% fewer than 3,671 in 2013, although the total has climbed from its 2020 low of 1,798. This framing answers whether the total reported pedestrian harm count is lower than in 2013; the chart shows a decline through 2020 followed by a steady rise through 2025. Adding injury and death counts measures total affected people, with each casualty counted once. It cannot establish whether individual pedestrian risk changed because the data has no walking-exposure denominator and covers police-reported crashes.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,pedestrian_casualties
2013,3671
2014,3391
2015,3075
2016,2937
2017,2683
2018,2808
2019,2733
2020,1798
2021,1937
2022,2298
2023,2407
2024,2676
2025,2874

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
pwd && ls -la
# bash
ls -l data
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute('describe select * from read_parquet(?)',[p]).fetchall()); print(c.execute(\"select min(crash_date), max(crash_date), count(*), count(*) filter (where upper(borough)='BROOKLYN') from read_parquet(?)\",[p]).fetchall())"
# bash
python3 -c "import duckdb; c=duckdb.connect(); q=\"select year(crash_date) as year, sum(coalesce(number_of_pedestrians_injured,0)) as injured, sum(coalesce(number_of_pedestrians_killed,0)) as killed, count(*) filter (where coalesce(number_of_pedestrians_injured,0)>0 or coalesce(number_of_pedestrians_killed,0)>0) as crashes_with_ped_casualty, count(*) as brooklyn_crashes from read_parquet('data/crashes.parquet') where upper(borough)='BROOKLYN' and crash_date >= date '2013-01-01' and crash_date < date '2026-01-01' group by 1 order by 1\"; print(c.execute(q).df().to_string(index=False)); print('date coverage',c.execute(\"select min(crash_date),max(crash_date) from read_parquet('data/crashes.parquet') where upper(borough)='BROOKLYN'\").fetchall())"
# bash
ls -la
# bash
python3 out/build_charts.py
# bash
python3 out/build_charts.py
# bash
python3 -c "import duckdb; c=duckdb.connect(); print(c.execute(\"select count(*) filter (where number_of_pedestrians_injured is null) as injury_null, count(*) filter (where number_of_pedestrians_killed is null) as death_null, count(*) as rows from read_parquet('data/crashes.parquet') where upper(borough)='BROOKLYN' and crash_date >= date '2013-01-01' and crash_date < date '2026-01-01'\").fetchall()); print(c.execute(\"select count(*) filter (where number_of_pedestrians_injured is null or number_of_pedestrians_killed is null), count(*) filter (where number_of_pedestrians_injured is null and number_of_pedestrians_killed is null) from read_parquet('data/crashes.parquet') where upper(borough)='BROOKLYN' and crash_date >= date '2013-01-01' and crash_date < date '2026-01-01'\").fetchall())"
# bash
python3 -c "import json, pathlib, pandas as pd; p=pathlib.Path('out'); d=json.loads((p/'options.json').read_text()); assert [o['id'] for o in d['options']]==[1,2,3]; assert abs(sum(o['probability'] for o in d['options'])-1)<1e-9; assert all((p/f'option_{i}.png').is_file() and (p/f'values_{i}.csv').is_file() for i in (1,2,3)); print('JSON valid; probabilities sum to',sum(o['probability'] for o in d['options'])); print('Options:',len(d['options'])); print('Artifacts:', sorted(f.name for f in p.iterdir()))"

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