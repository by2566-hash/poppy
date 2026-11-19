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
metric: Annual sum of number_of_persons_injured plus number_of_persons_killed per 100 eligible crashes.
denominator: Count of eligible police-reported crash rows in each year and time group; eligible means crash_time and both person outcome counts are nonmissing. Midnight rows are a separate group, and the night/day comparison uses the remaining clock times.
grouping: Calendar year and three clock-time groups: night 20:00–23:59 and 00:01–05:59; day 06:00–19:59; exactly 00:00:00 is reported separately as midnight/possible default.
chart_type: Annual line chart with separate day, night, and midnight/possible-default series.
probability: 0.45
WRITTEN ANSWER:
The dataset can answer only partly: recorded injured-plus-killed people per 100 crashes were higher at night than by day in every complete year, including 60.18 versus 57.57 in 2025. Only partly: for complete years 2013–2025, this chart reports the annual sum of recorded injured plus killed people divided by eligible police-reported crash rows and multiplied by 100; night means 20:00–23:59 and 00:01–05:59, day means 06:00–19:59, and 00:00 is shown separately as midnight/possible default. The nighttime casualty burden per 100 crashes exceeded daytime in each complete year, including 60.18 versus 57.57 in 2025. This is a defensible measure of recorded casualty burden per reported crash, but it is not a per-trip danger rate, does not account for traffic exposure or actual darkness, and cannot establish causation. The check found 42 of 2,132,218 complete-year rows (0.001970%) missing at least one outcome count and excluded them (18 rows lacked the injured count and 36 lacked the killed count, with overlap); partial 2012 (100,545 rows) and 2026 (36,424 rows) were excluded, while 23,786 eligible 00:00 rows were separated after midnight records jumped from 24 in 2015 to 2,895 in 2016; the largest neighboring-year group-denominator change was 79,435 fewer day crashes from 2019 to 2020, so a rise or fall in the measure across those years may result from this denominator change rather than a change in the outcome and should be compared cautiously.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,time_group,eligible_crashes,persons_injured,persons_killed,injured_plus_killed_people,injured_plus_killed_per_100_crashes
2013,Day,158695,39961.000000,158.000000,40119.000000,25.280570
2013,Night,45022,15158.000000,139.000000,15297.000000,33.976722
2013,Midnight / possible default,25,9.000000,0.000000,9.000000,36.000000
2014,Day,160471,36687.000000,153.000000,36840.000000,22.957419
2014,Night,45554,14539.000000,109.000000,14648.000000,32.155244
2014,Midnight / possible default,21,4.000000,0.000000,4.000000,19.047619
2015,Day,169298,37042.000000,134.000000,37176.000000,21.958913
2015,Night,48386,14312.000000,109.000000,14421.000000,29.804076
2015,Midnight / possible default,24,15.000000,0.000000,15.000000,62.500000
2016,Day,176645,42792.000000,132.000000,42924.000000,24.299584
2016,Night,50291,16795.000000,113.000000,16908.000000,33.620330
2016,Midnight / possible default,2895,730.000000,1.000000,731.000000,25.250432
2017,Day,177547,43045.000000,142.000000,43187.000000,24.324263
2017,Night,49623,16662.000000,114.000000,16776.000000,33.806904
2017,Midnight / possible default,3818,930.000000,0.000000,930.000000,24.358303
2018,Day,179183,44273.000000,124.000000,44397.000000,24.777462
2018,Night,48875,16732.000000,107.000000,16839.000000,34.453197
2018,Midnight / possible default,3490,926.000000,0.000000,926.000000,26.532951
2019,Day,162068,43199.000000,134.000000,43333.000000,26.737542
2019,Night,46273,17287.000000,110.000000,17397.000000,37.596439
2019,Midnight / possible default,3145,905.000000,0.000000,905.000000,28.775835
2020,Day,82633,30547.000000,135.000000,30682.000000,37.130444
2020,Night,28443,13394.000000,134.000000,13528.000000,47.561790
2020,Midnight / possible default,1841,673.000000,0.000000,673.000000,36.556219
2021,Day,77477,34532.000000,148.000000,34680.000000,44.761671
2021,Night,31168,16406.000000,147.000000,16553.000000,53.108958
2021,Midnight / possible default,1912,847.000000,2.000000,849.000000,44.403766
2022,Day,72578,35385.000000,155.000000,35540.000000,48.968007
2022,Night,29694,15815.000000,135.000000,15950.000000,53.714555
2022,Midnight / possible default,1615,733.000000,0.000000,733.000000,45.386997
2023,Day,67304,37254.000000,131.000000,37385.000000,55.546476
2023,Night,27687,16126.000000,149.000000,16275.000000,58.782100
2023,Midnight / possible default,1616,872.000000,0.000000,872.000000,53.960396
2024,Day,63676,37184.000000,130.000000,37314.000000,58.599786
2024,Night,25998,15938.000000,138.000000,16076.000000,61.835526
2024,Midnight / possible default,1642,908.000000,0.000000,908.000000,55.298417
2025,Day,59891,34357.000000,122.000000,34479.000000,57.569585
2025,Night,23910,14283.000000,107.000000,14390.000000,60.184023
2025,Midnight / possible default,1742,990.000000,0.000000,990.000000,56.831228

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python3 out/check_data.py
# bash
python3 out/check_data.py
# bash
python3 out/check_data.py
# bash
python3 out/check_data.py
# bash
python3 out/check_data.py
# bash
python3 out/analyze.py
# bash
python3 out/analyze.py
# bash
python3 out/analyze.py && python3 -c "import json; from pathlib import Path; p=Path('out'); plans=[json.loads((p/f'plan_{i}.json').read_text()) for i in (1,2)]; opts=json.loads((p/'options.json').read_text()); assert len(opts['options']) == 2; assert abs(sum(o['probability'] for o in opts['options'])-1) < 1e-9; print('JSON valid; probabilities sum to', sum(o['probability'] for o in opts['options']))"
# bash
python3 out/check_data.py

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