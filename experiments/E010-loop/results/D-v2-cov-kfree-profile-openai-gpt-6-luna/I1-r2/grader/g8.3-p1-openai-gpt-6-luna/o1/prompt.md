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
metric: Annual count of motorist deaths
denominator: None (absolute count; sum of number_of_motorist_killed)
grouping: Crash year, 2013–2025
chart_type: Line chart
probability: 0.5
WRITTEN ANSWER:
Recorded motorist deaths declined from 110 in 2013 to 81 in 2025 (26.4% lower), but the data cannot establish whether deaths per mile driven declined. This framing answers whether the number of motorists killed in reported NYC crashes changed, and the chart shows 110 deaths in 2013 versus 81 in 2025. A death count is a defensible description of the observed fatality burden, but it is not a risk rate because no miles-driven exposure is present. It therefore leaves the question of motorist deaths per mile unanswered. It uses complete calendar years 2013–2025 and excludes 2012 (100,545 rows, 4.43% of file) and 2026 (36,424 rows, 1.61% of file) as outside the requested interval; no in-range rows are omitted for NULL required values, and no included year is partial.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,motorist_deaths
2013,110.0
2014,109.0
2015,95.0
2016,72.0
2017,107.0
2018,98.0
2019,82.0
2020,139.0
2021,134.0
2022,116.0
2023,123.0
2024,111.0
2025,81.0

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
pwd && ls
# bash
ls
# bash
python3 -c "import duckdb; print(duckdb.sql(\"DESCRIBE SELECT * FROM read_parquet('data/crashes.parquet')\").fetchall())"
# bash
python3 - <<'PY'
import duckdb, pandas as pd, matplotlib.pyplot as plt, json, os
path='data/crashes.parquet'
con=duckdb.connect()
summary=con.execute("""
WITH annual AS (
 SELECT year(crash_date) AS year,
        count(*) AS crashes,
        sum(number_of_motorist_killed) AS motorist_deaths,
        count(*) FILTER (WHERE number_of_motorist_killed > 0) AS crashes_with_motorist_death,
        count(*) FILTER (WHERE crash_date IS NULL) AS null_dates,
        count(*) FILTER (WHERE number_of_motorist_killed IS NULL) AS null_motorist_killed
 FROM read_parquet(?)
 GROUP BY 1
)
SELECT * FROM annual ORDER BY year
""", [path]).df()
all_rows=int(summary.crashes.sum())
base=summary[summary.year.between(2013,2025)].copy()
base['deaths_per_1000_crashes']=base.motorist_deaths/base.crashes*1000
base['crashes_with_motorist_death_pct']=base.crashes_with_motorist_death/base.crashes*100
print('ANNUAL', base[['year','crashes','motorist_deaths','crashes_with_motorist_death','deaths_per_1000_crashes','crashes_with_motorist_death_pct','null_dates','null_motorist_killed']].to_string(index=False))
print('ALL_ROWS',all_rows)
print('EXCLUDED',summary[~summary.year.between(2013,2025)][['year','crashes']].to_dict('records'))
print('SHARES',[(int(r.year), int(r.crashes), r.crashes/all_rows*100) for r in summary[~summary.year.between(2013,2025)].itertuples()])

os.makedirs('out',exist_ok=True)
# Option 1: absolute motorist deaths
v1=base[['year','motorist_deaths']].copy()
v1.to_csv('out/values_1.csv',index=False)
fig,ax=plt.subplots(figsize=(10,5.5))
ax.plot(v1.year,v1.motorist_deaths,marker='o',linewidth=2,color='#1769aa')
ax.set(title='Motorist deaths in NYC crashes, 2013–2025',xlabel='Crash year',ylabel='Motorist deaths (people)')
ax.set_xticks(v1.year); ax.tick_params(axis='x',rotation=45); ax.grid(axis='y',alpha=.25)
ax.annotate(f"{int(v1.motorist_deaths.iloc[0]):,}",(v1.year.iloc[0],v1.motorist_deaths.iloc[0]),xytext=(0,8),textcoords='offset points',ha='center')
ax.annotate(f"{int(v1.motorist_deaths.iloc[-1]):,}",(v1.year.iloc[-1],v1.motorist_deaths.iloc[-1]),xytext=(0,8),textcoords='offset points',ha='center')
fig.tight_layout(); fig.savefig('out/option_1.png',dpi=160); plt.close(fig)
# Option 2: fraction of crash rows with at least one motorist death
v2=base[['year','crashes_with_motorist_death','crashes','crashes_with_motorist_death_pct']].copy()
v2.to_csv('out/values_2.csv',index=False)
fig,ax=plt.subplots(figsize=(10,5.5))
ax.plot(v2.year,v2.crashes_with_motorist_death_pct,marker='o',linewidth=2,color='#c4512d')
ax.set(title='Share of reported crashes involving a motorist death, 2013–2025',xlabel='Crash year',ylabel='Crashes with ≥1 motorist death (% of crash records)')
ax.set_xticks(v2.year); ax.tick_params(axis='x',rotation=45); ax.grid(axis='y',alpha=.25)
for i in [0,len(v2)-1]:
 r=v2.iloc[i]; ax.annotate(f"{r.crashes_with_motorist_death_pct:.3f}%",(r.year,r.crashes_with_motorist_death_pct),xytext=(0,8),textcoords='offset points',ha='center')
