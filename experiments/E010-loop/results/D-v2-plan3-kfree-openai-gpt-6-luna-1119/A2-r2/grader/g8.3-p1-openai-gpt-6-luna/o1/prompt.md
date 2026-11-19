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
metric: Police-reported crash records per 1,000 elapsed clock-hours in each time period and year
denominator: Elapsed clock-hours per period for each complete calendar year (10 hours/day at night, 14 hours/day by day)
grouping: Calendar year (2013-2025) and time period: night 20:00-05:59, day 06:00-19:59, unknown time as its own group
chart_type: Annual two-series line chart
probability: 0.25
WRITTEN ANSWER:
The data answer this only partly: the clock-hour crash rate was higher by day in all 13 years, with 2025 rates of 11,721 day versus 7,028 night crashes per 1,000 clock-hours. The data answer this only partly: the chart covers all police-reported crashes in full date-extent years 2013-2025 and divides records by elapsed clock-hours, defining night as 20:00-05:59 (10 hours/day), day as 06:00-19:59 (14 hours/day), and unknown times as a separate 24-hours/day group. The day rate exceeds the night rate in every one of the 13 years; in 2025 the values are 11,721 and 7,028 per 1,000 clock-hours, respectively, making this a defensible way to compare reported crash frequency across periods of unequal duration, but not traveler risk because trip and distance exposure are unavailable. Annual dated crash rows decrease from 203,742 in 2013 to 85,546 in 2025, so the amount of crash reporting behind the yearly rates changes and these rates still do not account for changes in road use. Date extents show 2012 (July-December) and 2026 (January-June 11) are partial and excluded; there are no missing, placeholder, or invalid times, 23,787 midnight times are retained in night though possible default coding cannot be checked, and the unknown-time group has no rows.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,period,crash_records,hours_in_period,crashes_per_1000_clock_hours,population_crash_records
2013,Night,45047.0,3650,12341.643835616438,45047.0
2013,Day,158695.0,5110,31055.772994129158,158695.0
2013,Unknown,0.0,8760,0.0,0.0
2014,Night,45575.0,3650,12486.301369863015,45575.0
2014,Day,160471.0,5110,31403.326810176124,160471.0
2014,Unknown,0.0,8760,0.0,0.0
2015,Night,48410.0,3650,13263.013698630137,48410.0
2015,Day,169298.0,5110,33130.7240704501,169298.0
2015,Unknown,0.0,8760,0.0,0.0
2016,Night,53187.0,3660,14531.967213114754,53187.0
2016,Day,176646.0,5124,34474.23887587822,176646.0
2016,Unknown,0.0,8784,0.0,0.0
2017,Night,53445.0,3650,14642.465753424658,53445.0
2017,Day,177562.0,5110,34747.94520547945,177562.0
2017,Unknown,0.0,8760,0.0,0.0
2018,Night,52368.0,3650,14347.397260273972,52368.0
2018,Day,179196.0,5110,35067.710371819965,179196.0
2018,Unknown,0.0,8760,0.0,0.0
2019,Night,49418.0,3650,13539.17808219178,49418.0
2019,Day,162068.0,5110,31715.851272015654,162068.0
2019,Unknown,0.0,8760,0.0,0.0
2020,Night,30284.0,3660,8274.31693989071,30284.0
2020,Day,82634.0,5124,16126.854020296643,82634.0
2020,Unknown,0.0,8784,0.0,0.0
2021,Night,33080.0,3650,9063.013698630137,33080.0
2021,Day,77478.0,5110,15162.035225048923,77478.0
2021,Unknown,0.0,8760,0.0,0.0
2022,Night,31309.0,3650,8577.808219178083,31309.0
2022,Day,72578.0,5110,14203.131115459882,72578.0
2022,Unknown,0.0,8760,0.0,0.0
2023,Night,29303.0,3650,8028.219178082192,29303.0
2023,Day,67304.0,5110,13171.037181996086,67304.0
2023,Unknown,0.0,8760,0.0,0.0
2024,Night,27640.0,3660,7551.912568306011,27640.0
2024,Day,63676.0,5124,12427.010148321624,63676.0
2024,Unknown,0.0,8784,0.0,0.0
2025,Night,25653.0,3650,7028.219178082191,25653.0
2025,Day,59893.0,5110,11720.743639921722,59893.0
2025,Unknown,0.0,8760,0.0,0.0

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python out/run_checks.py
# bash
python out/run_checks.py
# bash
python out/analyze.py
# bash
python out/run_checks.py
# bash
python -c "import json, pathlib; p=pathlib.Path('out'); options=json.loads((p/'options.json').read_text()); assert len(options['options'])==3; assert abs(sum(o['probability'] for o in options['options'])-1)<1e-9; [json.loads((p/f'plan_{i}.json').read_text()) for i in range(1,4)]; assert all((p/f'option_{i}.png').is_file() and (p/f'values_{i}.csv').is_file() and (p/f'check_{i}.csv').is_file() for i in range(1,4)); print('Validated JSON, probabilities, and all option/check/value/chart files.')"

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