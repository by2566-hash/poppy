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

QUESTION ASKED: How do motorist and cyclist deaths compare year by year in NYC, 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Annual sum of motorist deaths and annual sum of cyclist deaths
denominator: None; raw annual death counts
grouping: Calendar year (2013–2025), by road-user type
chart_type: Grouped bar chart
probability: 0.65
WRITTEN ANSWER:
Motorist deaths exceeded cyclist deaths in every year; motorist deaths peaked at 139 in 2020, while cyclist deaths peaked at 31 in both 2019 and 2023. This answers the year-by-year comparison in absolute numbers: motorist deaths were higher each year, with the peaks shown in the answer. Raw counts are defensible because they show the annual fatality totals directly. It does not express cyclist deaths relative to the motorist total or estimate risk per traveler, for which exposure data are unavailable here. The date filter uses only 2013–2025; none of those rows are omitted for NULL death counts (0% in each year), and none of the included years is partial; records outside 2013–2025 are outside the requested period.

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
python3 -c "import duckdb, pandas, matplotlib; print('duckdb', duckdb.__version__, 'pandas', pandas.__version__, 'matplotlib', matplotlib.__version__)"
# bash
ls
# bash
python3 -c "import duckdb; c=duckdb.connect(); print(c.execute(\"SELECT year(crash_date) AS year, count(*) AS crashes, sum(number_of_motorist_killed) AS motorist_deaths, sum(number_of_cyclist_killed) AS cyclist_deaths FROM read_parquet('./data/crashes.parquet') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1\").df().to_string(index=False))"
# bash
python3 -c 'import os,json,duckdb,pandas as pd,matplotlib.pyplot as plt; from matplotlib.ticker import MaxNLocator; con=duckdb.connect(); df=con.execute("SELECT year(crash_date) AS year, count(*) AS crash_rows, sum(number_of_motorist_killed) AS motorist_deaths, sum(number_of_cyclist_killed) AS cyclist_deaths, count(*) FILTER (WHERE number_of_motorist_killed IS NULL OR number_of_cyclist_killed IS NULL) AS rows_missing_death_counts, min(crash_date) AS first_date, max(crash_date) AS last_date FROM read_parquet('./data/crashes.parquet') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1").df(); assert len(df)==13 and df.rows_missing_death_counts.sum()==0; assert all((r.first_date==pd.Timestamp(f"{int(r.year)}-01-01")) and (r.last_date==pd.Timestamp(f"{int(r.year)}-12-31")) for r in df.itertuples()); df["motorist_deaths"]=df.motorist_deaths.astype(int); df["cyclist_deaths"]=df.cyclist_deaths.astype(int); df["cyclist_per_100_motorist"]=100*df.cyclist_deaths/df.motorist_deaths; os.makedirs('./out',exist_ok=True); colors={"motorist":"#235789","cyclist":"#F29E4C"}; x=range(len(df)); w=0.38; fig,ax=plt.subplots(figsize=(12,6.5)); ax.bar([i-w/2 for i in x],df.motorist_deaths,width=w,label="Motorist deaths",color=colors["motorist"]); ax.bar([i+w/2 for i in x],df.cyclist_deaths,width=w,label="Cyclist deaths",color=colors["cyclist"]); ax.set_xticks(list(x),df.year.astype(str)); ax.set_ylabel("Deaths (annual sum)"); ax.set_xlabel("Year"); ax.set_title("Motorist and cyclist deaths in NYC, 2013–2025"); ax.yaxis.set_major_locator(MaxNLocator(integer=True)); ax.grid(axis="y",alpha=.25); ax.set_axisbelow(True); ax.legend(frameon=False,ncol=2,loc="upper right"); fig.tight_layout(); fig.savefig('./out/option_1.png',dpi=180); plt.close(fig); df[["year","motorist_deaths","cyclist_deaths"]].to_csv('./out/values_1.csv',index=False); fig,ax=plt.subplots(figsize=(12,6.5)); ax.plot(df.year,df.cyclist_per_100_motorist,color="#9C2C77",marker="o",linewidth=2.5,markersize=6); ax.set_xticks(df.year); ax.set_ylabel("Cyclist deaths per 100 motorist deaths"); ax.set_xlabel("Year"); ax.set_title("Cyclist deaths relative to motorist deaths, NYC, 2013–2025"); ax.grid(axis="y",alpha=.25); ax.set_axisbelow(True); ax.set_ylim(bottom=0); fig.tight_layout(); fig.savefig('./out/option_2.png',dpi=180); plt.close(fig); df[["year","cyclist_deaths","motorist_deaths","cyclist_per_100_motorist"]].to_csv('./out/values_2.csv',index=False,float_format="%.2f"); opts={"options":[{"id":1,"metric":"Annual sum of motorist deaths and annual sum of cyclist deaths","denominator":"None; raw annual death counts","grouping":"Calendar year (2013–2025), by road-user type","chart_type":"Grouped bar chart","reason":"Raw yearly counts directly show the difference in fatality totals between the two road-user groups.","probability":0.65,"answer":"Motorist deaths exceeded cyclist deaths in every year; motorist deaths peaked at 139 in 2020, while cyclist deaths peaked at 31 in both 2019 and 2023.","interpretation":"This answers the year-by-year comparison in absolute numbers: motorist deaths were higher each year, with the peaks shown in the answer. Raw counts are defensible because they show the annual fatality totals directly. It does not express cyclist deaths relative to the motorist total or estimate risk per traveler, for which exposure data are unavailable here. The date filter uses only 2013–2025; among those rows, 0% per year are omitted for NULL death counts and no included year is partial; records outside 2013–2025 are outside the requested period."},{"id":2,"metric":"Cyclist deaths per 100 motorist deaths","denominator":"Annual motorist deaths","grouping":"Calendar year (2013–2025)","chart_type":"Line chart","reason":"A ratio makes the cyclist-to-motorist comparison explicit even as the yearly motorist death total changes.","probability":0.35,"answer":"Cyclist deaths ranged from 9.2 per 100 motorist deaths in 2013 to a peak of 37.8 in 2019, and were 28.4 per 100 in 2025.","interpretation":"This answers how cyclist deaths compare relative to motorist deaths each year: the ratio varies, reaching its high in 2019 and remaining below 100 in every year. The denominator is defensible for comparing the relative number of these two kinds of deaths as motorist totals vary. It leaves the absolute annual death burden unanswered and is not a per-traveler risk comparison because travel exposure is not in the data. The date filter uses only 2013–2025; among those rows, 0% per year are omitted for NULL death counts and no included year is partial; records outside 2013–2025 are outside the requested period."}]}; open('./out/options.json','w').write(json.dumps(opts,indent=2)+"\n"); print(df[["year","motorist_deaths","cyclist_deaths","cyclist_per_100_motorist","rows_missing_death_counts","first_date","last_date"]].to_string(index=False)); print("saved",os.listdir('./out'))'
# bash
python3 - <<'PY'
import os, json, duckdb, pandas as pd, matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

