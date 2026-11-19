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
metric: Annual number of motorist and cyclist fatalities
denominator: None; raw counts of persons killed in crashes during each calendar year
grouping: Crash year and road-user group (motorist, cyclist)
chart_type: Two-series line chart
probability: 0.7
WRITTEN ANSWER:
Motorist deaths exceeded cyclist deaths every year; annual counts ranged from 72 to 139 motorists and 10 to 31 cyclists, with peaks of 139 motorists in 2020 and 31 cyclists in 2019 and 2023. This framing answers how the absolute number of deaths for the two road-user groups changed year by year, and the chart shows that motorist fatalities were higher in every year. Raw counts are a direct and easily interpreted measure of fatalities. It leaves unanswered how the two groups compare as a share of their combined deaths or relative to exposure such as trips taken.

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
python3 -c "import duckdb; print(duckdb.query(\"SELECT MIN(crash_date), MAX(crash_date), COUNT(*), SUM(number_of_motorist_killed), SUM(number_of_cyclist_killed) FROM read_parquet('data/crashes.parquet')\").fetchall()); print(duckdb.query(\"SELECT YEAR(crash_date) y, COUNT(*) rows, SUM(number_of_motorist_killed) motorist, SUM(number_of_cyclist_killed) cyclist FROM read_parquet('data/crashes.parquet') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY y ORDER BY y\").df().to_string(index=False))"
# bash
python3 -c "import duckdb; print(duckdb.query(\"SELECT YEAR(crash_date) AS yr, COUNT(*) AS crash_count, SUM(number_of_motorist_killed) AS motorist, SUM(number_of_cyclist_killed) AS cyclist FROM read_parquet('data/crashes.parquet') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY yr ORDER BY yr\").df().to_string(index=False))"
# bash
ls out
# bash
python3 -c "import duckdb; print(duckdb.query(\"SELECT YEAR(crash_date) AS yr, MIN(crash_date) AS first_date, MAX(crash_date) AS last_date, COUNT(*) AS crashes FROM read_parquet('data/crashes.parquet') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY yr ORDER BY yr\").df().to_string(index=False))"
# bash
python3 -c 'import duckdb, matplotlib.pyplot as plt, numpy as np
from pathlib import Path
out=Path("out")
df=duckdb.query("SELECT YEAR(crash_date) AS year, SUM(number_of_motorist_killed) AS motorist_deaths, SUM(number_of_cyclist_killed) AS cyclist_deaths FROM read_parquet(\"data/crashes.parquet\") WHERE crash_date >= DATE \'2013-01-01\' AND crash_date < DATE \'2026-01-01\' GROUP BY year ORDER BY year").df()
for col in ["motorist_deaths", "cyclist_deaths"]: df[col]=df[col].fillna(0).astype(int)
df.to_csv(out/"values_1.csv", index=False)
fig, ax=plt.subplots(figsize=(10,5.5))
ax.plot(df.year, df.motorist_deaths, marker="o", linewidth=2, label="Motorists")
ax.plot(df.year, df.cyclist_deaths, marker="o", linewidth=2, label="Cyclists")
ax.set(title="Motorist and cyclist deaths in NYC, 2013–2025", xlabel="Crash year", ylabel="Deaths")
ax.set_xticks(df.year); ax.tick_params(axis="x", rotation=45); ax.grid(axis="y", alpha=.25); ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(out/"option_1.png", dpi=160); plt.close(fig)
df["combined_deaths"]=df.motorist_deaths+df.cyclist_deaths
df["motorist_share_pct"]=df.motorist_deaths/df.combined_deaths*100
df["cyclist_share_pct"]=df.cyclist_deaths/df.combined_deaths*100
df[["year","motorist_deaths","cyclist_deaths","combined_deaths","motorist_share_pct","cyclist_share_pct"]].to_csv(out/"values_2.csv", index=False, float_format="%.4f")
fig, ax=plt.subplots(figsize=(10,5.5))
x=np.arange(len(df))
ax.bar(x, df.motorist_share_pct, label="Motorists")
ax.bar(x, df.cyclist_share_pct, bottom=df.motorist_share_pct, label="Cyclists")
ax.set(title="Share of motorist and cyclist deaths in NYC, 2013–2025", xlabel="Crash year", ylabel="Share of combined deaths (%)", ylim=(0,100))
ax.set_xticks(x, df.year.astype(str), rotation=45); ax.grid(axis="y", alpha=.25); ax.legend(frameon=False, loc="lower left")
fig.tight_layout(); fig.savefig(out/"option_2.png", dpi=160); plt.close(fig)
print(df.to_string(index=False))'
# bash
python3 out/build_charts.py
# bash
ls out
# bash
python3 -c "import json; p=json.load(open('out/options.json')); print(len(p['options']), sum(o['probability'] for o in p['options']))"

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