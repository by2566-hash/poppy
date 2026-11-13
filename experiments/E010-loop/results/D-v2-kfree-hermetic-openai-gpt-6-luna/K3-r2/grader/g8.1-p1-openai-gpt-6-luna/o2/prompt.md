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
metric: Cyclist deaths per 100 motorist deaths
denominator: Annual motorist deaths
grouping: Calendar year
chart_type: Line chart
probability: 0.35
WRITTEN ANSWER:
Cyclist deaths ranged from 10 per 100 motorist deaths in 2013 to 38 per 100 in 2019, and were 28 per 100 in 2025. This framing answers how cyclist deaths compare proportionally with motorist deaths over time, and the line shows the cyclist-to-motorist count ratio fluctuating from 10 to about 38 per 100. The ratio is a defensible measure of the relative counts, but it does not measure risk per trip, distance traveled, or population.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,motorist_deaths,cyclist_deaths,cyclist_deaths_per_100_motorist_deaths
2013,110,11,10.0
2014,109,20,18.34862385321101
2015,95,15,15.789473684210526
2016,72,18,25.0
2017,107,27,25.233644859813083
2018,98,10,10.204081632653061
2019,82,31,37.80487804878049
2020,139,29,20.863309352517987
2021,134,19,14.17910447761194
2022,116,19,16.379310344827587
2023,123,31,25.203252032520325
2024,111,24,21.62162162162162
2025,81,23,28.39506172839506

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
pwd && ls
# bash
ls
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; print(c.execute("describe select * from read_parquet(?)", [p]).fetchall()); print(c.execute("select min(crash_date), max(crash_date), count(*) from read_parquet(?)", [p]).fetchall())'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; q="select year(crash_date) y, sum(coalesce(number_of_motorist_killed,0)) motorist_deaths, sum(coalesce(number_of_cyclist_killed,0)) cyclist_deaths, count(*) crashes, max(crash_date) latest_date from read_parquet(?) where crash_date >= date \"2013-01-01\" and crash_date < date \"2026-01-01\" group by 1 order by 1"; print(c.execute(q,[p]).fetchdf().to_string(index=False)); print(c.execute("select count(*) from read_parquet(?) where crash_date >= date \'2025-01-01\' and crash_date < date \'2026-01-01\'",[p]).fetchone())'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; q="select year(crash_date) y, sum(coalesce(number_of_motorist_killed,0)) motorist_deaths, sum(coalesce(number_of_cyclist_killed,0)) cyclist_deaths, count(*) crashes, max(crash_date) latest_date from read_parquet(?) where year(crash_date) between 2013 and 2025 group by 1 order by 1"; print(c.execute(q,[p]).fetchdf().to_string(index=False))'
# bash
python3 -c 'import duckdb, pandas as pd, matplotlib.pyplot as plt; from pathlib import Path; out=Path("out"); out.mkdir(exist_ok=True); con=duckdb.connect(); df=con.execute("select year(crash_date) as year, sum(coalesce(number_of_motorist_killed,0))::int as motorist_deaths, sum(coalesce(number_of_cyclist_killed,0))::int as cyclist_deaths from read_parquet(?) where year(crash_date) between 2013 and 2025 group by 1 order by 1", ["data/crashes.parquet"]).fetchdf(); df["motorist_minus_cyclist_deaths"]=df.motorist_deaths-df.cyclist_deaths; df["cyclist_deaths_per_100_motorist_deaths"]=df.cyclist_deaths/df.motorist_deaths*100; assert df.year.tolist()==list(range(2013,2026)); df[["year","motorist_deaths","cyclist_deaths","motorist_minus_cyclist_deaths"]].to_csv(out/"values_1.csv",index=False); df[["year","motorist_deaths","cyclist_deaths","cyclist_deaths_per_100_motorist_deaths"]].to_csv(out/"values_2.csv",index=False); plt.figure(figsize=(12,6.5)); x=range(len(df)); w=.38; plt.bar([i-w/2 for i in x],df.motorist_deaths,width=w,label="Motorist deaths",color="#3b6fb6"); plt.bar([i+w/2 for i in x],df.cyclist_deaths,width=w,label="Cyclist deaths",color="#e58a36"); plt.xticks(list(x),df.year); plt.ylabel("Deaths (annual total)"); plt.title("Motorist and cyclist deaths in NYC, 2013–2025"); plt.grid(axis="y",alpha=.25); plt.legend(frameon=False); plt.tight_layout(); plt.savefig(out/"option_1.png",dpi=180); plt.close(); plt.figure(figsize=(12,6.5)); plt.plot(df.year,df.cyclist_deaths_per_100_motorist_deaths,marker="o",linewidth=2.3,color="#713f8c"); plt.axhline(100,color="#777",linestyle="--",linewidth=1,label="Equal deaths (100 per 100)"); plt.xticks(df.year); plt.ylabel("Cyclist deaths per 100 motorist deaths"); plt.title("Cyclist deaths relative to motorist deaths in NYC, 2013–2025"); plt.grid(alpha=.25); plt.legend(frameon=False); plt.tight_layout(); plt.savefig(out/"option_2.png",dpi=180); plt.close(); print(df.to_string(index=False)); print("saved outputs:",sorted(p.name for p in out.iterdir()))'
# bash
python3 -c 'import duckdb, matplotlib.pyplot as plt; from pathlib import Path; out=Path("out"); df=duckdb.connect().execute("select year(crash_date) as year, sum(coalesce(number_of_motorist_killed,0))::int as motorist_deaths, sum(coalesce(number_of_cyclist_killed,0))::int as cyclist_deaths from read_parquet(?) where year(crash_date) between 2013 and 2025 group by 1 order by 1", ["data/crashes.parquet"]).fetchdf(); plt.figure(figsize=(12,6.5)); x=range(len(df)); w=.38; plt.bar([i-w/2 for i in x],df.motorist_deaths,width=w,label="Motorist deaths",color="#3b6fb6"); plt.bar([i+w/2 for i in x],df.cyclist_deaths,width=w,label="Cyclist deaths",color="#e58a36"); plt.xticks(list(x),df.year); plt.xlabel("Year"); plt.ylabel("Deaths (annual total)"); plt.title("Motorist and cyclist deaths in NYC, 2013–2025"); plt.grid(axis="y",alpha=.25); plt.legend(frameon=False); plt.tight_layout(); plt.savefig(out/"option_1.png",dpi=180); plt.close(); df["ratio"]=df.cyclist_deaths/df.motorist_deaths*100; plt.figure(figsize=(12,6.5)); plt.plot(df.year,df.ratio,marker="o",linewidth=2.3,color="#713f8c"); plt.xticks(df.year); plt.xlabel("Year"); plt.ylabel("Cyclist deaths per 100 motorist deaths"); plt.title("Cyclist deaths relative to motorist deaths in NYC, 2013–2025"); plt.ylim(0,45); plt.grid(alpha=.25); plt.tight_layout(); plt.savefig(out/"option_2.png",dpi=180); plt.close()'
# bash
python3 -c 'import json; p="out/options.json"; d=json.load(open(p)); print(len(d["options"]),sum(x["probability"] for x in d["options"])); print(all(set(x)=={"id","metric","denominator","grouping","chart_type","reason","probability","answer","interpretation"} for x in d["options"]))'

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