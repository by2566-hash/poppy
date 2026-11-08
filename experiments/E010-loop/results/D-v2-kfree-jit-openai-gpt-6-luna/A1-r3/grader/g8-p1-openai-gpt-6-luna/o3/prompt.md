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
metric: Annual crashes with at least one pedestrian injured or killed
denominator: None; annual crash count among crashes recorded in Brooklyn, not adjusted for pedestrian exposure
grouping: Calendar year, 2013–2025
chart_type: Line chart
probability: 0.22
WRITTEN ANSWER:
Brooklyn crashes involving an injured or killed pedestrian declined from 3,498 in 2013 to 2,766 in 2025 (21% lower), but were 5% above the 2019 count. This answers whether harmful pedestrian-involved crash events have become less frequent in annual counts; after the 2020 dip, the count rose to slightly above its 2019 level by 2025. It is a defensible event-frequency measure, but it does not show injury severity or risk per walking trip because exposure is unavailable.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,pedestrian_involved_crashes
2013,3498
2014,3234
2015,2962
2016,2797
2017,2550
2018,2697
2019,2623
2020,1724
2021,1856
2022,2185
2023,2310
2024,2576
2025,2766

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python3 -c "import duckdb; p='data/crashes.parquet'; print(duckdb.sql(f\"DESCRIBE SELECT * FROM read_parquet('{p}')\").df().to_string(index=False)); print(duckdb.sql(f\"SELECT COUNT(*) n, MIN(crash_date) min_date, MAX(crash_date) max_date, COUNT_IF(upper(borough)='BROOKLYN') brooklyn_rows FROM read_parquet('{p}')\").df().to_string(index=False))"
# bash
python3 -c "import duckdb; c=duckdb.connect(); c.execute(\"CREATE VIEW crashes AS SELECT * FROM read_parquet('data/crashes.parquet')\"); print(c.sql(\"SELECT year(crash_date) year, COUNT(*) all_crashes, SUM(COALESCE(number_of_pedestrians_injured,0)) ped_injured, SUM(COALESCE(number_of_pedestrians_killed,0)) ped_killed, COUNT(*) FILTER (WHERE COALESCE(number_of_pedestrians_injured,0)>0 OR COALESCE(number_of_pedestrians_killed,0)>0) ped_crashes FROM crashes WHERE borough='Brooklyn' AND crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1\").df().to_string(index=False)); print(c.sql(\"SELECT year(crash_date) year, COUNT(*) FILTER (WHERE crash_date IS NULL) null_date, COUNT(*) FILTER (WHERE number_of_pedestrians_injured IS NULL) null_inj, COUNT(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) null_kill, MIN(crash_date) min_date, MAX(crash_date) max_date FROM crashes WHERE borough='Brooklyn' GROUP BY 1 ORDER BY 1\").df().to_string(index=False))"
# bash
python3 -c "import duckdb; c=duckdb.connect(); c.execute(\"CREATE VIEW crashes AS SELECT * FROM read_parquet('data/crashes.parquet')\"); print(c.sql(\"SELECT EXTRACT(YEAR FROM crash_date) AS yr, COUNT(*) AS all_crashes, SUM(COALESCE(number_of_pedestrians_injured,0)) AS ped_injured, SUM(COALESCE(number_of_pedestrians_killed,0)) AS ped_killed, COUNT(*) FILTER (WHERE COALESCE(number_of_pedestrians_injured,0)>0 OR COALESCE(number_of_pedestrians_killed,0)>0) AS ped_crashes FROM crashes WHERE borough='Brooklyn' AND crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1\").df().to_string(index=False)); print(c.sql(\"SELECT EXTRACT(YEAR FROM crash_date) AS yr, COUNT(*) AS rows, MIN(crash_date) AS min_date, MAX(crash_date) AS max_date, COUNT(*) FILTER (WHERE number_of_pedestrians_injured IS NULL) AS null_inj, COUNT(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS null_kill FROM crashes WHERE borough='Brooklyn' AND crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1\").df().to_string(index=False))"
# bash
python3 -c "import duckdb; c=duckdb.connect(); c.execute(\"CREATE VIEW crashes AS SELECT * FROM read_parquet('data/crashes.parquet')\"); print(c.sql(\"SELECT borough, COUNT(*) FROM crashes WHERE borough IS NOT NULL GROUP BY borough ORDER BY 2 DESC LIMIT 10\").df().to_string(index=False)); print(c.sql(\"SELECT EXTRACT(YEAR FROM crash_date) AS yr, COUNT(*) AS all_crashes, SUM(COALESCE(number_of_pedestrians_injured,0)) AS ped_injured, SUM(COALESCE(number_of_pedestrians_killed,0)) AS ped_killed, COUNT(*) FILTER (WHERE COALESCE(number_of_pedestrians_injured,0)>0 OR COALESCE(number_of_pedestrians_killed,0)>0) AS ped_crashes FROM crashes WHERE UPPER(borough)='BROOKLYN' AND crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1\").df().to_string(index=False))"
# bash
python3 -c 'import duckdb, pandas as pd, matplotlib.pyplot as plt, pathlib
out=pathlib.Path("out"); out.mkdir(exist_ok=True)
db=duckdb.connect(); df=db.execute("""SELECT EXTRACT(YEAR FROM crash_date)::INT AS year, SUM(COALESCE(number_of_pedestrians_injured,0))::INT AS pedestrians_injured, SUM(COALESCE(number_of_pedestrians_killed,0))::INT AS pedestrians_killed, COUNT(*) FILTER (WHERE COALESCE(number_of_pedestrians_injured,0)>0 OR COALESCE(number_of_pedestrians_killed,0)>0)::INT AS pedestrian_involved_crashes FROM read_parquet(\"data/crashes.parquet\") WHERE UPPER(borough)=\"BROOKLYN\" AND crash_date >= DATE \"2013-01-01\" AND crash_date < DATE \"2026-01-01\" GROUP BY 1 ORDER BY 1""").df()
df["pedestrian_casualties"]=df.pedestrians_injured+df.pedestrians_killed
colors={"blue":"#176B87","red":"#B23A48","gold":"#C27C0E"}
plt.rcParams.update({"font.family":"DejaVu Sans","axes.spines.top":False,"axes.spines.right":False,"axes.titleweight":"bold"})
def chart(idx, col, title, ylabel, color, csv_cols):
    vals=df[csv_cols].copy(); vals.to_csv(out/f"values_{idx}.csv",index=False)
    fig,ax=plt.subplots(figsize=(10,5.7)); fig.patch.set_facecolor("white")
    ax.plot(df.year,df[col],color=color,linewidth=2.8,marker="o",markersize=5.5)
    ax.fill_between(df.year,df[col],color=color,alpha=.09)
    ax.set_title(title,loc="left",fontsize=17,pad=16)
    ax.set_ylabel(ylabel,fontsize=11); ax.set_xlabel("Crash year",fontsize=10)
    ax.set_xticks(df.year); ax.tick_params(axis="x",rotation=0,labelsize=9); ax.tick_params(axis="y",labelsize=10)
    ax.grid(axis="y",color="#D9DEE3",linewidth=.8); ax.set_axisbelow(True)
    y0=int(df.loc[df.year.eq(2013),col].iloc[0]); y1=int(df.loc[df.year.eq(2025),col].iloc[0]); change=(y1/y0-1)*100
    sign="+" if change>0 else ""
    ax.annotate(f"2013  {y0:,}",(2013,y0),xytext=(7,11),textcoords="offset points",fontsize=9,color="#333")
    ax.annotate(f"2025  {y1:,} ({sign}{change:.0f}%)",(2025,y1),xytext=(-8,13),textcoords="offset points",ha="right",fontsize=9,fontweight="bold",color=color)
    ax.text(0,-.22,"Brooklyn crashes with borough recorded; annual counts, not adjusted for walking exposure. Source: NYC police-reported crash records.",transform=ax.transAxes,fontsize=8.5,color="#555")
    fig.tight_layout(); fig.savefig(out/f"option_{idx}.png",dpi=180,bbox_inches="tight"); plt.close(fig)
