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

DATA FACTS (pinned snapshot):
- The file covers 2012-07-01 to 2026-06-11; 2013-2025 are complete calendar years; 2026 is partial (to June 11).
- borough is NULL for about 20-38% of crashes in every year (TR05): a borough filter silently drops them.
- number_of_persons_killed is NULL in most May-2026 and all June-2026 rows (TR08); 2013-2025 killed counts have no NULLs.
- crash_time has no NULL rows. Reported crash counts (the number of crash records) fall sharply in 2020 (TR01), so a per-reported-crash rate (deaths or injuries divided by reported crashes) compared across years spanning 2020 needs a caveat. Counts of deaths or injuries by year do NOT need it (they are not affected by the reporting change), and a comparison between groups within one pooled window (e.g. day vs night) does not either (decided 2026-11-04; g5 wording after g4 failed c6 on plain death counts).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: From 2013 to 2025, how were NYC crashes spread across the days of the week?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Police-reported crash count and percentage of all crashes
denominator: All crashes with crash_date from 2013-01-01 through 2025-12-31 (2,132,218 records)
grouping: Day of week across the full period
chart_type: Horizontal bar chart
probability: 0.65
WRITTEN ANSWER:
Friday had the most crashes (338,800; 15.9% of the total), while Sunday had the fewest (257,544; 12.1%). This framing answers how the recorded crashes were divided among weekdays over the full period: Friday has the largest share and Sunday the smallest. It is a defensible pooled distribution of crash records, but it does not adjust for the slightly different number of each weekday in the calendar or show year-to-year shifts.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
weekday,crashes,share_percent
Monday,304518,14.2817
Tuesday,313488,14.7024
Wednesday,311111,14.5910
Thursday,318376,14.9317
Friday,338800,15.8896
Saturday,288381,13.5249
Sunday,257544,12.0787

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
pwd && ls
# bash
ls
# bash
python3 -c "import duckdb; p='data/crashes.parquet'; print(duckdb.sql(f\"describe select * from read_parquet('{p}')\").df().to_string(index=False)); print(duckdb.sql(f\"select min(crash_date), max(crash_date), count(*), count(*) filter(where crash_date between date '2013-01-01' and date '2025-12-31') from read_parquet('{p}')\").fetchall())"
# bash
python3 -c "import duckdb; p='data/crashes.parquet'; print(duckdb.sql(f\"select dayofweek(crash_date) dow, strftime(crash_date,'%A') weekday, count(*) crashes, count(distinct crash_date) days from read_parquet('{p}') where crash_date >= date '2013-01-01' and crash_date < date '2026-01-01' group by 1,2 order by 1\").df().to_string(index=False)); print(duckdb.sql(f\"select year(crash_date) yr, count(*) n, min(crash_date), max(crash_date) from read_parquet('{p}') where crash_date >= date '2013-01-01' and crash_date < date '2026-01-01' group by 1 order by 1\").df().to_string(index=False))"
# bash
python3 -c "import duckdb; p='data/crashes.parquet'; print(duckdb.sql(f\"select dayofweek(crash_date) dow, strftime(crash_date,'%A') weekday, count(*) crashes, count(distinct crash_date) as day_count from read_parquet('{p}') where crash_date >= date '2013-01-01' and crash_date < date '2026-01-01' group by 1,2 order by 1\").df().to_string(index=False)); print(duckdb.sql(f\"select year(crash_date) yr, count(*) n, min(crash_date), max(crash_date) from read_parquet('{p}') where crash_date >= date '2013-01-01' and crash_date < date '2026-01-01' group by 1 order by 1\").df().to_string(index=False))"
# bash
ls out
# bash
python3 -c 'import os, json, duckdb, pandas as pd, matplotlib.pyplot as plt; os.makedirs("out", exist_ok=True); p="data/crashes.parquet"; q=f"select isodow(crash_date) as dow, strftime(crash_date, %s) as weekday, count(*) as crashes from read_parquet(%s) where crash_date >= date %s and crash_date < date %s group by 1,2 order by 1"; df=duckdb.sql(q, params=["%A", p, "2013-01-01", "2026-01-01"]).df(); order=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]; df["weekday"]=pd.Categorical(df.weekday, categories=order, ordered=True); df=df.sort_values("weekday").reset_index(drop=True); total=int(df.crashes.sum()); df["share_percent"]=df.crashes/total*100; cal=pd.date_range("2013-01-01","2025-12-31",freq="D"); days=pd.Series(cal.day_name()).value_counts().reindex(order); df["calendar_days"]=df.weekday.astype(str).map(days).astype(int); df["average_crashes_per_day"]=df.crashes/df.calendar_days; d1=df[["weekday","crashes","share_percent"]].copy(); d1.to_csv("out/values_1.csv", index=False, float_format="%.4f"); fig,ax=plt.subplots(figsize=(9,5.2)); bars=ax.barh(order, d1.share_percent, color="#3b82a0"); ax.invert_yaxis(); ax.set_xlabel("Share of all police-reported crashes (%)"); ax.set_title("NYC crashes by weekday, 2013–2025"); ax.grid(axis="x", alpha=.22); ax.set_axisbelow(True); ax.bar_label(bars, labels=[f"{int(n):,}  ({s:.1f}%)" for n,s in zip(df.crashes,df.share_percent)], padding=4, fontsize=9); ax.set_xlim(0, max(d1.share_percent)*1.25); fig.tight_layout(); fig.savefig("out/option_1.png", dpi=180); plt.close(fig); d2=df[["weekday","crashes","calendar_days","average_crashes_per_day"]].copy(); d2.to_csv("out/values_2.csv", index=False, float_format="%.4f"); fig,ax=plt.subplots(figsize=(9,5.2)); bars=ax.bar(order, d2.average_crashes_per_day, color="#ce8b45"); ax.set_ylabel("Average crashes per calendar day"); ax.set_title("Average NYC crashes per weekday occurrence, 2013–2025"); ax.grid(axis="y", alpha=.22); ax.set_axisbelow(True); ax.bar_label(bars, labels=[f"{x:,.1f}" for x in d2.average_crashes_per_day], padding=3, fontsize=9); ax.set_ylim(0, max(d2.average_crashes_per_day)*1.15); fig.tight_layout(); fig.savefig("out/option_2.png", dpi=180); plt.close(fig); print(d1.to_string(index=False)); print("total",total); print(d2.to_string(index=False))'
# bash
python3 -c 'import os, duckdb, pandas as pd, matplotlib.pyplot as plt; os.makedirs("out", exist_ok=True); p="data/crashes.parquet"; q=f"select isodow(crash_date) as dow, case isodow(crash_date) when 1 then '\''Monday'\'' when 2 then '\''Tuesday'\'' when 3 then '\''Wednesday'\'' when 4 then '\''Thursday'\'' when 5 then '\''Friday'\'' when 6 then '\''Saturday'\'' else '\''Sunday'\'' end as weekday, count(*) as crashes from read_parquet('\''{p}'\'') where crash_date >= date '\''2013-01-01'\'' and crash_date < date '\''2026-01-01'\'' group by 1,2 order by 1"; df=duckdb.sql(q).df(); order=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]; df["weekday"]=pd.Categorical(df.weekday, categories=order, ordered=True); df=df.sort_values("weekday").reset_index(drop=True); total=int(df.crashes.sum()); df["share_percent"]=df.crashes/total*100; cal=pd.date_range("2013-01-01","2025-12-31",freq="D"); days=pd.Series(cal.day_name()).value_counts().reindex(order); df["calendar_days"]=df.weekday.astype(str).map(days).astype(int); df["average_crashes_per_day"]=df.crashes/df.calendar_days; d1=df[["weekday","crashes","share_percent"]].copy(); d1.to_csv("out/values_1.csv", index=False, float_format="%.4f"); fig,ax=plt.subplots(figsize=(9,5.2)); bars=ax.barh(order, d1.share_percent, color="#3b82a0"); ax.invert_yaxis(); ax.set_xlabel("Share of all police-reported crashes (%)"); ax.set_title("NYC crashes by weekday, 2013–2025"); ax.grid(axis="x", alpha=.22); ax.set_axisbelow(True); ax.bar_label(bars, labels=[f"{int(n):,}  ({s:.1f}%)" for n,s in zip(df.crashes,df.share_percent)], padding=4, fontsize=9); ax.set_xlim(0, max(d1.share_percent)*1.25); fig.tight_layout(); fig.savefig("out/option_1.png", dpi=180); plt.close(fig); d2=df[["weekday","crashes","calendar_days","average_crashes_per_day"]].copy(); d2.to_csv("out/values_2.csv", index=False, float_format="%.4f"); fig,ax=plt.subplots(figsize=(9,5.2)); bars=ax.bar(order, d2.average_crashes_per_day, color="#ce8b45"); ax.set_ylabel("Average crashes per calendar day"); ax.set_title("Average NYC crashes per weekday occurrence, 2013–2025"); ax.grid(axis="y", alpha=.22); ax.set_axisbelow(True); ax.bar_label(bars, labels=[f"{x:,.1f}" for x in d2.average_crashes_per_day], padding=3, fontsize=9); ax.set_ylim(0, max(d2.average_crashes_per_day)*1.15); fig.tight_layout(); fig.savefig("out/option_2.png", dpi=180); plt.close(fig); print(d1.to_string(index=False)); print("total",total); print(d2.to_string(index=False))'
# bash
python3 -c 'import json, pathlib, pandas as pd; d=pathlib.Path("out"); o=json.loads((d/"options.json").read_text()); assert abs(sum(x["probability"] for x in o["options"])-1)<1e-9; assert all((d/f"option_{i}.png").is_file() and (d/f"values_{i}.csv").is_file() for i in (1,2)); a=pd.read_csv(d/"values_1.csv"); b=pd.read_csv(d/"values_2.csv"); assert int(a.crashes.sum())==2132218; assert a.loc[a.weekday=="Friday","crashes"].item()==338800; assert round(a.loc[a.weekday=="Sunday","share_percent"].item(),1)==12.1; assert round(b.loc[b.weekday=="Friday","average_crashes_per_day"].item(),1)==499.7; assert round(b.loc[b.weekday=="Sunday","average_crashes_per_day"].item(),1)==379.9; print("Validated JSON, output files, totals, and stated weekday values.")'

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