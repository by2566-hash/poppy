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
metric: Annual ratio of motorist deaths to cyclist deaths
denominator: Cyclist deaths in the same calendar year
grouping: Calendar year
chart_type: Line chart
probability: 0.35
WRITTEN ANSWER:
Motorist deaths were 2.6 times cyclist deaths in 2019 (the lowest ratio) and 10.0 times in 2013 (the highest); the 2025 ratio was 3.5. This framing answers how the relative number of motorist deaths compared with cyclist deaths changed year by year: the ratio ranged from 2.6 in 2019 to 10.0 in 2013, and was 3.5 in 2025. A same-year ratio is a defensible way to compare relative counts when the groups have different totals, but it does not show the absolute size of the death counts or death risk per traveler. Within 2013–2025, 0% of rows are omitted for NULL motorist or cyclist death counts in every year, and no included year is partial (each year has dates from January 1 through December 31). The year filter excludes 2012: 100% of its 100,545 rows excluded (outside the requested interval); 2026: 100% of its 36,424 rows excluded (outside the requested interval).

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,motorist_deaths,cyclist_deaths,motorist_to_cyclist_ratio
2013,110,11,10.000000
2014,109,20,5.450000
2015,95,15,6.333333
2016,72,18,4.000000
2017,107,27,3.962963
2018,98,10,9.800000
2019,82,31,2.645161
2020,139,29,4.793103
2021,134,19,7.052632
2022,116,19,6.105263
2023,123,31,3.967742
2024,111,24,4.625000
2025,81,23,3.521739

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
ls data
# bash
ls out
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("select min(crash_date), max(crash_date), count(*) from read_parquet(?)", [p]).fetchall()); print(c.execute("select year(crash_date), count(*) n, sum(number_of_motorist_killed) motorist, sum(number_of_cyclist_killed) cyclist, count(*) filter (where number_of_motorist_killed is null) motorist_null, count(*) filter (where number_of_cyclist_killed is null) cyclist_null, min(crash_date), max(crash_date) from read_parquet(?) where year(crash_date) between 2013 and 2025 group by 1 order by 1", [p]).df().to_string(index=False))'
# bash
python3 generate_outputs.py
# bash
python3 -c 'import json, pathlib, pandas as pd; p=pathlib.Path("out"); o=json.loads((p/"options.json").read_text()); assert abs(sum(x["probability"] for x in o["options"])-1)<1e-9; assert all((p/f"option_{i}.png").is_file() and (p/f"values_{i}.csv").is_file() for i in (1,2)); a=pd.read_csv(p/"values_1.csv"); b=pd.read_csv(p/"values_2.csv"); assert len(a)==len(b)==13 and (a.year==b.year).all(); print("validated JSON, probabilities, chart/value files, and 13-year series")'

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