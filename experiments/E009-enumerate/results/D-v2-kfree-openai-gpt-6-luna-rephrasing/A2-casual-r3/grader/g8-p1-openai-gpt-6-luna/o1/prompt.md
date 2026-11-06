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

QUESTION ASKED: Is it more dangerous to be on NYC's streets at night? Make a chart and say what you conclude for a news report.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Police-reported crash count standardized by clock-hours
denominator: Clock-hours in each defined period across the 5,094 calendar dates
grouping: Day (6:00 a.m.–7:59 p.m.) versus night (8:00 p.m.–5:59 a.m.)
chart_type: Bar chart
probability: 0.2
WRITTEN ANSWER:
The dataset averages 24.0 reported crashes per daytime clock-hour versus 11.0 per nighttime clock-hour, but this does not measure an individual's risk. This framing answers whether crash reports are more frequent at night after accounting for the 14-hour daytime and 10-hour nighttime windows; they are less frequent per clock-hour at night. It is a defensible description of recorded crash volume, but without traffic or traveler exposure it cannot establish whether a person on the street is safer or less safe at night.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
period,crashes,calendar_days,hours_per_daypart,observed_clock_hours,crashes_per_clock_hour
Day,1710183,5094,14,71316,23.980355039542317
Night,559004,5094,10,50940,10.973773066352571

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("DESCRIBE SELECT * FROM read_parquet(?)",[p]).fetchall()); print(c.execute("SELECT COUNT(*), MIN(crash_date), MAX(crash_date), COUNT(*) FILTER (WHERE crash_time IS NULL) FROM read_parquet(?)",[p]).fetchall()); print(c.execute("SELECT EXTRACT(hour FROM crash_time) AS h, COUNT(*) AS n, SUM(number_of_persons_injured) AS injured, SUM(number_of_persons_killed) AS killed FROM read_parquet(?) WHERE crash_time IS NOT NULL GROUP BY h ORDER BY h",[p]).fetchall())'
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); q="WITH x AS (SELECT CASE WHEN EXTRACT(hour FROM crash_time) >= 20 OR EXTRACT(hour FROM crash_time) < 6 THEN \'Night\' ELSE \'Day\' END AS period, * FROM read_parquet(?) WHERE crash_time IS NOT NULL) SELECT period, COUNT(*) crashes, SUM(number_of_persons_injured) injured_people, SUM(number_of_persons_killed) killed_people, COUNT(*) FILTER (WHERE COALESCE(number_of_persons_injured,0)>0) injury_crashes, COUNT(*) FILTER (WHERE COALESCE(number_of_persons_killed,0)>0) fatal_crashes, SUM(number_of_pedestrians_injured) ped_injured, SUM(number_of_pedestrians_killed) ped_killed, COUNT(*) FILTER (WHERE COALESCE(number_of_pedestrians_injured,0)>0 OR COALESCE(number_of_pedestrians_killed,0)>0) ped_casualty_crashes FROM x GROUP BY period ORDER BY period"; print(c.execute(q,[p]).fetchdf().to_string(index=False)); print(c.execute("SELECT MIN(crash_date), MAX(crash_date), COUNT(DISTINCT crash_date) FROM read_parquet(?)",[p]).fetchall())'
# bash
python3 -c "import duckdb; c=duckdb.connect(); print(c.execute(\"SELECT CASE WHEN EXTRACT(hour FROM crash_time)>=20 OR EXTRACT(hour FROM crash_time)<6 THEN 'Night' ELSE 'Day' END p, COUNT(*) n, SUM(number_of_persons_injured) inj, SUM(number_of_persons_killed) killed, COUNT(*) FILTER (WHERE number_of_persons_injured>0) injcr, COUNT(*) FILTER (WHERE number_of_persons_killed>0) fatalcr, COUNT(*) FILTER (WHERE number_of_pedestrians_injured>0 OR number_of_pedestrians_killed>0) pedcr FROM read_parquet('data/crashes.parquet') GROUP BY p ORDER BY p\").fetchdf().to_string(index=False))"
# bash
python3 -c "import duckdb; c=duckdb.connect(); print(c.execute(\"SELECT MIN(crash_date), MAX(crash_date), COUNT(DISTINCT crash_date), COUNT(*) FILTER (WHERE crash_time IS NULL) FROM read_parquet('data/crashes.parquet')\").fetchall()); print(c.execute(\"SELECT CASE WHEN EXTRACT(hour FROM crash_time)>=20 OR EXTRACT(hour FROM crash_time)<6 THEN 'Night' ELSE 'Day' END p, COUNT(*) n, SUM(number_of_persons_injured+number_of_persons_killed) people_harmed, COUNT(*) FILTER (WHERE number_of_pedestrians_injured>0 OR number_of_pedestrians_killed>0) pedcr, SUM(number_of_pedestrians_injured+number_of_pedestrians_killed) pedharm FROM read_parquet('data/crashes.parquet') GROUP BY p ORDER BY p\").fetchdf().to_string(index=False))"
# bash
python3 analysis.py
# bash
python3 analysis.py
# bash
python3 analysis.py
# bash
python3 -c "import json, pathlib; p=pathlib.Path('out/options.json'); d=json.loads(p.read_text()); print('options', len(d['options']), 'probability_sum', sum(x['probability'] for x in d['options'])); print('artifacts', all(pathlib.Path(f'out/{stem}_{i}.{ext}').exists() for i in range(1,4) for stem,ext in [('option','png'),('values','csv')]))"

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