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

QUESTION ASKED: Did motorist fatality risk per mile driven in NYC decrease from 2013 to 2025? Create a chart and answer using this crash dataset.
QUESTION TYPE: insufficient
DECLARED FRAMING:
metric: Annual motorist fatalities (sum of number_of_motorist_killed)
denominator: None; annual count
grouping: Calendar year, 2013–2025
chart_type: Line chart
probability: 0.5
WRITTEN ANSWER:
The dataset cannot establish whether per-mile fatality risk decreased because it has no miles-driven denominator; recorded motorist fatalities fell from 110 in 2013 to 81 in 2025. This framing answers the trend in the number of motorist deaths recorded in NYC crashes, which declined between 2013 and 2025. Counts are a defensible descriptive substitute when the underlying exposure denominator is not present. It leaves the per-mile risk question unanswered because annual miles driven are unavailable.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,motorist_fatalities
2013,110
2014,109
2015,95
2016,72
2017,107
2018,98
2019,82
2020,139
2021,134
2022,116
2023,123
2024,111
2025,81

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c "import duckdb; p='data/crashes.parquet'; print(duckdb.query(f\"SELECT count(*) AS n, min(crash_date), max(crash_date), count(*) FILTER (WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01') AS rows_2013_2025 FROM read_parquet('{p}')\").df().to_string(index=False)); print(duckdb.query(f\"SELECT year(crash_date) AS year, sum(coalesce(number_of_motorist_killed,0)) AS motorist_deaths, count(*) AS crashes, sum(coalesce(number_of_persons_killed,0)) AS all_deaths FROM read_parquet('{p}') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1\").df().to_string(index=False))"
# bash
ls -ld . data
# bash
python - <<'PY'
import json
from pathlib import Path
import duckdb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

out = Path('out')
out.mkdir(exist_ok=True)
source = Path('data/crashes.parquet')
df = duckdb.query(f"""
    SELECT year(crash_date)::INTEGER AS year,
           sum(coalesce(number_of_motorist_killed, 0))::INTEGER AS motorist_fatalities,
           count(*)::INTEGER AS reported_crashes
    FROM read_parquet('{source.as_posix()}')
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY 1 ORDER BY 1
""").df()
expected_years = list(range(2013, 2026))
if df['year'].tolist() != expected_years:
    raise ValueError(f'Unexpected year coverage: {df["year"].tolist()}')
df['motorist_fatalities_per_1000_crashes'] = df['motorist_fatalities'] / df['reported_crashes'] * 1000

# Option 1: annual count of motorist deaths.
opt1 = df[['year', 'motorist_fatalities']].copy()
opt1.to_csv(out / 'values_1.csv', index=False)
fig, ax = plt.subplots(figsize=(10, 5.5))
ax.plot(opt1['year'], opt1['motorist_fatalities'], marker='o', linewidth=2.2, color='#245b8f')
ax.set(title='Motorist fatalities in NYC crashes, 2013–2025',
       xlabel='Year', ylabel='Motorist fatalities (people)')
ax.set_xticks(expected_years)
ax.tick_params(axis='x', rotation=45)
ax.grid(axis='y', alpha=.25)
ax.annotate(f'{int(opt1.iloc[0].motorist_fatalities)}', (2013, int(opt1.iloc[0].motorist_fatalities)), xytext=(0, 10), textcoords='offset points', ha='center')
ax.annotate(f'{int(opt1.iloc[-1].motorist_fatalities)}', (2025, int(opt1.iloc[-1].motorist_fatalities)), xytext=(0, 10), textcoords='offset points', ha='center')
fig.text(.01, .01, 'Crash records do not include vehicle miles traveled; counts are not per-mile risk.', fontsize=9, color='#555555')
fig.tight_layout(rect=(0, .04, 1, 1))
fig.savefig(out / 'option_1.png', dpi=180, bbox_inches='tight')
plt.close(fig)

# Option 2: fatality count normalized by police-reported crash count.
opt2 = df[['year', 'motorist_fatalities', 'reported_crashes', 'motorist_fatalities_per_1000_crashes']].copy()
opt2.to_csv(out / 'values_2.csv', index=False, float_format='%.6f')
fig, ax = plt.subplots(figsize=(10, 5.5))
ax.plot(opt2['year'], opt2['motorist_fatalities_per_1000_crashes'], marker='o', linewidth=2.2, color='#b45a31')
ax.set(title='Motorist fatalities per 1,000 reported NYC crashes, 2013–2025',
       xlabel='Year', ylabel='Motorist fatalities per 1,000 reported crashes')
