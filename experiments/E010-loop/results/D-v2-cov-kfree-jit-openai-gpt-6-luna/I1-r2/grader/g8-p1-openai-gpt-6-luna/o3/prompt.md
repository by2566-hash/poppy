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

QUESTION ASKED: Did the risk of a motorist being killed per mile driven in NYC decline from 2013 to 2025? Make a chart and answer based on this crash data.
QUESTION TYPE: insufficient
DECLARED FRAMING:
metric: Motorist deaths per 1,000 crashes involving a motorist injury or death
denominator: Crash rows with at least one motorist injured or killed
grouping: Calendar year, 2013–2025
chart_type: Line chart
probability: 0.28
WRITTEN ANSWER:
Motorist deaths per 1,000 motorist-casualty crashes fell from 4.43 in 2013 to 3.64 in 2025, but this does not measure risk per mile driven. This chart answers whether fatal outcomes per crash event with at least one motorist casualty changed: the rate is lower at the 2025 endpoint than in 2013. Using casualty-involved crash events as the denominator is a defensible crash-severity framing, though it differs from an individual motorist's travel risk. It leaves the per-mile question unanswered because the crash file records neither miles driven nor trips. No rows with NULL crash dates or required motorist injury/death values are omitted within 2013–2025 (0 of 2,132,218; 0%). The analysis excludes 136,969 of 2,269,187 file rows (6.04%) outside the full-year 2013–2025 window (partial 2012 and 2026); none of the included years is partial.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,motorist_killed,motorist_casualty_crashes,deaths_per_1000_motorist_casualty_crashes
2013,110,24819,4.432088
2014,109,23258,4.686559
2015,95,24130,3.937008
2016,72,28605,2.517042
2017,107,29340,3.646898
2018,98,30482,3.215012
2019,82,30422,2.695418
2020,139,21582,6.440552
2021,134,24834,5.395828
2022,116,23673,4.900097
2023,123,24680,4.983793
2024,111,24424,4.544710
2025,81,22245,3.641268

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute('describe select * from read_parquet(?)',[p]).fetchdf().to_string(index=False)); print(c.execute(\"select min(crash_date), max(crash_date), count(*) from read_parquet(?)\",[p]).fetchall())"
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; q=\"\"\"select year(crash_date) y, count(*) crashes, count(*) filter (where number_of_motorist_killed is null) nk_null, count(*) filter (where number_of_motorist_injured is null) ni_null, sum(number_of_motorist_killed) m_killed, sum(number_of_motorist_injured) m_injured, count(*) filter (where number_of_motorist_killed > 0 or number_of_motorist_injured > 0) casualty_crashes, count(*) filter (where number_of_motorist_killed is not null and number_of_motorist_injured is not null) both_known from read_parquet(?) where crash_date >= date '2013-01-01' and crash_date < date '2026-01-01' group by y order by y\"\"\"; print(c.execute(q,[p]).fetchdf().to_string(index=False))"
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(\"select year(crash_date) y, min(number_of_motorist_injured), max(number_of_motorist_injured), count(*) filter(where number_of_motorist_injured = 0) zeros, count(*) filter(where number_of_motorist_injured > 0) positives, count(*) filter(where number_of_motorist_killed > 0) deaths, sum(number_of_motorist_injured + number_of_motorist_killed) casualties from read_parquet(?) where year(crash_date) in (2013,2020,2025) group by y order by y\",[p]).fetchdf().to_string(index=False))"
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; q=\"select year(crash_date) y, count(*) filter (where number_of_motorist_injured > 0) inj_gt, count(*) filter (where number_of_motorist_killed > 0) kill_gt, count(*) filter (where number_of_motorist_injured > 0 or number_of_motorist_killed > 0) either_gt, count(*) filter (where (number_of_motorist_injured > 0) or (number_of_motorist_killed > 0)) either_parenthesized from read_parquet(?) where crash_date >= date '2013-01-01' and crash_date < date '2026-01-01' and year(crash_date) in (2013,2020,2025) group by y order by y\"; print(c.execute(q,[p]).fetchdf().to_string(index=False))"
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; q=\"\"\"with src as (select * from read_parquet(?)), annual as (select year(crash_date) y, count(*) rows, sum(number_of_motorist_killed) motorist_killed, sum(number_of_motorist_injured) motorist_injured, count(*) filter(where number_of_motorist_injured > 0 or number_of_motorist_killed > 0) motorist_casualty_crashes, count(*) filter(where number_of_motorist_killed is null) killed_null, count(*) filter(where number_of_motorist_injured is null) injured_null from src where crash_date >= date '2013-01-01' and crash_date < date '2026-01-01' group by y) select * from annual order by y;\"\"\"; print(c.execute(q,[p]).fetchdf().to_string(index=False)); print('coverage',c.execute(\"select count(*) n, count(*) filter(where crash_date is null) null_date, count(*) filter(where crash_date < date '2013-01-01' or crash_date >= date '2026-01-01') outside, count(*) filter(where crash_date >= date '2013-01-01' and crash_date < date '2026-01-01') inside from read_parquet(?)\",[p]).fetchall()); print('years',c.execute(\"select year(crash_date), count(*) from read_parquet(?) group by 1 order by 1\",[p]).fetchall())"
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; q=\"\"\"select year(crash_date) y, count(*) n_rows, sum(number_of_motorist_killed) motorist_killed, sum(number_of_motorist_injured) motorist_injured, count(*) filter(where number_of_motorist_injured > 0 or number_of_motorist_killed > 0) motorist_casualty_crashes, count(*) filter(where number_of_motorist_killed is null) killed_null, count(*) filter(where number_of_motorist_injured is null) injured_null from read_parquet(?) where crash_date >= date '2013-01-01' and crash_date < date '2026-01-01' group by y order by y\"\"\"; print(c.execute(q,[p]).fetchdf().to_string(index=False)); print('coverage',c.execute(\"select count(*) n, count(*) filter(where crash_date is null) null_date, count(*) filter(where crash_date < date '2013-01-01' or crash_date >= date '2026-01-01') outside, count(*) filter(where crash_date >= date '2013-01-01' and crash_date < date '2026-01-01') inside from read_parquet(?)\",[p]).fetchall()); print('years',c.execute(\"select year(crash_date), count(*) from read_parquet(?) group by 1 order by 1\",[p]).fetchall())"
# bash
ls
# bash
python3 -c 'import duckdb, pandas as pd; c=duckdb.connect(); df=c.execute("select year(crash_date) as year, count(*) as crash_rows, sum(number_of_motorist_killed)::BIGINT as motorist_killed, sum(number_of_motorist_injured)::BIGINT as motorist_injured, count(*) filter (where number_of_motorist_injured > 0 or number_of_motorist_killed > 0)::BIGINT as motorist_casualty_crashes, count(*) filter (where number_of_motorist_killed is null)::BIGINT as killed_null, count(*) filter (where number_of_motorist_injured is null)::BIGINT as injured_null from read_parquet(?) where crash_date >= date "2013-01-01" and crash_date < date "2026-01-01" group by year order by year", ["data/crashes.parquet"]).fetchdf(); print(df.to_string(index=False))'
# bash
python3 out/build_outputs.py

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR01: If a per-reported-crash rate spanning 2020 is shown, the output caveats the 2020 change in crash recording (fewer minor crashes reported).
- tr_PERMILE: A per-reported-crash rate, if shown, is not presented as a substitute for per-mile risk.
- tr_VMT: No vehicle-miles figure is imported, assumed or estimated from outside the data.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence
- required_statement: PASS if the output states, in its own words: Per-mile (per vehicle-mile) risk cannot be determined from this data because it has no vehicle-miles or traffic volume.

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.