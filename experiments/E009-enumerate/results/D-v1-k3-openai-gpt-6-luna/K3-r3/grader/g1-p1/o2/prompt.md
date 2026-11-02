You are grading ONE output of a data-analysis agent against a written standard. The chart is attached as an image.
Judge from the materials below only. Do not fix anything, do not redo the analysis. For each item answer PASS or FAIL
(NA if the item does not apply to this output) and quote the sentence, number or chart element that decides it.
Be strict: a limitation that matters but is not stated is a FAIL on the item that asks for it.

QUESTION ASKED: K3
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Motorist-to-cyclist death-count ratio
denominator: Cyclist deaths in the same year
grouping: Year
chart_type: Line chart
probability: 0.28
WRITTEN ANSWER:
Motorist deaths were 10.0 times cyclist deaths in 2013, the largest annual ratio, and 3.52 times cyclist deaths in 2025; the ratio stayed above 1 in every year.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,motorist_deaths,cyclist_deaths,motorist_to_cyclist_ratio
2013,110,11,10.0000
2014,109,20,5.4500
2015,95,15,6.3333
2016,72,18,4.0000
2017,107,27,3.9630
2018,98,10,9.8000
2019,82,31,2.6452
2020,139,29,4.7931
2021,134,19,7.0526
2022,116,19,6.1053
2023,123,31,3.9677
2024,111,24,4.6250
2025,81,23,3.5217

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