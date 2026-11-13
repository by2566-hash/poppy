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
metric: Number of police-reported crashes
denominator: None; a count of crashes
grouping: Day of week derived from crash_date, Monday through Sunday, pooled across 2013-2025
chart_type: Bar chart
probability: 0.6
WRITTEN ANSWER:
Among the 2,132,218 in-range crash records, Friday had the most reported crashes (338,800) and Sunday the fewest (257,544). Each row is one police-reported crash, and its weekday is derived from crash_date; the bars count records from 2013-01-01 through 2025-12-31 pooled together. Friday is the largest category at 338,800 crashes and Sunday the smallest at 257,544, giving the aggregate weekday distribution but not its year-to-year variation or exposure-adjusted risk. The check found 2,132,218 in-range rows, no missing crash dates or derived weekdays, and no default/sentinel dates, so all in-range rows were retained; 100,545 records before 2013 and 36,424 after 2025 were excluded. Observed dates span January 1 to December 31 in every year, though those endpoints alone do not prove complete reporting within each year.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
weekday,crashes
Monday,304518
Tuesday,313488
Wednesday,311111
Thursday,318376
Friday,338800
Saturday,288381
Sunday,257544

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls -la && mkdir -p out
# bash
./.bin/python -c 'import duckdb; con=duckdb.connect(); p="data/crashes.parquet"; print("duckdb", duckdb.__version__); print(con.execute("SELECT COUNT(*) AS source_rows, COUNT(*) FILTER (WHERE crash_date IS NULL) AS null_date_rows, COUNT(*) FILTER (WHERE crash_date < DATE '"'"'2013-01-01'"'"' OR crash_date > DATE '"'"'2025-12-31'"'"') AS out_of_range_rows FROM read_parquet(?)", [p]).fetchdf().to_string(index=False)); print(con.execute("SELECT year(crash_date) AS year, COUNT(*) AS rows, min(crash_date) AS first_date, max(crash_date) AS last_date FROM read_parquet(?) WHERE crash_date >= DATE '"'"'2013-01-01'"'"' AND crash_date <= DATE '"'"'2025-12-31'"'"' GROUP BY 1 ORDER BY 1", [p]).fetchdf().to_string(index=False))'
# bash
python3 -c 'import duckdb; print(duckdb.__version__)'
# bash
python3 -c "import duckdb; con=duckdb.connect(); p='data/crashes.parquet'; print(con.execute(\"SELECT COUNT(*) AS source_rows, COUNT(*) FILTER (WHERE crash_date IS NULL) AS null_date_rows, COUNT(*) FILTER (WHERE crash_date < DATE '2013-01-01' OR crash_date > DATE '2025-12-31') AS out_of_range_rows FROM read_parquet(?)\", [p]).fetchdf().to_string(index=False)); print(con.execute(\"SELECT year(crash_date) AS year, COUNT(*) AS rows, min(crash_date) AS first_date, max(crash_date) AS last_date FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date <= DATE '2025-12-31' GROUP BY 1 ORDER BY 1\", [p]).fetchdf().to_string(index=False))"
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(\"SELECT COUNT(*) AS in_scope, COUNT(*) FILTER (WHERE crash_date IN (DATE '1900-01-01', DATE '1970-01-01', DATE '0001-01-01')) AS sentinel_dates, COUNT(*) FILTER (WHERE dayname(crash_date) IS NULL) AS missing_or_invalid_weekday FROM read_parquet(?) WHERE crash_date BETWEEN DATE '2013-01-01' AND DATE '2025-12-31'\",[p]).fetchdf().to_string(index=False)); print(c.execute(\"SELECT COUNT(*) AS before_range FROM read_parquet(?) WHERE crash_date < DATE '2013-01-01',\",[p]).fetchdf().to_string(index=False))"
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(\"SELECT COUNT(*) FILTER (WHERE crash_date < DATE '2013-01-01') AS before_2013, COUNT(*) FILTER (WHERE crash_date > DATE '2025-12-31') AS after_2025 FROM read_parquet(?)\",[p]).fetchdf().to_string(index=False))"
# bash
python3 out/analyze.py
# bash
python3 -c "import json,csv,math; from pathlib import Path; o=Path('out'); plans=[json.loads((o/f'plan_{i}.json').read_text()) for i in (1,2)]; opts=json.loads((o/'options.json').read_text()); assert len(opts['options'])==2 and abs(sum(x['probability'] for x in opts['options'])-1)<1e-12; v1=list(csv.DictReader((o/'values_1.csv').open())); assert sum(int(x['crashes']) for x in v1)==2132218; assert max(v1,key=lambda x:int(x['crashes']))['weekday']=='Friday' and min(v1,key=lambda x:int(x['crashes']))['weekday']=='Sunday'; v2=list(csv.DictReader((o/'values_2.csv').open())); assert len(v2)==91; years=sorted(set(int(x['year']) for x in v2)); assert years==list(range(2013,2026)); assert all(abs(sum(float(x['share_percent']) for x in v2 if int(x['year'])==y)-100)<0.001 for y in years); assert all((o/f'option_{i}.png').stat().st_size>0 for i in (1,2)); assert all(int(x['year_total']) in [203742,206046,217708,229833,231007,231564,211486,112918,110558,103887,96607,91316,85546] for x in v2); print('Validated JSON, probabilities, values totals/shares, year coverage, and nonempty charts.')"

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