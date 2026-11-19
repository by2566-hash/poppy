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
metric: Annual percentage of eligible crashes with at least one person injured or killed, calculated as 100 times crashes with number_of_persons_injured + number_of_persons_killed > 0 divided by eligible crash rows.
denominator: Count of eligible police-reported crash rows in each year and time group; eligible means crash_time and both person outcome counts are nonmissing. Midnight rows are a separate group, and the night/day comparison uses the remaining clock times.
grouping: Calendar year and three clock-time groups: night 20:00–23:59 and 00:01–05:59; day 06:00–19:59; exactly 00:00:00 is reported separately as midnight/possible default.
chart_type: Annual line chart with separate day, night, and midnight/possible-default series.
probability: 0.55
WRITTEN ANSWER:
The dataset can answer only partly: the injury-or-death crash share was higher at night in 2013 (23.77% vs 18.63% by day), while in 2025 the daytime share was higher (44.29% vs 42.41% at night). Only partly: for complete years 2013–2025, this chart reports the annual share of eligible police-reported crashes with at least one recorded injury or death, calculated as injury-or-death crashes divided by eligible crash rows; night means 20:00–23:59 and 00:01–05:59, day means 06:00–19:59, and 00:00 is shown separately as midnight/possible default. Night's share was higher through 2021 (36.64% vs 34.52% in 2021), while daytime's share was slightly higher in 2022 and reached 44.29% versus 42.41% at night in 2025. This is a defensible crash-level measure of injury involvement, but it does not measure risk per trip or actual darkness and cannot establish that darkness caused crashes. The check found 42 of 2,132,218 complete-year rows (0.001970%) missing at least one outcome count and excluded them (18 rows lacked the injured count and 36 lacked the killed count, with overlap); partial 2012 (100,545 rows) and 2026 (36,424 rows) were excluded, while 23,786 eligible 00:00 rows were separated after midnight records jumped from 24 in 2015 to 2,895 in 2016; the largest neighboring-year group-denominator change was 79,435 fewer day crashes from 2019 to 2020, so a rise or fall in the measure across those years may result from this denominator change rather than a change in the outcome and should be compared cautiously.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,time_group,eligible_crashes,crashes_with_injury_or_death,injury_or_death_crash_share_pct
2013,Day,158695,29566.000000,18.630707
2013,Night,45022,10702.000000,23.770601
2013,Midnight / possible default,25,5.000000,20.000000
2014,Day,160471,27421.000000,17.087823
2014,Night,45554,10280.000000,22.566624
2014,Midnight / possible default,21,3.000000,14.285714
2015,Day,169298,27827.000000,16.436697
2015,Night,48386,10205.000000,21.090811
2015,Midnight / possible default,24,8.000000,33.333333
2016,Day,176645,31976.000000,18.101843
2016,Night,50291,11707.000000,23.278519
2016,Midnight / possible default,2895,556.000000,19.205527
2017,Day,177547,32366.000000,18.229539
2017,Night,49623,11614.000000,23.404470
2017,Midnight / possible default,3818,694.000000,18.177056
2018,Day,179183,33341.000000,18.607234
2018,Night,48875,11752.000000,24.045013
2018,Midnight / possible default,3490,674.000000,19.312321
2019,Day,162068,32670.000000,20.158205
2019,Night,46273,12121.000000,26.194541
2019,Midnight / possible default,3145,648.000000,20.604134
2020,Day,82633,23507.000000,28.447473
2020,Night,28443,9375.000000,32.960658
2020,Midnight / possible default,1841,479.000000,26.018468
2021,Day,77477,26743.000000,34.517341
2021,Night,31168,11419.000000,36.636935
2021,Midnight / possible default,1912,647.000000,33.838912
2022,Day,72578,27531.000000,37.932982
2022,Night,29694,11232.000000,37.825823
2022,Midnight / possible default,1615,573.000000,35.479876
2023,Day,67304,28497.000000,42.340723
2023,Night,27687,11322.000000,40.892838
2023,Midnight / possible default,1616,653.000000,40.408416
2024,Day,63676,28390.000000,44.585087
2024,Night,25998,11169.000000,42.960997
2024,Midnight / possible default,1642,670.000000,40.803898
2025,Day,59891,26526.000000,44.290461
2025,Night,23910,10141.000000,42.413216
2025,Midnight / possible default,1742,750.000000,43.053961

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