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
metric: Motorist deaths per 1,000 reported crash records
denominator: All dated reported crash records in that calendar year
grouping: Crash year, 2013–2025
chart_type: Line chart
probability: 0.5
WRITTEN ANSWER:
Motorist deaths per 1,000 reported crash records rose from 0.54 in 2013 to 0.95 in 2025 (75.4%), so this crash-normalized proxy did not decline, but it is not risk per mile. This dataset cannot answer whether motorist death risk per mile declined because it has no miles-driven exposure; this framing instead compares deaths with the number of reported crash records. The rate rose from 0.54 deaths per 1,000 records in 2013 to 0.95 in 2025, a 75.4% increase. This is a defensible crash-severity comparison because it adjusts fatality counts for the volume of reported crash records, but it leaves exposure-adjusted, per-mile risk unanswered. No in-window rows are excluded for NULL crash dates or motorist-fatality values (0 of 2,132,218, or 0%); no partial year is included, and all partial-year rows from 2012 (100,545; 4.43% of the file) and 2026 (36,424; 1.60%) are outside the date filter.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,motorist_deaths,reported_crashes,motorist_deaths_per_1000_crashes
2013,110,203742,0.53989850
2014,109,206046,0.52900809
2015,95,217708,0.43636430
2016,72,229833,0.31327094
2017,107,231007,0.46318943
2018,98,231564,0.42320913
2019,82,211486,0.38773252
2020,139,112918,1.23098177
2021,134,110558,1.21203350
2022,116,103887,1.11659784
2023,123,96607,1.27319966
2024,111,91316,1.21555916
2025,81,85546,0.94685900

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; print(duckdb.sql(f"describe select * from read_parquet(\"{p}\")").df().to_string(index=False)); print(duckdb.sql(f"select min(crash_date) first_date, max(crash_date) last_date, count(*) n from read_parquet(\"{p}\")").df().to_string(index=False))'
# bash
ls
# bash
python3 -c 'import duckdb; q="""WITH y AS (SELECT year(crash_date) yr, count(*) rows, count(*) FILTER (WHERE number_of_motorist_killed IS NULL) null_mk, sum(number_of_motorist_killed) motorist_deaths, count(*) FILTER (WHERE number_of_persons_killed IS NULL) null_allk, sum(number_of_persons_killed) deaths, count(*) FILTER (WHERE crash_date IS NULL) null_date FROM read_parquet(\"data/crashes.parquet\") GROUP BY 1) SELECT * FROM y WHERE yr BETWEEN 2012 AND 2026 ORDER BY yr"""; print(duckdb.sql(q).df().to_string(index=False)); q2="""SELECT count(*) total, count(*) FILTER (WHERE crash_date IS NULL) null_date, count(*) FILTER (WHERE number_of_motorist_killed IS NULL) null_motorist_killed FROM read_parquet(\"data/crashes.parquet\")"""; print(duckdb.sql(q2).df().to_string(index=False))'
# bash
python3 -c 'import duckdb; q="""WITH y AS (SELECT year(crash_date) yr, count(*) n_rows, count(*) FILTER (WHERE number_of_motorist_killed IS NULL) null_mk, sum(number_of_motorist_killed) motorist_deaths, count(*) FILTER (WHERE number_of_persons_killed IS NULL) null_allk, sum(number_of_persons_killed) deaths FROM read_parquet(\"data/crashes.parquet\") GROUP BY 1) SELECT * FROM y WHERE yr BETWEEN 2012 AND 2026 ORDER BY yr"""; print(duckdb.sql(q).df().to_string(index=False)); q2="""SELECT count(*) total, count(*) FILTER (WHERE crash_date IS NULL) null_date, count(*) FILTER (WHERE number_of_motorist_killed IS NULL) null_motorist_killed FROM read_parquet(\"data/crashes.parquet\")"""; print(duckdb.sql(q2).df().to_string(index=False))'
# bash
python3 -c 'import duckdb; q="""SELECT year(crash_date) yr, min(crash_date) first_date, max(crash_date) last_date, count(*) n, count(DISTINCT month(crash_date)) months FROM read_parquet(\"data/crashes.parquet\") GROUP BY 1 ORDER BY 1"""; print(duckdb.sql(q).df().to_string(index=False)); q="""SELECT year(crash_date) yr, month(crash_date) mo, count(*) n FROM read_parquet(\"data/crashes.parquet\") WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY 1,2 ORDER BY 1,2"""; print(duckdb.sql(q).df().to_string(index=False))'
# bash
python3 -c 'import duckdb; q="""SELECT year(crash_date) yr, min(crash_date) first_date, max(crash_date) last_date, count(*) n, count(DISTINCT month(crash_date)) month_count FROM read_parquet(\"data/crashes.parquet\") GROUP BY 1 ORDER BY 1"""; print(duckdb.sql(q).df().to_string(index=False)); q="""SELECT year(crash_date) yr, month(crash_date) mo, count(*) n FROM read_parquet(\"data/crashes.parquet\") WHERE year(crash_date) BETWEEN 2013 AND 2025 GROUP BY 1,2 ORDER BY 1,2"""; print(duckdb.sql(q).df().to_string(index=False))'
# bash
python3 - <<'PY'
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

