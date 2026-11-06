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

QUESTION ASKED: Are NYC's streets more dangerous at night? Make a chart and give a conclusion for a news report.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Fatal crashes per 1,000 crash records
denominator: Crash records with nonmissing injury and death counts
grouping: Night (8pm–5:59am) versus day (6am–7:59pm), 2012–2025
chart_type: Two-bar comparison
probability: 0.22
WRITTEN ANSWER:
These data cannot establish whether people face greater risk at night without traffic or travel-exposure data, but fatal crashes occurred at 2.90 per 1,000 nighttime crashes versus 1.08 per 1,000 daytime crashes. This framing addresses fatality severity conditional on a crash and shows a higher fatal-crash rate among nighttime records. It is a defensible measure of crash outcomes, but it cannot compare fatality risk per trip or per mile without exposure data.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
period,numerator,denominator_crashes,metric_value,metric
Night (8pm–5:59am),1591,548233,2.902050770384125,Fatal crash rate per crash
Day (6am–7:59pm),1811,1684488,1.0751041265951435,Fatal crash rate per crash

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
pwd
# bash
python3 -c 'import duckdb; p="./data/crashes.parquet"; con=duckdb.connect(); print(con.execute("DESCRIBE SELECT * FROM read_parquet(?)", [p]).fetchdf().to_string(index=False)); print(con.execute("SELECT COUNT(*) n, MIN(crash_date), MAX(crash_date), COUNT(*) FILTER (WHERE crash_time IS NULL) null_time, COUNT(*) FILTER (WHERE number_of_persons_injured IS NULL) null_inj FROM read_parquet(?)", [p]).fetchdf().to_string(index=False)); print(con.execute("SELECT EXTRACT(hour FROM crash_time) h, COUNT(*) n FROM read_parquet(?) WHERE crash_time IS NOT NULL GROUP BY h ORDER BY h", [p]).fetchdf().to_string(index=False))'
# bash
python3 -c 'import duckdb; p="./data/crashes.parquet"; q="""WITH b AS (SELECT CASE WHEN EXTRACT(hour FROM crash_time) >= 20 OR EXTRACT(hour FROM crash_time) < 6 THEN '\''Night (8pm–5:59am)'\'' ELSE '\''Day (6am–7:59pm)'\'' END period, COALESCE(number_of_persons_injured,0) injured, COALESCE(number_of_persons_killed,0) killed FROM read_parquet(?)), s AS (SELECT period, COUNT(*) crashes, COUNT(*) FILTER (WHERE injured > 0 OR killed > 0) casualty_crashes, COUNT(*) FILTER (WHERE killed > 0) fatal_crashes, SUM(injured) injured_people, SUM(killed) killed_people FROM b GROUP BY period) SELECT *, ROUND(100.0*casualty_crashes/crashes,3) casualty_crash_pct, ROUND(1000.0*fatal_crashes/crashes,3) fatal_crashes_per_1000, ROUND(100.0*(injured_people+killed_people)/crashes,3) casualties_per_100_crashes FROM s ORDER BY CASE WHEN period LIKE '\''Night%'\'' THEN 1 ELSE 2 END"""; print(duckdb.connect().execute(q,[p]).fetchdf().to_string(index=False)); print(duckdb.connect().execute("SELECT COUNT(*) FILTER (WHERE number_of_persons_injured IS NULL) ni, COUNT(*) FILTER (WHERE number_of_persons_killed IS NULL) nk, COUNT(*) FILTER (WHERE crash_time IS NULL) nt FROM read_parquet(?)",[p]).fetchdf().to_string(index=False))'
# bash
python3 -c 'import duckdb; p="./data/crashes.parquet"; q="""SELECT year(crash_date) yr, COUNT(*) n, COUNT(*) FILTER (WHERE number_of_persons_injured IS NULL) ni, COUNT(*) FILTER (WHERE number_of_persons_killed IS NULL) nk, COUNT(*) FILTER (WHERE number_of_persons_injured IS NULL OR number_of_persons_killed IS NULL) either_null FROM read_parquet(?) GROUP BY yr ORDER BY yr"""; print(duckdb.connect().execute(q,[p]).fetchdf().to_string(index=False)); print(duckdb.connect().execute("SELECT number_of_persons_injured, number_of_persons_killed, COUNT(*) n FROM read_parquet(?) WHERE number_of_persons_killed IS NULL GROUP BY 1,2 ORDER BY n DESC LIMIT 15",[p]).fetchdf().to_string(index=False))'
# bash
python3 -c 'import os, duckdb, pandas as pd, matplotlib.pyplot as plt; os.makedirs("./out", exist_ok=True); p="./data/crashes.parquet"; q="""WITH base AS (SELECT CASE WHEN EXTRACT(hour FROM crash_time) >= 20 OR EXTRACT(hour FROM crash_time) < 6 THEN '\''Night (8pm–5:59am)'\'' ELSE '\''Day (6am–7:59pm)'\'' END period, number_of_persons_injured injured, number_of_persons_killed killed FROM read_parquet(?) WHERE crash_date < DATE '\''2026-01-01'\'' AND number_of_persons_injured IS NOT NULL AND number_of_persons_killed IS NOT NULL), s AS (SELECT period, COUNT(*) crashes, COUNT(*) FILTER (WHERE injured > 0 OR killed > 0) casualty_crashes, COUNT(*) FILTER (WHERE killed > 0) fatal_crashes, SUM(injured) injured_people, SUM(killed) killed_people FROM base GROUP BY period) SELECT *, 100.0*casualty_crashes/crashes casualty_crash_pct, 1000.0*fatal_crashes/crashes fatal_crashes_per_1000, 100.0*(injured_people+killed_people)/crashes casualties_per_100_crashes FROM s ORDER BY CASE WHEN period LIKE '\''Night%'\'' THEN 1 ELSE 2 END"""; df=duckdb.connect().execute(q,[p]).fetchdf(); print(df.to_string(index=False)); metrics=[("casualty_crash_pct","Share of crashes with at least one person injured or killed","Percent of crashes","share of crashes (%)","Any injury or death per crash"),("fatal_crashes_per_1000","Fatal crashes per 1,000 recorded crashes","Fatal crashes per 1,000 crashes","fatal crashes per 1,000","Fatal crash rate per crash"),("casualties_per_100_crashes","Injured and killed people per 100 recorded crashes","People injured or killed per 100 crashes","people per 100 crashes","Casualty burden per crash")]; colors=["#17324D","#D58B32"]; order=["Night (8pm–5:59am)","Day (6am–7:59pm)"]; df=df.set_index("period").loc[order].reset_index(); note="2012–2025; night 8pm–5:59am, day 6am–7:59pm. Per-crash measures; no traffic/exposure denominator."; exec("for i,(col,title,ylabel,csvname,short) in enumerate(metrics,1):\n    numcol={1:\"casualty_crashes\",2:\"fatal_crashes\",3:None}[i]\n    rows=[]\n    for _,r in df.iterrows():\n        value=r[col]\n        numerator=r[numcol] if numcol else r[\"injured_people\"]+r[\"killed_people\"]\n        denominator=r[\"crashes\"]\n        rows.append({\"period\":r[\"period\"],\"numerator\":int(numerator),\"denominator_crashes\":int(denominator),\"metric_value\":float(value),\"metric\":short})\n    vals=pd.DataFrame(rows); vals.to_csv(f\"./out/values_{i}.csv\",index=False)\n    fig,ax=plt.subplots(figsize=(8,5.4)); bars=ax.bar([\"Night\\n8pm–5:59am\",\"Day\\n6am–7:59pm\"],vals.metric_value,color=colors,width=.58)\n    ax.set_ylabel(ylabel); ax.set_title(title,fontsize=15,weight=\"bold\",pad=14); ax.grid(axis=\"y\",alpha=.25); ax.set_axisbelow(True)\n    for b,v in zip(bars,vals.metric_value): ax.annotate(f\"{v:.2f}\",(b.get_x()+b.get_width()/2,b.get_height()),xytext=(0,6),textcoords=\"offset points\",ha=\"center\",fontsize=11,weight=\"bold\")\n    ax.text(.5,-.22,note,transform=ax.transAxes,ha=\"center\",fontsize=8.5,color=\"#444\",wrap=True); fig.tight_layout(); fig.savefig(f\"./out/option_{i}.png\",dpi=170,bbox_inches=\"tight\"); plt.close(fig)\nprint(\"Saved three charts and values files.\")")'
# bash
python3 -c 'import json, pandas as pd, os; opts=json.load(open("./out/options.json")); assert len(opts["options"])==3; assert abs(sum(x["probability"] for x in opts["options"])-1)<1e-9; expected=[("metric_value",28.270096838388056,23.20717036868176),("metric_value",2.902050770384125,1.0751041265951435),("metric_value",40.42095240527294,30.730287185186242)]; [(lambda d,e: (None if all(abs(a-b)<1e-8 for a,b in zip(d.metric_value.tolist(),e)) else (_ for _ in ()).throw(AssertionError((d.metric_value.tolist(),e)))))(pd.read_csv(f"./out/values_{i}.csv"), (n,d)) for i,(n,d) in enumerate(expected,1)]; [print(f"option {i}: chart={os.path.exists(f\"./out/option_{i}.png\")}, values={os.path.exists(f\"./out/values_{i}.csv\")}") for i in range(1,4)]; print("JSON valid; probabilities sum to",sum(x["probability"] for x in opts["options"]))'
# bash
python3 -c 'import json, pandas as pd, pathlib; opts=json.load(open("./out/options.json")); assert len(opts["options"])==3 and abs(sum(x["probability"] for x in opts["options"])-1)<1e-9; expected=[(28.270096838388056,23.20717036868176),(2.902050770384125,1.0751041265951435),(40.42095240527294,30.730287185186242)]; assert all(all(abs(a-b)<1e-8 for a,b in zip(pd.read_csv("./out/values_"+str(i)+".csv").metric_value.tolist(), pair)) for i,pair in enumerate(expected,1)); files=[pathlib.Path("./out/option_"+str(i)+".png").exists() and pathlib.Path("./out/values_"+str(i)+".csv").exists() for i in range(1,4)]; assert all(files); print("JSON valid; probabilities sum to",sum(x["probability"] for x in opts["options"])); print("All chart/value files exist and CSV metrics match the reviewed values:",files)'

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR11: Severity per crash (deaths or injuries per crash) is described as such, not as the risk of being on the street at night (no traffic volume by hour exists).
- tr_TR08: NA if the option uses no killed or injured counts. Otherwise the analysis window excludes 2026, or the 2026 rows with NULL killed counts (87.8% of May-2026, 100% of June-2026) are excluded or the resulting bias is disclosed; COALESCE to 0 alone is not handling (decided by Bo 2026-11-04).
- tr_NIGHTDEF: The definition of 'night' (hours) is stated.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.