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
metric: Annual pedestrian casualties (pedestrians injured plus pedestrians killed)
denominator: None; annual count
grouping: Crash year for Brooklyn, 2013–2025
chart_type: Stacked bar chart of pedestrians injured and killed
probability: 0.55
WRITTEN ANSWER:
Annual pedestrian casualties fell 21.7% from 3,671 in 2013 to 2,874 in 2025, but rose from a low of 2,298 in 2022 and included 39 pedestrian deaths in 2025 versus 30 in 2013. This framing answers whether the annual number of pedestrians injured or killed in Brooklyn crashes has fallen: casualties decreased from 3,671 in 2013 to 2,874 in 2025, after a low of 2,298 in 2022. The stacked bars separate injury and death counts, making the total harm burden and the recent rebound visible. This is a defensible measure of the number of people harmed, but it does not account for how many people walked or distinguish injury severity beyond killed versus injured. Of all NYC crash records dated 2013–2025, 659,713 of 2,132,218 (30.94%) have NULL borough and cannot be assigned to Brooklyn; known crashes in other boroughs are outside this grouping, and no required pedestrian count is NULL; 2026 is omitted because the file covers only January 1 through June 11, so no partial year is included.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,brooklyn_crashes,pedestrian_injured,pedestrian_killed,crashes_with_pedestrian_casualty,pedestrian_casualties,crashes_with_pedestrian_casualty_pct
2013,47024,3641,30,3498,3671,7.438754678462062
2014,47761,3349,42,3234,3391,6.77121500806097
2015,50851,3029,46,2962,3075,5.824860868026194
2016,47464,2917,20,2797,2937,5.892887240856228
2017,44915,2663,20,2550,2683,5.677390626739396
2018,47313,2785,23,2697,2808,5.700336059856699
2019,44479,2700,33,2623,2733,5.897164954248072
2020,25473,1781,17,1724,1798,6.76795037883249
2021,25174,1905,32,1856,1937,7.37268610471121
2022,23369,2275,23,2185,2298,9.349993581240104
2023,22890,2385,22,2310,2407,10.091743119266056
2024,22785,2645,31,2576,2676,11.30568356374808
2025,24303,2835,39,2766,2874,11.381310949265522

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c "import duckdb, pandas, matplotlib; print('duckdb', duckdb.__version__, 'pandas', pandas.__version__, 'matplotlib', matplotlib.__version__)"
# bash
ls -ld . data
# bash
python -c "import duckdb; p='data/crashes.parquet'; print(duckdb.sql(f\"SELECT year(crash_date) y, count(*) rows, count(*) FILTER (WHERE borough IS NULL) null_borough, sum(number_of_pedestrians_injured) ped_inj, sum(number_of_pedestrians_killed) ped_killed, count(*) FILTER (WHERE number_of_pedestrians_injured + number_of_pedestrians_killed > 0) ped_crashes FROM read_parquet('{p}') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' AND borough='BROOKLYN' GROUP BY y ORDER BY y\").df().to_string(index=False)"); print('MISSING_BOROUGH:', duckdb.sql(\"SELECT count(*) FILTER (WHERE borough IS NULL) null_rows, count(*) all_rows, count(*) FILTER (WHERE borough IS NULL)*100.0/count(*) null_pct FROM read_parquet('data/crashes.parquet') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'\").df().to_string(index=False))"
# bash
mkdir out
# bash
python -c "print('ok')"
# bash
python out/create_options.py
# bash
ls -lh out
# bash
python -c "import json; x=json.load(open('out/options.json')); print('probability sum:', sum(i['probability'] for i in x['options'])); print('options:', len(x['options']))"
# bash
python -m json.tool out/options.json

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