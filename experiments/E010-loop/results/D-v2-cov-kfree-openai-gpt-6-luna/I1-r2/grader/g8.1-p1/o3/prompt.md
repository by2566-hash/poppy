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
metric: Share of reported crashes with at least one motorist death
denominator: All police-reported crashes with a non-NULL motorist-killed count in the same year
grouping: Calendar year (2013–2025)
chart_type: Line chart
probability: 0.3
WRITTEN ANSWER:
This crash file cannot determine per-mile risk; the share of crashes with at least one motorist death rose from 0.0501% in 2013 to 0.0877% in 2025. This answers whether the incidence of a crash involving a motorist death changed: the share rose from 0.0501% in 2013 to 0.0877% in 2025. Counting each crash at most once gives a defensible event-level view that differs from counting each person killed. It leaves per-mile risk unanswered because this file has no vehicle-miles-driven denominator. Rows omitted for NULL required values: none; no included year is partial.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,fatal_crashes,reported_crashes,fatal_crash_share_pct
2013,102,203742,0.050063
2014,99,206046,0.048048
2015,89,217708,0.040880
2016,63,229833,0.027411
2017,100,231007,0.043289
2018,97,231564,0.041889
2019,77,211486,0.036409
2020,126,112918,0.111585
2021,126,110558,0.113967
2022,107,103887,0.102997
2023,114,96607,0.118004
2024,98,91316,0.107320
2025,75,85546,0.087672

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
# bash
python -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("DESCRIBE SELECT * FROM read_parquet(?)", [p]).fetchdf().to_string(index=False)); print(c.execute("SELECT min(crash_date), max(crash_date), count(*) FROM read_parquet(?)", [p]).fetchall()); print(c.execute("SELECT year(crash_date) y, count(*) crashes, sum(number_of_motorist_killed) motorist_killed, sum(number_of_persons_killed) all_killed, sum(number_of_motorist_injured) motorist_injured FROM read_parquet(?) GROUP BY y ORDER BY y", [p]).fetchdf().to_string(index=False))'
# bash
python -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; q="SELECT count(*) rows, count(*) FILTER (WHERE crash_date IS NULL) null_date, count(*) FILTER (WHERE number_of_motorist_killed IS NULL) null_mk, count(*) FILTER (WHERE crash_date IS NULL OR number_of_motorist_killed IS NULL) null_either FROM read_parquet(?)"; print(c.execute(q,[p]).fetchdf().to_string(index=False)); print(c.execute("SELECT year(crash_date) y, min(crash_date) first_day, max(crash_date) last_day, count(*) n, count(*) FILTER (WHERE number_of_motorist_killed IS NOT NULL) usable, count(*) FILTER (WHERE number_of_motorist_killed > 0) death_crashes, sum(number_of_motorist_killed) killed FROM read_parquet(?) WHERE year(crash_date) IN (2013,2025) GROUP BY y ORDER BY y",[p]).fetchdf().to_string(index=False)); print(c.execute("SELECT count(*) FILTER (WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2014-01-01') n2013, count(*) FILTER (WHERE crash_date >= DATE '2025-01-01' AND crash_date < DATE '2026-01-01') n2025, count(*) FILTER (WHERE crash_date >= DATE '2025-01-01' AND crash_date < DATE '2026-01-01' AND number_of_motorist_killed IS NULL) nullmk2025 FROM read_parquet(?)",[p]).fetchall())'
# bash
python -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; q="SELECT count(*) AS total_rows, count(*) FILTER (WHERE crash_date IS NULL) AS null_date, count(*) FILTER (WHERE number_of_motorist_killed IS NULL) AS null_mk, count(*) FILTER (WHERE crash_date IS NULL OR number_of_motorist_killed IS NULL) AS null_either FROM read_parquet(?)"; print(c.execute(q,[p]).fetchdf().to_string(index=False)); print(c.execute("SELECT year(crash_date) y, min(crash_date) first_day, max(crash_date) last_day, count(*) n, count(*) FILTER (WHERE number_of_motorist_killed IS NOT NULL) usable, count(*) FILTER (WHERE number_of_motorist_killed > 0) death_crashes, sum(number_of_motorist_killed) killed FROM read_parquet(?) WHERE year(crash_date) IN (2013,2025) GROUP BY y ORDER BY y",[p]).fetchdf().to_string(index=False)); print(c.execute("SELECT count(*) FILTER (WHERE crash_date >= DATE \'2013-01-01\' AND crash_date < DATE \'2014-01-01\') n2013, count(*) FILTER (WHERE crash_date >= DATE \'2025-01-01\' AND crash_date < DATE \'2026-01-01\') n2025, count(*) FILTER (WHERE crash_date >= DATE \'2025-01-01\' AND crash_date < DATE \'2026-01-01\' AND number_of_motorist_killed IS NULL) nullmk2025 FROM read_parquet(?)",[p]).fetchall())'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); print(c.execute("SELECT count(*) FROM read_parquet(?)", ["data/crashes.parquet"]).fetchone())'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; q="SELECT count(*) AS total_rows, count(*) FILTER (WHERE crash_date IS NULL) AS null_date, count(*) FILTER (WHERE number_of_motorist_killed IS NULL) AS null_mk, count(*) FILTER (WHERE crash_date IS NULL OR number_of_motorist_killed IS NULL) AS null_either FROM read_parquet(?)"; print(c.execute(q,[p]).fetchdf().to_string(index=False)); print(c.execute("SELECT year(crash_date) y, min(crash_date) first_day, max(crash_date) last_day, count(*) n, count(*) FILTER (WHERE number_of_motorist_killed IS NOT NULL) usable, count(*) FILTER (WHERE number_of_motorist_killed > 0) death_crashes, sum(number_of_motorist_killed) killed FROM read_parquet(?) WHERE year(crash_date) IN (2013,2025) GROUP BY y ORDER BY y",[p]).fetchdf().to_string(index=False))'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; print(c.execute("SELECT year(crash_date) y, count(*) crashes, sum(number_of_motorist_killed) deaths, count(*) FILTER (WHERE number_of_motorist_killed > 0) fatal_crashes, round(100000.0 * sum(number_of_motorist_killed) / count(*), 3) deaths_per_100k, round(100.0 * count(*) FILTER (WHERE number_of_motorist_killed > 0) / count(*), 5) fatal_crash_pct FROM read_parquet(?) WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY y ORDER BY y", [p]).fetchdf().to_string(index=False))'
# bash
out = root / 'out'
source = str(root / 'data' / 'crashes.parquet')
    SELECT year(crash_date) AS year,
           sum(number_of_motorist_killed) AS motorist_deaths,
           count(*) FILTER (WHERE number_of_motorist_killed > 0) AS fatal_crashes,
           count(*) FILTER (WHERE crash_date IS NULL OR number_of_motorist_killed IS NULL) AS rows_missing_required
    WHERE year(crash_date) BETWEEN 2013 AND 2025
    GROUP BY year
    ORDER BY year
