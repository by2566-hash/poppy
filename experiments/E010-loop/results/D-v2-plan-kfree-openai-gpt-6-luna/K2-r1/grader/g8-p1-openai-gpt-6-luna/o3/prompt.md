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
metric: Percentage of each calendar year's eligible police-reported crash records occurring on each weekday
denominator: All eligible police-reported crash records in the corresponding calendar year
grouping: Calendar year and weekday derived from crash_date; weekdays Monday through Sunday
chart_type: Annotated heatmap
probability: 0.35
WRITTEN ANSWER:
Friday has the largest weekday share in every year, while Sunday's share rises from 11.85% in 2013 to 13.09% in 2025. This framing answers how the weekday distribution changes across the requested years: Friday is the largest share each year, while Sunday rises from 11.85% in 2013 to 13.09% in 2025. Year-specific percentages make compositions comparable even when annual record totals differ, but the heatmap does not communicate total crash volume as directly as pooled counts. The plan includes 2,132,218 in-range records and excludes 136,969 dated records outside 2013–2025; the check found no missing dates and full observed January 1–December 31 endpoints in every included year. The 381 records dated 2013-01-01 are retained as valid; shares describe police-reported records, and the date check cannot establish reporting completeness.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,weekday,crash_count,year_total,share_pct
2013,Monday,29454,203742,14.456519
2013,Tuesday,30216,203742,14.830521
2013,Wednesday,29395,203742,14.427560
2013,Thursday,29727,203742,14.590512
2013,Friday,33111,203742,16.251436
2013,Saturday,27703,203742,13.597098
2013,Sunday,24136,203742,11.846355
2014,Monday,29963,206046,14.541898
2014,Tuesday,30791,206046,14.943750
2014,Wednesday,30588,206046,14.845229
2014,Thursday,30778,206046,14.937441
2014,Friday,32417,206046,15.732895
2014,Saturday,27662,206046,13.425157
2014,Sunday,23847,206046,11.573629
2015,Monday,31061,217708,14.267275
2015,Tuesday,32685,217708,15.013229
2015,Wednesday,32405,217708,14.884616
2015,Thursday,32909,217708,15.116119
2015,Friday,34408,217708,15.804656
2015,Saturday,27981,217708,12.852536
2015,Sunday,26259,217708,12.061569
2016,Monday,32291,229833,14.049767
2016,Tuesday,34314,229833,14.929971
2016,Wednesday,34236,229833,14.896033
2016,Thursday,34682,229833,15.090087
2016,Friday,37147,229833,16.162605
2016,Saturday,30796,229833,13.399294
2016,Sunday,26367,229833,11.472243
2017,Monday,33049,231007,14.306493
2017,Tuesday,33721,231007,14.597393
2017,Wednesday,33856,231007,14.655833
2017,Thursday,35356,231007,15.305164
2017,Friday,36921,231007,15.982633
2017,Saturday,30640,231007,13.263667
2017,Sunday,27464,231007,11.888817
2018,Monday,33594,231564,14.507436
2018,Tuesday,34469,231564,14.885302
2018,Wednesday,33916,231564,14.646491
2018,Thursday,35585,231564,15.367242
2018,Friday,36928,231564,15.947211
2018,Saturday,30483,231564,13.163963
2018,Sunday,26589,231564,11.482355
2019,Monday,30478,211486,14.411356
2019,Tuesday,31833,211486,15.052060
2019,Wednesday,30932,211486,14.626027
2019,Thursday,31693,211486,14.985862
2019,Friday,33724,211486,15.946209
2019,Saturday,28124,211486,13.298280
2019,Sunday,24702,211486,11.680206
2020,Monday,15846,112918,14.033192
2020,Tuesday,16184,112918,14.332524
2020,Wednesday,16258,112918,14.398059
2020,Thursday,16817,112918,14.893108
2020,Friday,18104,112918,16.032873
2020,Saturday,15866,112918,14.050904
2020,Sunday,13843,112918,12.259339
2021,Monday,15567,110558,14.080392
2021,Tuesday,15674,110558,14.177174
2021,Wednesday,15794,110558,14.285714
2021,Thursday,16078,110558,14.542593
... (truncated)

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
python3 -c "import json,csv, pathlib; p=pathlib.Path('out'); o=json.loads((p/'options.json').read_text()); assert len(o['options'])==3; assert abs(sum(x['probability'] for x in o['options'])-1)<1e-9; [json.loads((p/f'plan_{i}.json').read_text()) for i in (1,2,3)]; [assertion for assertion in []]; print('options JSON and plans parse; probability sum:', sum(x['probability'] for x in o['options'])); [print(f'option {i}: chart={ (p/f"option_{i}.png").is_file() }, values={ (p/f"values_{i}.csv").is_file() }, rows={sum(1 for _ in open(p/f"values_{i}.csv"))-1}') for i in (1,2,3)]"
# bash
python3 -c 'import json, pathlib; p=pathlib.Path("out"); o=json.loads((p/"options.json").read_text()); assert len(o["options"])==3; assert abs(sum(x["probability"] for x in o["options"])-1)<1e-9; [json.loads((p/("plan_"+str(i)+".json")).read_text()) for i in (1,2,3)]; print("options JSON and plans parse; probability sum:", sum(x["probability"] for x in o["options"])); print([(i,(p/("option_"+str(i)+".png")).is_file(),(p/("values_"+str(i)+".csv")).is_file(),sum(1 for _ in open(p/("values_"+str(i)+".csv")))-1) for i in (1,2,3)])'

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