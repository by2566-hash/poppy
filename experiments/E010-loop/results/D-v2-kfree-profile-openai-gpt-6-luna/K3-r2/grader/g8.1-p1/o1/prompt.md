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
metric: Annual number of motorist and cyclist deaths
denominator: None; annual summed death counts
grouping: Year and road-user category
chart_type: Grouped bar chart
probability: 0.75
WRITTEN ANSWER:
Motorist deaths exceeded cyclist deaths in every year: motorists ranged from 72 in 2016 to 139 in 2020, while cyclist deaths ranged from 10 in 2018 to 31 in both 2019 and 2023. This framing directly answers how many motorist and cyclist deaths occurred year by year, and the chart shows the motorist total was higher in each year. Comparing counts is a defensible direct measure of the annual burden, but it does not express the cyclist deaths as a share of deaths across these two groups.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,motorist_deaths,cyclist_deaths
2013,110.0,11.0
2014,109.0,20.0
2015,95.0,15.0
2016,72.0,18.0
2017,107.0,27.0
2018,98.0,10.0
2019,82.0,31.0
2020,139.0,29.0
2021,134.0,19.0
2022,116.0,19.0
2023,123.0,31.0
2024,111.0,24.0
2025,81.0,23.0

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python -c 'import duckdb; p="./data/crashes.parquet"; print(duckdb.sql(f"SELECT year(crash_date) AS year, SUM(number_of_motorist_killed) AS motorist_deaths, SUM(number_of_cyclist_killed) AS cyclist_deaths, SUM(number_of_motorist_killed)-SUM(number_of_cyclist_killed) AS gap FROM read_parquet(\"{p}\") WHERE crash_date >= DATE \"2013-01-01\" AND crash_date < DATE \"2026-01-01\" GROUP BY 1 ORDER BY 1").df().to_string(index=False))'
# bash
python -c 'import duckdb; p="./data/crashes.parquet"; q=f"SELECT year(crash_date) AS year, SUM(number_of_motorist_killed) AS motorist_deaths, SUM(number_of_cyclist_killed) AS cyclist_deaths, SUM(number_of_motorist_killed)-SUM(number_of_cyclist_killed) AS gap FROM read_parquet(\"{p}\") WHERE crash_date >= DATE [39m2013-01-01[39m AND crash_date < DATE [39m2026-01-01[39m GROUP BY 1 ORDER BY 1"; print(duckdb.sql(q).df().to_string(index=False))'
# bash
python -c 'import duckdb; print(duckdb.sql("SELECT year(crash_date) AS year, SUM(number_of_motorist_killed) AS motorist_deaths, SUM(number_of_cyclist_killed) AS cyclist_deaths FROM read_parquet(\"./data/crashes.parquet\") WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY 1 ORDER BY 1").df().to_string(index=False))'
# bash
python -c 'import duckdb, pandas as pd, matplotlib.pyplot as plt, numpy as np, os; os.makedirs("./out", exist_ok=True); q="SELECT year(crash_date) AS year, SUM(number_of_motorist_killed) AS motorist_deaths, SUM(number_of_cyclist_killed) AS cyclist_deaths FROM read_parquet(\"./data/crashes.parquet\") WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY 1 ORDER BY 1"; df=duckdb.sql(q).df(); df[["year","motorist_deaths","cyclist_deaths"]].to_csv("./out/values_1.csv", index=False); years=df["year"].astype(int).to_numpy(); x=np.arange(len(df)); w=0.38; fig,ax=plt.subplots(figsize=(11,5.8)); ax.bar(x-w/2,df["motorist_deaths"],width=w,label="Motorists",color="#2369a1"); ax.bar(x+w/2,df["cyclist_deaths"],width=w,label="Cyclists",color="#e17c32"); ax.set_xticks(x,years); ax.set_xlabel("Year"); ax.set_ylabel("Deaths (annual total)"); ax.set_title("Motorist and cyclist deaths in NYC crashes, 2013–2025"); ax.legend(frameon=False); ax.grid(axis="y",alpha=.25); ax.set_axisbelow(True); fig.tight_layout(); fig.savefig("./out/option_1.png",dpi=180); plt.close(fig); df["combined_deaths"]=df["motorist_deaths"]+df["cyclist_deaths"]; df["motorist_share_pct"]=100*df["motorist_deaths"]/df["combined_deaths"]; df["cyclist_share_pct"]=100*df["cyclist_deaths"]/df["combined_deaths"]; df[["year","motorist_deaths","cyclist_deaths","combined_deaths","motorist_share_pct","cyclist_share_pct"]].to_csv("./out/values_2.csv",index=False,float_format="%.2f"); fig,ax=plt.subplots(figsize=(11,5.8)); ax.bar(x,df["motorist_share_pct"],label="Motorists",color="#2369a1"); ax.bar(x,df["cyclist_share_pct"],bottom=df["motorist_share_pct"],label="Cyclists",color="#e17c32"); ax.set_xticks(x,years); ax.set_ylim(0,100); ax.set_xlabel("Year"); ax.set_ylabel("Share of motorist + cyclist deaths (%)"); ax.set_title("Composition of motorist and cyclist deaths in NYC crashes, 2013–2025"); ax.legend(frameon=False,loc="upper right"); ax.grid(axis="y",alpha=.25); ax.set_axisbelow(True); fig.tight_layout(); fig.savefig("./out/option_2.png",dpi=180); plt.close(fig); print(df[["year","motorist_deaths","cyclist_deaths","combined_deaths","cyclist_share_pct"]].to_string(index=False))'
# bash
python -c 'import json, pathlib; p=pathlib.Path("./out/options.json"); data=json.loads(p.read_text()); print("valid JSON; options:", len(data["options"])); print("files:", sorted(x.name for x in pathlib.Path("./out").iterdir()))'

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