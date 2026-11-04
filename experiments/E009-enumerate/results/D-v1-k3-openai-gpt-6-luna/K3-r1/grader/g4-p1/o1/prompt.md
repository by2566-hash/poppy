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
- crash_time has no NULL rows. Reported crash counts fall sharply in 2020 (TR01): a per-reported-crash rate or a pooled count COMPARED ACROSS YEARS spanning 2020 needs a caveat; a comparison between groups within one pooled window (e.g. day vs night) does not (decided 2026-11-04).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: How do motorist and cyclist deaths compare year by year in NYC, 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Annual count of deaths in each road-user category
denominator: None; raw summed deaths per calendar year
grouping: Year and road-user category (motorist, cyclist)
chart_type: Two-series line chart
probability: 0.5
WRITTEN ANSWER:
Motorist deaths were higher than cyclist deaths in every year from 2013 to 2025. Motorist deaths peaked at 139 in 2020, while cyclist deaths peaked at 31 in both 2019 and 2023; in 2025 the counts were 81 and 23, respectively.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,motorist_deaths,cyclist_deaths
2013,110,11
2014,109,20
2015,95,15
2016,72,18
2017,107,27
2018,98,10
2019,82,31
2020,139,29
2021,134,19
2022,116,19
2023,123,31
2024,111,24
2025,81,23

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python -c 'import duckdb; p="data/crashes.parquet"; print(duckdb.sql(f"SELECT min(crash_date), max(crash_date), count(*) FROM read_parquet(\"{p}\")").fetchall()); print(duckdb.sql(f"SELECT year(crash_date) AS year, sum(coalesce(number_of_motorist_killed,0)) AS motorist_deaths, sum(coalesce(number_of_cyclist_killed,0)) AS cyclist_deaths, count(*) AS crashes FROM read_parquet(\"{p}\") WHERE crash_date >= DATE \'2013-01-01\' AND crash_date < DATE \'2026-01-01\' GROUP BY year ORDER BY year").df().to_string(index=False))'
# bash
python - <<'PY'
import duckdb
p = 'data/crashes.parquet'
con = duckdb.connect()
print(con.execute('SELECT min(crash_date), max(crash_date), count(*) FROM read_parquet(?)', [p]).fetchall())
q = """
SELECT year(crash_date) AS year,
       sum(coalesce(number_of_motorist_killed, 0)) AS motorist_deaths,
       sum(coalesce(number_of_cyclist_killed, 0)) AS cyclist_deaths,
       count(*) AS crashes
FROM read_parquet(?)
WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
GROUP BY year ORDER BY year
"""
print(con.execute(q, [p]).df().to_string(index=False))
PY
# bash
python - <<'PY'
import duckdb
p='data/crashes.parquet'
con=duckdb.connect()
q="""SELECT year(crash_date) AS year, sum(coalesce(number_of_motorist_killed,0))::INTEGER AS motorist_deaths, sum(coalesce(number_of_cyclist_killed,0))::INTEGER AS cyclist_deaths FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY year ORDER BY year"""
df=con.execute(q,[p]).df()
df['difference_motorist_minus_cyclist']=df.motorist_deaths-df.cyclist_deaths
df['cyclist_share_pct']=df.cyclist_deaths/(df.motorist_deaths+df.cyclist_deaths)*100
df['motorist_share_pct']=df.motorist_deaths/(df.motorist_deaths+df.cyclist_deaths)*100
print(df.to_string(index=False, formatters={'cyclist_share_pct':'{:.1f}'.format,'motorist_share_pct':'{:.1f}'.format}))
print('overall totals', df[['motorist_deaths','cyclist_deaths']].sum().to_dict())
PY
# bash
python - <<'PY'
import json
from pathlib import Path

import duckdb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

out = Path('out')
out.mkdir(exist_ok=True)
con = duckdb.connect()
query = """
SELECT year(crash_date) AS year,
       sum(coalesce(number_of_motorist_killed, 0))::INTEGER AS motorist_deaths,
       sum(coalesce(number_of_cyclist_killed, 0))::INTEGER AS cyclist_deaths
FROM read_parquet(?)
WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
GROUP BY year(crash_date)
ORDER BY year
"""
df = con.execute(query, ['data/crashes.parquet']).df()
if df['year'].tolist() != list(range(2013, 2026)):
    raise ValueError('Unexpected year coverage')
df['difference_motorist_minus_cyclist'] = df['motorist_deaths'] - df['cyclist_deaths']
denominator = df['motorist_deaths'] + df['cyclist_deaths']
df['motorist_share_pct'] = df['motorist_deaths'] / denominator * 100
df['cyclist_share_pct'] = df['cyclist_deaths'] / denominator * 100

# Option 1: two annual count series.
values1 = df[['year', 'motorist_deaths', 'cyclist_deaths']]
values1.to_csv(out / 'values_1.csv', index=False)
fig, ax = plt.subplots(figsize=(10.5, 5.8))
ax.plot(df['year'], df['motorist_deaths'], marker='o', linewidth=2.4, color='#245a9b', label='Motorist deaths')
ax.plot(df['year'], df['cyclist_deaths'], marker='o', linewidth=2.4, color='#e07a26', label='Cyclist deaths')
ax.set(title='Motorist and cyclist deaths by year, NYC (2013–2025)', xlabel='Year', ylabel='Deaths reported')
ax.set_xticks(df['year'])
ax.tick_params(axis='x', rotation=45)
ax.set_ylim(bottom=0)
ax.grid(axis='y', alpha=.25)
ax.legend(frameon=False, ncol=2, loc='upper left')
fig.tight_layout()
fig.savefig(out / 'option_1.png', dpi=180)
plt.close(fig)

