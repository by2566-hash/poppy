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

QUESTION ASKED: How do motorist and cyclist deaths compare year by year in NYC, 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Annual motorist and cyclist deaths
denominator: None; counts of people killed in crashes
grouping: Calendar year and road-user group
chart_type: Two-series line chart
probability: 0.3
WRITTEN ANSWER:
Motorist deaths were higher in every year, peaking at 139 in 2020 and falling to 81 in 2025, while cyclist deaths peaked at 31 in 2019 and 2023. This framing answers how the two annual death counts changed over time, showing a motorist peak in 2020 and cyclist peaks in 2019 and 2023. A line chart is defensible for ordered yearly observations and makes timing and direction salient, but the separation between series can make the proportional comparison less clear.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,motorist_deaths,cyclist_deaths
2013,110,11
2014,109,20
2015,95,15
2016,72,18
2017,107,27
2018,98,10
2019,82,31
2020,139,29
2021,134,19
2022,116,19
2023,123,31
2024,111,24
2025,81,23

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python3 -c "import duckdb; print(duckdb.sql(\"DESCRIBE SELECT * FROM read_parquet('data/crashes.parquet')\").df().to_string(index=False)); print(duckdb.sql(\"SELECT EXTRACT(YEAR FROM crash_date) AS year, SUM(number_of_motorist_killed) motorist_deaths, SUM(number_of_cyclist_killed) cyclist_deaths FROM read_parquet('data/crashes.parquet') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY year ORDER BY year\").df().to_string(index=False))"
# bash
python3 -c "import duckdb; print(duckdb.sql(\"SELECT MIN(crash_date) min_date, MAX(crash_date) max_date, COUNT(*) FILTER (WHERE crash_date IS NULL) null_dates, COUNT(*) FILTER (WHERE number_of_motorist_killed IS NULL) null_motorist, COUNT(*) FILTER (WHERE number_of_cyclist_killed IS NULL) null_cyclist FROM read_parquet('data/crashes.parquet')\").df().to_string(index=False)); print(duckdb.sql(\"SELECT COUNT(*) crashes_2025, MIN(crash_date) first_2025, MAX(crash_date) last_2025 FROM read_parquet('data/crashes.parquet') WHERE crash_date >= DATE '2025-01-01' AND crash_date < DATE '2026-01-01'\").df().to_string(index=False))"
# bash
python3 -c "import duckdb; print(duckdb.sql(\"SELECT COUNT(*) FILTER (WHERE number_of_motorist_killed > 0) motorist_positive, COUNT(*) FILTER (WHERE number_of_cyclist_killed > 0) cyclist_positive, SUM(number_of_motorist_killed) total_motorist, SUM(number_of_cyclist_killed) total_cyclist FROM read_parquet('data/crashes.parquet') WHERE crash_date BETWEEN DATE '2013-01-01' AND DATE '2025-12-31'\").df().to_string(index=False))"
# bash
python3 out/generate_options.py
# bash
python3 out/generate_options.py
# bash
python3 out/generate_options.py
# bash
python3 -c "import json, pandas as pd; from pathlib import Path; p=Path('out'); o=json.loads((p/'options.json').read_text()); a=pd.read_csv(p/'values_1.csv'); r=pd.read_csv(p/'values_3.csv'); assert len(o['options'])==3 and abs(sum(x['probability'] for x in o['options'])-1)<1e-9; assert a['year'].tolist()==list(range(2013,2026)); assert (a.motorist_deaths>a.cyclist_deaths).all(); gap=a.motorist_deaths-a.cyclist_deaths; assert (int(a.loc[gap.idxmax(),'year']),int(a.loc[gap.idxmax(),'motorist_deaths']),int(a.loc[gap.idxmax(),'cyclist_deaths']))==(2021,134,19); assert (int(a.loc[gap.idxmin(),'year']),int(a.loc[gap.idxmin(),'motorist_deaths']),int(a.loc[gap.idxmin(),'cyclist_deaths']))==(2019,82,31); assert (int(a.loc[a.motorist_deaths.idxmax(),'year']),int(a.motorist_deaths.max()))==(2020,139); assert int(a.cyclist_deaths.max())==31; assert (int(r.loc[r.motorist_to_cyclist_ratio.idxmin(),'year']),round(r.motorist_to_cyclist_ratio.min(),1))==(2019,2.6); assert (int(r.loc[r.motorist_to_cyclist_ratio.idxmax(),'year']),round(r.motorist_to_cyclist_ratio.max(),1))==(2013,10.0); assert all((p/f'option_{i}.png').is_file() and (p/f'values_{i}.csv').is_file() for i in (1,2,3)); print('Validated JSON, chart files, yearly measures, and answer claims.')"

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR15: Claims about cyclist deaths changing sharply (e.g. 'tripled') are qualified by the small counts (10 → 31).
- tr_TR03: The output does not claim that motorist + cyclist deaths are all deaths (pedestrians and unclassified deaths exist).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.