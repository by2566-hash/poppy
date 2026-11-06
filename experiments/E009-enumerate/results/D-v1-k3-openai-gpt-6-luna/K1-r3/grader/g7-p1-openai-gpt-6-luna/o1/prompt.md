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
- Qualifications (reported, recorded in this dataset) count when they are in the WRITTEN ANSWER or the DECLARED FRAMING; text
  that appears only inside the chart image (title, footnote, source note) does not satisfy an item on its own. The official-count
  part of unsupported_claim follows the same test as TR07.

DATA FACTS (pinned snapshot):
- The file covers 2012-07-01 to 2026-06-11; 2013-2025 are complete calendar years; 2026 is partial (to June 11).
- borough is NULL for about 20-38% of crashes in every year (TR05): a borough filter silently drops them.
- number_of_persons_killed is NULL in most May-2026 and all June-2026 rows (TR08); 2013-2025 killed counts have no NULLs.
- crash_time has no NULL rows. Reported crash counts (the number of crash records) fall sharply in 2020 (TR01), so a per-reported-crash rate (deaths or injuries divided by reported crashes) compared across years spanning 2020 needs a caveat. Counts of deaths or injuries by year do NOT need it (they are not affected by the reporting change), and a comparison between groups within one pooled window (e.g. day vs night) does not either (decided 2026-11-04; g5 wording after g4 failed c6 on plain death counts).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: How many pedestrians were killed in NYC motor vehicle crashes each year from 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Annual number of pedestrians killed
denominator: None; count of recorded pedestrian deaths
grouping: Crash year (2013–2025)
chart_type: Bar chart
probability: 0.55
WRITTEN ANSWER:
Pedestrians killed by year were 176 (2013), 133 (2014), 133 (2015), 149 (2016), 127 (2017), 123 (2018), 131 (2019), 101 (2020), 132 (2021), 135 (2022), 107 (2023), 124 (2024), and 119 (2025).

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,pedestrian_deaths
2013,176
2014,133
2015,133
2016,149
2017,127
2018,123
2019,131
2020,101
2021,132
2022,135
2023,107
2024,124
2025,119

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python3 -c 'import duckdb, pandas, matplotlib; print("duckdb", duckdb.__version__)'
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("SELECT min(crash_date), max(crash_date), count(*) FROM read_parquet(?)", [p]).fetchall()); print(c.execute("SELECT year(crash_date) AS year, sum(coalesce(number_of_pedestrians_killed,0)) AS pedestrian_deaths, sum(coalesce(number_of_persons_killed,0)) AS all_person_deaths FROM read_parquet(?) WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY 1 ORDER BY 1", [p]).df().to_string(index=False)); print(c.execute("SELECT coalesce(nullif(trim(borough), \'\'), \'Unknown\') borough, count(*) FROM read_parquet(?) GROUP BY 1 ORDER BY 2 DESC", [p]).df().to_string(index=False))'
# bash
python3 -c "import duckdb; c=duckdb.connect(); print(c.execute('SELECT min(crash_date), max(crash_date), count(*) FROM read_parquet(\'data/crashes.parquet\')').fetchall()); print(c.execute('SELECT year(crash_date) AS year, sum(coalesce(number_of_pedestrians_killed,0)) pedestrian_deaths, sum(coalesce(number_of_persons_killed,0)) all_person_deaths FROM read_parquet(\'data/crashes.parquet\') WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY 1 ORDER BY 1').df().to_string(index=False))"
# bash
python3 -c "import duckdb; c=duckdb.connect(); print(c.execute(\"SELECT coalesce(nullif(trim(borough), ''), 'Unknown') AS borough, sum(coalesce(number_of_pedestrians_killed,0)) AS deaths FROM read_parquet('data/crashes.parquet') WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY 1 ORDER BY 2 DESC\").df().to_string(index=False)); print(c.execute(\"SELECT count(*) FROM read_parquet('data/crashes.parquet') WHERE year(crash_date) BETWEEN 2013 AND 2025 AND number_of_pedestrians_killed IS NULL\").fetchone())"
# bash
python3 -c "exec(\"import duckdb, pandas as pd, matplotlib.pyplot as plt\\nfrom pathlib import Path\\nPath('out').mkdir(exist_ok=True)\\ndb=duckdb.connect()\\nsource='data/crashes.parquet'\\nannual=db.execute(\\\"SELECT year(crash_date) AS year, sum(number_of_pedestrians_killed)::BIGINT AS pedestrian_deaths, sum(number_of_persons_killed)::BIGINT AS all_person_deaths FROM read_parquet(?) WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY 1 ORDER BY 1\\\", [source]).df()\\nyears=pd.DataFrame({'year': range(2013,2026)})\\nannual=years.merge(annual,on='year',how='left').fillna(0)\\nannual[['year','pedestrian_deaths','all_person_deaths']]=annual[['year','pedestrian_deaths','all_person_deaths']].astype(int)\\nannual['pedestrian_share_of_all_deaths_pct']=100*annual.pedestrian_deaths/annual.all_person_deaths\\nannual[['year','pedestrian_deaths']].to_csv('out/values_1.csv',index=False)\\nfig,ax=plt.subplots(figsize=(10,5.5))\\nbars=ax.bar(annual.year,annual.pedestrian_deaths,color='#286b9e',width=.72)\\nax.bar_label(bars,padding=3,fontsize=9)\\nax.set(title='Pedestrians killed in NYC motor vehicle crashes, 2013–2025',xlabel='Crash year',ylabel='Pedestrians killed')\\nax.set_xticks(annual.year); ax.set_ylim(0, max(annual.pedestrian_deaths)*1.16); ax.grid(axis='y',alpha=.25); fig.tight_layout(); fig.savefig('out/option_1.png',dpi=160); plt.close(fig)\\nannual[['year','pedestrian_deaths','all_person_deaths','pedestrian_share_of_all_deaths_pct']].to_csv('out/values_2.csv',index=False,float_format='%.2f')\\nfig,ax=plt.subplots(figsize=(10,5.5))\\nax.plot(annual.year,annual.pedestrian_share_of_all_deaths_pct,marker='o',linewidth=2.2,color='#b45137')\\nfor x,y in zip(annual.year,annual.pedestrian_share_of_all_deaths_pct): ax.annotate(f'{y:.1f}%',(x,y),xytext=(0,8),textcoords='offset points',ha='center',fontsize=8)\\nax.set(title='Pedestrians’ share of all people killed in NYC crashes, 2013–2025',xlabel='Crash year',ylabel='Pedestrian deaths / all recorded deaths (%)')\\nax.set_xticks(annual.year); ax.set_ylim(0,max(annual.pedestrian_share_of_all_deaths_pct)*1.2); ax.grid(axis='y',alpha=.25); fig.tight_layout(); fig.savefig('out/option_2.png',dpi=160); plt.close(fig)\\nby_borough=db.execute(\\\"SELECT year(crash_date) AS year, coalesce(nullif(trim(borough), ''), 'Unknown') AS borough, sum(number_of_pedestrians_killed)::BIGINT AS pedestrian_deaths FROM read_parquet(?) WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY 1,2 ORDER BY 1,2\\\", [source]).df()\\nall_years=pd.MultiIndex.from_product([range(2013,2026),sorted(by_borough.borough.unique())],names=['year','borough']).to_frame(index=False)\\nby_borough=all_years.merge(by_borough,on=['year','borough'],how='left').fillna({'pedestrian_deaths':0})\\nby_borough['pedestrian_deaths']=by_borough.pedestrian_deaths.astype(int)\\nby_borough.to_csv('out/values_3.csv',index=False)\\nwide=by_borough.pivot(index='year',columns='borough',values='pedestrian_deaths')\\norder=['MANHATTAN','BROOKLYN','QUEENS','BRONX','STATEN ISLAND','Unknown']\\nwide=wide[[b for b in order if b in wide.columns]]\\ncolors=['#286b9e','#e08a39','#72a66a','#bb6573','#8b76ab','#aaaaaa']\\nfig,ax=plt.subplots(figsize=(11,6))\\nwide.plot(kind='bar',stacked=True,ax=ax,color=colors[:len(wide.columns)],width=.8)\\nax.set(title='Pedestrians killed by recorded borough in NYC crashes, 2013–2025',xlabel='Crash year',ylabel='Pedestrians killed')\\nax.legend(title='Borough',ncol=3,loc='upper center',bbox_to_anchor=(.5,-.12),frameon=False)\\nax.grid(axis='y',alpha=.2); ax.set_axisbelow(True); fig.tight_layout(); fig.savefig('out/option_3.png',dpi=160,bbox_inches='tight'); plt.close(fig)\\nprint(annual.to_string(index=False)); print('borough totals\\\\n',by_borough.groupby('borough').pedestrian_deaths.sum().sort_values(ascending=False).to_string())\\n\")"
# bash
python3 -c "import json, pathlib, pandas as pd; d=json.loads(pathlib.Path('out/options.json').read_text()); assert len(d['options'])==3; assert abs(sum(o['probability'] for o in d['options'])-1)<1e-9; a=pd.read_csv('out/values_1.csv'); b=pd.read_csv('out/values_3.csv'); assert a.pedestrian_deaths.tolist()==b.groupby('year').pedestrian_deaths.sum().reindex(a.year).tolist(); print('JSON valid; probabilities sum to',sum(o['probability'] for o in d['options'])); print('Charts/values present:', all(pathlib.Path(f'out/{name}').exists() for name in ['option_1.png','option_2.png','option_3.png','values_1.csv','values_2.csv','values_3.csv','options.json']))"

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR07: The output does not present the open-data death counts as the official NYC toll. The written output (answer, interpretation or declared framing fields) must say the counts are reported or recorded in this dataset; a qualification or source note that appears only inside the chart image does not count, and a chart title without it is fine when the written output has it. Counts called 'NYC totals' or 'killed in NYC' with no such qualification in the written output FAIL (Bo 2026-11-04, refined 2026-11-06).
- tr_CAUSAL: The output makes no causal attribution (e.g. 'because of the pandemic') that the data cannot support.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.