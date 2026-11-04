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
- crash_time has no NULL rows. Reported crash counts (the number of crash records) fall sharply in 2020 (TR01), so a per-reported-crash rate (deaths or injuries divided by reported crashes) compared across years spanning 2020 needs a caveat. Counts of deaths or injuries by year do NOT need it (they are not affected by the reporting change), and a comparison between groups within one pooled window (e.g. day vs night) does not either (decided 2026-11-04; g5 wording after g4 failed c6 on plain death counts).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: Did the risk of a motorist being killed per mile driven in NYC decline from 2013 to 2025? Make a chart and answer based on this crash data.
QUESTION TYPE: insufficient
DECLARED FRAMING:
metric: Motorist fatalities as a share of all traffic fatalities
denominator: All people killed in police-reported crashes in the year
grouping: Year (2013–2025)
chart_type: Line chart
probability: 0.25
WRITTEN ANSWER:
This data cannot establish whether per-mile risk declined because it does not measure miles driven. Motorist fatalities were 37.0% of all crash fatalities in 2013 and 35.4% in 2025, a change of -1.7 percentage points.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,motorist_fatalities,all_fatalities,motorist_share_of_fatalities_pct
2013,110.000000,297.000000,37.037037
2014,109.000000,262.000000,41.603053
2015,95.000000,243.000000,39.094650
2016,72.000000,246.000000,29.268293
2017,107.000000,256.000000,41.796875
2018,98.000000,231.000000,42.424242
2019,82.000000,244.000000,33.606557
2020,139.000000,269.000000,51.672862
2021,134.000000,297.000000,45.117845
2022,116.000000,290.000000,40.000000
2023,123.000000,280.000000,43.928571
2024,111.000000,268.000000,41.417910
2025,81.000000,229.000000,35.371179

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c "import duckdb; print(duckdb.__version__)"
# bash
python -c "import duckdb; p='data/crashes.parquet'; c=duckdb.connect(); print(c.execute('select min(crash_date), max(crash_date), count(*), count(distinct year(crash_date)) from read_parquet(?)',[p]).fetchall()); print(c.execute('select year(crash_date) y, count(*) crashes, sum(number_of_motorist_killed) motorist_killed, sum(number_of_persons_killed) all_killed, sum(number_of_motorist_injured) motorist_injured, sum(number_of_persons_injured) all_injured, count(*) filter (where number_of_motorist_killed is null) null_motorist_killed from read_parquet(?) where year(crash_date) between 2013 and 2025 group by y order by y',[p]).fetchdf().to_string(index=False))"
# bash
python - <<'PY'
import json
from pathlib import Path
import duckdb
import matplotlib.pyplot as plt
import pandas as pd

out = Path('out')
out.mkdir(exist_ok=True)
rows = duckdb.connect().execute("""
    SELECT year(crash_date) AS year,
           count(*) AS reported_crashes,
           sum(number_of_motorist_killed) AS motorist_fatalities,
           sum(number_of_persons_killed) AS all_fatalities
    FROM read_parquet('data/crashes.parquet')
    WHERE year(crash_date) BETWEEN 2013 AND 2025
    GROUP BY year(crash_date)
    ORDER BY year
""").fetchdf()
rows['motorist_fatalities_per_100k_crashes'] = rows['motorist_fatalities'] / rows['reported_crashes'] * 100000
rows['motorist_share_of_fatalities_pct'] = rows['motorist_fatalities'] / rows['all_fatalities'] * 100

# Option 1: annual fatality count.
d1 = rows[['year', 'motorist_fatalities']].copy()
d1.to_csv(out / 'values_1.csv', index=False)
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.plot(d1.year, d1.motorist_fatalities, marker='o', linewidth=2.2, color='#1769aa')
ax.set(title='Motorist fatalities in NYC crashes, 2013–2025', xlabel='Year', ylabel='Motorist fatalities (people)')
ax.set_xticks(d1.year)
ax.tick_params(axis='x', rotation=45)
ax.grid(axis='y', alpha=.25)
ax.annotate(f"2013: {int(d1.iloc[0].motorist_fatalities)}", (d1.iloc[0].year, d1.iloc[0].motorist_fatalities), xytext=(5, 9), textcoords='offset points')
ax.annotate(f"2025: {int(d1.iloc[-1].motorist_fatalities)}", (d1.iloc[-1].year, d1.iloc[-1].motorist_fatalities), xytext=(-42, 9), textcoords='offset points')
fig.tight_layout()
fig.savefig(out / 'option_1.png', dpi=160)
plt.close(fig)

