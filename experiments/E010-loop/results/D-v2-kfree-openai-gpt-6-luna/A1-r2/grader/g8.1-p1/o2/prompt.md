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

QUESTION ASKED: Has road safety for pedestrians in Brooklyn gotten better since 2013? Make a chart suitable for a local news story and summarize the findings.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Annual number of Brooklyn crashes with at least one pedestrian injured or killed
denominator: None; crash counts, not adjusted for population or walking exposure
grouping: Calendar year
chart_type: Line chart
probability: 0.35
WRITTEN ANSWER:
Crashes involving pedestrian injury or death fell from 3,498 in 2013 to 2,766 in 2025 (20.9% lower), although they increased from 1,724 in 2020 to 2,766 in 2025. This framing addresses the frequency of reported crashes that harmed at least one pedestrian, rather than the number of people harmed in those crashes. Although the 2025 count is below 2013, it rose each year from the 2020 low through 2025, so the endpoint comparison misses a substantial recent rebound. It does not measure the chance of being hit per walk or account for changes in pedestrian activity.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,pedestrian_involved_crashes
2013,3498
2014,3234
2015,2962
2016,2797
2017,2550
2018,2697
2019,2623
2020,1724
2021,1856
2022,2185
2023,2310
2024,2576
2025,2766

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c "import duckdb; p='data/crashes.parquet'; print(duckdb.query(f\"select min(crash_date), max(crash_date), count(*) from read_parquet('{p}')\").fetchall()); print(duckdb.query(f\"describe select * from read_parquet('{p}')\").fetchall())"
# bash
python -c "import duckdb; p='data/crashes.parquet'; q=f\"select year(crash_date) y, count(*) n, max(crash_date) latest, sum(number_of_pedestrians_injured) inj, sum(number_of_pedestrians_killed) killed, sum(case when coalesce(number_of_pedestrians_injured,0)+coalesce(number_of_pedestrians_killed,0)>0 then 1 else 0 end) pedestrian_involved_crashes from read_parquet('{p}') where borough='BROOKLYN' and crash_date >= date '2013-01-01' group by y order by y\"; print(duckdb.query(q).df().to_string(index=False)); print('boroughs',duckdb.query(f\"select borough,count(*) from read_parquet('{p}') group by borough order by 2 desc\").fetchall())"
# bash
ls .
# bash
python - <<'PY'
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import json

out = Path('out')
out.mkdir(exist_ok=True)
source = str(Path('data/crashes.parquet'))
query = f"""
SELECT
  year(crash_date) AS year,
  SUM(COALESCE(number_of_pedestrians_injured, 0))::BIGINT AS pedestrians_injured,
  SUM(COALESCE(number_of_pedestrians_killed, 0))::BIGINT AS pedestrians_killed,
  SUM(CASE WHEN COALESCE(number_of_pedestrians_injured, 0) + COALESCE(number_of_pedestrians_killed, 0) > 0 THEN 1 ELSE 0 END)::BIGINT AS pedestrian_involved_crashes
FROM read_parquet('{source}')
WHERE borough = 'BROOKLYN'
  AND crash_date >= DATE '2013-01-01'
  AND crash_date < DATE '2026-01-01'
GROUP BY year
ORDER BY year
"""
df = duckdb.query(query).df()
df['year'] = df['year'].astype(int)
df['total_pedestrian_casualties'] = df['pedestrians_injured'] + df['pedestrians_killed']
assert df['year'].tolist() == list(range(2013, 2026))

