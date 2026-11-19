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
metric: Mean reported persons injured per eligible crash record
denominator: Crash records in each year and time period with nonmissing number_of_persons_injured
grouping: Calendar year (2013-2025) and time period: night 20:00-05:59, day 06:00-19:59, unknown time as its own group
chart_type: Annual two-series line chart
probability: 0.35
WRITTEN ANSWER:
The data answer this only partly: night crashes averaged more reported injured people per crash in all 13 years; in 2025 the averages were 0.595 at night and 0.574 by day. The data answer this only partly: the chart reports total number_of_persons_injured divided by crash records with that count present in each full date-extent year from 2013-2025, comparing night (20:00-05:59) with day (06:00-19:59), and putting unknown times in their own group. Night averages more reported injured persons per crash in all 13 years, including 0.595 at night versus 0.574 by day in 2025; this is a defensible crash-severity comparison, but it does not indicate risk per traveler or distance traveled. Eligible crash records fall from 203,742 in 2013 to 85,546 in 2025, so the yearly means are based on different-sized crash groups and cannot adjust for changes in road use. The date-extent check excludes partial 2012 and 2026; 18 of 2,132,218 dated rows in complete years lack an injury count and are excluded, while no crash times are missing/invalid, 23,787 exact-midnight times are retained as night despite uncertain possible default coding, and the unknown-time group has no rows.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,days_in_year,period,eligible_crashes,reported_injured_persons,injured_persons_per_crash
2013,365,Night,45047.0,15167.0,0.33669278753302107
2013,365,Day,158695.0,39961.0,0.2518100759318189
2013,365,Unknown,0.0,0.0,
2014,365,Night,45575.0,14543.0,0.3191003839824465
2014,365,Day,160471.0,36687.0,0.22862074767403456
2014,365,Unknown,0.0,0.0,
2015,365,Night,48410.0,14327.0,0.2959512497417889
2015,365,Day,169298.0,37042.0,0.21879762312608536
2015,365,Unknown,0.0,0.0,
2016,366,Night,53186.0,17525.0,0.3295040048132967
2016,366,Day,176646.0,42792.0,0.2422472062769607
2016,366,Unknown,0.0,0.0,
2017,365,Night,53443.0,17598.0,0.3292854068820987
2017,365,Day,177553.0,43058.0,0.2425078708892556
2017,365,Unknown,0.0,0.0,
2018,365,Night,52368.0,17661.0,0.3372479376718607
2018,365,Day,179191.0,44279.0,0.2471050443381643
2018,365,Unknown,0.0,0.0,
2019,365,Night,49418.0,18192.0,0.36812497470557287
2019,365,Day,162068.0,43199.0,0.26654860922575707
2019,365,Unknown,0.0,0.0,
2020,366,Night,30284.0,14067.0,0.4645027077004359
2020,366,Day,82634.0,30548.0,0.3696783406346056
2020,366,Unknown,0.0,0.0,
2021,365,Night,33080.0,17253.0,0.5215538089480048
2021,365,Day,77477.0,34532.0,0.4457064677259058
2021,365,Unknown,0.0,0.0,
2022,365,Night,31309.0,16548.0,0.5285381200293845
2022,365,Day,72578.0,35385.0,0.4875444349527405
2022,365,Unknown,0.0,0.0,
2023,365,Night,29303.0,16998.0,0.580077125209023
2023,365,Day,67304.0,37254.0,0.5535183644359919
2023,365,Unknown,0.0,0.0,
2024,366,Night,27640.0,16846.0,0.609479015918958
2024,366,Day,63676.0,37184.0,0.5839562786607199
2024,366,Unknown,0.0,0.0,
2025,365,Night,25653.0,15275.0,0.5954469262854247
2025,365,Day,59893.0,34359.0,0.5736730502729869
2025,365,Unknown,0.0,0.0,

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