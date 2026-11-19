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

QUESTION ASKED: Are NYC's streets more dangerous at night? Make a chart and give a conclusion for a news report.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: percentage of eligible reported crashes with at least one person injured or killed, calculated as 100 × crashes where persons injured + persons killed > 0 / eligible crashes
denominator: eligible reported crash rows in the same year and time-of-day group, with both total outcome fields present
grouping: calendar year and crash-time period (night or day)
chart_type: line chart
probability: 0.55
WRITTEN ANSWER:
Crash records cannot establish exposure-adjusted street danger: the share of reported crashes involving injury or death was higher at night through 2021 but higher by day in 2022–2025 (2025: 42.46% night versus 44.29% day). This answers only part of whether NYC streets are more dangerous at night: for complete calendar years 2013–2025, the chart compares the share of police-reported crashes with any injury or death, and that share is higher at night through 2021 but higher by day in 2022–2025; night means 20:00–05:59 and day means 06:00–19:59. The metric is 100 times crashes with at least one person injured or killed divided by eligible crash rows in that year and time group, a defensible measure of the likelihood of recorded harm conditional on a crash. It leaves unanswered danger per trip, mile, or pedestrian exposure because the file contains crash records but no traffic or travel-exposure denominator. The check found no missing dates or times; it excludes partial 2012 (100,545 dated rows) and 2026 (36,424) and 42 of 2,132,218 complete-year candidates missing either outcome total, keeps valid midnight times as night (3,819 in 2017, though possible default-coded values cannot be distinguished), and shows eligible rows increasing from 203,742 in 2013 to a 231,548 peak in 2018 before falling to 112,917 in 2020 and 85,543 in 2025, so annual percentages reflect changing crash-record volumes rather than stable exposure.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,period,eligible_crashes,crashes_with_any_casualty,persons_injured,persons_killed,casualty_persons,crashes_with_casualty_pct,casualties_per_100_crashes
2013,Day,158695,29566,39961.000000,158.000000,40119.000000,18.630707,25.280570
2013,Night,45047,10707,15167.000000,139.000000,15306.000000,23.768508,33.977845
2014,Day,160471,27421,36687.000000,153.000000,36840.000000,17.087823,22.957419
2014,Night,45575,10283,14543.000000,109.000000,14652.000000,22.562809,32.149205
2015,Day,169298,27827,37042.000000,134.000000,37176.000000,16.436697,21.958913
2015,Night,48410,10213,14327.000000,109.000000,14436.000000,21.096881,29.820285
2016,Day,176645,31976,42792.000000,132.000000,42924.000000,18.101843,24.299584
2016,Night,53186,12263,17525.000000,114.000000,17639.000000,23.056819,33.164743
2017,Day,177547,32366,43045.000000,142.000000,43187.000000,18.229539,24.324263
2017,Night,53441,12308,17592.000000,114.000000,17706.000000,23.031006,33.131865
2018,Day,179183,33341,44273.000000,124.000000,44397.000000,18.607234,24.777462
2018,Night,52365,12426,17658.000000,107.000000,17765.000000,23.729590,33.925332
2019,Day,162068,32670,43199.000000,134.000000,43333.000000,20.158205,26.737542
2019,Night,49418,12769,18192.000000,110.000000,18302.000000,25.838763,37.035088
2020,Day,82633,23507,30547.000000,135.000000,30682.000000,28.447473,37.130444
2020,Night,30284,9854,14067.000000,134.000000,14201.000000,32.538634,46.892749
2021,Day,77477,26743,34532.000000,148.000000,34680.000000,34.517341,44.761671
2021,Night,33080,12066,17253.000000,149.000000,17402.000000,36.475212,52.605804
2022,Day,72578,27531,35385.000000,155.000000,35540.000000,37.932982,48.968007
2022,Night,31309,11805,16548.000000,135.000000,16683.000000,37.704813,53.284998
2023,Day,67304,28497,37254.000000,131.000000,37385.000000,42.340723,55.546476
2023,Night,29303,11975,16998.000000,149.000000,17147.000000,40.866123,58.516193
2024,Day,63676,28390,37184.000000,130.000000,37314.000000,44.585087,58.599786
2024,Night,27640,11839,16846.000000,138.000000,16984.000000,42.832851,61.447178
2025,Day,59891,26526,34357.000000,122.000000,34479.000000,44.290461,57.569585
2025,Night,25652,10891,15273.000000,107.000000,15380.000000,42.456729,59.956339

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python out/data_check.py
# bash
python out/data_check.py
# bash
python out/data_check.py
# bash
python out/analyze.py
# bash
python -c "import json; from pathlib import Path; files=['out/plan_1.json','out/plan_2.json','out/options.json']; [json.loads(Path(f).read_text()) for f in files]; print('JSON valid'); opts=json.loads(Path('out/options.json').read_text())['options']; print('probability sum:', sum(o['probability'] for o in opts))"
# bash
python -c "import json; from pathlib import Path; p1=json.loads(Path('out/plan_1.json').read_text()); p2=json.loads(Path('out/plan_2.json').read_text()); doc=json.loads(Path('out/options.json').read_text()); assert len(doc['options']) == 2 and abs(sum(x['probability'] for x in doc['options']) - 1) < 1e-9; assert all(p['final_plan'] is not None for p in (p1,p2)); print('Plans and options JSON valid; probabilities sum to 1.')"

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR11: Severity per crash (deaths or injuries per crash) is described as such, not as the risk of being on the street at night (no traffic volume by hour exists).
- tr_TR08: NA if the option uses no killed or injured counts. Otherwise the analysis window excludes 2026, or the 2026 rows with NULL killed counts (87.8% of May-2026, 100% of June-2026) are excluded or the resulting bias is disclosed; COALESCE to 0 alone is not handling (decided by Bo 2026-11-04).
- tr_NIGHTDEF: The definition of 'night' (hours) is stated.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.