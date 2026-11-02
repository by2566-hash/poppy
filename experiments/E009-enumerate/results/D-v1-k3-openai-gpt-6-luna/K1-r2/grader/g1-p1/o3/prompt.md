You are grading ONE output of a data-analysis agent against a written standard. The chart is attached as an image.
Judge from the materials below only. Do not fix anything, do not redo the analysis. For each item answer PASS or FAIL
(NA if the item does not apply to this output) and quote the sentence, number or chart element that decides it.
Be strict: a limitation that matters but is not stated is a FAIL on the item that asks for it.

QUESTION ASKED: K1
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Annual number of pedestrians killed, partitioned by recorded borough
denominator: None (raw counts; borough stacks sum to the annual citywide count)
grouping: Crash year and borough, with missing borough recorded as Unknown / missing
chart_type: Stacked vertical bar chart
probability: 0.25
WRITTEN ANSWER:
Summing the borough segments gives these NYC annual totals (including crashes with unknown or missing borough): 2013: 176; 2014: 133; 2015: 133; 2016: 149; 2017: 127; 2018: 123; 2019: 131; 2020: 101; 2021: 132; 2022: 135; 2023: 107; 2024: 124; 2025: 119.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,borough,pedestrians_killed
2013,BRONX,25
2013,BROOKLYN,30
2013,MANHATTAN,29
2013,QUEENS,45
2013,STATEN ISLAND,3
2013,Unknown / missing,44
2014,BRONX,10
2014,BROOKLYN,42
2014,MANHATTAN,25
2014,QUEENS,26
2014,STATEN ISLAND,5
2014,Unknown / missing,25
2015,BRONX,11
2015,BROOKLYN,46
2015,MANHATTAN,18
2015,QUEENS,25
2015,STATEN ISLAND,5
2015,Unknown / missing,28
2016,BRONX,14
2016,BROOKLYN,20
2016,MANHATTAN,30
2016,QUEENS,19
2016,STATEN ISLAND,3
2016,Unknown / missing,63
2017,BRONX,10
2017,BROOKLYN,20
2017,MANHATTAN,21
2017,QUEENS,23
2017,STATEN ISLAND,4
2017,Unknown / missing,49
2018,BRONX,10
2018,BROOKLYN,23
2018,MANHATTAN,13
2018,QUEENS,31
2018,STATEN ISLAND,3
2018,Unknown / missing,43
2019,BRONX,9
2019,BROOKLYN,33
2019,MANHATTAN,20
2019,QUEENS,26
2019,STATEN ISLAND,2
2019,Unknown / missing,41
2020,BRONX,10
2020,BROOKLYN,17
2020,MANHATTAN,9
2020,QUEENS,20
2020,STATEN ISLAND,3
2020,Unknown / missing,42
2021,BRONX,5
2021,BROOKLYN,32
2021,MANHATTAN,17
2021,QUEENS,16
2021,STATEN ISLAND,2
2021,Unknown / missing,60
2022,BRONX,13
2022,BROOKLYN,23
2022,MANHATTAN,18
2022,QUEENS,14
2022,STATEN ISLAND,3
2022,Unknown / missing,64
... (truncated)

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python3 -c "import duckdb; p='data/crashes.parquet'; print(duckdb.sql(f\"select min(crash_date), max(crash_date), count(*) from read_parquet('{p}')\").fetchall()); print(duckdb.sql(f\"select year(crash_date) yr, sum(number_of_pedestrians_killed) killed, sum(number_of_persons_killed) total_killed from read_parquet('{p}') where year(crash_date) between 2013 and 2025 group by yr order by yr\").df().to_string(index=False))"
# bash
python3 -c "import duckdb; p='data/crashes.parquet'; print(duckdb.sql(f\"select year(crash_date) yr, coalesce(borough,'Unknown / missing') borough, sum(number_of_pedestrians_killed)::int killed from read_parquet('{p}') where year(crash_date) between 2013 and 2025 group by yr, borough order by yr, borough\").df().to_string(index=False)); print(duckdb.sql(f\"select year(crash_date) yr, min(crash_date), max(crash_date), count(*) from read_parquet('{p}') where year(crash_date) between 2013 and 2025 group by yr order by yr\").df().to_string(index=False))"
# bash
python3 out/build_outputs.py
# bash
python3 -c "import json, pathlib, pandas as pd; p=pathlib.Path('out'); o=json.loads((p/'options.json').read_text()); assert len(o['options'])==3 and abs(sum(x['probability'] for x in o['options'])-1)<1e-9; a=pd.read_csv(p/'values_1.csv'); b=pd.read_csv(p/'values_2.csv'); c=pd.read_csv(p/'values_3.csv'); assert a.equals(b); assert c.groupby('year').pedestrians_killed.sum().reset_index().equals(a); assert all((p/f'option_{i}.png').is_file() and (p/f'values_{i}.csv').is_file() for i in (1,2,3)); print('JSON, annual values, borough totals, and all six chart/CSV files verified.')"

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR07: The output does not present the open-data death counts as the official NYC toll (reporting them as counts in this dataset is fine).
- tr_CAUSAL: The output makes no causal attribution (e.g. 'because of the pandemic') that the data cannot support.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.