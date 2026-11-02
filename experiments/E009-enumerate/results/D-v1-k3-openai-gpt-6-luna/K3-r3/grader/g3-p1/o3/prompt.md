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

QUESTION ASKED: How do motorist and cyclist deaths compare year by year in NYC, 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Each road-user type’s percentage share of the combined motorist and cyclist deaths
denominator: Motorist deaths plus cyclist deaths in the same year
grouping: Year, partitioned by road-user type
chart_type: 100% stacked bar chart
probability: 0.24
WRITTEN ANSWER:
Cyclists accounted for the highest share of combined motorist and cyclist deaths in 2019, at 27.4%; their share in 2025 was 22.1%.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,motorist_deaths,cyclist_deaths,combined_deaths,motorist_share_percent,cyclist_share_percent
2013,110,11,121,90.9091,9.0909
2014,109,20,129,84.4961,15.5039
2015,95,15,110,86.3636,13.6364
2016,72,18,90,80.0000,20.0000
2017,107,27,134,79.8507,20.1493
2018,98,10,108,90.7407,9.2593
2019,82,31,113,72.5664,27.4336
2020,139,29,168,82.7381,17.2619
2021,134,19,153,87.5817,12.4183
2022,116,19,135,85.9259,14.0741
2023,123,31,154,79.8701,20.1299
2024,111,24,135,82.2222,17.7778
2025,81,23,104,77.8846,22.1154

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c "import duckdb; p='data/crashes.parquet'; print(duckdb.sql(f\"DESCRIBE SELECT * FROM read_parquet('{p}')\").df().to_string(index=False)); print(duckdb.sql(f\"SELECT MIN(crash_date) min_date, MAX(crash_date) max_date, COUNT(*) rows FROM read_parquet('{p}')\").df().to_string(index=False))"
# bash
python -c "import duckdb; p='data/crashes.parquet'; q=f\"SELECT year(crash_date) year, count(*) crash_rows, sum(coalesce(number_of_motorist_killed,0)) motorist_deaths, sum(coalesce(number_of_cyclist_killed,0)) cyclist_deaths, min(crash_date) first_date, max(crash_date) last_date FROM read_parquet('{p}') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1\"; print(duckdb.sql(q).df().to_string(index=False)); print(duckdb.sql(f\"SELECT max(crash_date) max_date FROM read_parquet('{p}')\").df().to_string(index=False))"
# bash
python -c "import duckdb; p='data/crashes.parquet'; q=f\"SELECT year(crash_date) AS crash_year, count(*) AS crash_rows, sum(coalesce(number_of_motorist_killed,0)) AS motorist_deaths, sum(coalesce(number_of_cyclist_killed,0)) AS cyclist_deaths, min(crash_date) AS first_date, max(crash_date) AS last_date FROM read_parquet('{p}') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1\"; print(duckdb.sql(q).df().to_string(index=False)); print(duckdb.sql(f\"SELECT max(crash_date) max_date FROM read_parquet('{p}')\").df().to_string(index=False))"
# bash
ls
# bash
python .generate_crash_options.py
# bash
python .generate_crash_options.py
# bash
python .generate_crash_options.py
# bash
python -c "import json, pathlib; d=json.loads(pathlib.Path('out/options.json').read_text()); print('options', len(d['options']), 'probability sum', sum(x['probability'] for x in d['options'])); print('outputs', sorted(p.name for p in pathlib.Path('out').iterdir())); assert len(d['options']) == 3 and abs(sum(x['probability'] for x in d['options'])-1) < .01; assert all((pathlib.Path('out')/f'option_{i}.png').is_file() and (pathlib.Path('out')/f'values_{i}.csv').is_file() for i in (1,2,3))"

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR15: Claims about cyclist deaths changing sharply (e.g. 'tripled') are qualified by the small counts (10 → 31).
- tr_TR03: The output does not claim that motorist + cyclist deaths are all deaths (pedestrians and unclassified deaths exist).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.