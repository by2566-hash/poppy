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

QUESTION ASKED: What was the distribution of NYC crashes by day of the week over the period 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Number of police-reported crash records
denominator: None; raw crash-record counts
grouping: Day of week, across dates from 2013-01-01 through 2025-12-31
chart_type: Bar chart
probability: 0.4
WRITTEN ANSWER:
Friday had the most recorded crashes (338,800), while Sunday had the fewest (257,544). This framing answers the absolute-count part of the weekday distribution question, and the chart shows that Friday has the highest count and Sunday the lowest. It is defensible when the goal is to compare total recorded crash volume, but it does not express each weekday's share of all crashes or crash risk relative to traffic exposure.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
weekday,crashes
Monday,304518
Tuesday,313488
Wednesday,311111
Thursday,318376
Friday,338800
Saturday,288381
Sunday,257544

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c "import duckdb, pandas, matplotlib; print('duckdb', duckdb.__version__, 'pandas', pandas.__version__, 'matplotlib', matplotlib.__version__)"
# bash
python -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(f\"SELECT COUNT(*) AS rows, MIN(crash_date), MAX(crash_date), COUNT(*) FILTER (WHERE crash_date IS NULL) AS null_dates FROM read_parquet('{p}')\").fetchdf().to_string(index=False)); print(c.execute(f\"SELECT EXTRACT(YEAR FROM crash_date) AS year, COUNT(*) AS crashes FROM read_parquet('{p}') GROUP BY 1 ORDER BY 1\").fetchdf().to_string(index=False))"
# bash
ls
# bash
python -c "exec('''import duckdb, pandas as pd, matplotlib.pyplot as plt\nfrom pathlib import Path\nout=Path('out'); out.mkdir(exist_ok=True)\ncon=duckdb.connect()\nquery=\\\"\\\"\\\"SELECT CASE strftime(crash_date, '%w') WHEN '0' THEN 'Sunday' WHEN '1' THEN 'Monday' WHEN '2' THEN 'Tuesday' WHEN '3' THEN 'Wednesday' WHEN '4' THEN 'Thursday' WHEN '5' THEN 'Friday' WHEN '6' THEN 'Saturday' END AS weekday, COUNT(*) AS crashes FROM read_parquet('data/crashes.parquet') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY CASE weekday WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3 WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6 WHEN 'Sunday' THEN 7 END\\\"\\\"\\\"\ndf=con.execute(query).fetchdf()\ndf['share_pct']=df['crashes']/df['crashes'].sum()*100\ndf[['weekday','crashes']].to_csv(out/'values_1.csv',index=False)\ndf[['weekday','crashes','share_pct']].to_csv(out/'values_2.csv',index=False,float_format='%.6f')\nplt.figure(figsize=(9,5.3)); bars=plt.bar(df.weekday,df.crashes,color='#3478a8'); plt.bar_label(bars,labels=[f'{v:,.0f}' for v in df.crashes],padding=3,fontsize=8); plt.title('NYC police-reported crashes by weekday (2013–2025)'); plt.ylabel('Crash records'); plt.xlabel('Day of week'); plt.ylim(0,df.crashes.max()*1.12); plt.grid(axis='y',alpha=.2); plt.tight_layout(); plt.savefig(out/'option_1.png',dpi=180); plt.close()\nplt.figure(figsize=(9,5.3)); bars=plt.bar(df.weekday,df.share_pct,color='#e18c3a'); plt.bar_label(bars,labels=[f'{v:.1f}%' for v in df.share_pct],padding=3,fontsize=8); plt.title('Share of NYC police-reported crashes by weekday (2013–2025)'); plt.ylabel('Share of crashes'); plt.xlabel('Day of week'); plt.ylim(0,df.share_pct.max()*1.15); plt.grid(axis='y',alpha=.2); plt.tight_layout(); plt.savefig(out/'option_2.png',dpi=180); plt.close()\nprint(df.to_string(index=False)); print('TOTAL',int(df.crashes.sum()))\n''')"
# bash
python -c "import json, pathlib, pandas as pd; p=pathlib.Path('out'); o=json.loads((p/'options.json').read_text()); print('options',len(o['options']),'probability_sum',sum(x['probability'] for x in o['options'])); a=pd.read_csv(p/'values_1.csv'); b=pd.read_csv(p/'values_2.csv'); print('count_sum',a.crashes.sum(),'pct_sum',b.share_pct.sum()); print('assets',[(f.name,f.stat().st_size) for f in sorted(p.iterdir())])"

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_DAYCOUNT: If per-day averages or 'X% fewer on <day>' comparisons are given, the arithmetic is right (e.g. Sunday has 24% fewer than the mean weekday, Friday 32% more) and unequal day counts (678/679) are handled or noted.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.