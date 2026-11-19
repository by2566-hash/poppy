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

QUESTION ASKED: How are NYC crashes distributed across the days of the week, 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Total police-reported crashes
denominator: All 2,132,218 crashes in 2013–2025 for the reported weekday shares
grouping: Weekday, Monday through Sunday
chart_type: Bar chart
probability: 0.6
WRITTEN ANSWER:
Friday had the most crashes (338,800; 15.89% of all crashes), while Sunday had the fewest (257,544; 12.08%). This answers how the full-period crash total is distributed by weekday: Friday is highest and Sunday lowest. Totals give the cumulative burden, but do not show the average for a single weekday date or explain why the pattern occurs.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
weekday,crash_count,crash_share_percent,calendar_dates,avg_crashes_per_date
Monday,304518,14.28,678,449.14
Tuesday,313488,14.70,679,461.69
Wednesday,311111,14.59,679,458.19
Thursday,318376,14.93,678,469.58
Friday,338800,15.89,678,499.71
Saturday,288381,13.52,678,425.34
Sunday,257544,12.08,678,379.86

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
ls
# bash
ls
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; print(duckdb.query(f"select count(*) n, min(crash_date) first_date, max(crash_date) last_date, count(*) filter (where crash_date between date '\''2013-01-01'\'' and date '\''2025-12-31'\'') in_period from read_parquet('\''{p}'\'')").df().to_string(index=False)); print(duckdb.query(f"describe select * from read_parquet('\''{p}'\'')").df().to_string(index=False))'
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; q=f"""with d as (select crash_date, extract(isodow from crash_date)::int iso_dow, count(*) crashes from read_parquet(\047{p}\047) where crash_date between date \0472013-01-01\047 and date \0472025-12-31\047 group by crash_date) select extract(year from crash_date)::int year, min(crash_date) first_crash_date, max(crash_date) last_crash_date, count(*) days_with_crashes, sum(crashes) crashes from d group by year order by year"""; print(duckdb.query(q).df().to_string(index=False)); q=f"""with d as (select crash_date, extract(isodow from crash_date)::int iso_dow from read_parquet(\047{p}\047) where crash_date between date \0472013-01-01\047 and date \0472025-12-31\047) select iso_dow, count(*) crashes, count(distinct crash_date) days_with_crashes from d group by iso_dow order by iso_dow"""; print(duckdb.query(q).df().to_string(index=False))'
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; q=f"""with d as (select crash_date, extract(isodow from crash_date)::int iso_dow, count(*) crashes from read_parquet(\047{p}\047) where crash_date between date \0472013-01-01\047 and date \0472025-12-31\047 group by crash_date) select extract(year from crash_date)::int calendar_year, min(crash_date) first_crash_date, max(crash_date) last_crash_date, count(*) days_with_crashes, sum(crashes) crashes from d group by calendar_year order by calendar_year"""; print(duckdb.query(q).df().to_string(index=False)); q=f"""with d as (select crash_date, extract(isodow from crash_date)::int iso_dow from read_parquet(\047{p}\047) where crash_date between date \0472013-01-01\047 and date \0472025-12-31\047) select iso_dow, count(*) crashes, count(distinct crash_date) days_with_crashes from d group by iso_dow order by iso_dow"""; print(duckdb.query(q).df().to_string(index=False))'
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; q=f"""with weekdays as (select * from (values (1,\047Monday\047),(2,\047Tuesday\047),(3,\047Wednesday\047),(4,\047Thursday\047),(5,\047Friday\047),(6,\047Saturday\047),(7,\047Sunday\047)) w(iso_dow, weekday)), cal as (select extract(isodow from d)::int iso_dow, count(*) days from generate_series(date \0472013-01-01\047,date \0472025-12-31\047,interval \0471 day\047) x(d) group by 1), crashes as (select extract(isodow from crash_date)::int iso_dow, count(*) crash_count from read_parquet(\047{p}\047) where crash_date between date \0472013-01-01\047 and date \0472025-12-31\047 group by 1) select weekday, crashes.crash_count, cal.days, round(crashes.crash_count::double / sum(crashes.crash_count) over ()*100, 3) share_pct, round(crashes.crash_count::double/cal.days, 2) avg_per_calendar_day from weekdays join cal using(iso_dow) join crashes using(iso_dow) order by iso_dow"""; print(duckdb.query(q).df().to_string(index=False))'
# bash
python3 -c 'import duckdb, pandas as pd; p="data/crashes.parquet"; d=duckdb.query(f"select extract(isodow from crash_date)::int iso_dow, count(*) crash_count from read_parquet(\047{p}\047) where crash_date between date \0472013-01-01\047 and date \0472025-12-31\047 group by 1 order by 1").df(); dates=pd.date_range("2013-01-01","2025-12-31"); n=dates.dayofweek.value_counts().sort_index(); d["weekday"]=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]; d["calendar_dates"]=n.values; d["share_pct"]=(d.crash_count/d.crash_count.sum()*100).round(3); d["avg_crashes_per_date"]=(d.crash_count/d.calendar_dates).round(2); print(d.to_string(index=False)); print("total",d.crash_count.sum())'
# bash
python3 -c 'import duckdb, pandas as pd, matplotlib.pyplot as plt, os; p="data/crashes.parquet"; os.makedirs("out", exist_ok=True); d=duckdb.query(f"select extract(isodow from crash_date)::int iso_dow, count(*) crash_count from read_parquet(\047{p}\047) where crash_date between date \0472013-01-01\047 and date \0472025-12-31\047 group by 1 order by 1").df(); weekdays=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]; d["weekday"]=[weekdays[i-1] for i in d.iso_dow]; d["calendar_dates"]=pd.date_range("2013-01-01","2025-12-31").dayofweek.value_counts().sort_index().values; d["crash_share_percent"]=d.crash_count/d.crash_count.sum()*100; d["avg_crashes_per_date"]=d.crash_count/d.calendar_dates; d=d[["weekday","crash_count","crash_share_percent","calendar_dates","avg_crashes_per_date"]]; d.to_csv("out/values_1.csv",index=False,float_format="%.2f"); d.to_csv("out/values_2.csv",index=False,float_format="%.2f"); plt.figure(figsize=(9,5.2)); bars=plt.bar(d.weekday,d.crash_count,color="#377eb8"); plt.title("NYC police-reported crashes by weekday, 2013–2025"); plt.ylabel("Crashes (count)"); plt.xlabel("Day of week"); plt.grid(axis="y",alpha=.25); plt.gca().set_axisbelow(True); plt.bar_label(bars,labels=[f"{x:,.0f}" for x in d.crash_count],padding=3,fontsize=8); plt.ylim(0,d.crash_count.max()*1.13); plt.tight_layout(); plt.savefig("out/option_1.png",dpi=180); plt.close(); plt.figure(figsize=(9,5.2)); bars=plt.bar(d.weekday,d.avg_crashes_per_date,color="#4daf4a"); plt.title("Average NYC crashes per calendar date, by weekday, 2013–2025"); plt.ylabel("Average crashes per date"); plt.xlabel("Day of week"); plt.grid(axis="y",alpha=.25); plt.gca().set_axisbelow(True); plt.bar_label(bars,labels=[f"{x:.1f}" for x in d.avg_crashes_per_date],padding=3,fontsize=8); plt.ylim(0,d.avg_crashes_per_date.max()*1.13); plt.tight_layout(); plt.savefig("out/option_2.png",dpi=180); plt.close(); print(d.to_string(index=False)); print("written charts and CSVs")'
# bash
python3 -c 'import json, pandas as pd, os; opts=json.load(open("out/options.json"))["options"]; assert len(opts)==2 and abs(sum(x["probability"] for x in opts)-1)<1e-9; a=pd.read_csv("out/values_1.csv"); b=pd.read_csv("out/values_2.csv"); assert a.loc[a.crash_count.idxmax(),"weekday"]=="Friday" and a.loc[a.crash_count.idxmin(),"weekday"]=="Sunday"; assert b.loc[b.avg_crashes_per_date.idxmax(),"weekday"]=="Friday" and b.loc[b.avg_crashes_per_date.idxmin(),"weekday"]=="Sunday"; assert int(a.crash_count.sum())==2132218; assert all(os.path.exists(f"out/{f}") for f in ["option_1.png","option_2.png","values_1.csv","values_2.csv","options.json"]); print("Valid JSON; both chart/data options agree; counts sum to 2,132,218; all outputs present.")'

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