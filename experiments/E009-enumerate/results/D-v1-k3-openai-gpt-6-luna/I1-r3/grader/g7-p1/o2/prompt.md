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
- Qualifications (reported, recorded in this dataset) count when they are in the WRITTEN ANSWER or the DECLARED FRAMING; text
  that appears only inside the chart image (title, footnote, source note) does not satisfy an item on its own. The official-count
  part of unsupported_claim follows the same test as TR07.

DATA FACTS (pinned snapshot):
- The file covers 2012-07-01 to 2026-06-11; 2013-2025 are complete calendar years; 2026 is partial (to June 11).
- borough is NULL for about 20-38% of crashes in every year (TR05): a borough filter silently drops them.
- number_of_persons_killed is NULL in most May-2026 and all June-2026 rows (TR08); 2013-2025 killed counts have no NULLs.
- crash_time has no NULL rows. Reported crash counts (the number of crash records) fall sharply in 2020 (TR01), so a per-reported-crash rate (deaths or injuries divided by reported crashes) compared across years spanning 2020 needs a caveat. Counts of deaths or injuries by year do NOT need it (they are not affected by the reporting change), and a comparison between groups within one pooled window (e.g. day vs night) does not either (decided 2026-11-04; g5 wording after g4 failed c6 on plain death counts).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: Did the risk of a motorist being killed per mile driven in NYC decline from 2013 to 2025? Make a chart and answer based on this crash data.
QUESTION TYPE: insufficient
DECLARED FRAMING:
metric: Number of crashes with at least one motorist death
denominator: None (count of crash records meeting the condition)
grouping: Crash year
chart_type: Bar chart
probability: 0.32
WRITTEN ANSWER:
This crash data cannot establish deaths per mile because it contains no miles-driven denominator. Crashes with at least one motorist death declined from 102 in 2013 to 75 in 2025.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,crashes_with_motorist_death
2013,102
2014,99
2015,89
2016,63
2017,100
2018,97
2019,77
2020,126
2021,126
2022,107
2023,114
2024,98
2025,75

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c "import duckdb, pandas, matplotlib; print('duckdb', duckdb.__version__, 'pandas', pandas.__version__, 'matplotlib', matplotlib.__version__)"
# bash
ls
# bash
python -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(f\"DESCRIBE SELECT * FROM read_parquet('{p}')\").df().to_string(index=False)); print(c.execute(f\"SELECT MIN(crash_date) min_date, MAX(crash_date) max_date, COUNT(*) rows, COUNT_IF(number_of_motorist_killed IS NULL) null_motorist_killed, COUNT_IF(number_of_persons_killed IS NULL) null_persons_killed FROM read_parquet('{p}')\").df().to_string(index=False)); print(c.execute(f\"SELECT EXTRACT(YEAR FROM crash_date)::INT year, SUM(COALESCE(number_of_motorist_killed,0)) motorist_killed, SUM(COALESCE(number_of_persons_killed,0)) persons_killed, COUNT(*) crash_count, COUNT_IF(COALESCE(number_of_motorist_killed,0)>0) crashes_with_motorist_fatality FROM read_parquet('{p}') WHERE EXTRACT(YEAR FROM crash_date) BETWEEN 2013 AND 2025 GROUP BY year ORDER BY year\").df().to_string(index=False))"
# bash
python -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(f\"SELECT MIN(crash_date) min_date, MAX(crash_date) max_date, COUNT(*) AS n_records, COUNT_IF(number_of_motorist_killed IS NULL) AS null_motorist_killed, COUNT_IF(number_of_persons_killed IS NULL) AS null_persons_killed FROM read_parquet('{p}')\").df().to_string(index=False)); print(c.execute(f\"SELECT EXTRACT(YEAR FROM crash_date)::INT AS year, SUM(COALESCE(number_of_motorist_killed,0)) AS motorist_killed, SUM(COALESCE(number_of_persons_killed,0)) AS persons_killed, COUNT(*) AS crash_count, COUNT_IF(COALESCE(number_of_motorist_killed,0)>0) AS crashes_with_motorist_fatality FROM read_parquet('{p}') WHERE EXTRACT(YEAR FROM crash_date) BETWEEN 2013 AND 2025 GROUP BY year ORDER BY year\").df().to_string(index=False))"
# bash
python out/generate_options.py
# bash
python out/generate_options.py
# bash
python -c "import json, pandas as pd; from pathlib import Path; d=Path('out'); opts=json.loads((d/'options.json').read_text())['options']; assert len(opts)==3 and abs(sum(o['probability'] for o in opts)-1)<1e-9; v1=pd.read_csv(d/'values_1.csv').set_index('year'); v2=pd.read_csv(d/'values_2.csv').set_index('year'); v3=pd.read_csv(d/'values_3.csv').set_index('year'); assert (v1.loc[2013,'motorist_deaths'],v1.loc[2025,'motorist_deaths'])==(110,81); assert (v2.loc[2013,'crashes_with_motorist_death'],v2.loc[2025,'crashes_with_motorist_death'])==(102,75); assert round(v3.loc[2013,'motorist_deaths_per_1000_crashes'],3)==0.540 and round(v3.loc[2025,'motorist_deaths_per_1000_crashes'],3)==0.947; print('valid JSON; probabilities sum to 1; all answer endpoints match CSVs')"

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