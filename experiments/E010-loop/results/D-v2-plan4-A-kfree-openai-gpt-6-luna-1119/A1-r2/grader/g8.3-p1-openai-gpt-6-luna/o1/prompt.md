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
metric: Annual count of recorded pedestrian casualties, calculated as the sum of number_of_pedestrians_injured and number_of_pedestrians_killed
denominator: None; this is an absolute count, not an exposure-adjusted rate
grouping: Calendar year of crash_date
chart_type: line chart
probability: 0.65
WRITTEN ANSWER:
This only partly answers road safety: recorded Brooklyn pedestrian casualties (injuries plus deaths) numbered 3,671 in 2013, reached a low of 1,798 in 2020, and numbered 2,874 in 2025, but without pedestrian exposure data these counts cannot establish risk or overall safety. This answers only part of the question because the file has no pedestrian travel or exposure denominator, so it cannot establish risk per trip or overall road safety. The line chart groups crashes by crash_date year from 2013 through 2025 and sums recorded pedestrian injuries plus deaths in Brooklyn crashes, matching borough labels after trimming whitespace and ignoring case and requiring both counts to be nonmissing; the total was 3,671 in 2013, bottomed at 1,798 in 2020, and was 2,874 in 2025. This absolute count is a defensible measure of recorded pedestrian harm, while leaving unanswered whether risk per pedestrian trip changed. Checks found 668,406 of 2,168,642 dated NYC rows (30.82%) had missing, blank, or unknown borough labels and 0 had unsupported labels, with no missing required outcome counts or crash dates; 102 of 47,024 Brooklyn crashes in 2013 have the checked date 2013-01-01 and were retained as in-period rather than treated as a pile-up, while unlabeled rows were not assigned to Brooklyn and 9,700 Brooklyn crashes from partial 2026 coverage (January 1–June 11) were excluded.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,pedestrian_injuries,pedestrian_deaths,pedestrian_casualties
2013,3641.0,30.0,3671.0
2014,3349.0,42.0,3391.0
2015,3029.0,46.0,3075.0
2016,2917.0,20.0,2937.0
2017,2663.0,20.0,2683.0
2018,2785.0,23.0,2808.0
2019,2700.0,33.0,2733.0
2020,1781.0,17.0,1798.0
2021,1905.0,32.0,1937.0
2022,2275.0,23.0,2298.0
2023,2385.0,22.0,2407.0
2024,2645.0,31.0,2676.0
2025,2835.0,39.0,2874.0

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
pwd && ls
# bash
mkdir out
# bash
python3 out/data_check.py
# bash
python3 out/data_check.py
# bash
python3 out/data_check.py
# bash
python3 out/data_check.py
# bash
python3 out/analyze.py
# bash
python3 out/analyze.py
# bash
python3 out/data_check.py
# bash
python3 -m json.tool out/options.json
# bash
python3 out/data_check.py
# bash
python3 -m json.tool out/options.json
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(\"SELECT crash_date, count(*) FROM read_parquet(?) WHERE crash_date IN (DATE '0001-01-01', DATE '1900-01-01', DATE '1970-01-01', DATE '2013-01-01', DATE '9999-12-31') GROUP BY crash_date ORDER BY crash_date\", [p]).fetchall())"
# bash
python3 -c "import duckdb; c=duckdb.connect(); print(c.execute(\"SELECT upper(trim(borough)) AS borough, count(*) FROM read_parquet('data/crashes.parquet') WHERE crash_date = DATE '2013-01-01' GROUP BY borough ORDER BY count(*) DESC\").fetchall())"
# bash
python3 out/data_check.py
# bash
python3 -m json.tool out/options.json

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR05: If a borough filter (borough = 'BROOKLYN') is used, the output discloses that crashes with no borough recorded are left out of the borough figure. Saying that such rows exist and are excluded is enough; a number is not required, and an overall share or a per-year share both count (for reference only: 19.9–38.1% of rows per year have no borough). Saying only that other boroughs or non-matching rows are excluded, or that no borough values are missing among the Brooklyn rows, does not count.
- tr_TR11: The output does not call Brooklyn 'safer' or 'less safe' from counts alone without saying that there is no pedestrian exposure measure.
- tr_TR01: If a per-reported-crash rate spanning 2020 is shown, the output says that the number of recorded crashes changes sharply around 2020 and that this affects comparing the per-crash rate across years (naming the cause, the 2020 recording change, is not required: it is not in the data or the dictionary).
- tr_TR15: Claims about pedestrian deaths changing are qualified by the small counts (about 30–39 per year).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.