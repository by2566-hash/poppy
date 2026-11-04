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
- crash_time has no NULL rows. Reported crash counts fall sharply in 2020 (TR01): a per-reported-crash rate or a pooled count COMPARED ACROSS YEARS spanning 2020 needs a caveat; a comparison between groups within one pooled window (e.g. day vs night) does not (decided 2026-11-04).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: How are NYC crashes distributed across the days of the week, 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Mean crash records per calendar date
denominator: Calendar dates of each weekday from 2013-01-01 through 2025-12-31 (678 or 679 dates, depending on weekday)
grouping: Day of week
chart_type: Vertical bar chart of mean crashes per weekday date
probability: 0.4
WRITTEN ANSWER:
Friday averaged 499.7 crashes per Friday, the highest daily average, while Sunday averaged 379.9 per Sunday, the lowest. This framing answers how the typical calendar date's crash volume varies by weekday, again showing Friday highest and Sunday lowest. Averaging by the number of dates is defensible because weekdays occur 678 or 679 times in this interval. It does not show each weekday's cumulative share of all crashes.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
weekday,weekday_dates,crash_count,avg_crashes_per_weekday_date
Monday,678,304518,449.141593
Tuesday,679,313488,461.690722
Wednesday,679,311111,458.189985
Thursday,678,318376,469.581121
Friday,678,338800,499.705015
Saturday,678,288381,425.340708
Sunday,678,257544,379.858407

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c "import duckdb; con=duckdb.connect(); p='data/crashes.parquet'; print(con.execute('DESCRIBE SELECT * FROM read_parquet(?)',[p]).fetchall()); print(con.execute('SELECT COUNT(*), MIN(crash_date), MAX(crash_date), COUNT(*) FILTER (WHERE crash_date IS NULL) FROM read_parquet(?)',[p]).fetchall())"
# bash
ls
# bash
python -c "import duckdb; c=duckdb.connect(); print(c.execute(\"SELECT year(crash_date), count(*), min(crash_date), max(crash_date) FROM read_parquet('data/crashes.parquet') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1\").fetchall()); print(c.execute(\"SELECT dayname(crash_date), count(*) FROM read_parquet('data/crashes.parquet') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY min(isodow(crash_date))\").fetchall())"
# bash
python -c "exec(\"import duckdb, pandas as pd, matplotlib.pyplot as plt, calendar, datetime, os\\nfrom matplotlib.ticker import FuncFormatter\\np='data/crashes.parquet'; out='out'; os.makedirs(out, exist_ok=True)\\norder=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']\\ncon=duckdb.connect()\\ndf=con.execute(\\\"SELECT dayname(crash_date) AS weekday, COUNT(*) AS crash_count FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY weekday\\\", [p]).df()\\nstart=datetime.date(2013,1,1); end=datetime.date(2025,12,31); days=pd.date_range(start,end,freq='D')\\nocc=pd.Series(days.day_name()).value_counts()\\ndf=df.set_index('weekday').reindex(order).reset_index()\\ndf['weekday_dates']=df['weekday'].map(occ).astype(int)\\ndf['share_of_crashes_pct']=df.crash_count/df.crash_count.sum()*100\\ndf['avg_crashes_per_weekday_date']=df.crash_count/df.weekday_dates\\ndf.to_csv(out+'/values_1.csv', index=False, float_format='%.6f')\\nfig,ax=plt.subplots(figsize=(10,5.5)); bars=ax.bar(df.weekday,df.crash_count,color='#3977a8'); ax.set_title('NYC police-reported crashes by weekday, 2013–2025'); ax.set_ylabel('Crash records'); ax.set_xlabel('Day of week'); ax.yaxis.set_major_formatter(FuncFormatter(lambda x,pos: f'{x:,.0f}')); ax.grid(axis='y',alpha=.25); ax.bar_label(bars,labels=[f'{x:,.0f}' for x in df.crash_count],padding=3,fontsize=8); fig.tight_layout(); fig.savefig(out+'/option_1.png',dpi=160); plt.close(fig)\\ndf[['weekday','weekday_dates','crash_count','avg_crashes_per_weekday_date']].to_csv(out+'/values_2.csv',index=False,float_format='%.6f')\\nfig,ax=plt.subplots(figsize=(10,5.5)); bars=ax.bar(df.weekday,df.avg_crashes_per_weekday_date,color='#d17b32'); ax.set_title('Average NYC crashes per calendar weekday, 2013–2025'); ax.set_ylabel('Average crash records per date'); ax.set_xlabel('Day of week'); ax.yaxis.set_major_formatter(FuncFormatter(lambda x,pos: f'{x:,.1f}')); ax.grid(axis='y',alpha=.25); ax.bar_label(bars,labels=[f'{x:,.1f}' for x in df.avg_crashes_per_weekday_date],padding=3,fontsize=8); fig.tight_layout(); fig.savefig(out+'/option_2.png',dpi=160); plt.close(fig)\\nprint(df.to_string(index=False)); print('TOTAL',int(df.crash_count.sum()),'CALENDAR_DATES',len(days))\")"
# bash
python -c "import json, pandas as pd; x=json.load(open('out/options.json')); print('options',len(x['options']),'probability_sum',sum(o['probability'] for o in x['options'])); a=pd.read_csv('out/values_1.csv'); b=pd.read_csv('out/values_2.csv'); print('count_total',a.crash_count.sum(),'share_total',a.share_of_crashes_pct.sum()); print('count_max',a.loc[a.crash_count.idxmax(),['weekday','crash_count']].to_dict(),'count_min',a.loc[a.crash_count.idxmin(),['weekday','crash_count']].to_dict()); print('average_max',b.loc[b.avg_crashes_per_weekday_date.idxmax(),['weekday','avg_crashes_per_weekday_date']].to_dict(),'average_min',b.loc[b.avg_crashes_per_weekday_date.idxmin(),['weekday','avg_crashes_per_weekday_date']].to_dict())"

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