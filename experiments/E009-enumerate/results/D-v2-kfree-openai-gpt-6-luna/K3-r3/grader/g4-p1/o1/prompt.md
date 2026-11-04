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

QUESTION ASKED: How do motorist and cyclist deaths compare year by year in NYC, 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Annual deaths
denominator: None; absolute counts
grouping: Crash year and road-user category (motorist or cyclist)
chart_type: Two-series line chart
probability: 0.55
WRITTEN ANSWER:
Motorist deaths exceeded cyclist deaths in every year; motorist deaths peaked at 139 in 2020, while cyclist deaths peaked at 31 in 2019 and 2023. This framing answers the year-by-year comparison by showing both annual death totals on a shared timeline; motorist deaths were higher throughout, and the lines show each series' changes over time. A line chart is defensible because the years are ordered and the trajectories matter. It does not compare risk per traveler or explain causes, which these fields cannot establish.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,motorist_deaths,cyclist_deaths
2013,110,11
2014,109,20
2015,95,15
2016,72,18
2017,107,27
2018,98,10
2019,82,31
2020,139,29
2021,134,19
2022,116,19
2023,123,31
2024,111,24
2025,81,23

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("SELECT MIN(crash_date), MAX(crash_date), COUNT(*) FROM read_parquet(?)", [p]).fetchall()); print(c.execute("SELECT EXTRACT(YEAR FROM crash_date)::INT year, SUM(number_of_motorist_killed) motorist_deaths, SUM(number_of_cyclist_killed) cyclist_deaths, COUNT(*) crashes FROM read_parquet(?) WHERE crash_date >= DATE \"2013-01-01\" AND crash_date < DATE \"2026-01-01\" GROUP BY year ORDER BY year", [p]).df().to_string(index=False))'
# bash
python -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); q="SELECT EXTRACT(YEAR FROM crash_date)::INT AS yr, SUM(number_of_motorist_killed) AS motorist_deaths, SUM(number_of_cyclist_killed) AS cyclist_deaths, COUNT(*) AS crashes FROM read_parquet(?) WHERE crash_date >= DATE ''2013-01-01'' AND crash_date < DATE ''2026-01-01'' GROUP BY yr ORDER BY yr"; print(c.execute(q,[p]).df().to_string(index=False))'
# bash
python -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); q="SELECT EXTRACT(YEAR FROM crash_date)::INT AS yr, SUM(number_of_motorist_killed) AS motorist_deaths, SUM(number_of_cyclist_killed) AS cyclist_deaths, COUNT(*) AS crashes FROM read_parquet(?) WHERE EXTRACT(YEAR FROM crash_date) BETWEEN 2013 AND 2025 GROUP BY yr ORDER BY yr"; print(c.execute(q,[p]).df().to_string(index=False))'
# bash
ls
# bash
python -c 'import duckdb, pandas as pd, matplotlib.pyplot as plt, json, os; p="data/crashes.parquet"; out="out"; os.makedirs(out, exist_ok=True); con=duckdb.connect(); df=con.execute("SELECT EXTRACT(YEAR FROM crash_date)::INT AS year, CAST(SUM(number_of_motorist_killed) AS BIGINT) AS motorist_deaths, CAST(SUM(number_of_cyclist_killed) AS BIGINT) AS cyclist_deaths FROM read_parquet(?) WHERE EXTRACT(YEAR FROM crash_date) BETWEEN 2013 AND 2025 GROUP BY year ORDER BY year", [p]).df(); df.to_csv(out+"/values_1.csv", index=False); df.to_csv(out+"/values_2.csv", index=False); years=df.year.astype(int); motor=df.motorist_deaths.astype(int); cycle=df.cyclist_deaths.astype(int); plt.figure(figsize=(11.5,6.4)); plt.plot(years,motor,color="#1f5a94",marker="o",linewidth=2.6,markersize=5.5,label="Motorist deaths"); plt.plot(years,cycle,color="#d17b27",marker="o",linewidth=2.6,markersize=5.5,label="Cyclist deaths"); plt.xticks(years, rotation=0); plt.xlim(2012.7,2025.3); plt.ylim(0,160); plt.ylabel("Deaths (count)"); plt.xlabel("Year of crash"); plt.title("Motorist and cyclist deaths in NYC by year, 2013–2025"); plt.suptitle("Annual sums of crash-level deaths reported in the crash file",y=.94,fontsize=10,color="#555555"); plt.grid(axis="y",alpha=.25); plt.legend(frameon=False,ncol=2,loc="upper left"); plt.tight_layout(rect=[0,0,1,.92]); plt.savefig(out+"/option_1.png",dpi=180,bbox_inches="tight"); plt.close(); x=range(len(df)); width=.38; plt.figure(figsize=(11.5,6.4)); plt.bar([i-width/2 for i in x],motor,width,color="#1f5a94",label="Motorist deaths"); plt.bar([i+width/2 for i in x],cycle,width,color="#d17b27",label="Cyclist deaths"); plt.xticks(list(x),years); plt.ylim(0,160); plt.ylabel("Deaths (count)"); plt.xlabel("Year of crash"); plt.title("Motorist and cyclist deaths in NYC by year, 2013–2025"); plt.suptitle("Annual sums of crash-level deaths reported in the crash file",y=.94,fontsize=10,color="#555555"); plt.grid(axis="y",alpha=.25); plt.legend(frameon=False,ncol=2,loc="upper left"); plt.tight_layout(rect=[0,0,1,.92]); plt.savefig(out+"/option_2.png",dpi=180,bbox_inches="tight"); plt.close(); print(df.to_string(index=False)); print("Saved two charts and values CSVs")'
# bash
python -c 'import json, pathlib; p=pathlib.Path("out/options.json"); d=json.loads(p.read_text()); print("JSON valid; option IDs:", [o["id"] for o in d["options"]]); print("Probability sum:", sum(o["probability"] for o in d["options"])); print("Artifacts:", sorted(str(x) for x in pathlib.Path("out").glob("option_*.png"))+sorted(str(x) for x in pathlib.Path("out").glob("values_*.csv")))'

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR15: Claims about cyclist deaths changing sharply (e.g. 'tripled') are qualified by the small counts (10 → 31).
- tr_TR03: The output does not claim that motorist + cyclist deaths are all deaths (pedestrians and unclassified deaths exist).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.