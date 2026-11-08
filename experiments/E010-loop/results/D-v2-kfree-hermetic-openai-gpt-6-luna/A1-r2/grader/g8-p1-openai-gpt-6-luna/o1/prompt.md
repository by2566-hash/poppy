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
metric: Annual pedestrian casualties (injured + killed)
denominator: None; annual total count
grouping: Calendar year, Brooklyn
chart_type: Line chart
probability: 0.55
WRITTEN ANSWER:
Brooklyn recorded 2,874 pedestrian casualties in 2025, 21.7% fewer than 3,671 in 2013, although the total has risen from its 2020 low of 1,798. This addresses whether the total number of pedestrians harmed in reported Brooklyn crashes is lower than in 2013: it is, but the series has risen substantially since 2020. Annual counts are a defensible measure of the burden of harm; without pedestrian-trip or population exposure, they do not establish that an individual pedestrian’s risk fell.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,pedestrians_injured,pedestrians_killed,pedestrian_casualties
2013,3641,30,3671
2014,3349,42,3391
2015,3029,46,3075
2016,2917,20,2937
2017,2663,20,2683
2018,2785,23,2808
2019,2700,33,2733
2020,1781,17,1798
2021,1905,32,1937
2022,2275,23,2298
2023,2385,22,2407
2024,2645,31,2676
2025,2835,39,2874

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
pwd && ls
# bash
ls
# bash
python3 -c "import duckdb; print(duckdb.__version__)"
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute('DESCRIBE SELECT * FROM read_parquet(?)',[p]).fetchdf().to_string(index=False)); print(c.execute(\"SELECT MIN(crash_date) min_date, MAX(crash_date) max_date, COUNT(*) rows, COUNT(DISTINCT borough) boroughs FROM read_parquet(?)\",[p]).fetchdf().to_string(index=False)); print(c.execute(\"SELECT EXTRACT(year FROM crash_date) yr, COUNT(*) crashes, SUM(number_of_pedestrians_injured) ped_inj, SUM(number_of_pedestrians_killed) ped_killed, COUNT(*) FILTER (WHERE number_of_pedestrians_injured+number_of_pedestrians_killed>0) ped_casualty_crashes FROM read_parquet(?) WHERE borough='BROOKLYN' GROUP BY yr ORDER BY yr\",[p]).fetchdf().to_string(index=False))"
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(\"SELECT MIN(crash_date) min_date, MAX(crash_date) max_date, COUNT(*) AS n_records, COUNT(DISTINCT borough) boroughs FROM read_parquet(?)\",[p]).fetchdf().to_string(index=False)); print(c.execute(\"SELECT EXTRACT(year FROM crash_date) yr, COUNT(*) crashes, SUM(number_of_pedestrians_injured) ped_inj, SUM(number_of_pedestrians_killed) ped_killed, COUNT(*) FILTER (WHERE number_of_pedestrians_injured+number_of_pedestrians_killed>0) ped_casualty_crashes FROM read_parquet(?) WHERE borough='BROOKLYN' GROUP BY yr ORDER BY yr\",[p]).fetchdf().to_string(index=False))"
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(\"SELECT EXTRACT(year FROM crash_date)::INT year, MIN(crash_date) first_day, MAX(crash_date) last_day, SUM(number_of_pedestrians_injured) injured, SUM(number_of_pedestrians_killed) killed FROM read_parquet(?) WHERE borough='BROOKLYN' AND crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY year ORDER BY year\",[p]).fetchdf().to_string(index=False))"
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(\"SELECT EXTRACT(year FROM crash_date)::INT AS yr, MIN(crash_date) first_day, MAX(crash_date) last_day, SUM(number_of_pedestrians_injured) injured, SUM(number_of_pedestrians_killed) killed FROM read_parquet(?) WHERE borough='BROOKLYN' AND crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY yr ORDER BY yr\",[p]).fetchdf().to_string(index=False))"
# bash
python3 - <<'PY'
import os, json
import duckdb
import pandas as pd
import matplotlib.pyplot as plt

os.makedirs('out', exist_ok=True)
con = duckdb.connect()
df = con.execute("""
    SELECT EXTRACT(YEAR FROM crash_date)::INT AS year,
           SUM(number_of_pedestrians_injured)::BIGINT AS pedestrians_injured,
           SUM(number_of_pedestrians_killed)::BIGINT AS pedestrians_killed
    FROM read_parquet('data/crashes.parquet')
    WHERE borough = 'BROOKLYN'
      AND crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY year ORDER BY year
""").fetchdf()
df['pedestrian_casualties'] = df.pedestrians_injured + df.pedestrians_killed
df['fatal_share_pct'] = df.pedestrians_killed / df.pedestrian_casualties * 100
assert df.year.tolist() == list(range(2013, 2026))

navy = '#17324D'
blue = '#277DA1'
red = '#C33C54'
gray = '#64748B'
plt.rcParams.update({'font.family':'DejaVu Sans', 'axes.spines.top':False,
                     'axes.spines.right':False, 'axes.titleweight':'bold'})

# Option 1: total reported pedestrian casualties
cols = ['year','pedestrians_injured','pedestrians_killed','pedestrian_casualties']
df[cols].to_csv('out/values_1.csv', index=False)
fig, ax = plt.subplots(figsize=(10,5.8))
ax.plot(df.year, df.pedestrian_casualties, color=blue, linewidth=3, marker='o', markersize=5)
ax.fill_between(df.year, df.pedestrian_casualties, color=blue, alpha=.10)
ax.set(title='Brooklyn pedestrian casualties fell from 2013, then climbed',
       ylabel='Pedestrians injured or killed in reported crashes', xlabel='Calendar year')
ax.set_xticks(df.year); ax.tick_params(axis='x', rotation=0)
ax.grid(axis='y', color='#D9E0E7', linewidth=.8); ax.set_axisbelow(True)
first, last = int(df.iloc[0].pedestrian_casualties), int(df.iloc[-1].pedestrian_casualties)
ax.annotate(f'{first:,}', (2013, first), xytext=(5,10), textcoords='offset points', color=navy, fontweight='bold')
ax.annotate(f'{last:,}', (2025, last), xytext=(-5,10), textcoords='offset points', ha='right', color=navy, fontweight='bold')
fig.text(.01,.01,'Source: NYC police-reported motor vehicle crashes. Annual counts; not adjusted for pedestrian activity.', color=gray, fontsize=9)
fig.tight_layout(rect=(0,.05,1,1)); fig.savefig('out/option_1.png', dpi=180, bbox_inches='tight'); plt.close(fig)

# Option 2: reported pedestrian deaths
cols = ['year','pedestrians_killed']
df[cols].to_csv('out/values_2.csv', index=False)
fig, ax = plt.subplots(figsize=(10,5.8))
ax.bar(df.year, df.pedestrians_killed, color=red, width=.72)
ax.set(title='Pedestrian deaths in Brooklyn remain above the 2013 count',
       ylabel='Pedestrians killed in reported crashes', xlabel='Calendar year')
ax.set_xticks(df.year); ax.grid(axis='y', color='#D9E0E7', linewidth=.8); ax.set_axisbelow(True)
for year in (2013, 2015, 2025):
    val = int(df.loc[df.year == year, 'pedestrians_killed'].iloc[0])
    ax.text(year, val + 1, str(val), ha='center', va='bottom', fontsize=9, color=navy, fontweight='bold')
fig.text(.01,.01,'Source: NYC police-reported motor vehicle crashes. Annual counts; not adjusted for pedestrian activity.', color=gray, fontsize=9)
fig.tight_layout(rect=(0,.05,1,1)); fig.savefig('out/option_2.png', dpi=180, bbox_inches='tight'); plt.close(fig)

# Option 3: fatal share among reported pedestrian casualties
cols = ['year','pedestrians_injured','pedestrians_killed','pedestrian_casualties','fatal_share_pct']
df[cols].to_csv('out/values_3.csv', index=False, float_format='%.4f')
fig, ax = plt.subplots(figsize=(10,5.8))
ax.plot(df.year, df.fatal_share_pct, color=navy, linewidth=2.7, marker='o', markersize=5)
ax.set(title='Fatalities made up a larger share of Brooklyn pedestrian casualties',
       ylabel='Pedestrians killed as % of injured + killed', xlabel='Calendar year')
ax.set_xticks(df.year); ax.grid(axis='y', color='#D9E0E7', linewidth=.8); ax.set_axisbelow(True)
start, end = float(df.iloc[0].fatal_share_pct), float(df.iloc[-1].fatal_share_pct)
ax.annotate(f'{start:.2f}%', (2013,start), xytext=(5,9), textcoords='offset points', color=navy, fontweight='bold')
ax.annotate(f'{end:.2f}%', (2025,end), xytext=(-5,9), textcoords='offset points', ha='right', color=navy, fontweight='bold')
fig.text(.01,.01,'Denominator: all reported Brooklyn pedestrian injuries plus deaths. Not an exposure-adjusted fatality risk.', color=gray, fontsize=9)
fig.tight_layout(rect=(0,.05,1,1)); fig.savefig('out/option_3.png', dpi=180, bbox_inches='tight'); plt.close(fig)

cas_start, cas_end = int(df.iloc[0].pedestrian_casualties), int(df.iloc[-1].pedestrian_casualties)
injury_start, injury_end = int(df.iloc[0].pedestrians_injured), int(df.iloc[-1].pedestrians_injured)
death_start, death_end = int(df.iloc[0].pedestrians_killed), int(df.iloc[-1].pedestrians_killed)
share_start, share_end = float(df.iloc[0].fatal_share_pct), float(df.iloc[-1].fatal_share_pct)
cas_pct = (cas_end/cas_start-1)*100
death_pct = (death_end/death_start-1)*100
change_pp = share_end-share_start
options = {'options': [
    {'id':1, 'metric':'Annual pedestrian casualties (injured + killed)', 'denominator':'None; annual total count', 'grouping':'Calendar year, Brooklyn', 'chart_type':'Line chart',
     'reason':'Combining injuries and deaths captures the overall annual burden of pedestrian harm in one directly interpretable measure.',
     'probability':0.55,
     'answer':f'Brooklyn recorded {cas_end:,} pedestrian casualties in 2025, {abs(cas_pct):.1f}% fewer than {cas_start:,} in 2013, although the total has risen from its 2020 low of {int(df.loc[df.year==2020,"pedestrian_casualties"].iloc[0]):,}.',
     'interpretation':'This addresses whether the total number of pedestrians harmed in reported Brooklyn crashes is lower than in 2013: it is, but the series has risen substantially since 2020. Annual counts are a defensible measure of the burden of harm; without pedestrian-trip or population exposure, they do not establish that an individual pedestrian’s risk fell.'},
    {'id':2, 'metric':'Pedestrians killed', 'denominator':'None; annual total count', 'grouping':'Calendar year, Brooklyn', 'chart_type':'Bar chart',
     'reason':'Deaths are the most severe pedestrian outcome and should be visible separately from nonfatal injuries.',
     'probability':0.32,
     'answer':f'Brooklyn recorded {death_end} pedestrian deaths in 2025, {death_pct:.0f}% more than the {death_start} deaths in 2013.',
     'interpretation':'This answers the most severe part of the safety question, and the chart shows that pedestrian deaths were higher in 2025 than in 2013, despite fluctuations between years. Death counts are an important direct outcome, but do not describe nonfatal harm or exposure-adjusted risk.'},
    {'id':3, 'metric':'Fatal share of pedestrian casualties (deaths / [injuries + deaths])', 'denominator':'All reported Brooklyn pedestrian injuries plus deaths in that year', 'grouping':'Calendar year, Brooklyn', 'chart_type':'Line chart',
     'reason':'The fatal share compares severity within the reported pedestrian casualty total while accounting for its changing size.',
     'probability':0.13,
     'answer':f'Deaths were {share_end:.2f}% of Brooklyn pedestrian casualties in 2025, up from {share_start:.2f}% in 2013 (a rise of {change_pp:.2f} percentage points).',
     'interpretation':'This addresses whether outcomes among reported pedestrian casualties became less severe: the fatal share was higher in 2025 than in 2013. It is a defensible severity measure because its denominator is all injured and killed pedestrians, but it says nothing about pedestrians who were not in crashes and therefore is not a measure of overall pedestrian risk.'}
]}
with open('out/options.json','w') as f:
    json.dump(options,f,indent=2,ensure_ascii=False)
    f.write('\n')
print(df.to_string(index=False))
print(json.dumps(options, indent=2))
PY
# bash
python3 - <<'PY'
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('out/values_1.csv')
blue, navy, gray = '#277DA1', '#17324D', '#64748B'
fig, ax = plt.subplots(figsize=(10,5.8))
ax.plot(df.year, df.pedestrian_casualties, color=blue, linewidth=3, marker='o', markersize=5)
ax.fill_between(df.year, df.pedestrian_casualties, color=blue, alpha=.10)
ax.set(title='Brooklyn pedestrian casualties fell from 2013, then climbed',
       ylabel='Number of pedestrians injured or killed', xlabel='Calendar year')
ax.set_xticks(df.year); ax.grid(axis='y', color='#D9E0E7', linewidth=.8); ax.set_axisbelow(True)
for year, offset, align in [(2013,(5,10),'left'),(2025,(-5,10),'right')]:
    val = int(df.loc[df.year == year, 'pedestrian_casualties'].iloc[0])
    ax.annotate(f'{val:,}', (year,val), xytext=offset, textcoords='offset points', ha=align, color=navy, fontweight='bold')
fig.text(.01,.01,'Source: NYC police-reported motor vehicle crashes. Annual counts; not adjusted for pedestrian activity.', color=gray, fontsize=9)
fig.tight_layout(rect=(0,.05,1,1)); fig.savefig('out/option_1.png', dpi=180, bbox_inches='tight'); plt.close(fig)
PY
# bash
python3 -c "import json,os,pandas as pd; o=json.load(open('out/options.json')); print('valid json; probability sum=',sum(x['probability'] for x in o['options'])); print('outputs=',sorted(os.listdir('out'))); print('2025 values=',[pd.read_csv(f'out/values_{i}.csv').iloc[-1].to_dict() for i in range(1,4)])"

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
- tr_TR01: If a per-crash rate spanning 2020 is shown, the output caveats the 2020 change in crash recording.
- tr_TR15: Claims about pedestrian deaths changing are qualified by the small counts (about 30–39 per year).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.