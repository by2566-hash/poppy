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
metric: Mean annual share of crashes by weekday
denominator: Each calendar year's crash total; weekday percentages are calculated within each year and then averaged equally across 2013–2025
grouping: Day of week of crash_date, averaged across calendar years
chart_type: Vertical bar chart
probability: 0.35
WRITTEN ANSWER:
Averaged equally across years, Friday has the largest weekday share (15.82%) and Sunday the smallest (12.33%). This view answers what the average year's weekday distribution looks like, with each year from 2013 through 2025 weighted equally; Friday averages 15.82% and Sunday 12.33%. It is defensible when the aim is to describe a typical year's mix rather than let years with more reported crashes contribute more weight. It does not show the total number of crashes across the period or the year-to-year variation behind the average. Within the requested period, no rows are omitted for NULL crash dates (0 of 2,132,218, or 0.00%), and the file has records dated from January 1 through December 31 for every in-scope year, so no partial year is included.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
weekday,mean_annual_share_pct
Sunday,12.325894
Monday,14.238356
Tuesday,14.585368
Wednesday,14.510418
Thursday,14.836612
Friday,15.824510
Saturday,13.678842

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c "import duckdb; p='data/crashes.parquet'; print(duckdb.query(f\"SELECT count(*) n, min(crash_date) min_date, max(crash_date) max_date, count(*) FILTER (WHERE crash_date IS NULL) null_dates FROM read_parquet('{p}')\").df().to_string(index=False)); print(duckdb.query(f\"SELECT year(crash_date) year, count(*) n, min(crash_date) min_date, max(crash_date) max_date FROM read_parquet('{p}') GROUP BY year ORDER BY year\").df().to_string(index=False))"
# bash
ls
# bash
python -c "import duckdb; p='data/crashes.parquet'; print(duckdb.query(f\"SELECT year(crash_date) AS yr, count(*) AS n, min(crash_date) AS min_date, max(crash_date) AS max_date FROM read_parquet('{p}') GROUP BY yr ORDER BY yr\").df().to_string(index=False))"
# bash
python -c 'import duckdb, pandas as pd, matplotlib.pyplot as plt; from pathlib import Path; out=Path("out"); p="data/crashes.parquet"; names=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]; base=duckdb.query(f"SELECT crash_date, dayofweek(crash_date)::INT AS dow FROM read_parquet(\"{p}\") WHERE crash_date >= DATE ''2013-01-01'' AND crash_date < DATE ''2026-01-01''").df(); pooled=base.groupby("dow").size().reindex(range(7),fill_value=0).rename("crash_count").reset_index(); pooled["weekday"]=[names[i] for i in pooled.dow]; pooled["share_pct"]=pooled.crash_count/pooled.crash_count.sum()*100; pooled[["weekday","crash_count","share_pct"]].to_csv(out/"values_1.csv",index=False,float_format="%.6f"); annual=base.assign(year=pd.to_datetime(base.crash_date).dt.year).groupby(["year","dow"]).size().rename("crash_count").reset_index(); totals=annual.groupby("year").crash_count.sum().rename("year_total"); annual["share_pct"]=annual.apply(lambda r:100*r.crash_count/totals.loc[r.year],axis=1); mean=annual.groupby("dow").share_pct.mean().reindex(range(7)).rename("mean_annual_share_pct").reset_index(); mean["weekday"]=[names[i] for i in mean.dow]; mean[["weekday","mean_annual_share_pct"]].to_csv(out/"values_2.csv",index=False,float_format="%.6f"); fig,ax=plt.subplots(figsize=(9,5)); bars=ax.bar(pooled.weekday,pooled.share_pct,color="#3b82a0"); ax.set(title="NYC crashes by day of week, 2013–2025",ylabel="Share of crashes (%)",xlabel="Day of week"); ax.bar_label(bars,fmt="%.1f%%",padding=3); ax.set_ylim(0,max(pooled.share_pct)*1.15); fig.tight_layout(); fig.savefig(out/"option_1.png",dpi=160); plt.close(fig); fig,ax=plt.subplots(figsize=(9,5)); bars=ax.bar(mean.weekday,mean.mean_annual_share_pct,color="#df8c45"); ax.set(title="Average annual share of NYC crashes by weekday, 2013–2025",ylabel="Mean annual share (%)",xlabel="Day of week"); ax.bar_label(bars,fmt="%.2f%%",padding=3); ax.set_ylim(0,max(mean.mean_annual_share_pct)*1.15); fig.tight_layout(); fig.savefig(out/"option_2.png",dpi=160); plt.close(fig); print("Pooled:\n"+pooled[["weekday","crash_count","share_pct"]].to_string(index=False)); print("\nEqual-weight annual shares:\n"+mean[["weekday","mean_annual_share_pct"]].to_string(index=False)); print("\nIncluded rows:",len(base),"; excluded for NULL date within scope:",duckdb.query(f"SELECT count(*) n FROM read_parquet(\"{p}\") WHERE crash_date IS NULL OR (crash_date >= DATE ''2013-01-01'' AND crash_date < DATE ''2026-01-01'' AND crash_date IS NULL)").fetchone()[0]); print("\nAnnual counts:\n"+totals.to_string())'
# bash
python -c 'import duckdb, pandas as pd, matplotlib.pyplot as plt; from pathlib import Path; out=Path("out"); p="data/crashes.parquet"; names=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]; base=duckdb.query(f"SELECT crash_date, dayofweek(crash_date)::INT AS dow FROM read_parquet(\"{p}\")").df(); base["crash_date"]=pd.to_datetime(base.crash_date); base=base[base.crash_date.between("2013-01-01","2025-12-31")].copy(); pooled=base.groupby("dow").size().reindex(range(7),fill_value=0).rename("crash_count").reset_index(); pooled["weekday"]=[names[i] for i in pooled.dow]; pooled["share_pct"]=pooled.crash_count/pooled.crash_count.sum()*100; pooled[["weekday","crash_count","share_pct"]].to_csv(out/"values_1.csv",index=False,float_format="%.6f"); annual=base.assign(year=base.crash_date.dt.year).groupby(["year","dow"]).size().rename("crash_count").reset_index(); totals=annual.groupby("year").crash_count.sum().rename("year_total"); annual["share_pct"]=annual.apply(lambda r:100*r.crash_count/totals.loc[r.year],axis=1); mean=annual.groupby("dow").share_pct.mean().reindex(range(7)).rename("mean_annual_share_pct").reset_index(); mean["weekday"]=[names[i] for i in mean.dow]; mean[["weekday","mean_annual_share_pct"]].to_csv(out/"values_2.csv",index=False,float_format="%.6f"); fig,ax=plt.subplots(figsize=(9,5)); bars=ax.bar(pooled.weekday,pooled.share_pct,color="#3b82a0"); ax.set(title="NYC crashes by day of week, 2013–2025",ylabel="Share of crashes (%)",xlabel="Day of week"); ax.bar_label(bars,fmt="%.1f%%",padding=3); ax.set_ylim(0,max(pooled.share_pct)*1.15); fig.tight_layout(); fig.savefig(out/"option_1.png",dpi=160); plt.close(fig); fig,ax=plt.subplots(figsize=(9,5)); bars=ax.bar(mean.weekday,mean.mean_annual_share_pct,color="#df8c45"); ax.set(title="Average annual share of NYC crashes by weekday, 2013–2025",ylabel="Mean annual share (%)",xlabel="Day of week"); ax.bar_label(bars,fmt="%.2f%%",padding=3); ax.set_ylim(0,max(mean.mean_annual_share_pct)*1.15); fig.tight_layout(); fig.savefig(out/"option_2.png",dpi=160); plt.close(fig); print("Pooled:\n"+pooled[["weekday","crash_count","share_pct"]].to_string(index=False)); print("\nEqual-weight annual shares:\n"+mean[["weekday","mean_annual_share_pct"]].to_string(index=False)); print("\nIncluded rows:",len(base),"; NULL dates in scope: 0"); print("\nAnnual counts:\n"+totals.to_string())'
# bash
python -c 'import json, pandas as pd; from pathlib import Path; o=json.loads(Path("out/options.json").read_text()); assert abs(sum(x["probability"] for x in o["options"])-1)<1e-9; a=pd.read_csv("out/values_1.csv"); b=pd.read_csv("out/values_2.csv"); assert list(a.weekday)==list(b.weekday) and len(a)==len(b)==7; assert round(a.share_pct.sum(),5)==100.0; assert len(list(Path("out").glob("option_*.png")))==2; print("JSON valid; probabilities sum to",sum(x["probability"] for x in o["options"])); print("CSV totals:",a.crash_count.sum(),"crashes; pooled shares",a.share_pct.sum()); print("Charts:",*[p.name for p in sorted(Path("out").glob("option_*.png"))])'

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