assert data['year'].tolist() == list(range(2013, 2026))
assert int(data['rows_missing_required'].sum()) == 0
    SELECT year(crash_date) AS year, min(crash_date) AS first_date, max(crash_date) AS last_date
    WHERE year(crash_date) BETWEEN 2013 AND 2025
    GROUP BY year
    ORDER BY year
assert str(coverage.iloc[0]['first_date']) == '2013-01-01'
assert str(coverage.iloc[-1]['last_date']) == '2025-12-31'
data['deaths_per_100000_crashes'] = data['motorist_deaths'] / data['reported_crashes'] * 100000
data['fatal_crash_share_pct'] = data['fatal_crashes'] / data['reported_crashes'] * 100
        'grouping': 'Calendar year (2013–2025)',
        'answer': 'This crash file cannot determine per-mile risk; recorded annual motorist deaths fell from 110 in 2013 to 81 in 2025 (26.4%).',
        'interpretation': 'This answers the annual fatality-count part of the question: recorded motorist deaths fell from 110 in 2013 to 81 in 2025, with the intervening years shown in the chart. Annual totals are a direct measure of fatality burden in the crash file, but they are not exposure-adjusted. The per-mile risk trend remains unanswered because the file has no vehicle-miles-driven measure. Rows omitted for NULL required values: none; no included year is partial.'
        'denominator': 'All police-reported crashes with a non-NULL motorist-killed count in the same year',
        'grouping': 'Calendar year (2013–2025)',
        'answer': 'This crash file cannot determine per-mile risk; motorist deaths per 100,000 reported crashes rose from 54.0 in 2013 to 94.7 in 2025 (75.4%).',
        'interpretation': 'This answers whether motorist deaths fell relative to the number of reported crashes: the rate rose from 54.0 per 100,000 crashes in 2013 to 94.7 in 2025. A crash-count denominator adjusts for the annual volume of recorded crashes and is a defensible crash-based proxy. It does not answer risk per mile because crash counts are not miles driven. Rows omitted for NULL required values: none; no included year is partial.'
        'denominator': 'All police-reported crashes with a non-NULL motorist-killed count in the same year',
        'grouping': 'Calendar year (2013–2025)',
        'answer': 'This crash file cannot determine per-mile risk; the share of crashes with at least one motorist death rose from 0.0501% in 2013 to 0.0877% in 2025.',
        'interpretation': 'This answers whether the incidence of a crash involving a motorist death changed: the share rose from 0.0501% in 2013 to 0.0877% in 2025. Counting each crash at most once gives a defensible event-level view that differs from counting each person killed. It leaves per-mile risk unanswered because this file has no vehicle-miles-driven denominator. Rows omitted for NULL required values: none; no included year is partial.'
    (2, 'deaths_per_100000_crashes', 'Deaths per 100,000 reported crashes', 'Motorist deaths per 100,000 NYC crash reports', None),
        values = data[['year', 'motorist_deaths', 'reported_crashes']].copy()
        values.to_csv(out / f'values_{option_id}.csv', index=False, float_format='%.6f')
        values = data[['year', 'motorist_deaths', 'reported_crashes', 'deaths_per_100000_crashes']].copy()
        values.to_csv(out / f'values_{option_id}.csv', index=False, float_format='%.6f')
        values = data[['year', 'fatal_crashes', 'reported_crashes', 'fatal_crash_share_pct']].copy()
        values.to_csv(out / f'values_{option_id}.csv', index=False, float_format='%.6f')
    ax.plot(data['year'], data[column], marker='o', linewidth=2.2, markersize=5)
    ax.set_title(title + ' (2013–2025)', pad=14, fontsize=13)
    ax.set_xlabel('Crash year')
    ax.set_xticks(data['year'])
    fig.savefig(out / f'option_{option_id}.png', dpi=170, bbox_inches='tight')
