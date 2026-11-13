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

QUESTION ASKED: Are NYC's streets more dangerous at night? Make a chart and give a conclusion for a news report.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Number of persons killed per 1,000 reported crashes
denominator: Crash reports with a non-NULL death count
grouping: Night (8 p.m.–5:59 a.m.) versus daytime (6 a.m.–7:59 p.m.); complete calendar years 2013–2025
chart_type: Two-bar comparison of deaths per 1,000 crashes
probability: 0.5
WRITTEN ANSWER:
The records show 3.08 people killed per 1,000 nighttime crashes versus 1.12 per 1,000 daytime crashes, indicating greater fatal harm per reported crash at night. This framing answers whether nighttime crashes produce more fatal harm per reported crash: there were 3.08 deaths per 1,000 nighttime crashes versus 1.12 per 1,000 daytime crashes. This is defensible as a fatal-severity rate because it accounts for the number of crash reports in each period, rather than comparing raw death totals alone. It does not establish that an individual traveler is at greater risk at night, because the file contains no traffic or travel-exposure denominator. It omits records dated in partial 2012 and 2026 (136969 rows, 6.04% of all file rows) and 2013–2025 records with a NULL death count (36 rows, 0.0017% of complete-year rows); no rows are omitted for missing crash time.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
period,metric,denominator,crashes,events,rate,rate_per_1000
Daytime,"Persons killed per 1,000 crash reports",Crash reports with death count present,1607471,1798,0.00111853,1.11852718
Night,"Persons killed per 1,000 crash reports",Crash reports with death count present,524711,1614,0.00307598,3.07597897

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c "import duckdb, pandas, matplotlib; print('duckdb', duckdb.__version__, 'pandas', pandas.__version__, 'matplotlib', matplotlib.__version__)"
# bash
python -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(\"select count(*) n, min(crash_date), max(crash_date), count(*) filter(where crash_time is null) time_null, count(*) filter(where number_of_persons_injured is null) injury_null, count(*) filter(where number_of_persons_killed is null) death_null from read_parquet(?)\", [p]).fetchall()); print(c.execute(\"select date_trunc('year', crash_date) yr, count(*) n, min(crash_date), max(crash_date) from read_parquet(?) group by 1 order by 1\", [p]).fetchall()); print(c.execute(\"describe select * from read_parquet(?)\", [p]).fetchall())"
# bash
ls
# bash
python generate_crash_options.py
# bash
python -c "import duckdb; print(duckdb.connect().execute(\"select date_part('year', crash_date) yr, count(*) n, count(*) filter(where number_of_persons_injured is null) injury_null, count(*) filter(where number_of_persons_killed is null) death_null from read_parquet('data/crashes.parquet') group by 1 order by 1\").fetchall())"
# bash
python generate_crash_options.py
# bash
python -c "import json, pathlib; p=pathlib.Path('out/options.json'); d=json.loads(p.read_text()); print('valid_json', len(d['options'])==2, 'probability_sum', sum(x['probability'] for x in d['options']), 'ids', [x['id'] for x in d['options']]); print('outputs', sorted(x.name for x in pathlib.Path('out').iterdir()))"

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