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

QUESTION ASKED: How do motorist and cyclist deaths compare year by year in NYC, 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Annual number of reported motorist and cyclist deaths
denominator: None; count of deaths
grouping: Year and road-user type
chart_type: Two-series line chart
probability: 0.45
WRITTEN ANSWER:
Motorist deaths exceeded cyclist deaths in every year, ranging from 72 versus 18 in 2016 to 139 versus 29 in 2020. This framing answers how the annual death counts for the two road-user groups compare, with motorists higher in every year shown. Counts are a defensible direct comparison, but without travel or population exposure data they do not compare per-trip or per-person risk.

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
ls
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("DESCRIBE SELECT * FROM read_parquet(?)",[p]).fetchall()); print(c.execute("SELECT MIN(crash_date), MAX(crash_date), COUNT(*) FROM read_parquet(?)",[p]).fetchall()); print(c.execute("SELECT year(crash_date) y, SUM(number_of_motorist_killed) motorist, SUM(number_of_cyclist_killed) cyclist, SUM(number_of_persons_killed) total FROM read_parquet(?) WHERE crash_date >= DATE \'2013-01-01\' AND crash_date < DATE \'2026-01-01\' GROUP BY y ORDER BY y",[p]).fetchall())'
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("DESCRIBE SELECT * FROM read_parquet(?)",[p]).fetchall()); print(c.execute("SELECT MIN(crash_date), MAX(crash_date), COUNT(*) FROM read_parquet(?)",[p]).fetchall()); print(c.execute("SELECT year(crash_date) y, SUM(number_of_motorist_killed) motorist, SUM(number_of_cyclist_killed) cyclist, SUM(number_of_persons_killed) total FROM read_parquet(?) WHERE crash_date >= ? AND crash_date < ? GROUP BY y ORDER BY y",[p,"2013-01-01","2026-01-01"]).fetchall())'
# bash
python3 -c 'import duckdb, pandas as pd, matplotlib.pyplot as plt, os; p="data/crashes.parquet"; out="out"; os.makedirs(out, exist_ok=True); con=duckdb.connect(); df=con.execute("SELECT year(crash_date) AS year, COALESCE(SUM(number_of_motorist_killed), 0)::BIGINT AS motorist_deaths, COALESCE(SUM(number_of_cyclist_killed), 0)::BIGINT AS cyclist_deaths FROM read_parquet(?) WHERE crash_date >= ? AND crash_date < ? GROUP BY year ORDER BY year", [p,"2013-01-01","2026-01-01"]).df(); df["year"]=df["year"].astype(int); assert df["year"].tolist()==list(range(2013,2026)); df.to_csv(out+"/values_1.csv",index=False); plt.figure(figsize=(10,5.5)); plt.plot(df.year,df.motorist_deaths,marker="o",linewidth=2.3,label="Motorist deaths",color="#2463A6"); plt.plot(df.year,df.cyclist_deaths,marker="o",linewidth=2.3,label="Cyclist deaths",color="#E07A24"); plt.xticks(df.year,rotation=45); plt.ylabel("Deaths"); plt.xlabel("Year"); plt.title("Motorist and cyclist deaths by year, NYC (2013–2025)"); plt.grid(axis="y",alpha=.25); plt.legend(frameon=False); plt.tight_layout(); plt.savefig(out+"/option_1.png",dpi=180); plt.close(); gap=df[["year","motorist_deaths","cyclist_deaths"]].copy(); gap["motorist_minus_cyclist_deaths"]=gap.motorist_deaths-gap.cyclist_deaths; gap[["year","motorist_minus_cyclist_deaths"]].to_csv(out+"/values_2.csv",index=False); plt.figure(figsize=(10,5.5)); colors=["#2463A6" if x>=0 else "#E07A24" for x in gap.motorist_minus_cyclist_deaths]; plt.bar(gap.year,gap.motorist_minus_cyclist_deaths,color=colors,width=.72); plt.xticks(df.year,rotation=45); plt.ylabel("More motorist than cyclist deaths"); plt.xlabel("Year"); plt.title("Annual gap: motorist deaths minus cyclist deaths, NYC (2013–2025)"); plt.axhline(0,color="#444444",linewidth=.9); plt.grid(axis="y",alpha=.25); plt.tight_layout(); plt.savefig(out+"/option_2.png",dpi=180); plt.close(); share=df.copy(); share["combined_deaths"]=share.motorist_deaths+share.cyclist_deaths; share["cyclist_share_pct"]=100*share.cyclist_deaths/share.combined_deaths; share[["year","motorist_deaths","cyclist_deaths","combined_deaths","cyclist_share_pct"]].to_csv(out+"/values_3.csv",index=False,float_format="%.4f"); plt.figure(figsize=(10,5.5)); plt.plot(share.year,share.cyclist_share_pct,marker="o",linewidth=2.3,color="#7B4AB5"); plt.xticks(df.year,rotation=45); plt.ylabel("Cyclist share of motorist + cyclist deaths (%)"); plt.xlabel("Year"); plt.title("Cyclist share of deaths among motorists and cyclists, NYC (2013–2025)"); plt.ylim(0, max(35,share.cyclist_share_pct.max()+4)); plt.grid(axis="y",alpha=.25); plt.tight_layout(); plt.savefig(out+"/option_3.png",dpi=180); plt.close(); print(df.to_string(index=False)); print("\nGAP range",gap.motorist_minus_cyclist_deaths.min(),gap.loc[gap.motorist_minus_cyclist_deaths.idxmin(),"year"],gap.motorist_minus_cyclist_deaths.max(),gap.loc[gap.motorist_minus_cyclist_deaths.idxmax(),"year"]); print("\nSHARE range",share.cyclist_share_pct.min(),share.loc[share.cyclist_share_pct.idxmin(),"year"],share.cyclist_share_pct.max(),share.loc[share.cyclist_share_pct.idxmax(),"year"])'
# bash
python3 -c 'import json, os; p="out/options.json"; d=json.load(open(p)); assert len(d["options"])==3; assert abs(sum(o["probability"] for o in d["options"])-1)<1e-9; assert all(os.path.isfile("out/option_%d.png"%i) and os.path.isfile("out/values_%d.csv"%i) for i in range(1,4)); print("JSON valid; probabilities sum to",sum(o["probability"] for o in d["options"])); print("All three charts and values files exist")'

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