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
metric: Percentage of each year's included crash rows assigned to each weekday
denominator: All rows with crash_date in the same calendar year
grouping: Year and weekday derived from crash_date (Monday–Sunday), separately within each year from 2013 to 2025
chart_type: Annotated heatmap
probability: 0.3
WRITTEN ANSWER:
Friday has the largest share in every year, ranging from 15.3% in 2023 to 16.3% in 2013. Each heatmap row is one complete calendar year from 2013 through 2025, and its cells are the weekday shares of that year's crash rows; Friday is largest in every year, ranging from 15.3% in 2023 to 16.3% in 2013. Normalizing within year is a defensible way to compare annual weekday composition without pooling row counts across years. This answers how the reported-crash weekday mix varies by year, but not how weekday crash risk or traffic exposure varies. The check found 0 NULL crash dates and January 1–December 31 date coverage in every year, so no in-range rows were dropped; annual rows fell by 98,568 from 211,486 in 2019 to 112,918 in 2020, so a rise or fall in annual shares can come from the changed row-count denominator rather than the underlying crash outcome, and cross-year comparisons need that caution.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,weekday,crash_rows,year_rows,share_percent
2013,Monday,29454,203742,14.456518538151192
2013,Tuesday,30216,203742,14.830520952969934
2013,Wednesday,29395,203742,14.427560345927692
2013,Thursday,29727,203742,14.59051152928704
2013,Friday,33111,203742,16.251435639190742
2013,Saturday,27703,203742,13.597098290975843
2013,Sunday,24136,203742,11.84635470349756
2014,Monday,29963,206046,14.54189841103443
2014,Tuesday,30791,206046,14.943750424662456
2014,Wednesday,30588,206046,14.845228735330945
2014,Thursday,30778,206046,14.937441153917085
2014,Friday,32417,206046,15.73289459635227
2014,Saturday,27662,206046,13.425157489104375
2014,Sunday,23847,206046,11.573629189598439
2015,Monday,31061,217708,14.267275433148988
2015,Tuesday,32685,217708,15.013228728388484
2015,Wednesday,32405,217708,14.884616091278227
2015,Thursday,32909,217708,15.116118838076689
2015,Friday,34408,217708,15.804655777463392
2015,Saturday,27981,217708,12.852536424936153
2015,Sunday,26259,217708,12.061568706708067
2016,Monday,32291,229833,14.049766569639695
2016,Tuesday,34314,229833,14.929970891908473
2016,Wednesday,34236,229833,14.896033206719661
2016,Thursday,34682,229833,15.09008715023517
2016,Friday,37147,229833,16.16260502190721
2016,Saturday,30796,229833,13.399294270187484
2016,Sunday,26367,229833,11.472242889402304
2017,Monday,33049,231007,14.306492876839231
2017,Tuesday,33721,231007,14.59739315258845
2017,Wednesday,33856,231007,14.655832940127356
2017,Thursday,35356,231007,15.305163912781863
2017,Friday,36921,231007,15.982632560918066
2017,Saturday,30640,231007,13.263667334756091
2017,Sunday,27464,231007,11.888817221988944
2018,Monday,33594,231564,14.507436389076023
2018,Tuesday,34469,231564,14.885301687654383
2018,Wednesday,33916,231564,14.64649081895286
2018,Thursday,35585,231564,15.367241885612618
2018,Friday,36928,231564,15.947211138173465
2018,Saturday,30483,231564,13.163963310359122
2018,Sunday,26589,231564,11.48235477017153
2019,Monday,30478,211486,14.411355834428758
2019,Tuesday,31833,211486,15.052060183652818
2019,Wednesday,30932,211486,14.62602725475918
2019,Thursday,31693,211486,14.985861948308635
2019,Friday,33724,211486,15.94620920533747
2019,Saturday,28124,211486,13.298279791570128
2019,Sunday,24702,211486,11.680205781943013
2020,Monday,15846,112918,14.033192227988453
2020,Tuesday,16184,112918,14.332524486795728
2020,Wednesday,16258,112918,14.398058768309745
2020,Thursday,16817,112918,14.893108273260241
2020,Friday,18104,112918,16.03287341256487
2020,Saturday,15866,112918,14.050904195965213
2020,Sunday,13843,112918,12.259338635115748
2021,Monday,15567,110558,14.080392192333434
2021,Tuesday,15674,110558,14.177173972032781
2021,Wednesday,15794,110558,14.285714285714285
2021,Thursday,16078,110558,14.542593028093851
... (truncated)

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
pwd && python3 -c "import duckdb, pandas, matplotlib; print('duckdb', duckdb.__version__); print('pandas', pandas.__version__); print('matplotlib', matplotlib.__version__)"
# bash
ls
# bash
python3 out/data_check.py
# bash
python3 out/data_check.py
# bash
python3 out/data_check.py
# bash
python3 out/analyze.py
# bash
python3 out/data_check.py
# bash
python3 -c "import json, pathlib, pandas as pd; p=pathlib.Path('out'); opts=json.loads((p/'options.json').read_text()); plans=[json.loads((p/f'plan_{i}.json').read_text()) for i in (1,2,3)]; probs=sum(x['probability'] for x in opts['options']); v1=pd.read_csv(p/'values_1.csv'); v2=pd.read_csv(p/'values_2.csv'); v3=pd.read_csv(p/'values_3.csv'); print('options',len(opts['options']),'probability_sum',probs,'plan_jsons',len(plans)); print('count_total',int(v1.crash_rows.sum()),'shares_total_pct',v2.share_percent.sum(),'annual_rows',len(v3),'annual_share_min_max',v3.groupby('year').share_percent.sum().min(),v3.groupby('year').share_percent.sum().max()); print('artifacts',all((p/f'{name}_{i}.{ext}').exists() for i in (1,2,3) for name,ext in [('option','png'),('values','csv'),('check','csv')]))"
# bash
python3 -c "import json, pathlib, pandas as pd; p=pathlib.Path('out'); opts=json.loads((p/'options.json').read_text()); plans=[json.loads((p/f'plan_{i}.json').read_text()) for i in (1,2,3)]; probs=sum(x['probability'] for x in opts['options']); v1=pd.read_csv(p/'values_1.csv'); v2=pd.read_csv(p/'values_2.csv'); v3=pd.read_csv(p/'values_3.csv'); print('options',len(opts['options']),'probability_sum',probs,'plan_jsons',len(plans)); print('count_total',int(v1.crash_rows.sum()),'shares_total_pct',v2.share_percent.sum(),'annual_rows',len(v3),'annual_share_min_max',v3.groupby('year').share_percent.sum().min(),v3.groupby('year').share_percent.sum().max()); print('artifacts',all((p/f'{name}_{i}.{ext}').exists() for i in (1,2,3) for name,ext in [('option','png'),('values','csv'),('check','csv')]))"

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