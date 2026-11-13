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
metric: Annual number of pedestrians killed in Brooklyn police-reported crashes
denominator: No exposure denominator; annual count of pedestrian deaths
grouping: Calendar year, 2013–2025
chart_type: Line chart
probability: 0.35
WRITTEN ANSWER:
Pedestrian deaths increased from 30 in 2013 to 39 in 2025 (30%), with substantial year-to-year fluctuation. This framing answers whether the most severe pedestrian harm has declined: the chart shows 39 deaths in 2025, more than the 30 recorded in 2013. Death counts are a direct measure of fatal harm, but they do not account for pedestrian exposure and say nothing about nonfatal injuries.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,pedestrians_killed
2013,30
2014,42
2015,46
2016,20
2017,20
2018,23
2019,33
2020,17
2021,32
2022,23
2023,22
2024,31
2025,39

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute(f"describe select * from read_parquet(\"{p}\")").fetchdf().to_string(index=False)); print(c.execute(f"select count(*) n,min(crash_date),max(crash_date) from read_parquet(\"{p}\")").fetchall()); print(c.execute(f"select distinct borough from read_parquet(\"{p}\") order by 1").fetchall())'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); q="""select year(crash_date) year, count(*) crash_records, sum(coalesce(number_of_pedestrians_injured,0)) injured, sum(coalesce(number_of_pedestrians_killed,0)) killed, sum(coalesce(number_of_pedestrians_injured,0)+coalesce(number_of_pedestrians_killed,0)) casualties, sum(case when coalesce(number_of_pedestrians_injured,0)+coalesce(number_of_pedestrians_killed,0)>0 then 1 else 0 end) crashes_with_ped_casualty from read_parquet(''data/crashes.parquet'') where borough=''''BROOKLYN'''' and crash_date >= date ''''2013-01-01'''' and crash_date < date ''''2026-01-01'''' group by 1 order by 1"""; print(c.execute(q).fetchdf().to_string(index=False))'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); q="select year(crash_date) as calendar_year, count(*) as crash_records, sum(coalesce(number_of_pedestrians_injured,0)) as injured, sum(coalesce(number_of_pedestrians_killed,0)) as killed, sum(coalesce(number_of_pedestrians_injured,0)+coalesce(number_of_pedestrians_killed,0)) as casualties, sum(case when coalesce(number_of_pedestrians_injured,0)+coalesce(number_of_pedestrians_killed,0)>0 then 1 else 0 end) as crashes_with_ped_casualty from read_parquet(?) where borough=? and crash_date >= ? and crash_date < ? group by 1 order by 1"; print(c.execute(q,["data/crashes.parquet","BROOKLYN","2013-01-01","2026-01-01"]).fetchdf().to_string(index=False))'
# bash
ls -ld . data
# bash
python3 -c 'from pathlib import Path; import duckdb, pandas as pd, matplotlib.pyplot as plt, numpy as np; out=Path("out"); out.mkdir(exist_ok=True); con=duckdb.connect(); q="select year(crash_date) as year, sum(coalesce(number_of_pedestrians_injured,0))::BIGINT as injured, sum(coalesce(number_of_pedestrians_killed,0))::BIGINT as killed from read_parquet(?) where borough=? and crash_date >= ? and crash_date < ? group by 1 order by 1"; df=con.execute(q,["data/crashes.parquet","BROOKLYN","2013-01-01","2026-01-01"]).fetchdf(); df["casualties"]=df.injured+df.killed; df["fatal_share_pct"]=df.killed / df.casualties * 100; plt.rcParams.update({"font.family":"DejaVu Sans","axes.spines.top":False,"axes.spines.right":False,"axes.titlesize":17,"axes.titleweight":"bold","axes.labelsize":11}); configs=[(1,"injured","Pedestrians injured","People", "Annual injured pedestrians", "#177E89", f"{int(df.injured.iloc[0]):,} in 2013 → {int(df.injured.iloc[-1]):,} in 2025 ({(df.injured.iloc[-1]/df.injured.iloc[0]-1)*100:+.0f}%)", "pedestrians_injured"),(2,"killed","Pedestrians killed","People", "Annual pedestrian deaths", "#C43C39", f"{int(df.killed.iloc[0]):,} in 2013 → {int(df.killed.iloc[-1]):,} in 2025 ({(df.killed.iloc[-1]/df.killed.iloc[0]-1)*100:+.0f}%)", "pedestrians_killed"),(3,"fatal_share_pct","Fatalities as share of pedestrian casualties","Percent of injured or killed pedestrians", "Share of pedestrian casualties that were fatal", "#665191", f"{df.fatal_share_pct.iloc[0]:.2f}% in 2013 → {df.fatal_share_pct.iloc[-1]:.2f}% in 2025 (+{df.fatal_share_pct.iloc[-1]-df.fatal_share_pct.iloc[0]:.2f} percentage points)", "fatality_share_percent")];
for i,key,ylab,title,color,annotation,colname in configs:
 vals=df[["year",key]].rename(columns={key:colname}); vals.to_csv(out/f"values_{i}.csv",index=False); fig,ax=plt.subplots(figsize=(10,5.8)); x=df.year.to_numpy(); y=df[key].to_numpy(); ax.plot(x,y,color=color,lw=2.7,marker="o",ms=5.5); ax.scatter([x[0],x[-1]],[y[0],y[-1]],color=color,s=55,zorder=3); ax.set_title(title,loc="left",pad=15); ax.text(0,1.015,annotation,transform=ax.transAxes,color=color,fontsize=11,fontweight="bold"); ax.set_ylabel(ylab); ax.set_xlabel("Crash year"); ax.set_xticks(x); ax.tick_params(axis="x",rotation=0,labelsize=9); ax.grid(axis="y",color="#d9d9d9",lw=.7); ax.set_axisbelow(True); ax.margins(x=.04); ax.text(0,-.19,"Brooklyn • annual totals from police-reported crashes • complete years only (2013–2025)\n2026 excluded because the data year is incomplete; counts are not adjusted for population or pedestrian exposure.",transform=ax.transAxes,fontsize=8.5,color="#555555",va="top"); fig.tight_layout(rect=[0,.08,1,1]); fig.savefig(out/f"option_{i}.png",dpi=180,bbox_inches="tight"); plt.close(fig); print(f"{i}: {annotation}"); print(vals.to_string(index=False))'
