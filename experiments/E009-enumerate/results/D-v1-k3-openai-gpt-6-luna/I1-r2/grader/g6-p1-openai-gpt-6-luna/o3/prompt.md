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

DATA FACTS (pinned snapshot):
- The file covers 2012-07-01 to 2026-06-11; 2013-2025 are complete calendar years; 2026 is partial (to June 11).
- borough is NULL for about 20-38% of crashes in every year (TR05): a borough filter silently drops them.
- number_of_persons_killed is NULL in most May-2026 and all June-2026 rows (TR08); 2013-2025 killed counts have no NULLs.
- crash_time has no NULL rows. Reported crash counts (the number of crash records) fall sharply in 2020 (TR01), so a per-reported-crash rate (deaths or injuries divided by reported crashes) compared across years spanning 2020 needs a caveat. Counts of deaths or injuries by year do NOT need it (they are not affected by the reporting change), and a comparison between groups within one pooled window (e.g. day vs night) does not either (decided 2026-11-04; g5 wording after g4 failed c6 on plain death counts).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: Did the risk of a motorist being killed per mile driven in NYC decline from 2013 to 2025? Make a chart and answer based on this crash data.
QUESTION TYPE: insufficient
DECLARED FRAMING:
metric: Motorist deaths as a percentage of all persons killed in NYC crashes
denominator: All persons killed in police-reported NYC crashes in the same year
grouping: Calendar year, 2013–2025
chart_type: Line chart
probability: 0.3
WRITTEN ANSWER:
Per-mile risk cannot be determined because miles driven are absent from the data. Motorists accounted for 37.0% of all traffic deaths in 2013 and 35.4% in 2025, about 1.7 percentage points lower based on unrounded values; this is a change in share, not a per-mile risk estimate.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,motorist_deaths,all_person_deaths,motorist_share_of_deaths_pct
2013,110.0000,297.0000,37.0370
2014,109.0000,262.0000,41.6031
2015,95.0000,243.0000,39.0947
2016,72.0000,246.0000,29.2683
2017,107.0000,256.0000,41.7969
2018,98.0000,231.0000,42.4242
2019,82.0000,244.0000,33.6066
2020,139.0000,269.0000,51.6729
2021,134.0000,297.0000,45.1178
2022,116.0000,290.0000,40.0000
2023,123.0000,280.0000,43.9286
2024,111.0000,268.0000,41.4179
2025,81.0000,229.0000,35.3712

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c "import duckdb; p='data/crashes.parquet'; print(duckdb.sql(f\"DESCRIBE SELECT * FROM read_parquet('{p}')\").df().to_string(index=False)); print(duckdb.sql(f\"SELECT MIN(crash_date), MAX(crash_date), COUNT(*) FROM read_parquet('{p}')\").df().to_string(index=False))"
# bash
python -c "import duckdb; p='data/crashes.parquet'; print(duckdb.sql(f\"SELECT year(crash_date) yr, min(crash_date) start, max(crash_date) end, count(*) crashes, sum(coalesce(number_of_motorist_killed,0)) motorist_deaths, sum(coalesce(number_of_persons_killed,0)) all_deaths, sum(CASE WHEN coalesce(number_of_motorist_killed,0)>0 THEN 1 ELSE 0 END) crashes_with_motorist_death FROM read_parquet('{p}') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY yr ORDER BY yr\").df().to_string(index=False))"
# bash
python -c "import duckdb; p='data/crashes.parquet'; print(duckdb.sql(f\"SELECT year(crash_date) yr, min(crash_date) first_date, max(crash_date) last_date, count(*) crashes, sum(coalesce(number_of_motorist_killed,0)) motorist_deaths, sum(coalesce(number_of_persons_killed,0)) all_deaths, sum(CASE WHEN coalesce(number_of_motorist_killed,0)>0 THEN 1 ELSE 0 END) crashes_with_motorist_death FROM read_parquet('{p}') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY yr ORDER BY yr\").df().to_string(index=False))"
# bash
python -c "import duckdb; p='data/crashes.parquet'; print(duckdb.sql(f\"SELECT count(*) FILTER (WHERE number_of_motorist_killed IS NULL) null_motorist_killed, count(*) total FROM read_parquet('{p}') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'\").df().to_string(index=False))"
# bash
python generate_options.py
# bash
python generate_options.py
# bash
python -c "import json, pathlib; p=pathlib.Path('out'); o=json.loads((p/'options.json').read_text()); print('options:', len(o['options']), 'probability_sum:', sum(x['probability'] for x in o['options'])); print('files:', sorted(x.name for x in p.iterdir())); print('answers:'); [print(x['id'], x['answer']) for x in o['options']]"

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