con = duckdb.connect()
df = con.execute("""
SELECT year(crash_date) AS year,
       count(*) AS crash_rows,
       sum(number_of_motorist_killed) AS motorist_deaths,
       sum(number_of_cyclist_killed) AS cyclist_deaths,
       count(*) FILTER (WHERE number_of_motorist_killed IS NULL OR number_of_cyclist_killed IS NULL) AS rows_missing_death_counts,
       min(crash_date) AS first_date,
       max(crash_date) AS last_date
FROM read_parquet('./data/crashes.parquet')
WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
GROUP BY 1 ORDER BY 1
""").df()
assert len(df) == 13 and df.rows_missing_death_counts.sum() == 0
assert all(
    r.first_date == pd.Timestamp(f'{int(r.year)}-01-01')
    and r.last_date == pd.Timestamp(f'{int(r.year)}-12-31')
    for r in df.itertuples()
)
df['motorist_deaths'] = df.motorist_deaths.astype(int)
df['cyclist_deaths'] = df.cyclist_deaths.astype(int)
df['cyclist_per_100_motorist'] = 100 * df.cyclist_deaths / df.motorist_deaths
os.makedirs('./out', exist_ok=True)

colors = {'motorist': '#235789', 'cyclist': '#F29E4C'}
x = range(len(df))
w = 0.38
fig, ax = plt.subplots(figsize=(12, 6.5))
ax.bar([i-w/2 for i in x], df.motorist_deaths, width=w, label='Motorist deaths', color=colors['motorist'])
ax.bar([i+w/2 for i in x], df.cyclist_deaths, width=w, label='Cyclist deaths', color=colors['cyclist'])
ax.set_xticks(list(x), df.year.astype(str))
ax.set_ylabel('Deaths (annual sum)')
ax.set_xlabel('Year')
ax.set_title('Motorist and cyclist deaths in NYC, 2013–2025')
ax.yaxis.set_major_locator(MaxNLocator(integer=True))
ax.grid(axis='y', alpha=.25)
ax.set_axisbelow(True)
ax.legend(frameon=False, ncol=2, loc='upper right')
fig.tight_layout()
fig.savefig('./out/option_1.png', dpi=180)
plt.close(fig)
df[['year', 'motorist_deaths', 'cyclist_deaths']].to_csv('./out/values_1.csv', index=False)

