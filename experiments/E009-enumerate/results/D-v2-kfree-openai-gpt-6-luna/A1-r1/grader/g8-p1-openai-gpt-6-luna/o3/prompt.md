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

QUESTION ASKED: Has road safety for pedestrians in Brooklyn gotten better since 2013? Make a chart suitable for a local news story and summarize the findings.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Share of reported Brooklyn crashes with a pedestrian injured or killed
denominator: All police-reported motor vehicle crashes with Brooklyn recorded as borough
grouping: Calendar year, Brooklyn, 2013–2025
chart_type: Line chart
probability: 0.35
WRITTEN ANSWER:
The file cannot establish whether risk per walking trip improved; pedestrian-harm crashes rose from 7.4% of reported Brooklyn crashes in 2013 to 11.4% in 2025 (+3.9 percentage points). This framing answers whether pedestrian-injury-or-death crashes became a larger part of Brooklyn's reported crash record: their share rose from 2013 to 2025. It is a defensible relative measure when the overall number of recorded crashes changes substantially. It is not a pedestrian exposure rate and misses pedestrian-involved crashes with no reported pedestrian injury or death.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,crashes_with_pedestrian_harm,all_reported_crashes,pedestrian_harm_share_percent
2013,3498,47024,7.4388
2014,3234,47761,6.7712
2015,2962,50851,5.8249
2016,2797,47464,5.8929
2017,2550,44915,5.6774
2018,2697,47313,5.7003
2019,2623,44479,5.8972
2020,1724,25473,6.7680
2021,1856,25174,7.3727
2022,2185,23369,9.3500
2023,2310,22890,10.0917
2024,2576,22785,11.3057
2025,2766,24303,11.3813

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("DESCRIBE SELECT * FROM read_parquet(?)", [p]).fetchdf().to_string(index=False)); print(c.execute("SELECT min(crash_date), max(crash_date), count(*) FROM read_parquet(?)", [p]).fetchall())'
# bash
python -c 'import duckdb; c=duckdb.connect(); q="""SELECT year(crash_date) yr, count(*) crashes, sum(coalesce(number_of_pedestrians_injured,0)) injured, sum(coalesce(number_of_pedestrians_killed,0)) killed, max(crash_date) latest, sum(case when coalesce(number_of_pedestrians_injured,0)>0 or coalesce(number_of_pedestrians_killed,0)>0 then 1 else 0 end) injured_or_fatal_crashes FROM read_parquet(\"data/crashes.parquet\") WHERE upper(trim(borough))=\'BROOKLYN\' AND crash_date >= DATE \'2013-01-01\' GROUP BY 1 ORDER BY 1"""; print(c.execute(q).fetchdf().to_string(index=False))'
# bash
python - <<'PY'
import duckdb
c=duckdb.connect()
q='''SELECT year(crash_date) yr, count(*) crashes,
 sum(coalesce(number_of_pedestrians_injured,0)) injured,
 sum(coalesce(number_of_pedestrians_killed,0)) killed,
 max(crash_date) latest,
 sum(case when coalesce(number_of_pedestrians_injured,0)>0 or coalesce(number_of_pedestrians_killed,0)>0 then 1 else 0 end) injured_or_fatal_crashes
FROM read_parquet('data/crashes.parquet')
WHERE upper(trim(borough))='BROOKLYN' AND crash_date >= DATE '2013-01-01'
GROUP BY 1 ORDER BY 1'''
print(c.execute(q).fetchdf().to_string(index=False))
PY
# bash
python out/generate_analysis.py
# bash
python out/generate_analysis.py
# bash
python - <<'PY'
import json
from pathlib import Path
p=Path('out')
options=json.loads((p/'options.json').read_text())['options']
assert [x['id'] for x in options] == [1,2,3]
assert abs(sum(x['probability'] for x in options)-1)<1e-9
for i in range(1,4):
    assert (p/f'option_{i}.png').is_file() and (p/f'values_{i}.csv').is_file()
    assert len((p/f'values_{i}.csv').read_text().splitlines()) == 14
print('Validated JSON, option IDs/probabilities, and all chart/value outputs.')
PY

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR05: If a borough filter (borough = 'BROOKLYN') is used, the output discloses that crashes with no borough recorded (19.9–38.1% per year) are excluded.
- tr_TR11: The output does not call Brooklyn 'safer' or 'less safe' from counts alone without saying that there is no pedestrian exposure measure.
- tr_TR01: If a per-crash rate spanning 2020 is shown, the output caveats the 2020 change in crash recording.
- tr_TR15: Claims about pedestrian deaths changing are qualified by the small counts (about 30–39 per year).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.