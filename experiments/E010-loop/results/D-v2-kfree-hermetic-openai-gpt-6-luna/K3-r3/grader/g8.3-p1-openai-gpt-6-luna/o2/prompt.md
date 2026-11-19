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
metric: Annual total number of motorist and cyclist deaths
denominator: None; counts of people killed
grouping: Year, with paired road-user-category bars
chart_type: Grouped bar chart
probability: 0.3
WRITTEN ANSWER:
Grouped annual counts show more motorist than cyclist deaths in all years from 2013 to 2025, with yearly totals of 72–139 versus 10–31. This framing answers the year-by-year absolute-count comparison, and the paired bars show motorists above cyclists in each year. It is defensible when the reader's main task is to compare the two categories within each calendar year. It does not summarize the difference as a single gap or relative ratio, and it does not indicate risk per trip or person.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
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
ls -la
# bash
python -c 'import duckdb; p="data/crashes.parquet"; print(duckdb.sql(f"SELECT min(crash_date), max(crash_date), count(*) FROM read_parquet(\"{p}\")").df().to_string(index=False)); print(duckdb.sql(f"SELECT year(crash_date) AS year, sum(coalesce(number_of_motorist_killed,0)) AS motorist_deaths, sum(coalesce(number_of_cyclist_killed,0)) AS cyclist_deaths, count(*) AS crashes FROM read_parquet(\"{p}\") WHERE crash_date >= DATE '\''2013-01-01'\'' AND crash_date < DATE '\''2026-01-01'\'' GROUP BY year ORDER BY year").df().to_string(index=False))'
# bash
python -c 'import duckdb, pandas as pd, matplotlib.pyplot as plt, numpy as np; from pathlib import Path; out=Path("out"); data=duckdb.sql("SELECT year(crash_date) AS year, CAST(sum(coalesce(number_of_motorist_killed,0)) AS BIGINT) AS motorist_deaths, CAST(sum(coalesce(number_of_cyclist_killed,0)) AS BIGINT) AS cyclist_deaths FROM read_parquet(\"data/crashes.parquet\") WHERE crash_date >= DATE '\''2013-01-01'\'' AND crash_date < DATE '\''2026-01-01'\'' GROUP BY year ORDER BY year").df(); data["motorist_minus_cyclist"]=data.motorist_deaths-data.cyclist_deaths; data["motorist_to_cyclist_ratio"]=data.motorist_deaths/data.cyclist_deaths; years=data.year.astype(int).to_numpy(); plt.rcParams.update({"font.size":10,"axes.titlesize":13});
# Option 1: paired trend lines
fig,ax=plt.subplots(figsize=(10,5.5)); ax.plot(years,data.motorist_deaths,marker="o",linewidth=2.4,label="Motorists"); ax.plot(years,data.cyclist_deaths,marker="o",linewidth=2.4,label="Cyclists"); ax.set(title="NYC motorist and cyclist deaths by year, 2013–2025",xlabel="Year",ylabel="People killed (annual total)"); ax.set_xticks(years); ax.grid(axis="y",alpha=.25); ax.legend(frameon=False); fig.tight_layout(); fig.savefig(out/"option_1.png",dpi=180); plt.close(fig); data[["year","motorist_deaths","cyclist_deaths"]].to_csv(out/"values_1.csv",index=False);
# Option 2: paired annual columns
fig,ax=plt.subplots(figsize=(11,5.5)); x=np.arange(len(years)); w=.38; ax.bar(x-w/2,data.motorist_deaths,width=w,label="Motorists"); ax.bar(x+w/2,data.cyclist_deaths,width=w,label="Cyclists"); ax.set(title="Annual motorist and cyclist deaths in NYC, 2013–2025",xlabel="Year",ylabel="People killed (annual total)",xticks=x,xticklabels=years); ax.grid(axis="y",alpha=.25); ax.legend(frameon=False); fig.tight_layout(); fig.savefig(out/"option_2.png",dpi=180); plt.close(fig); data[["year","motorist_deaths","cyclist_deaths"]].to_csv(out/"values_2.csv",index=False);
# Option 3: annual absolute difference
fig,ax=plt.subplots(figsize=(10,5.5)); vals=data.motorist_minus_cyclist; colors=["#d95f02" if v>=0 else "#1b9e77" for v in vals]; ax.bar(years,vals,color=colors,width=.72); ax.axhline(0,color="black",linewidth=.8); ax.set(title="Annual motorist deaths minus cyclist deaths, NYC, 2013–2025",xlabel="Year",ylabel="Difference in people killed (motorists − cyclists)"); ax.set_xticks(years); ax.grid(axis="y",alpha=.25); fig.tight_layout(); fig.savefig(out/"option_3.png",dpi=180); plt.close(fig); data[["year","motorist_minus_cyclist"]].to_csv(out/"values_3.csv",index=False);
# Option 4: annual ratio
fig,ax=plt.subplots(figsize=(10,5.5)); vals=data.motorist_to_cyclist_ratio; ax.plot(years,vals,marker="o",color="#7570b3",linewidth=2.4); ax.axhline(1,color="black",linestyle="--",linewidth=1,label="Equal counts"); ax.set(title="Motorist-to-cyclist death ratio by year, NYC, 2013–2025",xlabel="Year",ylabel="Motorist deaths per cyclist death"); ax.set_xticks(years); ax.grid(axis="y",alpha=.25); ax.legend(frameon=False); fig.tight_layout(); fig.savefig(out/"option_4.png",dpi=180); plt.close(fig); data[["year","motorist_deaths","cyclist_deaths","motorist_to_cyclist_ratio"]].to_csv(out/"values_4.csv",index=False);
print(data.to_string(index=False)); print("\\nmin/max gap",data.motorist_minus_cyclist.min(),data.motorist_minus_cyclist.max()); print("min/max ratio",data.motorist_to_cyclist_ratio.min(),data.motorist_to_cyclist_ratio.max())'
# bash
python -c 'import json; p="out/options.json"; d=json.load(open(p)); print("valid JSON; options:",len(d["options"]),"probability sum:",sum(o["probability"] for o in d["options"]))'

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