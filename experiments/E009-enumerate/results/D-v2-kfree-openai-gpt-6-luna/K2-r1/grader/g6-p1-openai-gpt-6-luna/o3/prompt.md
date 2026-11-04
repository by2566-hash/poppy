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

DATA FACTS (pinned snapshot):
- The file covers 2012-07-01 to 2026-06-11; 2013-2025 are complete calendar years; 2026 is partial (to June 11).
- borough is NULL for about 20-38% of crashes in every year (TR05): a borough filter silently drops them.
- number_of_persons_killed is NULL in most May-2026 and all June-2026 rows (TR08); 2013-2025 killed counts have no NULLs.
- crash_time has no NULL rows. Reported crash counts (the number of crash records) fall sharply in 2020 (TR01), so a per-reported-crash rate (deaths or injuries divided by reported crashes) compared across years spanning 2020 needs a caveat. Counts of deaths or injuries by year do NOT need it (they are not affected by the reporting change), and a comparison between groups within one pooled window (e.g. day vs night) does not either (decided 2026-11-04; g5 wording after g4 failed c6 on plain death counts).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: How are NYC crashes distributed across the days of the week, 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Weekday share of annual crashes
denominator: All crashes in the corresponding year
grouping: Year and day of week, 2013–2025
chart_type: Multi-series line chart
probability: 0.2
WRITTEN ANSWER:
Friday had the largest weekday share in every year, ranging from 15.32% in 2023 to 16.25% in 2013, while Sunday rose overall from 11.85% in 2013 to 13.09% in 2025. This answers how the weekday composition evolved during 2013–2025: Friday led each year, while Sunday accounted for a larger share at the end than at the start. Within-year percentages make the yearly distributions comparable even when annual crash totals differ. It does not show absolute crash volumes by year.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,day_of_week,crashes,annual_total,share_of_year_crashes_pct
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
python -c "import duckdb; p='data/crashes.parquet'; c=duckdb.connect(); print(c.execute(f\"DESCRIBE SELECT * FROM read_parquet('{p}')\").fetchdf().to_string(index=False)); print(c.execute(f\"SELECT count(*) n, min(crash_date) min_date, max(crash_date) max_date FROM read_parquet('{p}')\").fetchdf().to_string(index=False))"
# bash
ls -la
# bash
python -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; q=\"SELECT year(crash_date) yr, dayname(crash_date) dow, dayofweek(crash_date) dow_n, count(*) n FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1,2,3 ORDER BY 1,3\"; d=c.execute(q,[p]).fetchdf(); print(d.to_string(index=False)); print('TOTAL',d.n.sum()); print('BY DOW'); print(d.groupby(['dow','dow_n'],as_index=False).n.sum().sort_values('dow_n').to_string(index=False)); print('YEAR COUNTS'); print(d.groupby('yr').n.sum().to_string())"
# bash
python -c "import duckdb; c=duckdb.connect(); print(c.execute(\"SELECT year(crash_date) yr, min(crash_date) first_date, max(crash_date) last_date, count(DISTINCT crash_date) distinct_dates, count(*) n FROM read_parquet('data/crashes.parquet') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1\").fetchdf().to_string(index=False)); print(c.execute(\"SELECT count(*) FROM read_parquet('data/crashes.parquet') WHERE crash_date IS NULL\").fetchone())"
# bash
python out/build_options.py
# bash
python out/build_options.py
# bash
python -c "import json,pathlib; p=pathlib.Path('out'); o=json.loads((p/'options.json').read_text()); assert len(o['options'])==3; assert abs(sum(x['probability'] for x in o['options'])-1)<1e-9; [(_ for _ in ()).throw(AssertionError(f'missing {name}')) for name in ['option_1.png','option_2.png','option_3.png','values_1.csv','values_2.csv','values_3.csv'] if not (p/name).is_file()]; print('Valid JSON; probabilities sum to',sum(x['probability'] for x in o['options'])); print('Output sizes:', {x.name:x.stat().st_size for x in sorted(p.iterdir()) if x.name != 'build_options.py'})"

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