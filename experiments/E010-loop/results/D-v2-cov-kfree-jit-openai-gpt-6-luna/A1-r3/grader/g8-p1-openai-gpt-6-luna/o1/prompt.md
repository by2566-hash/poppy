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

QUESTION ASKED: Has road safety for pedestrians in Brooklyn gotten better since 2013? Make a chart suitable for a local news story and summarize the findings.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Annual pedestrian injury victims in Brooklyn crashes
denominator: Annual victim count; no population or walking-exposure denominator
grouping: Calendar year, Brooklyn borough, 2013–2025
chart_type: Line chart
probability: 0.55
WRITTEN ANSWER:
Brooklyn pedestrian injuries fell 22.1% from 3,641 in 2013 to 2,835 in 2025, but rose from a low of 1,781 in 2020. This answers whether the number of pedestrians injured in Brooklyn crashes has declined since 2013: the annual count dropped from 3,641 to 2,835 by 2025, though it rebounded from 1,781 in 2020. An annual count is a defensible measure of the recorded injury burden and avoids combining injuries with deaths of very different severity. It does not answer whether an individual pedestrian's risk fell, because the file has no walking exposure denominator, and the lower count is not necessarily a safer rate. It omits 659,713 of 2,132,218 city crash rows with NULL borough (30.94% overall; 19.91%–38.12% in each year from 2013–2025), which cannot be assigned to Brooklyn; no Brooklyn rows in 2013–2025 have a NULL value for the relevant pedestrian count, and it excludes all 9,700 available Brooklyn rows in 2026 (100% of the available year's Brooklyn rows; coverage only January 1–June 11); 2012 is outside the since-2013 period and the file covers it only July–December.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,pedestrians_injured,brooklyn_crash_rows,null_injury_rows,null_fatality_rows
2013,3641,47024,0,0
2014,3349,47761,0,0
2015,3029,50851,0,0
2016,2917,47464,0,0
2017,2663,44915,0,0
2018,2785,47313,0,0
2019,2700,44479,0,0
2020,1781,25473,0,0
2021,1905,25174,0,0
2022,2275,23369,0,0
2023,2385,22890,0,0
2024,2645,22785,0,0
2025,2835,24303,0,0

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
pwd && ls
# bash
ls
# bash
python3 -c 'import duckdb; con=duckdb.connect(); p="data/crashes.parquet"; print(con.execute("DESCRIBE SELECT * FROM read_parquet(?)", [p]).fetchall()); print(con.execute("SELECT min(crash_date), max(crash_date), count(*) FROM read_parquet(?)", [p]).fetchall()); print(con.execute("SELECT borough, count(*) n FROM read_parquet(?) GROUP BY 1 ORDER BY n DESC NULLS LAST", [p]).fetchall())'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; q="SELECT year(crash_date) y, count(*) rows, count(*) FILTER (WHERE number_of_pedestrians_injured IS NULL) ni_null, count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) nk_null, count(*) FILTER (WHERE number_of_pedestrians_injured IS NULL OR number_of_pedestrians_killed IS NULL) either_null, sum(number_of_pedestrians_injured) ped_inj, sum(number_of_pedestrians_killed) ped_kill, sum(coalesce(number_of_pedestrians_injured,0)+coalesce(number_of_pedestrians_killed,0)) sum_coalesced FROM read_parquet(?) WHERE borough=\u0027BROOKLYN\u0027 AND year(crash_date)>=2012 GROUP BY 1 ORDER BY 1"; print(c.execute(q,[p]).df().to_string(index=False)); print("\nNULL totals:"); print(c.execute("SELECT count(*) FILTER(WHERE number_of_pedestrians_injured IS NULL), count(*) FILTER(WHERE number_of_pedestrians_killed IS NULL), count(*) FROM read_parquet(?) WHERE borough=\u0027BROOKLYN\u0027 AND year(crash_date) BETWEEN 2013 AND 2025",[p]).fetchall())'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; q="SELECT year(crash_date) y, count(*) row_count, count(*) FILTER (WHERE number_of_pedestrians_injured IS NULL) ni_null, count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) nk_null, count(*) FILTER (WHERE number_of_pedestrians_injured IS NULL OR number_of_pedestrians_killed IS NULL) either_null, sum(number_of_pedestrians_injured) ped_inj, sum(number_of_pedestrians_killed) ped_kill, sum(coalesce(number_of_pedestrians_injured,0)+coalesce(number_of_pedestrians_killed,0)) sum_coalesced FROM read_parquet(?) WHERE borough=\u0027BROOKLYN\u0027 AND year(crash_date)>=2012 GROUP BY 1 ORDER BY 1"; print(c.execute(q,[p]).df().to_string(index=False)); print("\nNULL totals:"); print(c.execute("SELECT count(*) FILTER(WHERE number_of_pedestrians_injured IS NULL), count(*) FILTER(WHERE number_of_pedestrians_killed IS NULL), count(*) FROM read_parquet(?) WHERE borough=\u0027BROOKLYN\u0027 AND year(crash_date) BETWEEN 2013 AND 2025",[p]).fetchall())'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; q="SELECT year(crash_date) y, count(*) n, count(*) FILTER(WHERE borough IS NULL) borough_null, round(100.0*count(*) FILTER(WHERE borough IS NULL)/count(*),2) pct_borough_null FROM read_parquet(?) WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY 1 ORDER BY 1"; print(c.execute(q,[p]).df().to_string(index=False)); print(c.execute("SELECT count(*) n, count(*) FILTER(WHERE borough IS NULL) nnull, round(100.0*count(*) FILTER(WHERE borough IS NULL)/count(*),2) pct FROM read_parquet(?) WHERE year(crash_date) BETWEEN 2013 AND 2025",[p]).fetchall()); print("change",c.execute("SELECT round(100.0*(2835-3641)/3641,1),round(100.0*(39-30)/30,1)").fetchall())'
# bash
python3 out/.build_options.py
# bash
python3 out/.build_options.py
# bash
python3 -c 'import json,csv,os,struct; d=json.load(open("out/options.json")); assert len(d["options"])==2; assert abs(sum(o["probability"] for o in d["options"])-1)<1e-9; assert all(len(o["interpretation"].split(". "))==4 for o in d["options"]); assert [o["id"] for o in d["options"]]==[1,2]; [print(f, os.path.getsize(f), struct.unpack(">II",open(f,"rb").read()[16:24])) for f in ("out/option_1.png","out/option_2.png")]; [print(f, sum(1 for _ in csv.DictReader(open(f)))) for f in ("out/values_1.csv","out/values_2.csv")]; print("JSON valid; 2 options; probabilities sum to 1; four-sentence interpretations")'

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