# Option 2: annual absolute gap between the two death counts.
values2 = df[['year', 'motorist_deaths', 'cyclist_deaths', 'difference_motorist_minus_cyclist']]
values2.to_csv(out / 'values_2.csv', index=False)
fig, ax = plt.subplots(figsize=(10.5, 5.8))
colors = ['#6486ad' if value != df['difference_motorist_minus_cyclist'].max() else '#245a9b' for value in df['difference_motorist_minus_cyclist']]
bars = ax.bar(df['year'], df['difference_motorist_minus_cyclist'], color=colors, width=.72)
ax.set(title='Annual motorist–cyclist death gap, NYC (2013–2025)', xlabel='Year', ylabel='Motorist deaths minus cyclist deaths')
ax.set_xticks(df['year'])
ax.tick_params(axis='x', rotation=45)
ax.set_ylim(bottom=0)
ax.grid(axis='y', alpha=.25)
for bar, value in zip(bars, df['difference_motorist_minus_cyclist']):
    ax.annotate(f'{value}', (bar.get_x() + bar.get_width()/2, value), xytext=(0, 3), textcoords='offset points', ha='center', va='bottom', fontsize=8)
fig.tight_layout()
fig.savefig(out / 'option_2.png', dpi=180)
plt.close(fig)

# Option 3: relative composition of the two selected user categories.
values3 = df[['year', 'motorist_deaths', 'cyclist_deaths', 'motorist_share_pct', 'cyclist_share_pct']]
values3.to_csv(out / 'values_3.csv', index=False, float_format='%.4f')
fig, ax = plt.subplots(figsize=(10.5, 5.8))
ax.bar(df['year'], df['motorist_share_pct'], color='#245a9b', label='Motorist share')
ax.bar(df['year'], df['cyclist_share_pct'], bottom=df['motorist_share_pct'], color='#e07a26', label='Cyclist share')
ax.set(title='Share of motorist + cyclist deaths by year, NYC (2013–2025)', xlabel='Year', ylabel='Share of deaths in these two categories (%)')
ax.set_xticks(df['year'])
ax.tick_params(axis='x', rotation=45)
ax.set_ylim(0, 100)
ax.set_yticks(np.arange(0, 101, 20))
ax.grid(axis='y', alpha=.25)
ax.legend(frameon=False, ncol=2, loc='lower center')
fig.tight_layout()
fig.savefig(out / 'option_3.png', dpi=180)
plt.close(fig)

options = {
    'options': [
        {
            'id': 1,
            'metric': 'Annual count of deaths in each road-user category',
            'denominator': 'None; raw summed deaths per calendar year',
            'grouping': 'Year and road-user category (motorist, cyclist)',
            'chart_type': 'Two-series line chart',
            'reason': 'A paired time series makes the year-to-year levels and trends of both groups easy to compare directly.',
            'probability': 0.50,
            'answer': 'Motorist deaths were higher than cyclist deaths in every year from 2013 to 2025. Motorist deaths peaked at 139 in 2020, while cyclist deaths peaked at 31 in both 2019 and 2023; in 2025 the counts were 81 and 23, respectively.'
        },
        {
            'id': 2,
            'metric': 'Annual difference: motorist deaths minus cyclist deaths',
            'denominator': 'None; difference of annual counts',
            'grouping': 'Year',
            'chart_type': 'Vertical bar chart',
            'reason': 'The difference emphasizes how many more motorist deaths than cyclist deaths were reported each year.',
            'probability': 0.28,
            'answer': 'The motorist-minus-cyclist gap was positive every year, ranging from 51 deaths in 2019 to 115 in 2021. The gap was 58 deaths in 2025.'
        },
        {
            'id': 3,
            'metric': 'Cyclist and motorist shares of their combined annual deaths',
            'denominator': 'Motorist deaths plus cyclist deaths in the same year',
            'grouping': 'Year and road-user category',
            'chart_type': '100% stacked bar chart',
            'reason': 'A within-year percentage view compares the composition of deaths without being driven by changes in the combined count.',
            'probability': 0.22,
            'answer': 'Cyclists accounted for between 9.1% and 27.4% of the combined motorist-and-cyclist deaths by year, with the low in 2013 and high in 2019. The cyclist share was 22.1% in 2025; the remaining share was motorist deaths.'
        }
    ]
}
with (out / 'options.json').open('w') as f:
    json.dump(options, f, indent=2)
    f.write('\n')
PY
# bash
python - <<'PY'
import json
from pathlib import Path
out = Path('out')
options = json.loads((out / 'options.json').read_text())
assert [o['id'] for o in options['options']] == [1, 2, 3]
assert abs(sum(o['probability'] for o in options['options']) - 1.0) < 1e-9
for i in range(1, 4):
    assert (out / f'option_{i}.png').is_file()
    assert (out / f'values_{i}.csv').is_file()
print('Validated options.json, probability sum, and all six chart/value artifacts.')
PY

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