chart(1,"pedestrian_casualties","Brooklyn pedestrian casualties fell from 2013, then rebounded","Pedestrians injured or killed (people)",colors["blue"], ["year","pedestrians_injured","pedestrians_killed","pedestrian_casualties"])
chart(2,"pedestrians_killed","Brooklyn pedestrian deaths remain volatile","Pedestrians killed (people)",colors["red"],["year","pedestrians_killed"])
chart(3,"pedestrian_involved_crashes","Crashes involving Brooklyn pedestrians are near pre-pandemic levels","Crashes with ≥1 pedestrian injured or killed (crashes)",colors["gold"],["year","pedestrian_involved_crashes"])
print(df.to_string(index=False))'
# bash
python3 -c 'import duckdb, pandas as pd, matplotlib.pyplot as plt, pathlib
out=pathlib.Path("out"); out.mkdir(exist_ok=True)
db=duckdb.connect(); df=db.execute("""SELECT EXTRACT(YEAR FROM crash_date)::INT AS year, SUM(COALESCE(number_of_pedestrians_injured,0))::INT AS pedestrians_injured, SUM(COALESCE(number_of_pedestrians_killed,0))::INT AS pedestrians_killed, COUNT(*) FILTER (WHERE COALESCE(number_of_pedestrians_injured,0)>0 OR COALESCE(number_of_pedestrians_killed,0)>0)::INT AS pedestrian_involved_crashes FROM read_parquet(?) WHERE UPPER(borough)=? AND crash_date >= ? AND crash_date < ? GROUP BY 1 ORDER BY 1""",["data/crashes.parquet","BROOKLYN","2013-01-01","2026-01-01"]).df()
df["pedestrian_casualties"]=df.pedestrians_injured+df.pedestrians_killed
colors={"blue":"#176B87","red":"#B23A48","gold":"#C27C0E"}
plt.rcParams.update({"font.family":"DejaVu Sans","axes.spines.top":False,"axes.spines.right":False,"axes.titleweight":"bold"})
def chart(idx, col, title, ylabel, color, csv_cols):
    df[csv_cols].to_csv(out/f"values_{idx}.csv",index=False)
    fig,ax=plt.subplots(figsize=(10,5.7)); fig.patch.set_facecolor("white")
    ax.plot(df.year,df[col],color=color,linewidth=2.8,marker="o",markersize=5.5)
    ax.fill_between(df.year,df[col],color=color,alpha=.09)
    ax.set_title(title,loc="left",fontsize=17,pad=16)
    ax.set_ylabel(ylabel,fontsize=11); ax.set_xlabel("Crash year",fontsize=10)
    ax.set_xticks(df.year); ax.tick_params(axis="x",rotation=0,labelsize=9); ax.tick_params(axis="y",labelsize=10)
    ax.grid(axis="y",color="#D9DEE3",linewidth=.8); ax.set_axisbelow(True)
    y0=int(df.loc[df.year.eq(2013),col].iloc[0]); y1=int(df.loc[df.year.eq(2025),col].iloc[0]); change=(y1/y0-1)*100
    sign="+" if change>0 else ""
    ax.annotate(f"2013  {y0:,}",(2013,y0),xytext=(7,11),textcoords="offset points",fontsize=9,color="#333")
    ax.annotate(f"2025  {y1:,} ({sign}{change:.0f}%)",(2025,y1),xytext=(-8,13),textcoords="offset points",ha="right",fontsize=9,fontweight="bold",color=color)
    ax.text(0,-.22,"Brooklyn crashes with borough recorded; annual counts, not adjusted for walking exposure. Source: NYC police-reported crash records.",transform=ax.transAxes,fontsize=8.5,color="#555")
    fig.tight_layout(); fig.savefig(out/f"option_{idx}.png",dpi=180,bbox_inches="tight"); plt.close(fig)
