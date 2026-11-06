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
metric: Percentage of crashes involving at least one death
denominator: All reported crashes in the same time period
grouping: Daytime (6 a.m.–5:59 p.m.) vs nighttime (6 p.m.–5:59 a.m.)
chart_type: Two-bar percentage comparison
probability: 0.45
WRITTEN ANSWER:
Fatal crashes made up 0.245% of nighttime reports versus 0.101% of daytime reports, about 2.4 times the daytime share. This addresses whether a reported crash was more likely to involve at least one death: the fatal-crash share was markedly higher at night. Fatal outcome per crash is a defensible measure of crash severity, while the chart cannot tell whether a person traveling at night faces greater fatality risk because traffic exposure is unavailable.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
period,crashes,fatal_crashes,fatal_crash_pct
Daytime (6 a.m.–5:59 p.m.),1455425,1477,0.101482
Nighttime (6 p.m.–5:59 a.m.),813762,1992,0.244789

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
git status --short
# bash
ls
# bash
python3 -c "import duckdb; c=duckdb.connect(); print(c.execute(\"DESCRIBE SELECT * FROM read_parquet('data/crashes.parquet')\").fetchall()); print(c.execute(\"SELECT COUNT(*) AS n, MIN(crash_date), MAX(crash_date), COUNT(*) FILTER (WHERE crash_time IS NULL) FROM read_parquet('data/crashes.parquet')\").fetchall())"
# bash
python3 -c "import duckdb; c=duckdb.connect(); q=\"\"\"WITH x AS (SELECT CASE WHEN CAST(crash_time AS TIME) >= TIME '18:00:00' OR CAST(crash_time AS TIME) < TIME '06:00:00' THEN 'Night (6 p.m.–5:59 a.m.)' ELSE 'Day (6 a.m.–5:59 p.m.)' END AS period, number_of_persons_injured AS injured, number_of_persons_killed AS killed, number_of_pedestrians_injured AS ped_inj, number_of_pedestrians_killed AS ped_kill FROM read_parquet('data/crashes.parquet')) SELECT period, COUNT(*) crashes, SUM(injured) injured, SUM(killed) killed, COUNT(*) FILTER (WHERE injured>0) injury_crashes, COUNT(*) FILTER (WHERE killed>0) fatal_crashes, SUM(ped_inj) ped_inj, SUM(ped_kill) ped_kill FROM x GROUP BY period ORDER BY period\"\"\"; print(c.execute(q).df().to_string(index=False)); print(c.execute(\"SELECT MIN(crash_time), MAX(crash_time), COUNT(*) FILTER (WHERE crash_time IS NULL) FROM read_parquet('data/crashes.parquet')\").fetchall())"
# bash
ls out
# bash
python3 out/build_analysis.py
# bash
python3 out/build_analysis.py
# bash
python3 -c "import json, pathlib; p=pathlib.Path('out/options.json'); d=json.loads(p.read_text()); assert abs(sum(x['probability'] for x in d['options'])-1)<1e-9; assert len(d['options'])==3; assert all(pathlib.Path(f'out/{prefix}_{i}.{ext}').exists() for i in range(1,4) for prefix,ext in [('option','png'),('values','csv')]); print('options.json valid; probabilities sum to', sum(x['probability'] for x in d['options']))"

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