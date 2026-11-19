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

QUESTION ASKED: How many pedestrians were killed in NYC motor vehicle crashes each year from 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: sum of pedestrians killed
denominator: none (annual count, not a rate)
grouping: crash year, 2013–2025
chart_type: bar chart
probability: 0.55
WRITTEN ANSWER:
The annual pedestrian death counts were 2013: 176; 2014: 133; 2015: 133; 2016: 149; 2017: 127; 2018: 123; 2019: 131; 2020: 101; 2021: 132; 2022: 135; 2023: 107; 2024: 124; 2025: 119. This bar chart answers how many pedestrians were killed in each requested year by summing the crash-level pedestrian-fatality counts; it shows annual totals from 2013 through 2025. It is a defensible framing because the requested quantity is a yearly count, and the plotted values are the direct annual sums. It does not show where or why those deaths occurred. It excludes 100545 rows dated before 2013 (4.43% of all file rows, all in the partial 2012 coverage), 36424 rows dated in 2026 (1.61% of all file rows, 2026 is covered only through 2026-06-11), and no rows for NULL crash dates or NULL pedestrian-fatality counts.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,pedestrians_killed,crash_rows,null_metric_rows
2013,176,203742,0
2014,133,206046,0
2015,133,217708,0
2016,149,229833,0
2017,127,231007,0
2018,123,231564,0
2019,131,211486,0
2020,101,112918,0
2021,132,110558,0
2022,135,103887,0
2023,107,96607,0
2024,124,91316,0
2025,119,85546,0

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c 'import duckdb; p="data/crashes.parquet"; print(duckdb.query(f"SELECT count(*) n, min(crash_date) min_date, max(crash_date) max_date, count(*) FILTER (WHERE crash_date IS NULL) null_date, count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) null_ped_killed FROM read_parquet(\"{p}\")").df().to_string(index=False)); print(duckdb.query(f"SELECT year(crash_date) year, count(*) crashes, sum(number_of_pedestrians_killed) ped_killed, count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) null_metric FROM read_parquet(\"{p}\") WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1").df().to_string(index=False))'
# bash
python -c 'import duckdb; p="data/crashes.parquet"; con=duckdb.connect(); print(con.execute("SELECT year(crash_date) AS yr, min(crash_date) AS start_date, max(crash_date) AS end_date, count(*) AS crash_rows, sum(number_of_pedestrians_killed) AS pedestrians_killed, count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS null_metric_rows FROM read_parquet(?) WHERE crash_date >= DATE '"'"'2013-01-01'"'"' AND crash_date < DATE '"'"'2026-01-01'"'"' GROUP BY yr ORDER BY yr", [p]).df().to_string(index=False)); print(con.execute("SELECT min(crash_date) AS min_date, max(crash_date) AS max_date, count(*) AS all_rows FROM read_parquet(?)", [p]).df().to_string(index=False))'
# bash
python generate_crash_options.py
# bash
python -c 'import json, pathlib, pandas as pd; p=pathlib.Path("out"); opts=json.loads((p/"options.json").read_text())["options"]; assert abs(sum(x["probability"] for x in opts)-1)<1e-9; expected={2013:176,2014:133,2015:133,2016:149,2017:127,2018:123,2019:131,2020:101,2021:132,2022:135,2023:107,2024:124,2025:119}; [None for i in (1,2) if pd.read_csv(p/f"values_{i}.csv").set_index("year")["pedestrians_killed"].to_dict()==expected and (p/f"option_{i}.png").is_file()]; assert len(opts)==2 and all((p/f"option_{x[chr(105)+chr(100)]}.png").is_file() and (p/f"values_{x[chr(105)+chr(100)]}.csv").is_file() for x in opts); print("Validated JSON, probabilities, both chart files, and annual values:", "; ".join(f"{y}: {n}" for y,n in expected.items()))'
# bash
python -c 'import json, pathlib, pandas as pd; p=pathlib.Path("out"); opts=json.loads((p/"options.json").read_text())["options"]; expected={2013:176,2014:133,2015:133,2016:149,2017:127,2018:123,2019:131,2020:101,2021:132,2022:135,2023:107,2024:124,2025:119}; assert len(opts)==2; assert abs(sum(x["probability"] for x in opts)-1)<1e-9; assert all(pd.read_csv(p/f"values_{x[chr(105)+chr(100)]}.csv").set_index("year")["pedestrians_killed"].to_dict()==expected and (p/f"option_{x[chr(105)+chr(100)]}.png").is_file() for x in opts); print("All output files and annual values verified.")'

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR07: The output does not present the open-data death counts as the official NYC toll. The counts are qualified when the written output (answer, interpretation or declared framing fields) ties them to this data in any wording: reported, recorded, police-reported crashes, in this dataset (e.g. 'pedestrians killed in reported motor vehicle crashes' qualifies). A qualification or source note that appears only inside the chart image does not count, and a chart title without one is fine when the written output has it. FAIL only when no such qualification appears in the written output (Bo 2026-11-04, refined 2026-11-06).
- tr_CAUSAL: The output makes no causal attribution (e.g. 'because of the pandemic') that the data cannot support.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.