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
metric: Brooklyn crash reports with at least one pedestrian injured or killed
denominator: All Brooklyn police-reported crash records in the same calendar year
grouping: Year
chart_type: Line chart of annual percentages
probability: 0.45
WRITTEN ANSWER:
This file cannot establish whether walking risk fell, but the share of Brooklyn crash reports involving pedestrian injury or death rose from 7.4% in 2013 to 11.4% in 2025 (53.0% higher relative). This answers whether pedestrian-harm crashes became less common relative to all reported Brooklyn crashes: their share rose from 7.4% in 2013 to 11.4% in 2025. This denominator is defensible for comparing how often Brooklyn crash reports involve pedestrian harm despite changes in total crash-report volume. It leaves unanswered the risk per walking trip or population, because pedestrian exposure is not in the file. It uses full Brooklyn years 2013–2025; 0 of 473,801 selected rows (0.0%) lack either pedestrian count, 0 of 506,806 Brooklyn rows (0.0%) have NULL crash dates and cannot be assigned to a year, and 691,375 of 2,269,187 file rows (30.5%) have NULL borough and cannot be assigned to Brooklyn; partial 2012 and 2026 are excluded, so no partial year is included.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,brooklyn_crashes,crashes_with_pedestrian_harm,crashes_with_pedestrian_harm_pct
2013,47024,3498,7.438755
2014,47761,3234,6.771215
2015,50851,2962,5.824861
2016,47464,2797,5.892887
2017,44915,2550,5.677391
2018,47313,2697,5.700336
2019,44479,2623,5.897165
2020,25473,1724,6.767950
2021,25174,1856,7.372686
2022,23369,2185,9.349994
2023,22890,2310,10.091743
2024,22785,2576,11.305684
2025,24303,2766,11.381311

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("DESCRIBE SELECT * FROM read_parquet(?)", [p]).fetchdf().to_string(index=False)); print("coverage", c.execute("SELECT min(crash_date), max(crash_date), count(*) FROM read_parquet(?)", [p]).fetchall()); print(c.execute("SELECT year(crash_date) yr, count(*) rows, count(number_of_pedestrians_injured) ped_inj_known, sum(number_of_pedestrians_injured) ped_inj, count(number_of_pedestrians_killed) ped_kill_known, sum(number_of_pedestrians_killed) ped_kill, count(*) FILTER (WHERE borough = \'BROOKLYN\') bk_rows, sum(number_of_pedestrians_injured) FILTER (WHERE borough = \'BROOKLYN\') bk_ped_inj, sum(number_of_pedestrians_killed) FILTER (WHERE borough = \'BROOKLYN\') bk_ped_kill FROM read_parquet(?) GROUP BY 1 ORDER BY 1", [p]).fetchdf().to_string(index=False))'
# bash
ls
# bash
python3 -c 'print(1)'
# bash
python3 -c 'import duckdb; print(duckdb.__version__)'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; q="SELECT year(crash_date) yr, count(*) rows, count(number_of_pedestrians_injured) ped_inj_known, sum(number_of_pedestrians_injured) ped_inj, count(number_of_pedestrians_killed) ped_kill_known, sum(number_of_pedestrians_killed) ped_kill, count(*) FILTER (WHERE borough = ?) bk_rows, sum(number_of_pedestrians_injured) FILTER (WHERE borough = ?) bk_ped_inj, sum(number_of_pedestrians_killed) FILTER (WHERE borough = ?) bk_ped_kill FROM read_parquet(?) GROUP BY 1 ORDER BY 1"; print(c.execute(q,["BROOKLYN","BROOKLYN","BROOKLYN",p]).df().to_string(index=False)); print(c.execute("SELECT min(crash_date), max(crash_date), count(*) FROM read_parquet(?)",[p]).fetchall())'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; q="SELECT year(crash_date) yr, count(*) crash_count, count(number_of_pedestrians_injured) ped_inj_known, sum(number_of_pedestrians_injured) ped_inj, count(number_of_pedestrians_killed) ped_kill_known, sum(number_of_pedestrians_killed) ped_kill, count(*) FILTER (WHERE borough = ?) bk_rows, sum(number_of_pedestrians_injured) FILTER (WHERE borough = ?) bk_ped_inj, sum(number_of_pedestrians_killed) FILTER (WHERE borough = ?) bk_ped_kill FROM read_parquet(?) GROUP BY 1 ORDER BY 1"; print(c.execute(q,["BROOKLYN","BROOKLYN","BROOKLYN",p]).df().to_string(index=False)); print(c.execute("SELECT min(crash_date), max(crash_date), count(*) FROM read_parquet(?)",[p]).fetchall())'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; q="SELECT year(crash_date) yr, count(*) FILTER (WHERE borough = ?) bk_crashes, count(*) FILTER (WHERE borough = ? AND number_of_pedestrians_injured IS NULL) null_inj, count(*) FILTER (WHERE borough = ? AND number_of_pedestrians_killed IS NULL) null_kill, count(*) FILTER (WHERE borough IS NULL) null_borough, sum(number_of_pedestrians_injured) FILTER (WHERE borough = ?) ped_inj, sum(number_of_pedestrians_killed) FILTER (WHERE borough = ?) ped_kill FROM read_parquet(?) GROUP BY 1 ORDER BY 1"; print(c.execute(q,["BROOKLYN","BROOKLYN","BROOKLYN","BROOKLYN","BROOKLYN",p]).df().to_string(index=False)); print(c.execute("SELECT count(*) total, count(*) FILTER (WHERE borough IS NULL) null_borough, count(*) FILTER (WHERE number_of_pedestrians_injured IS NULL) null_inj, count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) null_kill FROM read_parquet(?)",[p]).fetchall())'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; print(c.execute("SELECT year(crash_date) yr, borough, count(*) n FROM read_parquet(?) WHERE year(crash_date) BETWEEN 2012 AND 2015 GROUP BY 1,2 ORDER BY 1,2",[p]).df().to_string(index=False)); print(c.execute("SELECT year(crash_date) yr, count(*) n FROM read_parquet(?) WHERE borough = ? AND year(crash_date) BETWEEN 2012 AND 2015 GROUP BY 1 ORDER BY 1",[p,"BROOKLYN"]).df().to_string(index=False))'
# bash
python3 out/build_options.py
# bash
python3 out/build_options.py
# bash
python3 -c 'import json,pathlib,csv; p=pathlib.Path("out"); o=json.loads((p/"options.json").read_text()); assert abs(sum(x["probability"] for x in o["options"])-1)<1e-9; assert len(o["options"])==2; assert all((p/f"option_{i}.png").is_file() and (p/f"values_{i}.csv").is_file() for i in (1,2)); rows1=list(csv.DictReader((p/"values_1.csv").open())); rows2=list(csv.DictReader((p/"values_2.csv").open())); assert len(rows1)==len(rows2)==13 and rows1[0]["year"]=="2013" and rows1[-1]["year"]=="2025"; print("Valid JSON; probabilities sum to",sum(x["probability"] for x in o["options"])); print("Output files:", sorted(x.name for x in p.iterdir()))'

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
- tr_TR01: If a per-reported-crash rate spanning 2020 is shown, the output says that the number of recorded crashes changes sharply around 2020 and that this affects comparing the per-crash rate across years (naming the cause, the 2020 recording change, is not required: it is not in the data or the dictionary).
- tr_TR15: Claims about pedestrian deaths changing are qualified by the small counts (about 30–39 per year).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.