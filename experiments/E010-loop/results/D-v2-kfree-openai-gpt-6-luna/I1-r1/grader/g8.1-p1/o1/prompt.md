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
metric: Annual motorist fatalities
denominator: None (absolute count)
grouping: Crash year, 2013–2025
chart_type: Line chart
probability: 0.45
WRITTEN ANSWER:
Recorded motorist fatalities fell from 110 in 2013 to 81 in 2025, but this dataset cannot determine whether deaths per mile driven declined. This chart answers how the annual number of motorist deaths in reported NYC crashes changed, showing a net decrease across the endpoints with year-to-year variation. Fatality counts are a direct measure of recorded burden, but they leave deaths per mile unanswered because the dataset has no miles-driven measure.

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
python3 -c "import duckdb; p='data/crashes.parquet'; c=duckdb.connect(); print(c.execute(\"select count(*), min(crash_date), max(crash_date) from read_parquet(?)\", [p]).fetchall()); print(c.execute(\"describe select * from read_parquet(?)\", [p]).fetchall())"
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; q=\"select year(crash_date) y, count(*) crashes, sum(coalesce(number_of_motorist_killed,0)) motorist_killed, sum(coalesce(number_of_motorist_injured,0)) motorist_injured, count(*) filter(where coalesce(number_of_motorist_killed,0)>0) crashes_with_motorist_fatality, sum(coalesce(number_of_persons_killed,0)) all_killed from read_parquet(?) where crash_date >= date '2013-01-01' and crash_date < date '2026-01-01' group by 1 order by 1\"; print(c.execute(q,[p]).df().to_string(index=False)); print('null deaths',c.execute(\"select count(*) filter(where number_of_motorist_killed is null), count(*) from read_parquet(?) where crash_date >= date '2013-01-01' and crash_date < date '2026-01-01'\",[p]).fetchall())"
# bash
ls
# bash
python3 - <<'PY'
import duckdb
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

out = Path('out')
out.mkdir(exist_ok=True)
con = duckdb.connect()
data = con.execute("""
    SELECT year(crash_date) AS year,
           count(*) AS reported_crashes,
           sum(coalesce(number_of_motorist_killed, 0))::BIGINT AS motorist_fatalities
    FROM read_parquet('data/crashes.parquet')
    WHERE crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY 1
    ORDER BY 1
""").df()
assert data['year'].tolist() == list(range(2013, 2026))
data['motorist_fatalities_per_1000_crashes'] = data['motorist_fatalities'] / data['reported_crashes'] * 1000

# Option 1: absolute fatality burden
v1 = data[['year', 'motorist_fatalities']]
v1.to_csv(out / 'values_1.csv', index=False)
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.plot(v1['year'], v1['motorist_fatalities'], marker='o', linewidth=2, color='#245b8f')
ax.set(title='NYC motorist fatalities in reported crashes, 2013–2025', xlabel='Crash year', ylabel='Motorist fatalities (people)')
ax.set_xticks(v1['year'])
ax.tick_params(axis='x', rotation=45)
ax.grid(axis='y', alpha=.28)
ax.annotate(f"2013: {int(v1.iloc[0]['motorist_fatalities'])}", (v1.iloc[0]['year'], v1.iloc[0]['motorist_fatalities']), xytext=(5, 9), textcoords='offset points')
ax.annotate(f"2025: {int(v1.iloc[-1]['motorist_fatalities'])}", (v1.iloc[-1]['year'], v1.iloc[-1]['motorist_fatalities']), xytext=(-42, 9), textcoords='offset points')
fig.tight_layout()
fig.savefig(out / 'option_1.png', dpi=160)
plt.close(fig)