# bash
python3 -c 'from pathlib import Path; import duckdb, pandas as pd, matplotlib.pyplot as plt; out=Path("out"); out.mkdir(exist_ok=True); con=duckdb.connect(); q="select year(crash_date) as year, sum(coalesce(number_of_pedestrians_injured,0))::BIGINT as injured, sum(coalesce(number_of_pedestrians_killed,0))::BIGINT as killed from read_parquet(?) where borough=? and crash_date >= ? and crash_date < ? group by 1 order by 1"; df=con.execute(q,["data/crashes.parquet","BROOKLYN","2013-01-01","2026-01-01"]).fetchdf(); df["casualties"]=df.injured+df.killed; df["fatal_share_pct"]=df.killed / df.casualties * 100; plt.rcParams.update({"font.family":"DejaVu Sans","axes.spines.top":False,"axes.spines.right":False,"axes.titlesize":17,"axes.titleweight":"bold","axes.labelsize":11}); configs=[(1,"injured","People","Annual pedestrians injured","#177E89",f"{int(df.injured.iloc[0]):,} in 2013 → {int(df.injured.iloc[-1]):,} in 2025 ({(df.injured.iloc[-1]/df.injured.iloc[0]-1)*100:+.0f}%)","pedestrians_injured"),(2,"killed","People","Annual pedestrian deaths","#C43C39",f"{int(df.killed.iloc[0]):,} in 2013 → {int(df.killed.iloc[-1]):,} in 2025 ({(df.killed.iloc[-1]/df.killed.iloc[0]-1)*100:+.0f}%)","pedestrians_killed"),(3,"fatal_share_pct","Percent of injured or killed pedestrians","Fatality share among recorded pedestrian casualties","#665191",f"{df.fatal_share_pct.iloc[0]:.2f}% in 2013 → {df.fatal_share_pct.iloc[-1]:.2f}% in 2025 (+{df.fatal_share_pct.iloc[-1]-df.fatal_share_pct.iloc[0]:.2f} percentage points)","fatality_share_percent")];
for i,key,ylab,title,color,annotation,colname in configs:
 vals=df[["year",key]].rename(columns={key:colname}); vals.to_csv(out/f"values_{i}.csv",index=False); fig,ax=plt.subplots(figsize=(10,5.8)); x=df.year.to_numpy(); y=df[key].to_numpy(); ax.plot(x,y,color=color,lw=2.7,marker="o",ms=5.5); ax.scatter([x[0],x[-1]],[y[0],y[-1]],color=color,s=55,zorder=3); ax.set_title(title,loc="left",pad=15); ax.text(0,1.015,annotation,transform=ax.transAxes,color=color,fontsize=11,fontweight="bold"); ax.set_ylabel(ylab); ax.set_xlabel("Crash year"); ax.set_xticks(x); ax.tick_params(axis="x",rotation=0,labelsize=9); ax.grid(axis="y",color="#d9d9d9",lw=.7); ax.set_axisbelow(True); ax.margins(x=.04); ax.text(0,-.19,"Brooklyn • annual totals from police-reported crashes • complete years only (2013–2025)\n2026 excluded because the data year is incomplete; counts are not adjusted for population or pedestrian exposure.",transform=ax.transAxes,fontsize=8.5,color="#555555",va="top"); fig.tight_layout(rect=[0,.08,1,1]); fig.savefig(out/f"option_{i}.png",dpi=180,bbox_inches="tight"); plt.close(fig); print(f"{i}: {annotation}"); print(vals.to_string(index=False))'