chart(1,"pedestrian_casualties","Brooklyn pedestrian casualties fell from 2013, then rebounded","Pedestrians injured or killed (people)",colors["blue"],["year","pedestrians_injured","pedestrians_killed","pedestrian_casualties"])
chart(2,"pedestrians_killed","Brooklyn pedestrian deaths remain volatile","Pedestrians killed (people)",colors["red"],["year","pedestrians_killed"])
chart(3,"pedestrian_involved_crashes","Crashes involving Brooklyn pedestrians are near pre-pandemic levels","Crashes with ≥1 pedestrian injured or killed (crashes)",colors["gold"],["year","pedestrian_involved_crashes"])
print(df.to_string(index=False))'
# bash
python3 -c 'import json,pathlib,pandas as pd; p=pathlib.Path("out"); o=json.loads((p/"options.json").read_text()); assert len(o["options"])==3; assert abs(sum(x["probability"] for x in o["options"])-1)<1e-9; expected=[(3671,2874),(30,39),(3498,2766)]; cols=["pedestrian_casualties","pedestrians_killed","pedestrian_involved_crashes"]; 
for i,(col,(a,b)) in enumerate(zip(cols,expected),1):
 d=pd.read_csv(p/f"values_{i}.csv"); assert len(d)==13 and int(d.loc[d.year.eq(2013),col].iloc[0])==a and int(d.loc[d.year.eq(2025),col].iloc[0])==b; assert (p/f"option_{i}.png").is_file(); print(i,a,b,round((b/a-1)*100),"%", "chart and values present")
print("JSON valid; probability total:",sum(x["probability"] for x in o["options"]))'

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
- tr_TR01: If a per-crash rate spanning 2020 is shown, the output caveats the 2020 change in crash recording.
- tr_TR15: Claims about pedestrian deaths changing are qualified by the small counts (about 30–39 per year).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.