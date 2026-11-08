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

QUESTION ASKED: How many pedestrians were killed in NYC motor vehicle crashes each year from 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Sum of pedestrians killed per calendar year
denominator: Not applicable; absolute count of people
grouping: Calendar year (2013–2025)
chart_type: Vertical bar chart
probability: 0.5
WRITTEN ANSWER:
Pedestrians killed by year were 2013: 176, 2014: 133, 2015: 133, 2016: 149, 2017: 127, 2018: 123, 2019: 131, 2020: 101, 2021: 132, 2022: 135, 2023: 107, 2024: 124, and 2025: 119. Bars answer the requested question with annual numbers of pedestrians killed: 2013: 176, 2014: 133, 2015: 133, 2016: 149, 2017: 127, 2018: 123, 2019: 131, 2020: 101, 2021: 132, 2022: 135, 2023: 107, 2024: 124, and 2025: 119. A bar chart treats years as separate categories, making the magnitude in each calendar year easy to compare. It does not show where fatalities occurred or how the totals relate to the number of crashes. The requested period uses 2,132,218 crash rows; none is omitted for NULL crash dates or pedestrian-fatality values (NULL dates: 0/2,269,187, 0.00%; NULL fatality values: 0/2,132,218, 0.00%), and all 13 included years are complete (0/13 partial years, 0%). Rows outside 2013–2025 are excluded by the date filter (136,969/2,269,187, 6.04%).

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,pedestrians_killed
2013,176
2014,133
2015,133
2016,149
2017,127
2018,123
2019,131
2020,101
2021,132
2022,135
2023,107
2024,124
2025,119

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
# bash
python -c "import duckdb; p='data/crashes.parquet'; q=duckdb.connect().execute('SELECT COUNT(*) n, MIN(crash_date) min_date, MAX(crash_date) max_date, COUNT(*) FILTER (WHERE crash_date IS NULL) null_date, COUNT(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) null_ped_killed FROM read_parquet(?)', [p]).fetchdf(); print(q.to_string(index=False)); print(duckdb.connect().execute(\"SELECT EXTRACT(YEAR FROM crash_date)::INT year, COUNT(*) rows, MIN(crash_date) min_date, MAX(crash_date) max_date, COUNT(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) null_values, SUM(number_of_pedestrians_killed) ped_killed FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY year ORDER BY year\", [p]).fetchdf().to_string(index=False))"
# bash
python -c "import duckdb; p='data/crashes.parquet'; print(duckdb.connect().execute(\"SELECT EXTRACT(YEAR FROM crash_date)::INT AS yr, COUNT(*) AS n_rows, MIN(crash_date) AS first_date, MAX(crash_date) AS last_date, COUNT(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS null_values, SUM(number_of_pedestrians_killed) AS pedestrian_fatalities FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY yr ORDER BY yr\", [p]).fetchdf().to_string(index=False))"
# bash
# bash
source = 'data/crashes.parquet'
values = con.execute(\"\"\"SELECT EXTRACT(YEAR FROM crash_date)::INTEGER AS year, SUM(number_of_pedestrians_killed)::BIGINT AS pedestrians_killed, COUNT(*) AS crash_rows, COUNT(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS null_fatality_rows, MIN(crash_date) AS first_date, MAX(crash_date) AS last_date FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY year ORDER BY year\"\"\", [source]).fetchdf()
coverage = con.execute(\"\"\"SELECT COUNT(*) AS total_rows, COUNT(*) FILTER (WHERE crash_date IS NULL) AS null_date_rows, COUNT(*) FILTER (WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01') AS requested_rows, COUNT(*) FILTER (WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' AND number_of_pedestrians_killed IS NULL) AS requested_null_fatality_rows, COUNT(*) FILTER (WHERE crash_date < DATE '2013-01-01' OR crash_date >= DATE '2026-01-01') AS out_of_period_rows FROM read_parquet(?)\"\"\", [source]).fetchone()
assert values['year'].tolist() == list(range(2013, 2026))
assert values['first_date'].astype(str).tolist() == [f'{y}-01-01' for y in range(2013, 2026)]
assert values['last_date'].astype(str).tolist() == [f'{y}-12-31' for y in range(2013, 2026)]
chart_data = values[['year', 'pedestrians_killed']].copy()
    chart_data.to_csv(out / f'values_{i}.csv', index=False)
plt.bar(chart_data['year'], chart_data['pedestrians_killed'], color='#2878B5', width=0.76)
plt.xticks(chart_data['year'], rotation=45)
plt.xlabel('Crash year')
plt.title('Pedestrians killed in NYC motor vehicle crashes, 2013–2025')
plt.savefig(out / 'option_1.png', dpi=160)
plt.plot(chart_data['year'], chart_data['pedestrians_killed'], color='#2878B5', marker='o', linewidth=2)
plt.xticks(chart_data['year'], rotation=45)
plt.xlabel('Crash year')
plt.title('Annual pedestrian fatalities in NYC motor vehicle crashes, 2013–2025')
plt.savefig(out / 'option_2.png', dpi=160)
requested_n, null_date_n, null_kill_n = int(coverage[2]), int(coverage[1]), int(coverage[3])
null_date_pct = (null_date_n / int(coverage[0]) * 100) if coverage[0] else 0
null_kill_pct = null_kill_n / requested_n * 100 if requested_n else 0
omitted_pct = omitted_n / int(coverage[0]) * 100 if coverage[0] else 0
answer = f\"Fatalities peaked at {int(peak['pedestrians_killed'])} in {int(peak['year'])}, fell to {int(low['pedestrians_killed'])} in {int(low['year'])}, and totaled {int(chart_data.iloc[-1]['pedestrians_killed'])} in 2025.\"
coverage_sentence = f\"The requested period uses {requested_n:,} crash rows; none is omitted for NULL crash dates or pedestrian-fatality values (NULL dates: {null_date_n:,}/{int(coverage[0]):,}, {null_date_pct:.2f}%; NULL fatality values: {null_kill_n:,}/{requested_n:,}, {null_kill_pct:.2f}%), and all 13 included years are complete (0/13 partial years, 0%). Rows outside 2013–2025 are excluded by the date filter ({omitted_n:,}/{int(coverage[0]):,}, {omitted_pct:.2f}%).\"
    {'id': 1, 'metric': 'Sum of pedestrians killed per calendar year', 'denominator': 'Not applicable; absolute count of people', 'grouping': 'Calendar year (2013–2025)', 'chart_type': 'Vertical bar chart', 'reason': 'A bar chart makes it easy to compare the separate annual totals requested.', 'probability': 0.5, 'answer': answer, 'interpretation': f\"Bars answer the requested question with annual numbers of pedestrians killed: {answer} A bar chart treats years as separate categories, making the magnitude in each calendar year easy to compare. It does not show where fatalities occurred or how the totals relate to the number of crashes. {coverage_sentence}\"},
    {'id': 2, 'metric': 'Sum of pedestrians killed per calendar year', 'denominator': 'Not applicable; absolute count of people', 'grouping': 'Calendar year (2013–2025)', 'chart_type': 'Line chart with annual points', 'reason': 'A line chart emphasizes how the annual pedestrian-fatality count changed over time.', 'probability': 0.5, 'answer': answer, 'interpretation': f\"The annual points answer how many pedestrians were killed in each year and show the rise and fall over the requested period: {answer} Connecting adjacent annual totals emphasizes the time trend while retaining the count for each year. It does not show where fatalities occurred or how the totals relate to the number of crashes. {coverage_sentence}\"}
(out / 'options.json').write_text(json.dumps(options, ensure_ascii=False, indent=2) + '\\n')
print(f'coverage total={int(coverage[0])}, requested={requested_n}, out_of_period={omitted_n}, null_dates={null_date_n}, requested_null_fatalities={null_kill_n}')
# bash
source = 'data/crashes.parquet'
values = con.execute(\"\"\"SELECT EXTRACT(YEAR FROM crash_date)::INTEGER AS year, SUM(number_of_pedestrians_killed)::BIGINT AS pedestrians_killed, COUNT(*) AS crash_rows, COUNT(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS null_fatality_rows, MIN(crash_date) AS first_date, MAX(crash_date) AS last_date FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY year ORDER BY year\"\"\", [source]).fetchdf()
coverage = con.execute(\"\"\"SELECT COUNT(*) AS total_rows, COUNT(*) FILTER (WHERE crash_date IS NULL) AS null_date_rows, COUNT(*) FILTER (WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01') AS requested_rows, COUNT(*) FILTER (WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' AND number_of_pedestrians_killed IS NULL) AS requested_null_fatality_rows, COUNT(*) FILTER (WHERE crash_date < DATE '2013-01-01' OR crash_date >= DATE '2026-01-01') AS out_of_period_rows FROM read_parquet(?)\"\"\", [source]).fetchone()
assert values['year'].tolist() == list(range(2013, 2026))
assert values['first_date'].astype(str).tolist() == [f'{y}-01-01' for y in range(2013, 2026)]
assert values['last_date'].astype(str).tolist() == [f'{y}-12-31' for y in range(2013, 2026)]
chart_data = values[['year', 'pedestrians_killed']].copy()
    chart_data.to_csv(out / f'values_{i}.csv', index=False)
plt.bar(chart_data['year'], chart_data['pedestrians_killed'], color='#2878B5', width=0.76)
plt.xticks(chart_data['year'], rotation=45)
plt.xlabel('Crash year')
plt.title('Pedestrians killed in NYC motor vehicle crashes, 2013–2025')
plt.savefig(out / 'option_1.png', dpi=160)
plt.plot(chart_data['year'], chart_data['pedestrians_killed'], color='#2878B5', marker='o', linewidth=2)
plt.xticks(chart_data['year'], rotation=45)
plt.xlabel('Crash year')
plt.title('Annual pedestrian fatalities in NYC motor vehicle crashes, 2013–2025')
plt.savefig(out / 'option_2.png', dpi=160)
requested_n, null_date_n, null_kill_n = int(coverage[2]), int(coverage[1]), int(coverage[3])
null_date_pct = null_date_n / int(coverage[0]) * 100 if coverage[0] else 0
null_kill_pct = null_kill_n / requested_n * 100 if requested_n else 0
omitted_pct = omitted_n / int(coverage[0]) * 100 if coverage[0] else 0
answer = f\"Fatalities peaked at {int(peak['pedestrians_killed'])} in {int(peak['year'])}, fell to {int(low['pedestrians_killed'])} in {int(low['year'])}, and totaled {int(chart_data.iloc[-1]['pedestrians_killed'])} in 2025.\"
coverage_sentence = f\"The requested period uses {requested_n:,} crash rows; none is omitted for NULL crash dates or pedestrian-fatality values (NULL dates: {null_date_n:,}/{int(coverage[0]):,}, {null_date_pct:.2f}%; NULL fatality values: {null_kill_n:,}/{requested_n:,}, {null_kill_pct:.2f}%), and all 13 included years are complete (0/13 partial years, 0%). Rows outside 2013–2025 are excluded by the date filter ({omitted_n:,}/{int(coverage[0]):,}, {omitted_pct:.2f}%).\"
    {'id': 1, 'metric': 'Sum of pedestrians killed per calendar year', 'denominator': 'Not applicable; absolute count of people', 'grouping': 'Calendar year (2013–2025)', 'chart_type': 'Vertical bar chart', 'reason': 'A bar chart makes it easy to compare the separate annual totals requested.', 'probability': 0.5, 'answer': answer, 'interpretation': f\"Bars answer the requested question with annual numbers of pedestrians killed: {answer} A bar chart treats years as separate categories, making the magnitude in each calendar year easy to compare. It does not show where fatalities occurred or how the totals relate to the number of crashes. {coverage_sentence}\"},
    {'id': 2, 'metric': 'Sum of pedestrians killed per calendar year', 'denominator': 'Not applicable; absolute count of people', 'grouping': 'Calendar year (2013–2025)', 'chart_type': 'Line chart with annual points', 'reason': 'A line chart emphasizes how the annual pedestrian-fatality count changed over time.', 'probability': 0.5, 'answer': answer, 'interpretation': f\"The annual points answer how many pedestrians were killed in each year and show the rise and fall over the requested period: {answer} Connecting adjacent annual totals emphasizes the time trend while retaining the count for each year. It does not show where fatalities occurred or how the totals relate to the number of crashes. {coverage_sentence}\"}
(out / 'options.json').write_text(json.dumps(options, ensure_ascii=False, indent=2) + chr(10))
print(f'coverage total={int(coverage[0])}, requested={requested_n}, out_of_period={omitted_n}, null_dates={null_date_n}, requested_null_fatalities={null_kill_n}')
# bash
python -c "import pandas as pd, matplotlib.pyplot as plt; d=pd.read_csv('out/values_2.csv'); plt.figure(figsize=(10,5.5)); plt.plot(d['year'],d['pedestrians_killed'],color='#2878B5',marker='o',linewidth=2); plt.xticks(d['year'],rotation=45); plt.ylim(bottom=0); plt.ylabel('Pedestrians killed (people)'); plt.xlabel('Crash year'); plt.title('Annual pedestrian fatalities in NYC motor vehicle crashes, 2013–2025'); plt.grid(alpha=0.25); plt.tight_layout(); plt.savefig('out/option_2.png',dpi=160); plt.close()"
# bash
python -c "import json,pandas as pd; o=json.load(open('out/options.json'))['options']; v=pd.read_csv('out/values_1.csv'); assert len(o)==2 and [x['id'] for x in o]==[1,2]; assert sum(x['probability'] for x in o)==1; expected='Pedestrians killed by year were '+', '.join(f\"{r.year}: {r.pedestrians_killed}\" for r in v.itertuples(index=False))+'.'; assert all(x['answer']==expected for x in o); assert v.equals(pd.read_csv('out/values_2.csv')); print('valid JSON; answers match both CSVs; probabilities sum to 1')"
# bash
python -c "import json,re,pandas as pd; o=json.load(open('out/options.json'))['options']; v=pd.read_csv('out/values_1.csv'); expected=list(zip(v.year.astype(int),v.pedestrians_killed.astype(int))); assert len(o)==2 and [x['id'] for x in o]==[1,2]; assert abs(sum(x['probability'] for x in o)-1)<1e-12; as
... (code lines filtered to those about filters, windows and denominators; truncated)

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR07: The output does not present the open-data death counts as the official NYC toll. The counts are qualified when the written output (answer, interpretation or declared framing fields) ties them to this data in any wording: reported, recorded, police-reported crashes, in this dataset (e.g. 'pedestrians killed in reported motor vehicle crashes' qualifies). A qualification or source note that appears only inside the chart image does not count, and a chart title without one is fine when the written output has it. FAIL only when no such qualification appears in the written output (Bo 2026-11-04, refined 2026-11-06).
- tr_CAUSAL: The output makes no causal attribution (e.g. 'because of the pandemic') that the data cannot support.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.