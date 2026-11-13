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
metric: Pedestrians injured plus pedestrians killed in Brooklyn crashes (annual count)
denominator: None; annual casualty count
grouping: Calendar year, 2013–2025
chart_type: Stacked annual bar chart (injured and killed)
probability: 0.5
WRITTEN ANSWER:
Annual pedestrian casualties fell from 3,671 in 2013 to 2,874 in 2025, a decrease of 21.7%, indicating improvement in the recorded toll. This framing answers whether the recorded number of pedestrians hurt or killed in Brooklyn crashes declined, and the chart shows 3,671 casualties in 2013 versus 2,874 in 2025 (21.7% fewer). It is defensible because injury and death counts measure the direct human toll, with deaths distinguished in the bars. It cannot establish risk per pedestrian trip, explain causes, or isolate changes in traffic or walking exposure. The analysis uses complete years 2013–2025, excludes partial 2012 and 2026 (2012 (100% of its 100,545 available rows omitted); 2026 (100% of its 36,424 available rows omitted)), excludes non-Brooklyn and NULL-borough rows (NULL borough accounts for 30.9% of NYC rows across these years; annual shares: 2013 23.4%, 2014 24.1%, 2015 24.9%, 2016 33.3%, 2017 38.1%, 2018 35.6%, 2019 35.2%, 2020 34.7%, 2021 34.7%, 2022 33.8%, 2023 32.0%, 2024 28.6%, 2025 19.9%), and excludes no Brooklyn rows for NULL pedestrian counts (0 of 473,801 Brooklyn records had either count missing).

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,pedestrians_injured,pedestrians_killed,pedestrian_casualties,brooklyn_crashes
2013,3641.0,30.0,3671.0,47024
2014,3349.0,42.0,3391.0,47761
2015,3029.0,46.0,3075.0,50851
2016,2917.0,20.0,2937.0,47464
2017,2663.0,20.0,2683.0,44915
2018,2785.0,23.0,2808.0,47313
2019,2700.0,33.0,2733.0,44479
2020,1781.0,17.0,1798.0,25473
2021,1905.0,32.0,1937.0,25174
2022,2275.0,23.0,2298.0,23369
2023,2385.0,22.0,2407.0,22890
2024,2645.0,31.0,2676.0,22785
2025,2835.0,39.0,2874.0,24303

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c "import duckdb, pandas, matplotlib; print('duckdb',duckdb.__version__,'pandas',pandas.__version__,'matplotlib',matplotlib.__version__)"
# bash
python -c "import duckdb; p='data/crashes.parquet'; print(duckdb.sql(f\"select count(*) n, min(crash_date) min_date, max(crash_date) max_date, count(*) filter (where borough='BROOKLYN') brooklyn, count(*) filter (where borough='BROOKLYN' and number_of_pedestrians_injured is null) null_pedinj, count(*) filter (where borough='BROOKLYN' and number_of_pedestrians_killed is null) null_pedkill from read_parquet('{p}')\").df().to_string(index=False)); print(duckdb.sql(f\"select year(crash_date) yr, count(*) n from read_parquet('{p}') group by yr order by yr\").df().to_string(index=False))"
# bash
python -c "import duckdb; p='data/crashes.parquet'; print(duckdb.sql(f\"select year(crash_date) year, count(*) total, count(*) filter (where borough is null) null_borough, count(*) filter (where borough='BROOKLYN') bk, count(*) filter (where borough='BROOKLYN' and (number_of_pedestrians_injured is null or number_of_pedestrians_killed is null)) ped_null, sum(number_of_pedestrians_injured+number_of_pedestrians_killed) filter (where borough='BROOKLYN') ped_casualties, sum(number_of_pedestrians_killed) filter (where borough='BROOKLYN') ped_deaths, count(*) filter (where borough='BROOKLYN' and number_of_pedestrians_injured+number_of_pedestrians_killed>0) ped_casualty_crashes from read_parquet('{p}') group by year order by year\").df().to_string(index=False))"
# bash
ls
# bash
python out/generate_options.py
# bash
python out/generate_options.py
# bash
python out/generate_options.py
# bash
python out/generate_options.py
# bash
python -c "import json, pathlib, pandas as pd; o=pathlib.Path('out'); x=json.loads((o/'options.json').read_text()); assert abs(sum(i['probability'] for i in x['options'])-1)<1e-9; assert len(x['options'])==3; assert all((o/f'option_{i}.png').is_file() and (o/f'values_{i}.csv').is_file() for i in range(1,4)); assert all(len(pd.read_csv(o/f'values_{i}.csv'))==13 for i in range(1,4)); print('Validated JSON, probability sum, and all 3 chart/value pairs; each contains 13 complete-year observations.')"

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