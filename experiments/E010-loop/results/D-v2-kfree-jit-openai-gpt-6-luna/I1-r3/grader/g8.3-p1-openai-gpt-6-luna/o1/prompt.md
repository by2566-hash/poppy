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

QUESTION ASKED: Did the risk of a motorist being killed per mile driven in NYC decline from 2013 to 2025? Make a chart and answer based on this crash data.
QUESTION TYPE: insufficient
DECLARED FRAMING:
metric: Motorist deaths
denominator: None; annual count
grouping: Crash year
chart_type: Line chart
probability: 0.5
WRITTEN ANSWER:
This data cannot establish per-mile risk, but recorded motorist deaths fell from 110 in 2013 to 81 in 2025 (26% lower). These annual counts show the absolute number of motorists recorded killed in NYC police-reported crashes, falling from 110 in 2013 to 81 in 2025. A count is a direct measure of fatality burden in this dataset, but it does not adjust for distance driven and therefore leaves per-mile risk unanswered.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,motorist_deaths
2013,110
2014,109
2015,95
2016,72
2017,107
2018,98
2019,82
2020,139
2021,134
2022,116
2023,123
2024,111
2025,81

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
pwd
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("DESCRIBE SELECT * FROM read_parquet(?)", [p]).fetchdf().to_string(index=False)); print(c.execute("SELECT min(crash_date), max(crash_date), count(*), count(*) FILTER (WHERE number_of_motorist_killed IS NULL), sum(number_of_motorist_killed) FROM read_parquet(?)", [p]).fetchall())'
# bash
ls .
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; q="SELECT year(crash_date) AS year, count(*) AS crashes, sum(number_of_motorist_killed) AS motorist_deaths, count(*) FILTER (WHERE number_of_motorist_killed > 0) AS crashes_with_motorist_death FROM read_parquet(?) WHERE crash_date >= DATE \"2013-01-01\" AND crash_date < DATE \"2026-01-01\" GROUP BY 1 ORDER BY 1"; print(c.execute(q,[p]).fetchdf().to_string(index=False))'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; q="SELECT year(crash_date) AS year, count(*) AS crashes, sum(number_of_motorist_killed) AS motorist_deaths, count(*) FILTER (WHERE number_of_motorist_killed > 0) AS crashes_with_motorist_death FROM read_parquet(?) WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY 1 ORDER BY 1"; print(c.execute(q,[p]).fetchdf().to_string(index=False))'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); print(c.execute("SELECT year(crash_date) AS year, min(crash_date), max(crash_date), count(*) FROM read_parquet(\"data/crashes.parquet\") WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY 1 ORDER BY 1").fetchdf().to_string(index=False))'
# bash
python3 -c 'import duckdb, pandas as pd, matplotlib.pyplot as plt; from pathlib import Path; out=Path("out"); data=duckdb.connect().execute("SELECT year(crash_date) AS year, count(*) AS crash_reports, sum(number_of_motorist_killed) AS motorist_deaths FROM read_parquet(\"data/crashes.parquet\") WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY 1 ORDER BY 1").fetchdf(); data["motorist_deaths"]=data["motorist_deaths"].astype(int); data["deaths_per_100k_crash_reports"]=data["motorist_deaths"] / data["crash_reports"] * 100000; data[["year","motorist_deaths"]].to_csv(out/"values_1.csv",index=False); data[["year","crash_reports","motorist_deaths","deaths_per_100k_crash_reports"]].to_csv(out/"values_2.csv",index=False); fig,ax=plt.subplots(figsize=(9,5)); ax.plot(data.year,data.motorist_deaths,marker="o",linewidth=2,color="#1769aa"); ax.set(title="Motorists killed in NYC police-reported crashes",xlabel="Crash year",ylabel="Motorist deaths (people)"); ax.set_xticks(data.year); ax.tick_params(axis="x",rotation=45); ax.grid(axis="y",alpha=.25); ax.annotate(f"{data.motorist_deaths.iloc[0]} (2013)",(data.year.iloc[0],data.motorist_deaths.iloc[0]),xytext=(5,9),textcoords="offset points"); ax.annotate(f"{data.motorist_deaths.iloc[-1]} (2025)",(data.year.iloc[-1],data.motorist_deaths.iloc[-1]),xytext=(-48,9),textcoords="offset points"); fig.text(.5,.01,"Descriptive annual counts; crash data contain no vehicle-miles-traveled denominator.",ha="center",fontsize=9); fig.tight_layout(rect=(0,.05,1,1)); fig.savefig(out/"option_1.png",dpi=160,bbox_inches="tight"); plt.close(fig); fig,ax=plt.subplots(figsize=(9,5)); ax.plot(data.year,data.deaths_per_100k_crash_reports,marker="o",linewidth=2,color="#b24a32"); ax.set(title="Motorist deaths per 100,000 reported crashes",xlabel="Crash year",ylabel="Deaths per 100,000 crash reports"); ax.set_xticks(data.year); ax.tick_params(axis="x",rotation=45); ax.grid(axis="y",alpha=.25); ax.annotate(f"{data.deaths_per_100k_crash_reports.iloc[0]:.1f} (2013)",(data.year.iloc[0],data.deaths_per_100k_crash_reports.iloc[0]),xytext=(5,9),textcoords="offset points"); ax.annotate(f"{data.deaths_per_100k_crash_reports.iloc[-1]:.1f} (2025)",(data.year.iloc[-1],data.deaths_per_100k_crash_reports.iloc[-1]),xytext=(-48,9),textcoords="offset points"); fig.text(.5,.01,"Crash-report denominator is not distance driven; this is not per-mile risk.",ha="center",fontsize=9); fig.tight_layout(rect=(0,.05,1,1)); fig.savefig(out/"option_2.png",dpi=160,bbox_inches="tight"); plt.close(fig); print(data.to_string(index=False))'
# bash
python3 -c 'import json; from pathlib import Path; p=Path("out"); d=json.loads((p/"options.json").read_text()); assert len(d["options"])==2; assert abs(sum(x["probability"] for x in d["options"])-1)<1e-9; required=["option_1.png","values_1.csv","option_2.png","values_2.csv"]; assert all((p/n).is_file() for n in required); print("JSON valid; probabilities sum to",sum(x["probability"] for x in d["options"])); print("Output files present:",", ".join(required+["options.json"]))'

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR01: If a per-reported-crash rate spanning 2020 is shown, the output says that the number of recorded crashes changes sharply around 2020 and that this affects comparing the per-crash rate across years (naming the cause, the 2020 recording change, is not required: it is not in the data or the dictionary).
- tr_PERMILE: A per-reported-crash rate, if shown, is not presented as a substitute for per-mile risk.
- tr_VMT: No vehicle-miles figure is imported, assumed or estimated from outside the data.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence
- required_statement: PASS if the output states, in its own words: Per-mile (per vehicle-mile) risk cannot be determined from this data because it has no vehicle-miles or traffic volume.

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.