# bash
python3 -c 'from pathlib import Path; import pandas as pd, matplotlib.pyplot as plt; out=Path("out"); plt.rcParams.update({"font.family":"DejaVu Sans","axes.spines.top":False,"axes.spines.right":False,"axes.titlesize":17,"axes.titleweight":"bold","axes.labelsize":11}); specs=[(1,"pedestrians_injured","People","Annual pedestrians injured","#177E89","pedestrians_injured"),(2,"pedestrians_killed","People","Annual pedestrian deaths","#C43C39","pedestrians_killed"),(3,"fatality_share_percent","Percent of injured or killed pedestrians","Fatality share among recorded pedestrian casualties","#665191","fatality_share_percent")];
for i,col,ylab,title,color,label in specs:
 d=pd.read_csv(out/f"values_{i}.csv"); y=d[col]; start,end=float(y.iloc[0]),float(y.iloc[-1]); change=(end/start-1)*100 if i<3 else end-start; annotation=(f"{int(start):,} in 2013 → {int(end):,} in 2025 ({change:+.0f}%)" if i<3 else f"{start:.2f}% in 2013 → {end:.2f}% in 2025 ({change:+.2f} percentage points)"); fig,ax=plt.subplots(figsize=(10,5.8)); ax.plot(d.year,y,color=color,lw=2.7,marker="o",ms=5.5); ax.scatter([d.year.iloc[0],d.year.iloc[-1]],[start,end],color=color,s=55,zorder=3); ax.set_title(title,loc="left",pad=15); ax.text(0,1.015,annotation,transform=ax.transAxes,color=color,fontsize=11,fontweight="bold"); ax.set_ylabel(ylab); ax.set_xlabel("Crash year"); ax.set_xticks(d.year); ax.tick_params(axis="x",labelsize=9); ax.grid(axis="y",color="#d9d9d9",lw=.7); ax.set_axisbelow(True); ax.set_ylim(bottom=0); ax.margins(x=.04); ax.text(0,-.19,"Brooklyn • annual totals from police-reported crashes • complete years only (2013–2025)\n2026 excluded because the data year is incomplete; counts are not adjusted for population or pedestrian exposure.",transform=ax.transAxes,fontsize=8.5,color="#555555",va="top"); fig.tight_layout(rect=[0,.08,1,1]); fig.savefig(out/f"option_{i}.png",dpi=180,bbox_inches="tight"); plt.close(fig)'
# bash
python3 -c 'import json; from pathlib import Path; p=Path("out/options.json"); d=json.loads(p.read_text()); print("JSON valid; probabilities sum:",sum(o["probability"] for o in d["options"])); print("Artifacts:", all(Path(f"out/{f}").is_file() for i in range(1,4) for f in [f"option_{i}.png",f"values_{i}.csv"]))'

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
- tr_TR01: If a per-reported-crash rate spanning 2020 is shown, the output says that the number of recorded crashes changes sharply around 2020 and that this affects comparing the per-crash rate across years (naming the cause, the 2020 recording change, is not required: it is not in the data or the dictionary).
- tr_TR15: Claims about pedestrian deaths changing are qualified by the small counts (about 30–39 per year).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.