fig.tight_layout(); fig.savefig('out/option_2.png',dpi=160); plt.close(fig)

first,last=base.iloc[0],base.iloc[-1]
pct=(last.motorist_deaths/first.motorist_deaths-1)*100
p0,p1=first.crashes_with_motorist_death_pct,last.crashes_with_motorist_death_pct
excluded=summary[~summary.year.between(2013,2025)]
excl_desc=', '.join(f"{int(r.year)}: {int(r.crashes):,} rows ({r.crashes/all_rows*100:.2f}% of file)" for r in excluded.itertuples())
null_in_range=int(base.null_dates.sum()+base.null_motorist_killed.sum())
shared=f"The analysis uses the complete calendar years 2013–2025; it excludes {excl_desc} because they fall outside the requested interval. No in-range rows are omitted for NULL crash dates or motorist-fatality counts, and no included year is partial."
opts={"options":[
 {"id":1,"metric":"Annual count of motorist deaths","denominator":"None (absolute count; sum of number_of_motorist_killed)","grouping":"Crash year, 2013–2025","chart_type":"Line chart","reason":"Absolute deaths provide a direct, transparent measure of the motorist fatality burden, though not a mileage-adjusted risk.","probability":0.5,"answer":f"Recorded motorist deaths declined from {int(first.motorist_deaths):,} in 2013 to {int(last.motorist_deaths):,} in 2025 ({abs(pct):.1f}% lower), but the data cannot establish whether deaths per mile driven declined.","interpretation":f"This framing answers whether the number of motorists killed in reported NYC crashes changed, and the chart shows {int(first.motorist_deaths):,} deaths in 2013 versus {int(last.motorist_deaths):,} in 2025. A death count is a defensible description of the observed fatality burden, but it is not a risk rate because no miles-driven exposure is present. It therefore leaves the question of motorist deaths per mile unanswered. {shared}"},
 {"id":2,"metric":"Share of reported crash records with at least one motorist death","denominator":"All reported crash records in each year","grouping":"Crash year, 2013–2025","chart_type":"Line chart","reason":"The share of crashes involving a motorist death normalizes fatal crashes by reported crash volume, offering a crash-level severity measure.","probability":0.5,"answer":f"The share of crash records with a motorist death changed from {p0:.3f}% in 2013 to {p1:.3f}% in 2025 ({p1-p0:+.3f} percentage points), but this is not risk per mile driven.","interpretation":f"This framing answers how often a reported crash record involved at least one motorist death, with {p0:.3f}% in 2013 and {p1:.3f}% in 2025 shown. Using all reported crash records as the denominator gives a defensible crash-level fatality measure, but it is not exposure-adjusted. It leaves the per-mile risk question unanswered because annual miles driven are absent from this file. {shared}"}
]}
with open('out/options.json','w') as f: json.dump(opts,f,indent=2); f.write('\n')
print('ENDPOINTS', int(first.motorist_deaths), int(last.motorist_deaths), pct, p0, p1, p1-p0)
PY
# bash
python3 - <<'PY'
import json, pandas as pd, os
p='out/'
j=json.load(open(p+'options.json'))
assert len(j['options']) == 2
assert abs(sum(o['probability'] for o in j['options'])-1) < 1e-9
for o in j['options']:
    text=o['interpretation']
    print(o['id'], 'interpretation sentences:', text.count('.') , 'chart bytes:', os.path.getsize(p+f"option_{o['id']}.png"))
    assert os.path.getsize(p+f"option_{o['id']}.png") > 0
x=pd.read_csv(p+'values_1.csv'); y=pd.read_csv(p+'values_2.csv')
assert int(x.loc[x.year.eq(2013),'motorist_deaths'].iloc[0]) == 110
assert int(x.loc[x.year.eq(2025),'motorist_deaths'].iloc[0]) == 81
assert abs(y.loc[y.year.eq(2013),'crashes_with_motorist_death_pct'].iloc[0] - 0.05006331536943782) < 1e-12
assert abs(y.loc[y.year.eq(2025),'crashes_with_motorist_death_pct'].iloc[0] - 0.08767212961447642) < 1e-12
print('JSON and values cross-check: OK')
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