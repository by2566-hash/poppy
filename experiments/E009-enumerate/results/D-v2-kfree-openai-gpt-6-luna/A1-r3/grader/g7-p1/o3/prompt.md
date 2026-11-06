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
- Qualifications (reported, recorded in this dataset) count when they are in the WRITTEN ANSWER or the DECLARED FRAMING; text
  that appears only inside the chart image (title, footnote, source note) does not satisfy an item on its own. The official-count
  part of unsupported_claim follows the same test as TR07.

DATA FACTS (pinned snapshot):
- The file covers 2012-07-01 to 2026-06-11; 2013-2025 are complete calendar years; 2026 is partial (to June 11).
- borough is NULL for about 20-38% of crashes in every year (TR05): a borough filter silently drops them.
- number_of_persons_killed is NULL in most May-2026 and all June-2026 rows (TR08); 2013-2025 killed counts have no NULLs.
- crash_time has no NULL rows. Reported crash counts (the number of crash records) fall sharply in 2020 (TR01), so a per-reported-crash rate (deaths or injuries divided by reported crashes) compared across years spanning 2020 needs a caveat. Counts of deaths or injuries by year do NOT need it (they are not affected by the reporting change), and a comparison between groups within one pooled window (e.g. day vs night) does not either (decided 2026-11-04; g5 wording after g4 failed c6 on plain death counts).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: Has road safety for pedestrians in Brooklyn gotten better since 2013? Make a chart suitable for a local news story and summarize the findings.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Share of Brooklyn police-reported crashes with at least one pedestrian injured or killed
denominator: All Brooklyn police-reported motor vehicle crashes in the same year
grouping: Calendar year
chart_type: Line chart
probability: 0.3
WRITTEN ANSWER:
The share of reported Brooklyn crashes involving pedestrian injury or death rose from 7.4% in 2013 to 11.4% in 2025, an increase of about 3.9 percentage points. This framing answers whether pedestrian-harm crashes make up a larger share of all reported Brooklyn crashes, and the chart shows that share increasing after 2019 to 11.4% in 2025. It is a defensible crash-composition measure, but it leaves pedestrian risk per trip or mile unanswered because all crashes are not a measure of pedestrian travel exposure.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,brooklyn_crashes,crashes_with_pedestrian_harm,pedestrian_harm_crash_share_pct
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
ls
# bash
ls out
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("SELECT COUNT(*) rows, MIN(crash_date) min_date, MAX(crash_date) max_date FROM read_parquet(?)", [p]).fetchdf().to_string(index=False)); print(c.execute("SELECT borough, COUNT(*) n FROM read_parquet(?) GROUP BY borough ORDER BY n DESC NULLS LAST", [p]).fetchdf().to_string(index=False))'
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("SELECT COUNT(*) AS total_rows, MIN(crash_date) AS min_date, MAX(crash_date) AS max_date FROM read_parquet(?)", [p]).fetchdf().to_string(index=False)); print(c.execute("SELECT borough, COUNT(*) AS n FROM read_parquet(?) GROUP BY borough ORDER BY n DESC NULLS LAST", [p]).fetchdf().to_string(index=False))'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); q="""SELECT YEAR(crash_date) AS year, COUNT(*) AS crashes, SUM(number_of_pedestrians_injured) AS pedestrian_injured, SUM(number_of_pedestrians_killed) AS pedestrian_killed, SUM(number_of_pedestrians_injured + number_of_pedestrians_killed) AS pedestrian_casualties, COUNT(*) FILTER (WHERE number_of_pedestrians_injured > 0 OR number_of_pedestrians_killed > 0) AS crashes_with_pedestrian_harm, MIN(crash_date) AS first_date, MAX(crash_date) AS last_date FROM read_parquet(\"data/crashes.parquet\") WHERE borough = \'BROOKLYN\' GROUP BY year ORDER BY year"""; print(c.execute(q).fetchdf().to_string(index=False))'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); q="SELECT YEAR(crash_date) AS year, COUNT(*) AS crashes, SUM(number_of_pedestrians_injured) AS pedestrian_injured, SUM(number_of_pedestrians_killed) AS pedestrian_killed, SUM(number_of_pedestrians_injured + number_of_pedestrians_killed) AS pedestrian_casualties, COUNT(*) FILTER (WHERE number_of_pedestrians_injured > 0 OR number_of_pedestrians_killed > 0) AS crashes_with_pedestrian_harm, MIN(crash_date) AS first_date, MAX(crash_date) AS last_date FROM read_parquet(\"data/crashes.parquet\") WHERE borough = chr(66)||chr(82)||chr(79)||chr(79)||chr(75)||chr(76)||chr(89)||chr(78) GROUP BY year ORDER BY year"; print(c.execute(q).fetchdf().to_string(index=False))'
# bash
python3 out/build_options.py
# bash
python3 -c 'import json, pathlib, pandas as pd; root=pathlib.Path("out"); x=json.loads((root/"options.json").read_text()); assert [o["id"] for o in x["options"]]==[1,2,3]; assert abs(sum(o["probability"] for o in x["options"])-1)<1e-9; assert all((root/f"option_{i}.png").is_file() and (root/f"values_{i}.csv").is_file() for i in [1,2,3]); a=pd.read_csv(root/"values_1.csv"); assert int(a.iloc[0].pedestrian_casualties)==3671 and int(a.iloc[-1].pedestrian_casualties)==2874; b=pd.read_csv(root/"values_2.csv"); assert int(b.iloc[0].pedestrian_killed)==30 and int(b.iloc[-1].pedestrian_killed)==39; c=pd.read_csv(root/"values_3.csv"); assert round(c.iloc[0].pedestrian_harm_crash_share_pct,1)==7.4 and round(c.iloc[-1].pedestrian_harm_crash_share_pct,1)==11.4; print("Validated JSON, probabilities, required files, and endpoint values.")'

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