fig, ax = plt.subplots(figsize=(12, 6.5))
ax.plot(df.year, df.cyclist_per_100_motorist, color='#9C2C77', marker='o', linewidth=2.5, markersize=6)
ax.set_xticks(df.year)
ax.set_ylabel('Cyclist deaths per 100 motorist deaths')
ax.set_xlabel('Year')
ax.set_title('Cyclist deaths relative to motorist deaths, NYC, 2013–2025')
ax.grid(axis='y', alpha=.25)
ax.set_axisbelow(True)
ax.set_ylim(bottom=0)
fig.tight_layout()
fig.savefig('./out/option_2.png', dpi=180)
plt.close(fig)
df[['year', 'cyclist_deaths', 'motorist_deaths', 'cyclist_per_100_motorist']].to_csv('./out/values_2.csv', index=False, float_format='%.2f')

opts = {'options': [
    {'id': 1, 'metric': 'Annual sum of motorist deaths and annual sum of cyclist deaths', 'denominator': 'None; raw annual death counts', 'grouping': 'Calendar year (2013–2025), by road-user type', 'chart_type': 'Grouped bar chart', 'reason': 'Raw yearly counts directly show the difference in fatality totals between the two road-user groups.', 'probability': 0.65, 'answer': 'Motorist deaths exceeded cyclist deaths in every year; motorist deaths peaked at 139 in 2020, while cyclist deaths peaked at 31 in both 2019 and 2023.', 'interpretation': 'This answers the year-by-year comparison in absolute numbers: motorist deaths were higher each year, with the peaks shown in the answer. Raw counts are defensible because they show the annual fatality totals directly. It does not express cyclist deaths relative to the motorist total or estimate risk per traveler, for which exposure data are unavailable here. The date filter uses only 2013–2025; among those rows, 0% per year are omitted for NULL death counts and no included year is partial; records outside 2013–2025 are outside the requested period.'},
    {'id': 2, 'metric': 'Cyclist deaths per 100 motorist deaths', 'denominator': 'Annual motorist deaths', 'grouping': 'Calendar year (2013–2025)', 'chart_type': 'Line chart', 'reason': 'A ratio makes the cyclist-to-motorist comparison explicit even as the yearly motorist death total changes.', 'probability': 0.35, 'answer': 'Cyclist deaths ranged from 9.2 per 100 motorist deaths in 2013 to a peak of 37.8 in 2019, and were 28.4 per 100 in 2025.', 'interpretation': 'This answers how cyclist deaths compare relative to motorist deaths each year: the ratio varies, reaching its high in 2019 and remaining below 100 in every year. The denominator is defensible for comparing the relative number of these two kinds of deaths as motorist totals vary. It leaves the absolute annual death burden unanswered and is not a per-traveler risk comparison because travel exposure is not in the data. The date filter uses only 2013–2025; among those rows, 0% per year are omitted for NULL death counts and no included year is partial; records outside 2013–2025 are outside the requested period.'}
]}
with open('./out/options.json', 'w') as f:
    json.dump(opts, f, indent=2)
    f.write('\n')
print(df[['year', 'motorist_deaths', 'cyclist_deaths', 'cyclist_per_100_motorist', 'rows_missing_death_counts', 'first_date', 'last_date']].to_string(index=False))
print('saved', sorted(os.listdir('./out')))
PY
# bash
python3 -c "import json,pandas as pd, pathlib; p=pathlib.Path('./out'); o=json.loads((p/'options.json').read_text()); a=pd.read_csv(p/'values_1.csv'); b=pd.read_csv(p/'values_2.csv'); assert len(o['options'])==2 and abs(sum(x['probability'] for x in o['options'])-1)<1e-9; assert a.motorist_deaths.gt(a.cyclist_deaths).all(); assert a.loc[a.motorist_deaths.idxmax(),'year']==2020 and a.loc[a.cyclist_deaths.idxmax(),'year'] in (2019,2023); assert round(b.cyclist_per_100_motorist.min(),1)==10.0 and b.loc[b.cyclist_per_100_motorist.idxmax(),'year']==2019; assert all((p/f'option_{i}.png').is_file() and (p/f'values_{i}.csv').is_file() for i in (1,2)); print('valid JSON; probabilities sum to',sum(x['probability'] for x in o['options'])); print('outputs:', ', '.join(sorted(x.name for x in p.iterdir())))"

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