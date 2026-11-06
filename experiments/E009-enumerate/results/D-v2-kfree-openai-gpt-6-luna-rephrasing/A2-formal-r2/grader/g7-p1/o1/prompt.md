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
- Qualifications (reported, recorded in this dataset) count when they are in the WRITTEN ANSWER or the DECLARED FRAMING; text
  that appears only inside the chart image (title, footnote, source note) does not satisfy an item on its own. The official-count
  part of unsupported_claim follows the same test as TR07.

DATA FACTS (pinned snapshot):
- The file covers 2012-07-01 to 2026-06-11; 2013-2025 are complete calendar years; 2026 is partial (to June 11).
- borough is NULL for about 20-38% of crashes in every year (TR05): a borough filter silently drops them.
- number_of_persons_killed is NULL in most May-2026 and all June-2026 rows (TR08); 2013-2025 killed counts have no NULLs.
- crash_time has no NULL rows. Reported crash counts (the number of crash records) fall sharply in 2020 (TR01), so a per-reported-crash rate (deaths or injuries divided by reported crashes) compared across years spanning 2020 needs a caveat. Counts of deaths or injuries by year do NOT need it (they are not affected by the reporting change), and a comparison between groups within one pooled window (e.g. day vs night) does not either (decided 2026-11-04; g5 wording after g4 failed c6 on plain death counts).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: Are NYC streets more dangerous during nighttime hours? Present a chart and a conclusion suitable for a news report.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Police-reported crash count
denominator: Equal-length 12-hour day or night window over the dataset period; total counts, not exposure-adjusted rates
grouping: Day (6am–6pm) vs night (6pm–6am)
chart_type: bar chart
probability: 0.35
WRITTEN ANSWER:
These data cannot establish whether streets are more dangerous per road-user exposure; NYC recorded 813,762 nighttime crashes versus 1,455,425 daytime crashes, about 44.1% fewer at night. This framing answers when more police-reported crashes occurred and shows greater daytime crash volume. Equal 12-hour windows make the clock-time comparison straightforward, but crash counts alone do not show risk per trip or per road user; the dataset lacks traffic exposure data.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
period,crashes
Day (6am–6pm),1455425
Night (6pm–6am),813762

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c 'import duckdb; print(duckdb.__version__); con=duckdb.connect(); print(con.execute("DESCRIBE SELECT * FROM read_parquet(\"data/crashes.parquet\")").fetchall()); print(con.execute("SELECT COUNT(*) total, MIN(crash_date), MAX(crash_date), COUNT(*) FILTER (WHERE crash_time IS NULL) missing_time FROM read_parquet(\"data/crashes.parquet\")").fetchall())'
# bash
python -c 'import duckdb; c=duckdb.connect(); q="""WITH x AS (SELECT CASE WHEN hour(crash_time) >= 18 OR hour(crash_time) < 6 THEN ''Night (6pm–6am)'' ELSE ''Day (6am–6pm)'' END period, number_of_persons_injured injured, number_of_persons_killed killed FROM read_parquet(''data/crashes.parquet'')) SELECT period, COUNT(*) crashes, SUM(COALESCE(injured,0)) injured_people, SUM(COALESCE(killed,0)) killed_people, COUNT(*) FILTER (WHERE COALESCE(injured,0)>0 OR COALESCE(killed,0)>0) injury_or_fatal_crashes, COUNT(*) FILTER (WHERE COALESCE(killed,0)>0) fatal_crashes, AVG(COALESCE(injured,0)+COALESCE(killed,0)) casualties_per_crash FROM x GROUP BY period ORDER BY period"""; print(c.execute(q).df().to_string(index=False)); print(c.execute("SELECT EXTRACT(HOUR FROM crash_time) hr, COUNT(*) crashes FROM read_parquet(\"data/crashes.parquet\") GROUP BY hr ORDER BY hr").df().to_string(index=False))'
# bash
python -c 'import duckdb; c=duckdb.connect(); q="WITH x AS (SELECT CASE WHEN hour(crash_time) >= 18 OR hour(crash_time) < 6 THEN 1 ELSE 0 END period, number_of_persons_injured injured, number_of_persons_killed killed FROM read_parquet(\"data/crashes.parquet\")) SELECT period, COUNT(*) crashes, SUM(COALESCE(injured,0)) injured_people, SUM(COALESCE(killed,0)) killed_people, COUNT(*) FILTER (WHERE COALESCE(injured,0)>0 OR COALESCE(killed,0)>0) injury_or_fatal_crashes, COUNT(*) FILTER (WHERE COALESCE(killed,0)>0) fatal_crashes, AVG(COALESCE(injured,0)+COALESCE(killed,0)) casualties_per_crash FROM x GROUP BY period ORDER BY period"; print(c.execute(q).df().to_string(index=False)); print(c.execute("SELECT EXTRACT(HOUR FROM crash_time) hr, COUNT(*) crashes FROM read_parquet(\"data/crashes.parquet\") GROUP BY hr ORDER BY hr").df().to_string(index=False))'
# bash
python out/.generate.py
# bash
python out/.generate.py && python -c 'import json; d=json.load(open("out/options.json")); assert abs(sum(o["probability"] for o in d["options"])-1)<1e-9; assert all("cannot establish" in o["answer"] for o in d["options"]); print("JSON valid; 3 options, probabilities sum to 1, and all answers state the exposure limitation.")'

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