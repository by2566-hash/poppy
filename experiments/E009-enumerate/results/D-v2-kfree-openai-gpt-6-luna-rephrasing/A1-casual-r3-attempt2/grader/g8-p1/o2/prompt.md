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

QUESTION ASKED: Since 2013, has it gotten safer for pedestrians in Brooklyn? Make a chart for a local news story and sum up what you find.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Annual pedestrian deaths
denominator: No rate denominator; annual number of pedestrian deaths in Brooklyn crashes
grouping: Crash year, 2013–2025
chart_type: Line chart
probability: 0.3
WRITTEN ANSWER:
Pedestrian deaths in Brooklyn were 30 in 2013 and 39 in 2025, a 30.0% increase, despite substantial year-to-year fluctuation. This addresses whether the most severe pedestrian outcome has become less frequent, and the chart shows no sustained decline through the latest full year. Fatality counts are directly supported and newsworthy, but they do not capture nonfatal injuries or risk relative to walking exposure.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,value
2013,30.0
2014,42.0
2015,46.0
2016,20.0
2017,20.0
2018,23.0
2019,33.0
2020,17.0
2021,32.0
2022,23.0
2023,22.0
2024,31.0
2025,39.0

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c 'import duckdb; p="data/crashes.parquet"; print(duckdb.query(f"SELECT min(crash_date), max(crash_date), count(*), count(*) FILTER (WHERE borough=\u0027BROOKLYN\u0027) FROM read_parquet(\u0027{p}\u0027)").fetchall()); print(duckdb.query(f"SELECT borough, count(*) FROM read_parquet(\u0027{p}\u0027) GROUP BY borough ORDER BY count(*) DESC").fetchall())'
# bash
python -c 'import duckdb; q="""SELECT year(crash_date) y, count(*) crash_count, sum(number_of_pedestrians_injured) ped_inj, sum(number_of_pedestrians_killed) ped_killed, sum(number_of_pedestrians_injured+number_of_pedestrians_killed) ped_casualties, count(*) FILTER (WHERE number_of_pedestrians_injured+number_of_pedestrians_killed>0) ped_harm_crashes FROM read_parquet(\u0027data/crashes.parquet\u0027) WHERE borough=\u0027BROOKLYN\u0027 AND crash_date >= DATE \u00272013-01-01\u0027 GROUP BY y ORDER BY y"""; print(duckdb.query(q).df().to_string(index=False));'
# bash
ls
# bash
python out/_generate.py
# bash
python -c 'import json, pathlib, pandas as pd; p=pathlib.Path("out"); d=json.loads((p/"options.json").read_text()); print("JSON valid; probability sum:", sum(x["probability"] for x in d["options"])); print("files:", sorted(x.name for x in p.iterdir())); print("endpoints:", [(i, pd.read_csv(p/f"values_{i}.csv").iloc[[0,-1]].values.tolist()) for i in (1,2,3)])'

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR05: If a borough filter (borough = 'BROOKLYN') is used, the output discloses that crashes with no borough recorded (19.9–38.1% per year) are excluded.
- tr_TR11: The output does not call Brooklyn 'safer' or 'less safe' from counts alone without saying that there is no pedestrian exposure measure.
- tr_TR01: If a per-crash rate spanning 2020 is shown, the output caveats the 2020 change in crash recording.
- tr_TR15: Claims about pedestrian deaths changing are qualified by the small counts (about 30–39 per year).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.