out = Path('out')
out.mkdir(exist_ok=True)
con = duckdb.connect()
query = """
SELECT year(crash_date) AS year,
       count(*) AS reported_crashes,
       sum(number_of_motorist_killed) AS motorist_deaths,
       count(*) FILTER (WHERE crash_date IS NULL) AS null_dates,
       count(*) FILTER (WHERE number_of_motorist_killed IS NULL) AS null_motorist_deaths
FROM read_parquet('data/crashes.parquet')
WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
GROUP BY year ORDER BY year
"""
df = con.execute(query).df()
df['motorist_deaths_per_1000_crashes'] = 1000 * df.motorist_deaths / df.reported_crashes
assert df.year.tolist() == list(range(2013, 2026))
assert df[['null_dates','null_motorist_deaths']].to_numpy().sum() == 0

v1 = df[['year','motorist_deaths']].copy()
v1['motorist_deaths'] = v1.motorist_deaths.astype(int)
v1.to_csv(out / 'values_1.csv', index=False)
v2 = df[['year','motorist_deaths','reported_crashes','motorist_deaths_per_1000_crashes']].copy()
v2['motorist_deaths'] = v2.motorist_deaths.astype(int)
v2['reported_crashes'] = v2.reported_crashes.astype(int)
v2.to_csv(out / 'values_2.csv', index=False, float_format='%.8f')

plt.figure(figsize=(10,5.5))
plt.plot(v1.year, v1.motorist_deaths, marker='o', linewidth=2, color='#1f77b4')
plt.xticks(v1.year, rotation=45)
plt.ylabel('Motorist deaths (people)')
plt.xlabel('Crash year')
plt.title('Recorded motorist deaths in NYC crashes, 2013–2025')
plt.grid(axis='y', alpha=.25)
plt.tight_layout()
plt.savefig(out / 'option_1.png', dpi=180)
plt.close()

plt.figure(figsize=(10,5.5))
plt.plot(v2.year, v2.motorist_deaths_per_1000_crashes, marker='o', linewidth=2, color='#d95f02')
plt.xticks(v2.year, rotation=45)
plt.ylabel('Motorist deaths per 1,000 reported crash records')
plt.xlabel('Crash year')
plt.title('Motorist fatality count relative to reported crash records, 2013–2025')
plt.grid(axis='y', alpha=.25)
plt.tight_layout()
plt.savefig(out / 'option_2.png', dpi=180)
plt.close()

start, end = df.iloc[0], df.iloc[-1]
print(df.to_string(index=False))
print('target_rows', int(df.reported_crashes.sum()))
print('rate2013', float(start.motorist_deaths_per_1000_crashes), 'rate2025', float(end.motorist_deaths_per_1000_crashes), 'rate_pct_change', float((end.motorist_deaths_per_1000_crashes/start.motorist_deaths_per_1000_crashes-1)*100))
print('death_pct_change', float((end.motorist_deaths/start.motorist_deaths-1)*100))
print('files', sorted(p.name for p in out.iterdir()))
PY
# bash
python3 -c 'import duckdb; q="""WITH dates AS (SELECT DISTINCT crash_date d FROM read_parquet(\"data/crashes.parquet\") WHERE crash_date >= DATE \'2013-01-01\' AND crash_date < DATE \'2026-01-01\'), expected AS (SELECT d::DATE AS d FROM generate_series(DATE \'2013-01-01\', DATE \'2025-12-31\', INTERVAL 1 DAY) t(d)) SELECT count(*) expected_days, count(dates.d) observed_days, count(*) FILTER (WHERE dates.d IS NULL) missing_days FROM expected LEFT JOIN dates USING (d)"""; print(duckdb.sql(q).df().to_string(index=False)); q="""SELECT year(crash_date) yr, count(*) n FROM read_parquet(\"data/crashes.parquet\") WHERE crash_date < DATE \'2013-01-01\' OR crash_date >= DATE \'2026-01-01\' GROUP BY 1 ORDER BY 1"""; print(duckdb.sql(q).df().to_string(index=False))'
# bash
python3 -c 'import json; d=json.load(open("out/options.json")); print("valid JSON; probability sum", sum(o["probability"] for o in d["options"])); print("partial shares", 100*100545/2269187, 100*36424/2269187)'

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