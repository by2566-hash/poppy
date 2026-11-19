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
metric: Annual number of motorists killed in police-reported NYC crashes
denominator: None (annual count)
grouping: Calendar year, 2013–2025
chart_type: Line chart
probability: 0.45
WRITTEN ANSWER:
The recorded annual count of motorists killed declined from 110 in 2013 to 81 in 2025 (26.4% lower), but this does not establish a decline per mile driven. Because this file has no miles-driven exposure, it cannot establish whether deaths per mile declined; the chart shows the annual number of motorists killed falling from 110 in 2013 to 81 in 2025. Annual fatalities are a directly observed burden measure, but they leave exposure-adjusted risk per mile unanswered.

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
ls
# bash
python -c "import duckdb; p='data/crashes.parquet'; c=duckdb.connect(); print(c.execute('DESCRIBE SELECT * FROM read_parquet(?)',[p]).fetchall()); print(c.execute('SELECT min(crash_date), max(crash_date), count(*), sum(number_of_motorist_killed) FROM read_parquet(?)',[p]).fetchall()); print(c.execute(\"SELECT year(crash_date) y, count(*) crashes, sum(number_of_motorist_killed) killed_motorists, sum(number_of_persons_killed) killed_all FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY y ORDER BY y\",[p]).fetchdf().to_string(index=False))"
# bash
python -c "import duckdb; p='data/crashes.parquet'; c=duckdb.connect(); print(c.execute(\"SELECT year(crash_date) y, min(crash_date), max(crash_date), count(DISTINCT month(crash_date)) months, sum(number_of_motorist_killed) killed FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY y ORDER BY y\",[p]).fetchdf().to_string(index=False)); print(c.execute(\"SELECT year(crash_date) y, month(crash_date) m, count(*) crashes FROM read_parquet(?) WHERE crash_date >= DATE '2025-01-01' AND crash_date < DATE '2026-01-01' GROUP BY y,m ORDER BY m\",[p]).fetchdf().to_string(index=False))"
# bash
python -c "import duckdb; p='data/crashes.parquet'; c=duckdb.connect(); print(c.execute(\"SELECT year(crash_date) y, min(crash_date) first_day, max(crash_date) last_day, count(DISTINCT month(crash_date)) num_months, sum(number_of_motorist_killed) killed FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY y ORDER BY y\",[p]).fetchdf().to_string(index=False)); print(c.execute(\"SELECT month(crash_date) m, count(*) crashes FROM read_parquet(?) WHERE crash_date >= DATE '2025-01-01' AND crash_date < DATE '2026-01-01' GROUP BY m ORDER BY m\",[p]).fetchdf().to_string(index=False))"
# bash
python - <<'PY'
import json
from pathlib import Path
import duckdb
import matplotlib.pyplot as plt
import pandas as pd

out = Path('out')
out.mkdir(exist_ok=True)
con = duckdb.connect()
df = con.execute("""
    SELECT year(crash_date) AS year,
           SUM(number_of_motorist_killed) AS motorist_fatalities,
           COUNT(*) AS reported_crashes
    FROM read_parquet('data/crashes.parquet')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
""").fetchdf()
df['motorist_fatalities'] = df['motorist_fatalities'].astype(int)
df['reported_crashes'] = df['reported_crashes'].astype(int)
df['deaths_per_1000_crashes'] = 1000 * df['motorist_fatalities'] / df['reported_crashes']

# Option 1: directly observed annual motorist death counts.
values1 = df[['year', 'motorist_fatalities']]
values1.to_csv(out / 'values_1.csv', index=False)
fig, ax = plt.subplots(figsize=(10, 5.5))
ax.plot(values1['year'], values1['motorist_fatalities'], marker='o', linewidth=2.5, color='#2457A7')
ax.annotate(f"2013: {values1.iloc[0]['motorist_fatalities']}", (2013, values1.iloc[0]['motorist_fatalities']), xytext=(7, 10), textcoords='offset points', fontsize=9)
ax.annotate(f"2025: {values1.iloc[-1]['motorist_fatalities']}", (2025, values1.iloc[-1]['motorist_fatalities']), xytext=(-40, 10), textcoords='offset points', fontsize=9)
ax.set(title='Motorists killed in NYC crashes, 2013–2025', xlabel='Crash year', ylabel='Motorists killed (count)')
ax.set_xticks(values1['year'])
ax.tick_params(axis='x', rotation=45)
ax.grid(axis='y', alpha=.25)
fig.text(.01, .01, 'Annual deaths are not adjusted for miles driven; source: NYC police-reported crash records.', fontsize=8)
fig.tight_layout(rect=(0, .04, 1, 1))
fig.savefig(out / 'option_1.png', dpi=180, bbox_inches='tight')
plt.close(fig)

