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
metric: Share of crashes involving at least one person injured or killed
denominator: Crashes with both number_of_persons_injured and number_of_persons_killed non-NULL
grouping: Night (7 p.m.–5:59 a.m.) versus day (6 a.m.–6:59 p.m.)
chart_type: Bar chart
probability: 0.45
WRITTEN ANSWER:
Among crashes with complete outcome counts, 28.32% at night involved injury or death, compared with 23.09% by day, indicating greater per-crash harm at night on this measure. This framing answers whether a reported crash is more likely to involve injury or death at night; the chart shows 28.32% at night versus 23.09% by day. It is a defensible per-crash harm measure, but it does not estimate risk per traveler or compare overall crash frequency. It excludes 8,919 rows (0.39% of the file) because at least one injury or fatality count is NULL: 5,820 of 1,594,921 day crashes (0.36%) and 3,099 of 674,266 night crashes (0.46%). The pooled file also includes partial 2012 coverage (2012-07-01–2012-12-31; 49.7% of that calendar year's days are outside the file) and partial 2026 coverage (2026-01-01–2026-06-11; 55.6% of that calendar year's days are outside the file).

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
period,injury_or_fatal_crashes,complete_outcome,missing_outcome,injury_or_fatal_crash_share_pct
Day,366983,1589101,5820,23.09374923
Night,190095,671167,3099,28.32305522

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls -la
# bash
python3 -c "import duckdb, pandas, matplotlib; print('duckdb', duckdb.__version__); print('pandas', pandas.__version__); print('matplotlib', matplotlib.__version__)"
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("DESCRIBE SELECT * FROM read_parquet(?)", [p]).fetchdf().to_string(index=False)); print("DATE RANGE", c.execute("SELECT min(crash_date), max(crash_date), count(*), count(crash_time), count(*) FILTER (WHERE crash_time IS NULL), count(*) FILTER (WHERE crash_date IS NULL) FROM read_parquet(?)", [p]).fetchall()); print("YEAR COUNTS", c.execute("SELECT year(crash_date) y, count(*) n, min(crash_date), max(crash_date) FROM read_parquet(?) GROUP BY 1 ORDER BY 1", [p]).fetchdf().to_string(index=False)); print("NULL METRICS", c.execute("SELECT count(*) FILTER (WHERE number_of_persons_injured IS NULL), count(*) FILTER (WHERE number_of_persons_killed IS NULL), count(*) FILTER (WHERE number_of_pedestrians_injured IS NULL), count(*) FILTER (WHERE number_of_cyclist_injured IS NULL) FROM read_parquet(?)", [p]).fetchall()); print("TIME AGG", c.execute("SELECT CASE WHEN hour(crash_time) >= 19 OR hour(crash_time) < 6 THEN \'Night\' ELSE \'Day\' END bucket, count(*) n, count(*) FILTER (WHERE number_of_persons_injured > 0 OR number_of_persons_killed > 0) hurt_crashes, sum(number_of_persons_injured) injured, sum(number_of_persons_killed) killed FROM read_parquet(?) WHERE crash_time IS NOT NULL GROUP BY 1", [p]).fetchdf().to_string(index=False))'
# bash
python3 -c "import duckdb; print(duckdb.__version__)"
# bash
python3 -c 'import duckdb
c=duckdb.connect()
p="data/crashes.parquet"
print(c.execute("DESCRIBE SELECT * FROM read_parquet(?)", [p]).fetchdf().to_string(index=False))
print("DATE RANGE", c.execute("SELECT min(crash_date), max(crash_date), count(*), count(crash_time), count(*) FILTER (WHERE crash_time IS NULL), count(*) FILTER (WHERE crash_date IS NULL) FROM read_parquet(?)", [p]).fetchall())
print("YEAR COUNTS", c.execute("SELECT year(crash_date) y, count(*) n, min(crash_date), max(crash_date) FROM read_parquet(?) GROUP BY 1 ORDER BY 1", [p]).fetchdf().to_string(index=False))
print("NULL METRICS", c.execute("SELECT count(*) FILTER (WHERE number_of_persons_injured IS NULL), count(*) FILTER (WHERE number_of_persons_killed IS NULL), count(*) FILTER (WHERE number_of_pedestrians_injured IS NULL), count(*) FILTER (WHERE number_of_cyclist_injured IS NULL) FROM read_parquet(?)", [p]).fetchall())
print("TIME AGG", c.execute("SELECT CASE WHEN hour(crash_time) >= 19 OR hour(crash_time) < 6 THEN \'Night\' ELSE \'Day\' END bucket, count(*) n, count(*) FILTER (WHERE number_of_persons_injured > 0 OR number_of_persons_killed > 0) hurt_crashes, sum(number_of_persons_injured) injured, sum(number_of_persons_killed) killed FROM read_parquet(?) WHERE crash_time IS NOT NULL GROUP BY 1", [p]).fetchdf().to_string(index=False))'
# bash
python3 -c 'exec("import duckdb\nc=duckdb.connect()\np=\"data/crashes.parquet\"\nprint(c.execute(\"DESCRIBE SELECT * FROM read_parquet(?)\", [p]).fetchdf().to_string(index=False))\nprint(\"DATE RANGE\", c.execute(\"SELECT min(crash_date), max(crash_date), count(*), count(crash_time), count(*) FILTER (WHERE crash_time IS NULL), count(*) FILTER (WHERE crash_date IS NULL) FROM read_parquet(?)\", [p]).fetchall())\nprint(\"YEAR COUNTS\", c.execute(\"SELECT year(crash_date) y, count(*) n, min(crash_date), max(crash_date) FROM read_parquet(?) GROUP BY 1 ORDER BY 1\", [p]).fetchdf().to_string(index=False))\nprint(\"NULL METRICS\", c.execute(\"SELECT count(*) FILTER (WHERE number_of_persons_injured IS NULL), count(*) FILTER (WHERE number_of_persons_killed IS NULL), count(*) FILTER (WHERE number_of_pedestrians_injured IS NULL), count(*) FILTER (WHERE number_of_cyclist_injured IS NULL) FROM read_parquet(?)\", [p]).fetchall())\nprint(\"TIME AGG\", c.execute(\"SELECT CASE WHEN hour(crash_time) >= 19 OR hour(crash_time) < 6 THEN \\\'Night\\\' ELSE \\\'Day\\\' END bucket, count(*) n, count(*) FILTER (WHERE number_of_persons_injured > 0 OR number_of_persons_killed > 0) hurt_crashes, sum(number_of_persons_injured) injured, sum(number_of_persons_killed) killed FROM read_parquet(?) WHERE crash_time IS NOT NULL GROUP BY 1\", [p]).fetchdf().to_string(index=False))")'
# bash
python3 out/inspect_data.py
# bash
python3 out/generate.py
# bash
python3 out/generate.py
# bash
python3 -m json.tool out/options.json

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