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

QUESTION ASKED: How are NYC crashes distributed across the days of the week, 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: percentage of each year's police-reported crashes occurring on each weekday
denominator: all crashes with a valid crash_date in the same calendar year; each year's weekday percentages sum to 100%
grouping: calendar year and weekday of crash_date, Monday through Sunday
chart_type: multi-series line chart
probability: 0.45
WRITTEN ANSWER:
Friday accounted for the largest share of crashes in every year (15.3%–16.3%), while Sunday was the smallest share each year (11.5%–13.6%). This answers how the weekday composition varied across 2013–2025 inclusive by grouping each NYC police-reported motor vehicle crash row by its crash_date year and Monday-through-Sunday weekday, then dividing each weekday's count by all crash rows in that same year; Friday had the largest yearly share throughout (15.3%–16.3%) and Sunday the smallest (11.5%–13.6%). Within-year shares are defensible because they compare weekday composition without letting years with more crash records dominate. They leave unanswered the pooled number of crashes by weekday and any traffic-exposure-adjusted crash risk. The data check found 0 missing or impossible crash dates and full calendar-date coverage in all 13 years; 136,969 dated records outside 2013–2025 are excluded, while every in-period row is kept in its year's denominator.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,weekday,crash_count,year_total,share_of_year_pct
2013,Monday,29454,203742,14.4565
2013,Tuesday,30216,203742,14.8305
2013,Wednesday,29395,203742,14.4276
2013,Thursday,29727,203742,14.5905
2013,Friday,33111,203742,16.2514
2013,Saturday,27703,203742,13.5971
2013,Sunday,24136,203742,11.8464
2014,Monday,29963,206046,14.5419
2014,Tuesday,30791,206046,14.9438
2014,Wednesday,30588,206046,14.8452
2014,Thursday,30778,206046,14.9374
2014,Friday,32417,206046,15.7329
2014,Saturday,27662,206046,13.4252
2014,Sunday,23847,206046,11.5736
2015,Monday,31061,217708,14.2673
2015,Tuesday,32685,217708,15.0132
2015,Wednesday,32405,217708,14.8846
2015,Thursday,32909,217708,15.1161
2015,Friday,34408,217708,15.8047
2015,Saturday,27981,217708,12.8525
2015,Sunday,26259,217708,12.0616
2016,Monday,32291,229833,14.0498
2016,Tuesday,34314,229833,14.9300
2016,Wednesday,34236,229833,14.8960
2016,Thursday,34682,229833,15.0901
2016,Friday,37147,229833,16.1626
2016,Saturday,30796,229833,13.3993
2016,Sunday,26367,229833,11.4722
2017,Monday,33049,231007,14.3065
2017,Tuesday,33721,231007,14.5974
2017,Wednesday,33856,231007,14.6558
2017,Thursday,35356,231007,15.3052
2017,Friday,36921,231007,15.9826
2017,Saturday,30640,231007,13.2637
2017,Sunday,27464,231007,11.8888
2018,Monday,33594,231564,14.5074
2018,Tuesday,34469,231564,14.8853
2018,Wednesday,33916,231564,14.6465
2018,Thursday,35585,231564,15.3672
2018,Friday,36928,231564,15.9472
2018,Saturday,30483,231564,13.1640
2018,Sunday,26589,231564,11.4824
2019,Monday,30478,211486,14.4114
2019,Tuesday,31833,211486,15.0521
2019,Wednesday,30932,211486,14.6260
2019,Thursday,31693,211486,14.9859
2019,Friday,33724,211486,15.9462
2019,Saturday,28124,211486,13.2983
2019,Sunday,24702,211486,11.6802
2020,Monday,15846,112918,14.0332
2020,Tuesday,16184,112918,14.3325
2020,Wednesday,16258,112918,14.3981
2020,Thursday,16817,112918,14.8931
2020,Friday,18104,112918,16.0329
2020,Saturday,15866,112918,14.0509
2020,Sunday,13843,112918,12.2593
2021,Monday,15567,110558,14.0804
2021,Tuesday,15674,110558,14.1772
2021,Wednesday,15794,110558,14.2857
2021,Thursday,16078,110558,14.5426
... (truncated)

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls -ld . data && mkdir out
# bash
python3 out/check_data.py
# bash
python3 out/check_data.py
# bash
python3 out/analyze.py
# bash
python3 out/analyze.py
# bash
python3 -c "import json,csv,pathlib; p=pathlib.Path('out'); o=json.loads((p/'options.json').read_text()); assert sum(x['probability'] for x in o['options'])==1; rows=list(csv.DictReader((p/'values_1.csv').open())); assert sum(int(r['crash_count']) for r in rows)==2132218; assert max(rows,key=lambda r:int(r['crash_count']))['weekday']=='Friday'; assert min(rows,key=lambda r:int(r['crash_count']))['weekday']=='Sunday'; yr=list(csv.DictReader((p/'values_2.csv').open())); assert len(yr)==91; assert all(abs(sum(float(r['share_of_year_pct']) for r in yr if int(r['year'])==y)-100)<0.001 for y in range(2013,2026)); assert all((p/f'option_{i}.png').is_file() for i in (1,2)); print('Validated JSON, probabilities, pooled totals/extremes, annual percentage totals, and chart files.')"

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_DAYCOUNT: If per-day averages or 'X% fewer on <day>' comparisons are given, the arithmetic is right (e.g. Sunday has 24% fewer than the mean weekday, Friday 32% more) and unequal day counts (678/679) are handled or noted.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.