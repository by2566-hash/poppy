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

QUESTION ASKED: Did the risk of a motorist being killed per mile driven in NYC decline from 2013 to 2025? Make a chart and answer based on this crash data.
QUESTION TYPE: insufficient
DECLARED FRAMING:
metric: Crashes with at least one motorist death per 100,000 reported crashes
denominator: All reported crash records in the same year
grouping: Calendar year
chart_type: Line chart
probability: 0.45
WRITTEN ANSWER:
Crashes with a motorist death increased from 50.1 to 87.7 per 100,000 reported crashes between 2013 and 2025 (75.1%), but this does not determine per-mile risk. This answers how often a reported crash involved at least one motorist death: the frequency increased from 50.1 to 87.7 per 100,000 crashes between 2013 and 2025. It adjusts for annual crash-report volume, a defensible crash-level comparison, but leaves per-mile risk unanswered because the data do not include vehicle-miles traveled.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,crashes_with_motorist_death,reported_crashes,motorist_fatal_crashes_per_100k
2013,102,203742,50.06331536943782
2014,99,206046,48.04752336856818
2015,89,217708,40.880445367189076
2016,63,229833,27.411207267885814
2017,100,231007,43.28873151030056
2018,97,231564,41.88906738525851
2019,77,211486,36.409029439300944
2020,126,112918,111.58539825359996
2021,126,110558,113.96732936558188
2022,107,103887,102.9965250705093
2023,114,96607,118.00387135507779
2024,98,91316,107.31963730342986
2025,75,85546,87.67212961447642

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c "import duckdb; p='data/crashes.parquet'; c=duckdb.connect(); print(c.execute('describe select * from read_parquet(?)',[p]).fetchall()); print(c.execute('select min(crash_date), max(crash_date), count(*), count(*) filter(where crash_date is null) from read_parquet(?)',[p]).fetchall())"
# bash
python -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute('select year(crash_date) y, count(*) crashes, sum(coalesce(number_of_motorist_killed,0)) motorist_deaths, count(*) filter (where coalesce(number_of_motorist_killed,0)>0) crashes_with_motorist_death, sum(coalesce(number_of_motorist_killed,0)) filter (where number_of_motorist_killed is null) null_as_zero_check, count(*) filter(where number_of_motorist_killed is null) null_killed from read_parquet(?) where crash_date >= date \'2013-01-01\' and crash_date < date \'2026-01-01\' group by y order by y',[p]).fetchdf().to_string(index=False)); print(c.execute('select year(crash_date) y, count(*) rows, min(crash_date), max(crash_date), count(*) filter(where number_of_motorist_killed is null) missing_killed from read_parquet(?) where year(crash_date) in (2013,2025) group by y order by y',[p]).fetchdf().to_string(index=False))"
# bash
ls
# bash
python - <<'PY'
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

out = Path('out')
out.mkdir(exist_ok=True)
con = duckdb.connect()
df = con.execute("""
    SELECT year(crash_date) AS year,
           COUNT(*) AS reported_crashes,
           SUM(number_of_motorist_killed) AS motorist_deaths,
           COUNT(*) FILTER (WHERE number_of_motorist_killed > 0) AS crashes_with_motorist_death
    FROM read_parquet('data/crashes.parquet')
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
""").fetchdf()
expected = list(range(2013, 2026))
assert df['year'].tolist() == expected, df
assert df['motorist_deaths'].notna().all()
df['motorist_fatal_crashes_per_100k'] = df['crashes_with_motorist_death'] / df['reported_crashes'] * 100000

