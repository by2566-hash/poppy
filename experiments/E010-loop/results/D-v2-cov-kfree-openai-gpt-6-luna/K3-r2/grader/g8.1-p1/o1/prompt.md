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
metric: Annual motorist and cyclist deaths
denominator: None; counts are summed deaths, not normalized by crashes, population, or exposure
grouping: Calendar year and road-user type
chart_type: Grouped bar chart
probability: 0.65
WRITTEN ANSWER:
Motorist deaths exceeded cyclist deaths every year; motorist deaths peaked at 139 in 2020, while cyclist deaths peaked at 31 in both 2019 and 2023. This answers the yearly count comparison directly: motorist deaths were higher in every year, with a maximum of 139 in 2020 versus a cyclist maximum of 31 in both 2019 and 2023. Comparing annual totals is defensible because the question asks how many deaths each group had year by year, and both groups use the same time scale. It does not adjust for population, travel exposure, or crash volume, so it does not compare individual risk. It uses rows dated 2013–2025 and leaves out 136,969 of 2,269,187 file rows (6.04%) dated outside that range; no included year is partial, and none of the included rows has a NULL date or fatality value needed for this calculation.

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
ls data && python -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; print(c.execute("DESCRIBE SELECT * FROM read_parquet(?)", [p]).fetchall()); print(c.execute("SELECT min(crash_date), max(crash_date), count(*) FROM read_parquet(?)", [p]).fetchall()); print(c.execute("SELECT year(crash_date), count(*), sum(number_of_motorist_killed), sum(number_of_cyclist_killed), count(*) FILTER (WHERE number_of_motorist_killed IS NULL), count(*) FILTER (WHERE number_of_cyclist_killed IS NULL) FROM read_parquet(?) WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY 1 ORDER BY 1", [p]).fetchall())'
# bash
python -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; print(c.execute("SELECT year(crash_date), min(crash_date), max(crash_date), count(*) FROM read_parquet(?) WHERE crash_date BETWEEN DATE '\''2013-01-01'\'' AND DATE '\''2025-12-31'\'' GROUP BY 1 ORDER BY 1", [p]).fetchall()); print(c.execute("SELECT count(*) total, count(*) FILTER (WHERE crash_date IS NULL) no_date, count(*) FILTER (WHERE crash_date < DATE '\''2013-01-01'\'' OR crash_date >= DATE '\''2026-01-01'\'') outside FROM read_parquet(?)", [p]).fetchall()); print(c.execute("SELECT year(crash_date), sum(number_of_motorist_killed), sum(number_of_cyclist_killed), sum(number_of_cyclist_killed)::DOUBLE/sum(number_of_motorist_killed), sum(number_of_motorist_killed)-sum(number_of_cyclist_killed) FROM read_parquet(?) WHERE crash_date >= DATE '\''2013-01-01'\'' AND crash_date < DATE '\''2026-01-01'\'' GROUP BY 1 ORDER BY 1", [p]).fetchall())'
# bash
ls .
# bash
python -c 'import duckdb, pandas as pd, matplotlib.pyplot as plt, numpy as np
from pathlib import Path
out=Path("out"); out.mkdir(exist_ok=True)
db=duckdb.connect()
query="""SELECT year(crash_date) AS year, sum(number_of_motorist_killed)::BIGINT AS motorist_deaths, sum(number_of_cyclist_killed)::BIGINT AS cyclist_deaths, count(*) AS crash_rows, count(*) FILTER (WHERE number_of_motorist_killed IS NULL) AS null_motorist, count(*) FILTER (WHERE number_of_cyclist_killed IS NULL) AS null_cyclist FROM read_parquet(\"data/crashes.parquet\") WHERE crash_date >= DATE \"2013-01-01\" AND crash_date < DATE \"2026-01-01\" GROUP BY 1 ORDER BY 1"""
df=db.execute(query).df()
assert df.year.tolist()==list(range(2013,2026))
assert (df[["null_motorist","null_cyclist"]].to_numpy()==0).all()
df["cyclist_as_pct_of_motorist"]=df.cyclist_deaths/df.motorist_deaths*100
# Option 1: annual count comparison
v1=df[["year","motorist_deaths","cyclist_deaths"]]
v1.to_csv(out/"values_1.csv",index=False)
x=np.arange(len(df)); width=0.38
fig,ax=plt.subplots(figsize=(12,6))
ax.bar(x-width/2,df.motorist_deaths,width,label="Motorist deaths",color="#3569a8")
ax.bar(x+width/2,df.cyclist_deaths,width,label="Cyclist deaths",color="#e58a32")
ax.set_xticks(x,df.year.astype(str),rotation=45,ha="right")
ax.set_ylabel("Deaths (people)"); ax.set_xlabel("Calendar year")
ax.set_title("Motorist and cyclist deaths in NYC, 2013–2025")
ax.legend(frameon=False); ax.grid(axis="y",alpha=.25); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig(out/"option_1.png",dpi=180); plt.close(fig)
# Option 2: cyclist deaths as a proportion of motorist deaths
v2=df[["year","motorist_deaths","cyclist_deaths","cyclist_as_pct_of_motorist"]]
v2.to_csv(out/"values_2.csv",index=False,float_format="%.4f")
fig,ax=plt.subplots(figsize=(11,5.5))
ax.plot(df.year,df.cyclist_as_pct_of_motorist,marker="o",linewidth=2,color="#7156a5")
ax.set_xticks(df.year); ax.tick_params(axis="x",rotation=45)
ax.set_ylabel("Cyclist deaths as % of motorist deaths")
ax.set_xlabel("Calendar year"); ax.set_title("Cyclist-to-motorist death ratio in NYC, 2013–2025")
ax.grid(axis="y",alpha=.3); ax.set_axisbelow(True); fig.tight_layout()
fig.savefig(out/"option_2.png",dpi=180); plt.close(fig)
# Persist exact coverage diagnostics for review
coverage=db.execute("""SELECT count(*) AS total_rows, count(*) FILTER (WHERE crash_date IS NULL OR crash_date < DATE \"2013-01-01\" OR crash_date >= DATE \"2026-01-01\") AS excluded_rows FROM read_parquet(\"data/crashes.parquet\")""").fetchone()
print("annual rows:",df.to_dict(orient="records")); print("coverage total/excluded:",coverage,"excluded share:",coverage[1]/coverage[0]*100)
'
# bash
python -c 'import duckdb, pandas as pd, matplotlib.pyplot as plt, numpy as np
from pathlib import Path
out=Path("out"); out.mkdir(exist_ok=True)
db=duckdb.connect()
query="""SELECT year(crash_date) AS year, sum(number_of_motorist_killed)::BIGINT AS motorist_deaths, sum(number_of_cyclist_killed)::BIGINT AS cyclist_deaths, count(*) AS crash_rows, count(*) FILTER (WHERE number_of_motorist_killed IS NULL) AS null_motorist, count(*) FILTER (WHERE number_of_cyclist_killed IS NULL) AS null_cyclist FROM read_parquet(?) WHERE crash_date >= make_date(2013,1,1) AND crash_date < make_date(2026,1,1) GROUP BY 1 ORDER BY 1"""
df=db.execute(query,["data/crashes.parquet"]).df()
assert df.year.tolist()==list(range(2013,2026))
assert (df[["null_motorist","null_cyclist"]].to_numpy()==0).all()
df["cyclist_as_pct_of_motorist"]=df.cyclist_deaths/df.motorist_deaths*100
v1=df[["year","motorist_deaths","cyclist_deaths"]]
v1.to_csv(out/"values_1.csv",index=False)
x=np.arange(len(df)); width=0.38
fig,ax=plt.subplots(figsize=(12,6))
ax.bar(x-width/2,df.motorist_deaths,width,label="Motorist deaths",color="#3569a8")
ax.bar(x+width/2,df.cyclist_deaths,width,label="Cyclist deaths",color="#e58a32")
ax.set_xticks(x,df.year.astype(str),rotation=45,ha="right")
ax.set_ylabel("Deaths (people)"); ax.set_xlabel("Calendar year")
ax.set_title("Motorist and cyclist deaths in NYC, 2013–2025")
ax.legend(frameon=False); ax.grid(axis="y",alpha=.25); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig(out/"option_1.png",dpi=180); plt.close(fig)
v2=df[["year","motorist_deaths","cyclist_deaths","cyclist_as_pct_of_motorist"]]
v2.to_csv(out/"values_2.csv",index=False,float_format="%.4f")
fig,ax=plt.subplots(figsize=(11,5.5))
ax.plot(df.year,df.cyclist_as_pct_of_motorist,marker="o",linewidth=2,color="#7156a5")
ax.set_xticks(df.year); ax.tick_params(axis="x",rotation=45)
ax.set_ylabel("Cyclist deaths as % of motorist deaths")
ax.set_xlabel("Calendar year"); ax.set_title("Cyclist-to-motorist death ratio in NYC, 2013–2025")
ax.grid(axis="y",alpha=.3); ax.set_axisbelow(True); fig.tight_layout()
fig.savefig(out/"option_2.png",dpi=180); plt.close(fig)
coverage=db.execute("""SELECT count(*) AS total_rows, count(*) FILTER (WHERE crash_date IS NULL OR crash_date < make_date(2013,1,1) OR crash_date >= make_date(2026,1,1)) AS excluded_rows FROM read_parquet(?)""",["data/crashes.parquet"]).fetchone()
print("annual rows:",df.to_dict(orient="records")); print("coverage total/excluded:",coverage,"excluded share:",coverage[1]/coverage[0]*100)
'
# bash
python -c 'import json, pandas as pd; p="out/options.json"; d=json.load(open(p)); assert abs(sum(x["probability"] for x in d["options"])-1)<1e-9; assert [x["id"] for x in d["options"]]==[1,2]; a=pd.read_csv("out/values_1.csv"); b=pd.read_csv("out/values_2.csv"); assert a[["year","motorist_deaths","cyclist_deaths"]].equals(b[["year","motorist_deaths","cyclist_deaths"]]); assert len(a)==13; print("JSON valid; probabilities sum to",sum(x["probability"] for x in d["options"])); print("CSV row counts and shared count fields verified.")'

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