with (out / 'options.json').open('w', encoding='utf-8') as f:
print(data[['year', 'reported_crashes', 'motorist_deaths', 'fatal_crashes', 'deaths_per_100000_crashes', 'fatal_crash_share_pct']].to_string(index=False))
print('Saved 3 charts, 3 CSV files, and options.json to ./out')
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; print(c.execute("SELECT year(crash_date) y, min(crash_date), max(crash_date) FROM read_parquet(?) WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY y ORDER BY y",[p]).fetchdf().to_string(index=False))'
# bash
source = 'data/crashes.parquet'
    SELECT year(crash_date) AS year,
           sum(number_of_motorist_killed) AS motorist_deaths,
           count(*) FILTER (WHERE number_of_motorist_killed > 0) AS fatal_crashes,
           count(*) FILTER (WHERE crash_date IS NULL OR number_of_motorist_killed IS NULL) AS rows_missing_required
    WHERE year(crash_date) BETWEEN 2013 AND 2025
    GROUP BY year ORDER BY year
assert data['year'].tolist() == list(range(2013, 2026))
assert int(data['rows_missing_required'].sum()) == 0
    SELECT year(crash_date) AS year, min(crash_date) AS first_date, max(crash_date) AS last_date
    FROM read_parquet(?) WHERE year(crash_date) BETWEEN 2013 AND 2025
    GROUP BY year ORDER BY year
assert coverage.iloc[0]['first_date'].strftime('%Y-%m-%d') == '2013-01-01'
assert coverage.iloc[-1]['last_date'].strftime('%Y-%m-%d') == '2025-12-31'
data['deaths_per_100000_crashes'] = data['motorist_deaths'] / data['reported_crashes'] * 100000
data['fatal_crash_share_pct'] = data['fatal_crashes'] / data['reported_crashes'] * 100
    {'id': 1, 'metric': 'Annual count of motorist deaths', 'denominator': 'None (raw annual total)', 'grouping': 'Calendar year (2013–2025)', 'chart_type': 'Line chart', 'reason': 'Annual deaths directly show whether the fatality burden rose or fell, without implying an exposure-adjusted risk.', 'probability': 0.2, 'answer': 'This crash file cannot determine per-mile risk; recorded annual motorist deaths fell from 110 in 2013 to 81 in 2025 (26.4%).', 'interpretation': 'This answers the annual fatality-count part of the question: recorded motorist deaths fell from 110 in 2013 to 81 in 2025, with the intervening years shown in the chart. Annual totals are a direct measure of fatality burden in the crash file, but they are not exposure-adjusted. The per-mile risk trend remains unanswered because the file has no vehicle-miles-driven measure. Rows omitted for NULL required values: none; no included year is partial.'},
    {'id': 2, 'metric': 'Motorist deaths per 100,000 reported crashes', 'denominator': 'All police-reported crashes with a non-NULL motorist-killed count in the same year', 'grouping': 'Calendar year (2013–2025)', 'chart_type': 'Line chart', 'reason': 'Dividing deaths by the number of reported crashes gives a crash-volume-adjusted comparison while staying within the available data.', 'probability': 0.5, 'answer': 'This crash file cannot determine per-mile risk; motorist deaths per 100,000 reported crashes rose from 54.0 in 2013 to 94.7 in 2025 (75.4%).', 'interpretation': 'This answers whether motorist deaths fell relative to the number of reported
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
- tr_TR01: If a per-reported-crash rate spanning 2020 is shown, the output says that the number of recorded crashes changes sharply around 2020 and that this affects comparing the per-crash rate across years (naming the cause, the 2020 recording change, is not required: it is not in the data or the dictionary).
- tr_PERMILE: A per-reported-crash rate, if shown, is not presented as a substitute for per-mile risk.
- tr_VMT: No vehicle-miles figure is imported, assumed or estimated from outside the data.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence
- required_statement: PASS if the output states, in its own words: Per-mile (per vehicle-mile) risk cannot be determined from this data because it has no vehicle-miles or traffic volume.

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.