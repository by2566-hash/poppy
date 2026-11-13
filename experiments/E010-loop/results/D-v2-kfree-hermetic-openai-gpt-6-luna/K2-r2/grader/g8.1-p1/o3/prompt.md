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
metric: Mean annual weekday share of crashes
denominator: Each calendar year's total crashes; annual weekday percentages are then averaged equally across 2013–2025
grouping: Day of week, with equal weighting of each year
chart_type: Bar chart
probability: 0.23
WRITTEN ANSWER:
Across the 13 equally weighted annual distributions, Friday accounted for the largest mean share (15.82%) and Sunday the smallest (12.33%). This framing answers which weekdays take larger or smaller shares in an average year, with Friday leading and Sunday lowest. It is defensible when the interest is the recurring weekday mix rather than pooled volume, but averaging hides how the pattern varied between individual years and gives no absolute crash totals.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
weekday,mean_annual_share_percent
Sunday,12.32589402185613
Monday,14.238355611403797
Tuesday,14.585368072312669
Wednesday,14.510417599780796
Thursday,14.836612337945578
Friday,15.824510241261372
Saturday,13.678842115439663

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
ls data out
# bash
python3 -c "import duckdb; print(duckdb.__version__)"
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(\"select count(*) total, min(crash_date), max(crash_date), count(*) filter (where crash_date is null) null_dates from read_parquet(?)\", [p]).fetchdf().to_string(index=False)); print(c.execute(\"select date_part('year',crash_date) yr,count(*) n from read_parquet(?) where crash_date between date '2013-01-01' and date '2025-12-31' group by yr order by yr\", [p]).fetchdf().to_string(index=False))"
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(\"select date_part('year',crash_date) yr,min(crash_date),max(crash_date),count(*) from read_parquet(?) where crash_date between date '2013-01-01' and date '2025-12-31' group by yr order by yr\",[p]).fetchdf().to_string(index=False)); print(c.execute(\"select dayname(crash_date) d,dayofweek(crash_date) dow,count(*) n from read_parquet(?) where crash_date >= date '2013-01-01' and crash_date < date '2026-01-01' group by 1,2 order by 2\",[p]).fetchdf().to_string(index=False))"
# bash
python3 -c 'import duckdb, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt; from pathlib import Path
p="data/crashes.parquet"; out=Path("out"); out.mkdir(exist_ok=True); con=duckdb.connect(); names=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
base="FROM read_parquet(?) WHERE crash_date >= DATE \"2013-01-01\" AND crash_date < DATE \"2026-01-01\""
counts=con.execute("SELECT dayofweek(crash_date) dow, count(*) crashes " + base + " GROUP BY dow ORDER BY dow",[p]).df(); counts["weekday"]=[names[i] for i in counts.dow]; counts=counts[["weekday","crashes"]]; counts.to_csv(out/"values_1.csv",index=False)
dates=con.execute("SELECT dayofweek(d) dow, count(*) calendar_days FROM generate_series(DATE \"2013-01-01\", DATE \"2025-12-31\", INTERVAL 1 DAY) AS t(d) GROUP BY dow ORDER BY dow").df(); daily=counts.copy(); daily["calendar_days"]=dates.calendar_days; daily["avg_crashes_per_day"]=daily.crashes/daily.calendar_days; daily.to_csv(out/"values_2.csv",index=False)
yr=con.execute("SELECT year(crash_date) year, dayofweek(crash_date) dow, count(*) crashes " + base + " GROUP BY year,dow ORDER BY year,dow",[p]).df(); yr["share_percent"]=yr.crashes/yr.groupby("year").crashes.transform("sum")*100; annual=yr.groupby("dow",as_index=False).share_percent.mean().rename(columns={"share_percent":"mean_annual_share_percent"}); annual["weekday"]=[names[i] for i in annual.dow]; annual=annual[["weekday","mean_annual_share_percent"]]; annual.to_csv(out/"values_3.csv",index=False)
series=[(counts,"crashes","Crashes","NYC motor-vehicle crashes by weekday, 2013–2025","Total police-reported crashes"),(daily,"avg_crashes_per_day","Average crashes per calendar day","NYC crashes per calendar day by weekday, 2013–2025","Mean crashes per weekday date"),(annual,"mean_annual_share_percent","Mean annual share (%)","Average yearly share of NYC crashes by weekday, 2013–2025","Mean of each year’s weekday share (%)")]
for i,(df,col,ylabel,title,foot) in enumerate(series,1):
 fig,ax=plt.subplots(figsize=(9,5.3)); bars=ax.bar(df.weekday,df[col],color="#3977a8"); ax.set_ylabel(ylabel); ax.set_title(title); ax.grid(axis="y",alpha=.25); ax.set_axisbelow(True); ax.bar_label(bars,fmt=("%.1f" if i>1 else "%.0f"),padding=3); ax.text(0,-.20,foot,transform=ax.transAxes,fontsize=9,color="#555"); fig.tight_layout(); fig.savefig(out/f"option_{i}.png",dpi=160,bbox_inches="tight"); plt.close(fig)
print("TOTAL",int(counts.crashes.sum())); print("COUNTS\n"+counts.to_string(index=False)); print("DAILY\n"+daily.to_string(index=False)); print("MEAN YEAR SHARES\n"+annual.to_string(index=False)); print("YEAR COUNT",yr.year.nunique())'
# bash
python3 -c 'import duckdb, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt; from pathlib import Path
p="data/crashes.parquet"; out=Path("out"); out.mkdir(exist_ok=True); con=duckdb.connect(); names=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
base="FROM read_parquet(?) WHERE year(crash_date) BETWEEN 2013 AND 2025"
counts=con.execute("SELECT dayofweek(crash_date) dow, count(*) crashes " + base + " GROUP BY dow ORDER BY dow",[p]).df(); counts["weekday"]=[names[i] for i in counts.dow]; counts=counts[["weekday","crashes"]]; counts.to_csv(out/"values_1.csv",index=False)
dates=con.execute("SELECT dayofweek(d) dow, count(*) calendar_days FROM generate_series(make_date(2013,1,1), make_date(2025,12,31), INTERVAL 1 DAY) AS t(d) GROUP BY dow ORDER BY dow").df(); daily=counts.copy(); daily["calendar_days"]=dates.calendar_days; daily["avg_crashes_per_day"]=daily.crashes/daily.calendar_days; daily.to_csv(out/"values_2.csv",index=False)
yr=con.execute("SELECT year(crash_date) year, dayofweek(crash_date) dow, count(*) crashes " + base + " GROUP BY year,dow ORDER BY year,dow",[p]).df(); yr["share_percent"]=yr.crashes/yr.groupby("year").crashes.transform("sum")*100; annual=yr.groupby("dow",as_index=False).share_percent.mean().rename(columns={"share_percent":"mean_annual_share_percent"}); annual["weekday"]=[names[i] for i in annual.dow]; annual=annual[["weekday","mean_annual_share_percent"]]; annual.to_csv(out/"values_3.csv",index=False)
series=[(counts,"crashes","Crashes","NYC motor-vehicle crashes by weekday, 2013–2025","Total police-reported crashes"),(daily,"avg_crashes_per_day","Average crashes per calendar day","NYC crashes per calendar day by weekday, 2013–2025","Mean crashes per weekday date"),(annual,"mean_annual_share_percent","Mean annual share (%)","Average yearly share of NYC crashes by weekday, 2013–2025","Mean of each year’s weekday share (%)")]
for i,(df,col,ylabel,title,foot) in enumerate(series,1):
 fig,ax=plt.subplots(figsize=(9,5.3)); bars=ax.bar(df.weekday,df[col],color="#3977a8"); ax.set_ylabel(ylabel); ax.set_title(title); ax.grid(axis="y",alpha=.25); ax.set_axisbelow(True); ax.bar_label(bars,fmt=("%.1f" if i>1 else "%.0f"),padding=3); ax.text(0,-.20,foot,transform=ax.transAxes,fontsize=9,color="#555"); fig.tight_layout(); fig.savefig(out/f"option_{i}.png",dpi=160,bbox_inches="tight"); plt.close(fig)
print("TOTAL",int(counts.crashes.sum())); print("COUNTS\n"+counts.to_string(index=False)); print("DAILY\n"+daily.to_string(index=False)); print("MEAN YEAR SHARES\n"+annual.to_string(index=False)); print("YEAR COUNT",yr.year.nunique())'
# bash
python3 -c 'import duckdb, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt; from pathlib import Path
p="data/crashes.parquet"; out=Path("out"); out.mkdir(exist_ok=True); con=duckdb.connect(); names=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
base="FROM read_parquet(?) WHERE year(crash_date) BETWEEN 2013 AND 2025"
counts=con.execute("SELECT dayofweek(crash_date) dow, count(*) crashes " + base + " GROUP BY dow ORDER BY dow",[p]).df(); counts["weekday"]=[names[i] for i in counts.dow]; counts=counts[["weekday","crashes"]]; counts.to_csv(out/"values_1.csv",index=False)
dates=con.execute("SELECT dayofweek(d) dow, count(*) calendar_days FROM generate_series(make_date(2013,1,1), make_date(2025,12,31), INTERVAL 1 DAY) AS t(d) GROUP BY dow ORDER BY dow").df(); daily=counts.copy(); daily["calendar_days"]=dates.calendar_days; daily["avg_crashes_per_day"]=daily.crashes/daily.calendar_days; daily.to_csv(out/"values_2.csv",index=False)
yr=con.execute("SELECT year(crash_date) yr_num, dayofweek(crash_date) dow, count(*) crashes " + base + " GROUP BY yr_num,dow ORDER BY yr_num,dow",[p]).df(); yr["share_percent"]=yr.crashes/yr.groupby("yr_num").crashes.transform("sum")*100; annual=yr.groupby("dow",as_index=False).share_percent.mean().rename(columns={"share_percent":"mean_annual_share_percent"}); annual["weekday"]=[names[i] for i in annual.dow]; annual=annual[["weekday","mean_annual_share_percent"]]; annual.to_csv(out/"values_3.csv",index=False)
series=[(counts,"crashes","Crashes","NYC motor-vehicle crashes by weekday, 2013–2025","Total police-reported crashes"),(daily,"avg_crashes_per_day","Average crashes per calendar day","NYC crashes per calendar day by weekday, 2013–2025","Mean crashes per weekday date"),(annual,"mean_annual_share_percent","Mean annual share (%)","Average yearly share of NYC crashes by weekday, 2013–2025","Mean of each year’s weekday share (%)")]
for i,(df,col,ylabel,title,foot) in enumerate(series,1):
 fig,ax=plt.subplots(figsize=(9,5.3)); bars=ax.bar(df.weekday,df[col],color="#3977a8"); ax.set_ylabel(ylabel); ax.set_title(title); ax.grid(axis="y",alpha=.25); ax.set_axisbelow(True); ax.bar_label(bars,fmt=("%.1f" if i>1 else "%.0f"),padding=3); ax.text(0,-.20,foot,transform=ax.transAxes,fontsize=9,color="#555"); fig.tight_layout(); fig.savefig(out/f"option_{i}.png",dpi=160,bbox_inches="tight"); plt.close(fig)
print("TOTAL",int(counts.crashes.sum())); print("COUNTS\n"+counts.to_string(index=False)); print("DAILY\n"+daily.to_string(index=False)); print("MEAN YEAR SHARES\n"+annual.to_string(index=False)); print("YEAR COUNT",yr.yr_num.nunique())'
# bash
python3 -c "import json; p='out/options.json'; d=json.load(open(p)); print('JSON valid; options:',len(d['options']),'probability sum:',sum(x['probability'] for x in d['options']))"

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