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
metric: Crash count
denominator: None (raw total); share_pct is the share of all selected crash rows
grouping: Weekday of crash_date
chart_type: Bar chart
probability: 0.58
WRITTEN ANSWER:
Friday had the most crashes (338,800, 15.89% of the total), while Sunday had the fewest (257,544). This framing answers how the total number of recorded crashes is distributed across weekdays: Friday is highest and Sunday lowest, with bar heights giving each weekday total. Raw totals are a direct interpretation of distribution over the specified period, and the CSV also reports each weekday share of the selected total. It does not adjust for the number of occurrences of each weekday and does not show crash severity or risk per trip. Rows left out for a NULL required crash date: none (0 of 2,132,218 selected rows, 0.00%); partial-year share left out: none, since 2013–2025 are complete years in the selected interval.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
weekday,crash_count,share_pct
Monday,304518,14.2817
Tuesday,313488,14.7024
Wednesday,311111,14.5910
Thursday,318376,14.9317
Friday,338800,15.8896
Saturday,288381,13.5249
Sunday,257544,12.0787

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python3 -c 'import duckdb; print(duckdb.__version__)'
# bash
ls out
# bash
python3 -c 'import duckdb, pandas as pd, matplotlib.pyplot as plt, json, os, calendar; from datetime import date, timedelta
out="out"
os.makedirs(out, exist_ok=True)
start, end = date(2013,1,1), date(2025,12,31)
labels=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
con=duckdb.connect()
df=con.execute("SELECT CAST(strftime(crash_date, %w) AS INTEGER) AS dow_sun0, COUNT(*) AS crash_count FROM read_parquet(\"data/crashes.parquet\") WHERE crash_date >= DATE 2013-01-01 AND crash_date <= DATE 2025-12-31 GROUP BY 1").df()
# Build aligned weekday counts, including explicit zeros if any.
counts={((int(r.dow_sun0)+6)%7):int(r.crash_count) for r in df.itertuples()}
days=[0]*7
for i in range((end-start).days+1): days[(start+timedelta(days=i)).weekday()]+=1
counts_list=[counts.get(i,0) for i in range(7)]
total=sum(counts_list)
base=pd.DataFrame({"weekday":labels,"crash_count":counts_list,"share_pct":[x/total*100 for x in counts_list],"calendar_days":days,"average_crashes_per_calendar_day":[counts_list[i]/days[i] for i in range(7)]})
base[["weekday","crash_count","share_pct"]].to_csv("out/values_1.csv",index=False,float_format="%.4f")
base[["weekday","crash_count","calendar_days","average_crashes_per_calendar_day"]].to_csv("out/values_2.csv",index=False,float_format="%.4f")
fig,ax=plt.subplots(figsize=(9,5.2)); bars=ax.bar(labels,counts_list,color="#3977a8"); ax.set_title("NYC police-reported crashes by weekday, 2013–2025"); ax.set_ylabel("Crash count"); ax.set_xlabel("Day of week"); ax.grid(axis="y",alpha=.25); ax.bar_label(bars,labels=[f"{v/1000:.1f}k" for v in counts_list],padding=3,fontsize=9); fig.tight_layout(); fig.savefig("out/option_1.png",dpi=160); plt.close(fig)
fig,ax=plt.subplots(figsize=(9,5.2)); vals=base["average_crashes_per_calendar_day"].tolist(); bars=ax.bar(labels,vals,color="#b96f3b"); ax.set_title("Average NYC crashes per calendar weekday, 2013–2025"); ax.set_ylabel("Average crashes per date"); ax.set_xlabel("Day of week"); ax.grid(axis="y",alpha=.25); ax.bar_label(bars,labels=[f"{v:.1f}" for v in vals],padding=3,fontsize=9); fig.tight_layout(); fig.savefig("out/option_2.png",dpi=160); plt.close(fig)
hi=int(max(range(7),key=lambda i:counts_list[i])); lo=int(min(range(7),key=lambda i:counts_list[i])); hi_avg=max(range(7),key=lambda i:vals[i]); lo_avg=min(range(7),key=lambda i:vals[i])
options={"options":[
{"id":1,"metric":"Crash count","denominator":"None (raw total); share_pct is the share of all selected crash rows","grouping":"Weekday of crash_date","chart_type":"Bar chart","reason":"Raw totals directly show how the recorded crashes are distributed across weekdays over the full period.","probability":0.58,"answer":f"{labels[hi]} had the most crashes ({counts_list[hi]:,}, {counts_list[hi]/total*100:.2f}% of the total), while {labels[lo]} had the fewest ({counts_list[lo]:,}).","interpretation":f"This framing answers how the total number of recorded crashes is distributed across weekdays: {labels[hi]} is highest and {labels[lo]} lowest, with bar heights giving each weekday total. Raw totals are a direct interpretation of distribution over the specified period, and the CSV also reports each weekday share of the selected total. It does not adjust for the number of occurrences of each weekday and does not show crash severity or risk per trip. No rows are left out because required crash dates are non-NULL; 2013–2025 are complete years in the selected interval, so no partial year is included."},
{"id":2,"metric":"Mean crash count per calendar date","denominator":"Number of calendar dates of each weekday from 2013-01-01 through 2025-12-31, including dates with zero reported crashes","grouping":"Weekday of calendar date","chart_type":"Bar chart","reason":"A per-date average controls for the small differences in how often each weekday occurs in the period.","probability":0.42,"answer":f"{labels[hi_avg]} averaged {vals[hi_avg]:.2f} crashes per calendar date, the highest weekday average, versus {labels[lo_avg]} at {vals[lo_avg]:.2f}, the lowest.","interpretation":f"This framing answers the typical number of recorded crashes on a date of each weekday; {labels[hi_avg]} has the highest average and {labels[lo_avg]} the lowest. Dividing each weekday total by all calendar dates of that weekday accounts for weekday exposure, including dates with no crash rows. It leaves unanswered the total contribution of each weekday to all crashes and does not measure per-person or per-trip risk. No crash rows are left out because required crash dates are non-NULL; 2013–2025 are complete years in the selected interval, so no partial year is included."}
]}
with open("out/options.json","w") as f: json.dump(options,f,indent=2); f.write("\n")
print(base.to_string(index=False)); print("Total:",total,"calendar dates:",sum(days))'
# bash
python3 -c 'import duckdb, pandas as pd, matplotlib.pyplot as plt, json, os; from datetime import date, timedelta
os.makedirs("out", exist_ok=True)
start, end = date(2013,1,1), date(2025,12,31)
labels=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
con=duckdb.connect()
df=con.execute("SELECT EXTRACT(ISODOW FROM crash_date) AS dow_iso, COUNT(*) AS crash_count FROM read_parquet(\"data/crashes.parquet\") WHERE crash_date >= ? AND crash_date <= ? GROUP BY 1",[start,end]).df()
counts={int(r.dow_iso)-1:int(r.crash_count) for r in df.itertuples()}
days=[0]*7
for i in range((end-start).days+1): days[(start+timedelta(days=i)).weekday()]+=1
counts_list=[counts.get(i,0) for i in range(7)]; total=sum(counts_list)
base=pd.DataFrame({"weekday":labels,"crash_count":counts_list,"share_pct":[x/total*100 for x in counts_list],"calendar_days":days,"average_crashes_per_calendar_day":[counts_list[i]/days[i] for i in range(7)]})
base[["weekday","crash_count","share_pct"]].to_csv("out/values_1.csv",index=False,float_format="%.4f")
base[["weekday","crash_count","calendar_days","average_crashes_per_calendar_day"]].to_csv("out/values_2.csv",index=False,float_format="%.4f")
fig,ax=plt.subplots(figsize=(9,5.2)); bars=ax.bar(labels,counts_list,color="#3977a8"); ax.set_title("NYC police-reported crashes by weekday, 2013–2025"); ax.set_ylabel("Crash count"); ax.set_xlabel("Day of week"); ax.grid(axis="y",alpha=.25); ax.bar_label(bars,labels=[f"{v/1000:.1f}k" for v in counts_list],padding=3,fontsize=9); fig.tight_layout(); fig.savefig("out/option_1.png",dpi=160); plt.close(fig)
fig,ax=plt.subplots(figsize=(9,5.2)); vals=base["average_crashes_per_calendar_day"].tolist(); bars=ax.bar(labels,vals,color="#b96f3b"); ax.set_title("Average NYC crashes per calendar weekday, 2013–2025"); ax.set_ylabel("Average crashes per date"); ax.set_xlabel("Day of week"); ax.grid(axis="y",alpha=.25); ax.bar_label(bars,labels=[f"{v:.1f}" for v in vals],padding=3,fontsize=9); fig.tight_layout(); fig.savefig("out/option_2.png",dpi=160); plt.close(fig)
hi=max(range(7),key=lambda i:counts_list[i]); lo=min(range(7),key=lambda i:counts_list[i]); hi_avg=max(range(7),key=lambda i:vals[i]); lo_avg=min(range(7),key=lambda i:vals[i])
options={"options":[
{"id":1,"metric":"Crash count","denominator":"None (raw total); share_pct is the share of all selected crash rows","grouping":"Weekday of crash_date","chart_type":"Bar chart","reason":"Raw totals directly show how the recorded crashes are distributed across weekdays over the full period.","probability":0.58,"answer":f"{labels[hi]} had the most crashes ({counts_list[hi]:,}, {counts_list[hi]/total*100:.2f}% of the total), while {labels[lo]} had the fewest ({counts_list[lo]:,}).","interpretation":f"This framing answers how the total number of recorded crashes is distributed across weekdays: {labels[hi]} is highest and {labels[lo]} lowest, with bar heights giving each weekday total. Raw totals are a direct interpretation of distribution over the specified period, and the CSV also reports each weekday share of the selected total. It does not adjust for the number of occurrences of each weekday and does not show crash severity or risk per trip. No rows are left out because required crash dates are non-NULL; 2013–2025 are complete years in the selected interval, so no partial year is included."},
{"id":2,"metric":"Mean crash count per calendar date","denominator":"Number of calendar dates of each weekday from 2013-01-01 through 2025-12-31, including dates with zero reported crashes","grouping":"Weekday of calendar date","chart_type":"Bar chart","reason":"A per-date average controls for the small differences in how often each weekday occurs in the period.","probability":0.42,"answer":f"{labels[hi_avg]} averaged {vals[hi_avg]:.2f} crashes per calendar date, the highest weekday average, versus {labels[lo_avg]} at {vals[lo_avg]:.2f}, the lowest." ,"interpretation":f"This framing answers the typical number of recorded crashes on a date of each weekday; {labels[hi_avg]} has the highest average and {labels[lo_avg]} the lowest. Dividing each weekday total by all calendar dates of that weekday accounts for weekday exposure, including dates with no crash rows. It leaves unanswered the total contribution of each weekday to all crashes and does not measure per-person or per-trip risk. No crash rows are left out because required crash dates are non-NULL; 2013–2025 are complete years in the selected interval, so no partial year is included."}
]}
with open("out/options.json","w") as f: json.dump(options,f,indent=2); f.write("\n")
print(base.to_string(index=False)); print("Total:",total,"calendar dates:",sum(days))'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; print(c.execute("SELECT COUNT(*) FILTER (WHERE crash_date IS NULL) AS null_dates, COUNT(*) FILTER (WHERE crash_date >= DATE 2013-01-01 AND crash_date <= DATE 2025-12-31) AS selected_rows FROM read_parquet(?)",[p]).fetchall()); print(c.execute("SELECT year(crash_date) AS year, min(crash_date), max(crash_date), count(DISTINCT crash_date) AS observed_dates FROM read_parquet(?) WHERE crash_date >= ? AND crash_date <= ? GROUP BY 1 ORDER BY 1",[p,"2013-01-01","2025-12-31"]).fetchall())'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; print(c.execute("SELECT COUNT(*) FILTER (WHERE crash_date IS NULL) AS null_dates, COUNT(*) FILTER (WHERE crash_date >= ? AND crash_date <= ?) AS selected_rows FROM read_parquet(?)",["2013-01-01","2025-12-31",p]).fetchall()); print(c.execute("SELECT year(crash_date) AS yr, min(crash_date), max(crash_date), count(DISTINCT crash_date) AS observed_dates FROM read_parquet(?) WHERE crash_date >= ? AND crash_date <= ? GROUP BY 1 ORDER BY 1",[p,"2013-01-01","2025-12-31"]).fetchall())'
# bash
python3 -c 'import json,csv,os; p="out/options.json"; d=json.load(open(p)); print("options",len(d["options"]),"probability sum",sum(x["probability"] for x in d["options"])); print("files",[(f,os.path.getsize("out/"+f)) for f in ["option_1.png","values_1.csv","option_2.png","values_2.csv","options.json"]]); print("csv1 total",sum(int(r["crash_count"]) for r in csv.DictReader(open("out/values_1.csv")))); print("csv2 means",[(r["weekday"],r["average_crashes_per_calendar_day"]) for r in csv.DictReader(open("out/values_2.csv"))])'

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