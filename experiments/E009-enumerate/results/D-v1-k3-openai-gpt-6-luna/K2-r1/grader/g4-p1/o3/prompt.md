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

DATA FACTS (pinned snapshot):
- The file covers 2012-07-01 to 2026-06-11; 2013-2025 are complete calendar years; 2026 is partial (to June 11).
- borough is NULL for about 20-38% of crashes in every year (TR05): a borough filter silently drops them.
- number_of_persons_killed is NULL in most May-2026 and all June-2026 rows (TR08); 2013-2025 killed counts have no NULLs.
- crash_time has no NULL rows. Reported crash counts fall sharply in 2020 (TR01): a per-reported-crash rate or a pooled count COMPARED ACROSS YEARS spanning 2020 needs a caveat; a comparison between groups within one pooled window (e.g. day vs night) does not (decided 2026-11-04).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: How are NYC crashes distributed across the days of the week, 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Share of that year's crash records (percent)
denominator: All crash records in the same calendar year
grouping: Year and weekday, 2013–2025
chart_type: Multi-series line chart
probability: 0.3
WRITTEN ANSWER:
Friday had the largest share of crashes in 13 of the 13 years, and Sunday had the smallest share in 13 years; the lines show the annual weekday mix rather than cumulative volume.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,weekday,crashes,annual_total,share_percent
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
python3 -c "import duckdb, pandas, matplotlib; print('duckdb',duckdb.__version__,'pandas',pandas.__version__,'matplotlib',matplotlib.__version__)"
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(\"SELECT min(crash_date), max(crash_date), count(*), count_if(crash_date IS NULL) FROM read_parquet(?)\",[p]).fetchall()); print(c.execute(\"SELECT strftime(crash_date, '%A') weekday, count(*) n FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY CASE weekday WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3 WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6 ELSE 7 END\",[p]).fetchall())"
# bash
python3 -c "import duckdb; c=duckdb.connect(); print(c.execute(\"SELECT year(crash_date), min(crash_date), max(crash_date), count(*) FROM read_parquet('data/crashes.parquet') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1\").fetchall())"
# bash
python3 out/.generate_options.py
# bash
python3 -c "import json, pandas as pd; from pathlib import Path; p=Path('out'); opts=json.loads((p/'options.json').read_text())['options']; a=pd.read_csv(p/'values_1.csv'); b=pd.read_csv(p/'values_2.csv'); c=pd.read_csv(p/'values_3.csv'); assert a.crashes.sum()==2132218 and len(a)==7; assert abs(b.share_percent.sum()-100)<1e-9; assert len(c)==91 and c.groupby('year').size().eq(7).all(); assert len(opts)==3 and abs(sum(x['probability'] for x in opts)-1)<1e-9; assert all((p/f'option_{i}.png').read_bytes()[:8]==b'\x89PNG\r\n\x1a\n' and (p/f'values_{i}.csv').exists() for i in (1,2,3)); print('Validated: totals, percentages, 13 years × 7 weekdays, JSON probabilities, and all three PNG/CSV pairs.')"

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