# Option 2: fatality burden relative to the number of reported crashes
v2 = data[['year', 'motorist_fatalities_per_1000_crashes']].copy()
v2.to_csv(out / 'values_2.csv', index=False, float_format='%.6f')
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.plot(v2['year'], v2['motorist_fatalities_per_1000_crashes'], marker='o', linewidth=2, color='#b45432')
ax.set(title='Motorist fatalities per 1,000 reported NYC crashes, 2013–2025', xlabel='Crash year', ylabel='Motorist fatalities per 1,000 reported crashes')
ax.set_xticks(v2['year'])
ax.tick_params(axis='x', rotation=45)
ax.grid(axis='y', alpha=.28)
ax.annotate(f"2013: {v2.iloc[0]['motorist_fatalities_per_1000_crashes']:.2f}", (v2.iloc[0]['year'], v2.iloc[0]['motorist_fatalities_per_1000_crashes']), xytext=(5, 9), textcoords='offset points')
ax.annotate(f"2025: {v2.iloc[-1]['motorist_fatalities_per_1000_crashes']:.2f}", (v2.iloc[-1]['year'], v2.iloc[-1]['motorist_fatalities_per_1000_crashes']), xytext=(-42, 9), textcoords='offset points')
fig.tight_layout()
fig.savefig(out / 'option_2.png', dpi=160)
plt.close(fig)

print(data.to_string(index=False, formatters={'motorist_fatalities_per_1000_crashes': '{:.6f}'.format}))
PY
# bash
python3 - <<'PY'
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
out = Path('out')
v1 = pd.read_csv(out / 'values_1.csv')
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.plot(v1['year'], v1['motorist_fatalities'], marker='o', linewidth=2, color='#245b8f')
ax.set(title='NYC motorist fatalities in reported crashes, 2013–2025', xlabel='Crash year', ylabel='Motorist fatalities (people)', ylim=(0, 150))
ax.set_xticks(v1['year']); ax.tick_params(axis='x', rotation=45); ax.grid(axis='y', alpha=.28)
ax.annotate(f"2013: {int(v1.iloc[0]['motorist_fatalities'])}", (v1.iloc[0]['year'], v1.iloc[0]['motorist_fatalities']), xytext=(5, 9), textcoords='offset points')
ax.annotate(f"2025: {int(v1.iloc[-1]['motorist_fatalities'])}", (v1.iloc[-1]['year'], v1.iloc[-1]['motorist_fatalities']), xytext=(-42, 9), textcoords='offset points')
fig.tight_layout(); fig.savefig(out / 'option_1.png', dpi=160); plt.close(fig)
v2 = pd.read_csv(out / 'values_2.csv')
fig, ax = plt.subplots(figsize=(9, 5.2))
ax.plot(v2['year'], v2['motorist_fatalities_per_1000_crashes'], marker='o', linewidth=2, color='#b45432')
ax.set(title='Motorist fatalities per 1,000 reported NYC crashes, 2013–2025', xlabel='Crash year', ylabel='Motorist fatalities per 1,000 reported crashes', ylim=(0, 1.4))
ax.set_xticks(v2['year']); ax.tick_params(axis='x', rotation=45); ax.grid(axis='y', alpha=.28)
ax.annotate(f"2013: {v2.iloc[0]['motorist_fatalities_per_1000_crashes']:.2f}", (v2.iloc[0]['year'], v2.iloc[0]['motorist_fatalities_per_1000_crashes']), xytext=(5, 9), textcoords='offset points')
ax.annotate(f"2025: {v2.iloc[-1]['motorist_fatalities_per_1000_crashes']:.2f}", (v2.iloc[-1]['year'], v2.iloc[-1]['motorist_fatalities_per_1000_crashes']), xytext=(-42, 9), textcoords='offset points')
fig.tight_layout(); fig.savefig(out / 'option_2.png', dpi=160); plt.close(fig)
PY
# bash
python3 -c "import json, pathlib; p=pathlib.Path('out/options.json'); o=json.loads(p.read_text()); print('options:', len(o['options']), 'probability sum:', sum(x['probability'] for x in o['options'])); print('files:', sorted(str(x) for x in pathlib.Path('out').iterdir()))"

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