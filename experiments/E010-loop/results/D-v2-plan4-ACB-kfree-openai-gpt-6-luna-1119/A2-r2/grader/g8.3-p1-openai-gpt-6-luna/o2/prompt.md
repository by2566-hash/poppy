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
metric: Annual mean recorded persons injured plus killed per eligible crash, by time of day
denominator: Eligible crash rows with nonmissing, non-midnight crash_time and nonmissing number_of_persons_injured and number_of_persons_killed
grouping: Calendar year and night (20:00–23:59 and 00:01–05:59) or day (06:00–19:59)
chart_type: Line chart
probability: 0.45
WRITTEN ANSWER:
This file cannot establish exposure-adjusted danger; among eligible crashes in 2025, the mean was 0.602 recorded people injured or killed per night crash versus 0.576 per day crash. The file only partly answers the question: this chart plots the annual mean of recorded persons injured plus killed per eligible police-reported NYC crash in complete years 2013–2025, with night defined as 20:00–23:59 and 00:01–05:59 and day as 06:00–19:59. In 2025, the mean was 0.602 casualties per night crash and 0.576 per day crash, making per-crash casualty severity a defensible measure of one part of danger. The data cannot show risk per trip or hour of travel because it has no traffic-exposure denominator. The check excludes partial 2012 (100,545 rows) and 2026 (36,424 rows), 23,787 midnight-coded rows because their count jumps from 24 in 2015 to 2,895 in 2016 and they may be default-coded, and rows missing casualty totals (18 missing injury values and 36 missing death values, with overlap possible); no NULL times were found. Eligible row denominators fall by 97,265 from 208,341 in 2019 to 111,076 in 2020, so a change in the average across those years can reflect a change in the size or composition of the crash denominator and not only casualty outcomes, and should be compared with that caution.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,time_group,recorded_casualties,eligible_crashes,mean_casualties_per_crash
2013,Night,15297,45022,0.339767
2013,Day,40119,158695,0.252806
2014,Night,14648,45554,0.321552
2014,Day,36840,160471,0.229574
2015,Night,14421,48386,0.298041
2015,Day,37176,169298,0.219589
2016,Night,16908,50291,0.336203
2016,Day,42924,176645,0.242996
2017,Night,16776,49623,0.338069
2017,Day,43187,177547,0.243243
2018,Night,16839,48875,0.344532
2018,Day,44397,179183,0.247775
2019,Night,17397,46273,0.375964
2019,Day,43333,162068,0.267375
2020,Night,13528,28443,0.475618
2020,Day,30682,82633,0.371304
2021,Night,16553,31168,0.531090
2021,Day,34680,77477,0.447617
2022,Night,15950,29694,0.537146
2022,Day,35540,72578,0.489680
2023,Night,16275,27687,0.587821
2023,Day,37385,67304,0.555465
2024,Night,16076,25998,0.618355
2024,Day,37314,63676,0.585998
2025,Night,14390,23910,0.601840
2025,Day,34479,59891,0.575696

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python3 out/data_check.py
# bash
python3 out/data_check.py
# bash
python3 out/analyze.py
# bash
python3 out/analyze.py
# bash
python3 -c "import json,pathlib; p=pathlib.Path('out/options.json'); d=json.loads(p.read_text()); print('options', len(d['options']), 'probability_sum', sum(x['probability'] for x in d['options'])); print('ids', [x['id'] for x in d['options']])"

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