# Option 1: annual pedestrian casualty counts, split by injury severity.
vals1 = df[['year', 'pedestrians_injured', 'pedestrians_killed', 'total_pedestrian_casualties']]
vals1.to_csv(out / 'values_1.csv', index=False)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7.5), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
years = df['year']
ax1.plot(years, df['pedestrians_injured'], color='#176B87', marker='o', linewidth=2.5, markersize=5)
ax1.fill_between(years, df['pedestrians_injured'], color='#176B87', alpha=.10)
ax1.set_ylabel('Pedestrians injured')
ax1.set_ylim(0, 4200)
ax1.grid(axis='y', color='#d9d9d9', linewidth=.8)
ax1.spines[['top', 'right']].set_visible(False)
ax1.annotate(f"{int(df.iloc[0]['pedestrians_injured']):,}", (2013, int(df.iloc[0]['pedestrians_injured'])), xytext=(0, 9), textcoords='offset points', ha='center', color='#176B87', fontweight='bold')
ax1.annotate(f"{int(df.iloc[-1]['pedestrians_injured']):,}", (2025, int(df.iloc[-1]['pedestrians_injured'])), xytext=(0, 9), textcoords='offset points', ha='center', color='#176B87', fontweight='bold')
ax2.plot(years, df['pedestrians_killed'], color='#C44736', marker='o', linewidth=2.5, markersize=5)
ax2.set_ylabel('Pedestrians killed')
ax2.set_ylim(0, 55)
ax2.set_xticks(years)
ax2.set_xticklabels([str(y) for y in years], rotation=45, ha='right')
ax2.grid(axis='y', color='#d9d9d9', linewidth=.8)
ax2.spines[['top', 'right']].set_visible(False)
ax2.annotate(f"{int(df.iloc[0]['pedestrians_killed'])}", (2013, int(df.iloc[0]['pedestrians_killed'])), xytext=(0, 8), textcoords='offset points', ha='center', color='#C44736', fontweight='bold')
ax2.annotate(f"{int(df.iloc[-1]['pedestrians_killed'])}", (2025, int(df.iloc[-1]['pedestrians_killed'])), xytext=(0, 8), textcoords='offset points', ha='center', color='#C44736', fontweight='bold')
fig.suptitle('Brooklyn pedestrian casualties, 2013–2025', x=.08, ha='left', fontsize=17, fontweight='bold', y=.99)
fig.text(.08, .945, 'Annual counts in police-reported crashes · complete calendar years only', color='#555555', fontsize=10)
fig.text(.08, .015, 'Source: NYC motor vehicle crash records. Counts do not account for changes in walking exposure.', color='#555555', fontsize=9)
fig.tight_layout(rect=[0.06, .045, .99, .93], h_pad=1.2)
fig.savefig(out / 'option_1.png', dpi=180, bbox_inches='tight', facecolor='white')
plt.close(fig)

# Option 2: crash-level count with at least one pedestrian injured or killed.
vals2 = df[['year', 'pedestrian_involved_crashes']]
vals2.to_csv(out / 'values_2.csv', index=False)
fig, ax = plt.subplots(figsize=(10, 5.8))
ax.plot(years, df['pedestrian_involved_crashes'], color='#176B87', marker='o', linewidth=2.7, markersize=5)
ax.fill_between(years, df['pedestrian_involved_crashes'], color='#176B87', alpha=.12)
ax.set_ylim(0, 4000)
ax.set_xticks(years)
ax.set_xticklabels([str(y) for y in years], rotation=45, ha='right')
ax.set_ylabel('Crashes involving pedestrian injury or death')
ax.set_title('Crashes that injured or killed pedestrians in Brooklyn', loc='left', fontsize=16, fontweight='bold', pad=28)
ax.text(0, 1.02, 'Annual number of police-reported crashes with ≥1 pedestrian injured or killed · 2013–2025', transform=ax.transAxes, color='#555555', fontsize=10)
ax.grid(axis='y', color='#d9d9d9', linewidth=.8)
ax.spines[['top', 'right']].set_visible(False)
ax.annotate(f"{int(df.iloc[0]['pedestrian_involved_crashes']):,}", (2013, int(df.iloc[0]['pedestrian_involved_crashes'])), xytext=(0, 9), textcoords='offset points', ha='center', color='#176B87', fontweight='bold')
ax.annotate(f"{int(df.iloc[-1]['pedestrian_involved_crashes']):,}", (2025, int(df.iloc[-1]['pedestrian_involved_crashes'])), xytext=(0, 9), textcoords='offset points', ha='center', color='#176B87', fontweight='bold')
fig.text(.08, .015, 'Source: NYC motor vehicle crash records. This is a crash count, not a rate per pedestrian or trip.', color='#555555', fontsize=9)
fig.tight_layout(rect=[0.06, .05, .99, .94])
fig.savefig(out / 'option_2.png', dpi=180, bbox_inches='tight', facecolor='white')
plt.close(fig)