# Option 2: fatalities relative to the number of crash records, not mileage exposure.
values2 = df[['year', 'motorist_fatalities', 'reported_crashes', 'deaths_per_1000_crashes']]
values2.to_csv(out / 'values_2.csv', index=False, float_format='%.6f')
fig, ax = plt.subplots(figsize=(10, 5.5))
ax.plot(values2['year'], values2['deaths_per_1000_crashes'], marker='o', linewidth=2.5, color='#B54735')
ax.annotate(f"2013: {values2.iloc[0]['deaths_per_1000_crashes']:.2f}", (2013, values2.iloc[0]['deaths_per_1000_crashes']), xytext=(7, 10), textcoords='offset points', fontsize=9)
ax.annotate(f"2025: {values2.iloc[-1]['deaths_per_1000_crashes']:.2f}", (2025, values2.iloc[-1]['deaths_per_1000_crashes']), xytext=(-40, 10), textcoords='offset points', fontsize=9)
ax.set(title='Motorist deaths per 1,000 reported crashes, 2013–2025', xlabel='Crash year', ylabel='Motorist deaths per 1,000 crash records')
ax.set_xticks(values2['year'])
ax.tick_params(axis='x', rotation=45)
ax.grid(axis='y', alpha=.25)
fig.text(.01, .01, 'Crash-record denominator is not miles driven; source: NYC police-reported crash records.', fontsize=8)
fig.tight_layout(rect=(0, .04, 1, 1))
fig.savefig(out / 'option_2.png', dpi=180, bbox_inches='tight')
plt.close(fig)

first, last = df.iloc[0], df.iloc[-1]
count_change = (last.motorist_fatalities / first.motorist_fatalities - 1) * 100
rate_change = (last.deaths_per_1000_crashes / first.deaths_per_1000_crashes - 1) * 100
options = {
    'options': [
        {
            'id': 1,
            'metric': 'Annual number of motorists killed in police-reported NYC crashes',
            'denominator': 'None (annual count)',
            'grouping': 'Calendar year, 2013–2025',
            'chart_type': 'Line chart',
            'reason': 'Annual deaths are a direct and easily interpreted measure of the fatal burden recorded in this dataset.',
            'probability': 0.45,
            'answer': f"The recorded annual count of motorists killed declined from {int(first.motorist_fatalities)} in 2013 to {int(last.motorist_fatalities)} in 2025 ({abs(count_change):.1f}% lower), but this does not establish a decline per mile driven.",
            'interpretation': f"Because this file has no miles-driven exposure, it cannot establish whether deaths per mile declined; the chart shows the annual number of motorists killed falling from {int(first.motorist_fatalities)} in 2013 to {int(last.motorist_fatalities)} in 2025. Annual fatalities are a directly observed burden measure, but they leave exposure-adjusted risk per mile unanswered."
        },
        {
            'id': 2,
            'metric': 'Motorist deaths per 1,000 police-reported crashes',
            'denominator': 'Number of police-reported crash records in that calendar year',
            'grouping': 'Calendar year, 2013–2025',
            'chart_type': 'Line chart',
            'reason': 'Normalizing deaths by crash-record volume provides a useful comparison when annual crash counts differ.',
            'probability': 0.55,
            'answer': f"Motorist deaths per 1,000 reported crashes rose from {first.deaths_per_1000_crashes:.2f} in 2013 to {last.deaths_per_1000_crashes:.2f} in 2025 ({rate_change:.1f}% higher), so this crash-normalized proxy did not decline, though it is not risk per mile.",
            'interpretation': f"This data lacks miles driven, so it cannot answer whether motorist deaths per mile declined; instead, deaths per 1,000 reported crashes rose from {first.deaths_per_1000_crashes:.2f} in 2013 to {last.deaths_per_1000_crashes:.2f} in 2025. Dividing by crash records provides a crash-volume-adjusted comparison, but it does not measure mileage exposure or individual motorist risk."
        }
    ]
}
(out / 'options.json').write_text(json.dumps(options, indent=2) + '\n')
print(df.to_string(index=False))
print(f'2013–2025 motorist-death count change: {count_change:.1f}%')
print(f'2013–2025 deaths per 1,000 crashes change: {rate_change:.1f}%')
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
- tr_TR01: If a per-reported-crash rate spanning 2020 is shown, the output says that the number of recorded crashes changes sharply around 2020 and that this affects comparing the per-crash rate across years (naming the cause, the 2020 recording change, is not required: it is not in the data or the dictionary).
- tr_PERMILE: A per-reported-crash rate, if shown, is not presented as a substitute for per-mile risk.
- tr_VMT: No vehicle-miles figure is imported, assumed or estimated from outside the data.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence
- required_statement: PASS if the output states, in its own words: Per-mile (per vehicle-mile) risk cannot be determined from this data because it has no vehicle-miles or traffic volume.

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.