# Option 1: annual motorist death counts.
fig, ax = plt.subplots(figsize=(10, 5.6))
ax.plot(df['year'], df['motorist_deaths'], marker='o', linewidth=2.4, color='#245a8d')
ax.annotate(f"2013: {int(df.iloc[0]['motorist_deaths'])}", (2013, df.iloc[0]['motorist_deaths']), xytext=(8, 9), textcoords='offset points', fontsize=9)
ax.annotate(f"2025: {int(df.iloc[-1]['motorist_deaths'])}", (2025, df.iloc[-1]['motorist_deaths']), xytext=(-42, 10), textcoords='offset points', fontsize=9)
ax.set(title='Reported motorist deaths in NYC crashes, 2013–2025', xlabel='Crash year', ylabel='Motorists killed (people)')
ax.set_xticks(expected)
ax.tick_params(axis='x', rotation=45)
ax.grid(axis='y', alpha=.25)
fig.text(.01, .01, 'Crash records show deaths, not vehicle-miles traveled; this is not a per-mile risk measure.', fontsize=9)
fig.tight_layout(rect=(0, .04, 1, 1))
fig.savefig(out / 'option_1.png', dpi=180, bbox_inches='tight')
plt.close(fig)
df[['year', 'motorist_deaths']].to_csv(out / 'values_1.csv', index=False)

# Option 2: share of reported crashes with one or more motorist deaths, expressed per 100k crashes.
fig, ax = plt.subplots(figsize=(10, 5.6))
ax.plot(df['year'], df['motorist_fatal_crashes_per_100k'], marker='o', linewidth=2.4, color='#a64b32')
ax.annotate(f"2013: {df.iloc[0]['motorist_fatal_crashes_per_100k']:.1f}", (2013, df.iloc[0]['motorist_fatal_crashes_per_100k']), xytext=(8, 9), textcoords='offset points', fontsize=9)
ax.annotate(f"2025: {df.iloc[-1]['motorist_fatal_crashes_per_100k']:.1f}", (2025, df.iloc[-1]['motorist_fatal_crashes_per_100k']), xytext=(-42, 10), textcoords='offset points', fontsize=9)
ax.set(title='Crashes with a motorist death per 100,000 reported NYC crashes, 2013–2025', xlabel='Crash year', ylabel='Fatal crashes per 100,000 reported crashes')
ax.set_xticks(expected)
ax.tick_params(axis='x', rotation=45)
ax.grid(axis='y', alpha=.25)
fig.text(.01, .01, 'Crash-based fatality frequency is not exposure-adjusted and does not measure risk per mile.', fontsize=9)
fig.tight_layout(rect=(0, .04, 1, 1))
fig.savefig(out / 'option_2.png', dpi=180, bbox_inches='tight')
plt.close(fig)
df[['year', 'crashes_with_motorist_death', 'reported_crashes', 'motorist_fatal_crashes_per_100k']].to_csv(out / 'values_2.csv', index=False)

print(df.to_string(index=False, formatters={'motorist_fatal_crashes_per_100k': '{:.3f}'.format}))
print('2013-2025 deaths change: {:.1f}%'.format((df.iloc[-1]['motorist_deaths'] / df.iloc[0]['motorist_deaths'] - 1) * 100))
print('2013-2025 crash-rate change: {:.1f}%'.format((df.iloc[-1]['motorist_fatal_crashes_per_100k'] / df.iloc[0]['motorist_fatal_crashes_per_100k'] - 1) * 100))
print('2025 date coverage:', con.execute("select min(crash_date), max(crash_date) from read_parquet('data/crashes.parquet') where year(crash_date)=2025").fetchone())
PY
# bash
python - <<'PY'
import json
from pathlib import Path
import pandas as pd
out=Path('out')
opts=json.loads((out/'options.json').read_text())
assert len(opts['options']) == 2
assert abs(sum(x['probability'] for x in opts['options']) - 1) < 1e-9
for i in (1,2):
    assert (out/f'option_{i}.png').is_file() and (out/f'option_{i}.png').stat().st_size > 0
    values=pd.read_csv(out/f'values_{i}.csv')
    assert len(values)==13 and values.iloc[0]['year']==2013 and values.iloc[-1]['year']==2025
print('Valid JSON; probabilities sum to', sum(x['probability'] for x in opts['options']))
print('Output files:', ', '.join(sorted(p.name for p in out.iterdir())))
print('Endpoint values option 1:', pd.read_csv(out/'values_1.csv').iloc[[0,-1]].to_dict('records'))
print('Endpoint values option 2:', pd.read_csv(out/'values_2.csv').iloc[[0,-1]].to_dict('records'))
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