inj0, injN = int(df.iloc[0]['pedestrians_injured']), int(df.iloc[-1]['pedestrians_injured'])
kill0, killN = int(df.iloc[0]['pedestrians_killed']), int(df.iloc[-1]['pedestrians_killed'])
crash0, crashN = int(df.iloc[0]['pedestrian_involved_crashes']), int(df.iloc[-1]['pedestrian_involved_crashes'])
cas0, casN = inj0 + kill0, injN + killN
pct = lambda a, b: (b-a)/a*100
options = {
  'options': [
    {
      'id': 1,
      'metric': 'Annual counts of pedestrians injured and killed in Brooklyn crashes',
      'denominator': 'None; raw counts, not adjusted for population or walking exposure',
      'grouping': 'Calendar year, split by injury outcome',
      'chart_type': 'Two-panel line chart',
      'reason': 'Separating injuries from deaths keeps the more severe but less frequent outcome visible while showing the overall burden.',
      'probability': 0.65,
      'answer': f"From 2013 to 2025, pedestrian injuries fell from {inj0:,} to {injN:,} ({abs(pct(inj0,injN)):.1f}% lower), but deaths rose from {kill0} to {killN} ({pct(kill0,killN):.1f}% higher); combined casualties fell from {cas0:,} to {casN:,}.",
      'interpretation': 'This framing answers whether the number of pedestrians harmed in reported Brooklyn crashes changed, while distinguishing nonfatal injuries from deaths. Injuries and total casualties are lower in 2025 than in 2013, but pedestrian deaths are higher, so the picture is mixed rather than uniformly better. Raw counts cannot show risk per pedestrian or trip because the file has no walking-exposure denominator.'
    },
    {
      'id': 2,
      'metric': 'Annual number of Brooklyn crashes with at least one pedestrian injured or killed',
      'denominator': 'None; crash counts, not adjusted for population or walking exposure',
      'grouping': 'Calendar year',
      'chart_type': 'Line chart',
      'reason': 'A crash-level count answers how often a reported collision caused pedestrian harm without counting multiple victims as separate crashes.',
      'probability': 0.35,
      'answer': f"Crashes involving pedestrian injury or death fell from {crash0:,} in 2013 to {crashN:,} in 2025 ({abs(pct(crash0,crashN)):.1f}% lower), although they increased from 1,724 in 2020 to {crashN:,} in 2025.",
      'interpretation': 'This framing addresses the frequency of reported crashes that harmed at least one pedestrian, rather than the number of people harmed in those crashes. The 2025 count is below 2013 but has climbed from the 2020 low, indicating improvement only in the endpoint comparison. It does not measure the chance of being hit per walk or account for changes in pedestrian activity.'
    }
  ]
}
with open(out / 'options.json', 'w', encoding='utf-8') as f:
    json.dump(options, f, indent=2, ensure_ascii=False)
    f.write('\n')
print(df.to_string(index=False))
print('2013-2025 percent changes:', {'injuries': pct(inj0,injN), 'deaths': pct(kill0,killN), 'casualties': pct(cas0,casN), 'crashes': pct(crash0,crashN)})
PY
# bash
python - <<'PY'
from pathlib import Path
import json
import pandas as pd
out=Path('out')
opts=json.loads((out/'options.json').read_text())
assert len(opts['options']) == 2
assert abs(sum(x['probability'] for x in opts['options'])-1) < 1e-9
for i in (1,2):
    assert (out/f'option_{i}.png').is_file() and (out/f'option_{i}.png').stat().st_size > 0
    data=pd.read_csv(out/f'values_{i}.csv')
    assert len(data)==13 and data.year.iloc[[0,-1]].tolist()==[2013,2025]
    print(f'option {i}: image { (out/f"option_{i}.png").stat().st_size } bytes; values {len(data)} years, {data.year.iloc[0]}–{data.year.iloc[-1]}')
print('JSON valid; probabilities sum to',sum(x['probability'] for x in opts['options']))
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
- tr_TR05: If a borough filter (borough = 'BROOKLYN') is used, the output discloses that crashes with no borough recorded (19.9–38.1% per year) are excluded.
- tr_TR11: The output does not call Brooklyn 'safer' or 'less safe' from counts alone without saying that there is no pedestrian exposure measure.
- tr_TR01: If a per-reported-crash rate spanning 2020 is shown, the output says that the number of recorded crashes changes sharply around 2020 and that this affects comparing the per-crash rate across years (naming the cause, the 2020 recording change, is not required: it is not in the data or the dictionary).
- tr_TR15: Claims about pedestrian deaths changing are qualified by the small counts (about 30–39 per year).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.