ax.set_xticks(expected_years)
ax.tick_params(axis='x', rotation=45)
ax.grid(axis='y', alpha=.25)
for row in (opt2.iloc[0], opt2.iloc[-1]):
    ax.annotate(f'{row.motorist_fatalities_per_1000_crashes:.3f}',
                (int(row.year), row.motorist_fatalities_per_1000_crashes),
                xytext=(0, 10), textcoords='offset points', ha='center')
fig.text(.01, .01, 'This is per reported crash, not per mile driven; vehicle miles traveled are unavailable.', fontsize=9, color='#555555')
fig.tight_layout(rect=(0, .04, 1, 1))
fig.savefig(out / 'option_2.png', dpi=180, bbox_inches='tight')
plt.close(fig)

start_fatalities, end_fatalities = int(df.iloc[0].motorist_fatalities), int(df.iloc[-1].motorist_fatalities)
start_rate, end_rate = df.iloc[0].motorist_fatalities_per_1000_crashes, df.iloc[-1].motorist_fatalities_per_1000_crashes
options = {
  'options': [
    {
      'id': 1,
      'metric': 'Annual motorist fatalities (sum of number_of_motorist_killed)',
      'denominator': 'None; annual count',
      'grouping': 'Calendar year, 2013–2025',
      'chart_type': 'Line chart',
      'reason': 'Annual counts directly show whether the recorded number of motorist deaths rose or fell over time.',
      'probability': 0.5,
      'answer': f'The dataset cannot establish whether per-mile fatality risk decreased because it has no miles-driven denominator; recorded motorist fatalities fell from {start_fatalities} in 2013 to {end_fatalities} in 2025.',
      'interpretation': 'This framing answers the trend in the number of motorist deaths recorded in NYC crashes, which declined between 2013 and 2025. Counts are a defensible descriptive substitute when the underlying exposure denominator is not present. It leaves the per-mile risk question unanswered because annual miles driven are unavailable.'
    },
    {
      'id': 2,
      'metric': 'Motorist fatalities per 1,000 police-reported crashes',
      'denominator': 'All police-reported crashes in the same calendar year',
      'grouping': 'Calendar year, 2013–2025',
      'chart_type': 'Line chart',
      'reason': 'Normalizing by crash count distinguishes fatality burden from changes in the number of reported crashes.',
      'probability': 0.5,
      'answer': f'The dataset cannot establish whether per-mile fatality risk decreased because it has no miles-driven denominator; instead, motorist fatalities per 1,000 reported crashes rose from {start_rate:.3f} in 2013 to {end_rate:.3f} in 2025.',
      'interpretation': 'This framing answers how motorist fatality counts compare with the number of reported crashes, and the rate per 1,000 crashes increased from 2013 to 2025. It is defensible as a measure of fatality burden relative to recorded crashes, rather than traffic exposure. It leaves unanswered whether motorist deaths per mile driven decreased, since miles driven are not recorded.'
    }
  ]
}
(out / 'options.json').write_text(json.dumps(options, indent=2) + '\n')
print(df.to_string(index=False))
print('\nFiles written:', ', '.join(p.name for p in sorted(out.iterdir())))
print(f'Endpoint rate calculation: {start_fatalities}/{int(df.iloc[0].reported_crashes)}*1000={start_rate:.6f}; {end_fatalities}/{int(df.iloc[-1].reported_crashes)}*1000={end_rate:.6f}')
PY
# bash
python - <<'PY'
import json
from pathlib import Path
import pandas as pd
out=Path('out')
opts=json.loads((out/'options.json').read_text())['options']
assert [o['id'] for o in opts]==[1,2]
assert abs(sum(o['probability'] for o in opts)-1)<1e-12
v1=pd.read_csv(out/'values_1.csv')
v2=pd.read_csv(out/'values_2.csv')
assert v1.iloc[0].motorist_fatalities==110 and v1.iloc[-1].motorist_fatalities==81
assert abs(v2.iloc[0].motorist_fatalities_per_1000_crashes-0.539898)<1e-6
assert abs(v2.iloc[-1].motorist_fatalities_per_1000_crashes-0.946859)<1e-6
assert all((out/f'option_{i}.png').stat().st_size>0 for i in [1,2])
print('Validation passed: JSON, probabilities, endpoint figures, and both charts.')
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
- tr_TR01: If a per-reported-crash rate spanning 2020 is shown, the output caveats the 2020 change in crash recording (fewer minor crashes reported).
- tr_PERMILE: A per-reported-crash rate, if shown, is not presented as a substitute for per-mile risk.
- tr_VMT: No vehicle-miles figure is imported, assumed or estimated from outside the data.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence
- required_statement: PASS if the output states, in its own words: Per-mile (per vehicle-mile) risk cannot be determined from this data because it has no vehicle-miles or traffic volume.

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.