# Option 2: normalize fatalities by number of reported crashes (not miles driven).
d2 = rows[['year', 'motorist_fatalities', 'reported_crashes', 'motorist_fatalities_per_100k_crashes']].copy()
d2.to_csv(out / 'values_2.csv', index=False, float_format='%.6f')
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.bar(d2.year, d2.motorist_fatalities_per_100k_crashes, color='#d17c16')
ax.set(title='Motorist fatalities per 100,000 reported crashes, 2013–2025', xlabel='Year', ylabel='Fatalities per 100,000 crashes')
ax.set_xticks(d2.year)
ax.tick_params(axis='x', rotation=45)
ax.grid(axis='y', alpha=.25)
fig.tight_layout()
fig.savefig(out / 'option_2.png', dpi=160)
plt.close(fig)

# Option 3: share of fatalities classified as motorist fatalities.
d3 = rows[['year', 'motorist_fatalities', 'all_fatalities', 'motorist_share_of_fatalities_pct']].copy()
d3.to_csv(out / 'values_3.csv', index=False, float_format='%.6f')
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.plot(d3.year, d3.motorist_share_of_fatalities_pct, marker='s', linewidth=2.2, color='#35814c')
ax.set(title='Motorist share of all traffic fatalities in NYC crashes, 2013–2025', xlabel='Year', ylabel='Motorist fatalities / all fatalities (%)', ylim=(0, 100))
ax.set_xticks(d3.year)
ax.tick_params(axis='x', rotation=45)
ax.grid(axis='y', alpha=.25)
fig.tight_layout()
fig.savefig(out / 'option_3.png', dpi=160)
plt.close(fig)

start, end = rows.iloc[0], rows.iloc[-1]
count_change = (end.motorist_fatalities / start.motorist_fatalities - 1) * 100
rate_change = end.motorist_fatalities_per_100k_crashes - start.motorist_fatalities_per_100k_crashes
share_change = end.motorist_share_of_fatalities_pct - start.motorist_share_of_fatalities_pct
options = {
    'options': [
        {
            'id': 1,
            'metric': 'Annual number of motorist fatalities',
            'denominator': 'None (annual count)',
            'grouping': 'Year (2013–2025)',
            'chart_type': 'Line chart',
            'reason': 'A careful analyst may start with the direct annual fatality burden without introducing an unobserved exposure denominator.',
            'probability': 0.45,
            'answer': f"This data cannot establish whether risk per mile driven declined because it contains no miles-driven measure. Annual motorist fatalities fell from {int(start.motorist_fatalities)} in 2013 to {int(end.motorist_fatalities)} in 2025 ({count_change:.1f}%), which is a decline in count, not necessarily in per-mile risk."
        },
        {
            'id': 2,
            'metric': 'Motorist fatalities per 100,000 reported crashes',
            'denominator': 'Number of police-reported crashes in the year',
            'grouping': 'Year (2013–2025)',
            'chart_type': 'Bar chart',
            'reason': 'Normalizing by reported crashes helps compare fatality burden relative to crash volume, while keeping the denominator observable in this dataset.',
            'probability': 0.30,
            'answer': f"This data cannot establish per-mile risk because miles driven are absent. Fatalities per 100,000 reported crashes increased from {start.motorist_fatalities_per_100k_crashes:.1f} in 2013 to {end.motorist_fatalities_per_100k_crashes:.1f} in 2025 (up {rate_change:.1f}), so this crash-normalized measure did not decline."
        },
        {
            'id': 3,
            'metric': 'Motorist fatalities as a share of all traffic fatalities',
            'denominator': 'All people killed in police-reported crashes in the year',
            'grouping': 'Year (2013–2025)',
            'chart_type': 'Line chart',
            'reason': 'The fatality share places motorist deaths in the context of all recorded crash deaths and can show whether their composition changed.',
            'probability': 0.25,
            'answer': f"This data cannot establish whether per-mile risk declined because it does not measure miles driven. Motorist fatalities were {start.motorist_share_of_fatalities_pct:.1f}% of all crash fatalities in 2013 and {end.motorist_share_of_fatalities_pct:.1f}% in 2025, a change of {share_change:.1f} percentage points."
        }
    ]
}
(out / 'options.json').write_text(json.dumps(options, indent=2) + '\n')
print(rows.to_string(index=False))
print('\nSaved charts, values, and options to out/.')
PY
# bash
python - <<'PY'
import json
from pathlib import Path
import pandas as pd
out = Path('out')
opts = json.loads((out / 'options.json').read_text())['options']
assert [o['id'] for o in opts] == [1, 2, 3]
assert abs(sum(o['probability'] for o in opts) - 1) < 1e-9
for i in range(1, 4):
    assert (out / f'option_{i}.png').stat().st_size > 0
    d = pd.read_csv(out / f'values_{i}.csv')
    assert len(d) == 13 and d.year.iloc[0] == 2013 and d.year.iloc[-1] == 2025
print('Validated JSON, probability sum, and all 3 chart/value pairs (2013–2025).')
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