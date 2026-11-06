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

QUESTION ASKED: What was the distribution of NYC crashes by day of the week over the period 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Mean number of police-reported crashes per calendar occurrence of weekday
denominator: Number of occurrences of that weekday from 2013-01-01 through 2025-12-31 (678 or 679 dates)
grouping: Day of week
chart_type: Vertical bar chart
probability: 0.45
WRITTEN ANSWER:
Friday averaged 499.71 crashes per Friday, the highest, while Sunday averaged 379.86 per Sunday, the lowest. This answers which weekday had the highest or lowest typical daily crash count across the period after accounting for weekday-date frequency. The average is defensible because weekdays occurred on 678 or 679 dates in the window, but it does not state each weekday's share of the full-period crash total.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
weekday,weekday_dates,crash_count_in_period,mean_crashes_per_occurrence
Monday,678,304518,449.1416
Tuesday,679,313488,461.6907
Wednesday,679,311111,458.1900
Thursday,678,318376,469.5811
Friday,678,338800,499.7050
Saturday,678,288381,425.3407
Sunday,678,257544,379.8584

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c "import duckdb; p='data/crashes.parquet'; print(duckdb.sql(f\"SELECT MIN(crash_date), MAX(crash_date), COUNT(*) FROM read_parquet('{p}')\").fetchall()); print(duckdb.sql(f\"SELECT COUNT(*) FILTER (WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01') FROM read_parquet('{p}')\").fetchall())"
# bash
ls
# bash
python - <<'PY'
import duckdb
p='data/crashes.parquet'
con=duckdb.connect()
con.execute(f"CREATE VIEW crashes AS SELECT * FROM read_parquet('{p}')")
print(con.execute("""
WITH weekdays AS (
  SELECT d::DATE AS day, strftime(d::DATE, '%w')::INT AS dow
  FROM generate_series(DATE '2013-01-01', DATE '2025-12-31', INTERVAL 1 DAY) AS t(d)
), counts AS (
  SELECT strftime(crash_date, '%w')::INT AS dow, count(*) AS crashes
  FROM crashes WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
  GROUP BY 1
), occurrences AS (SELECT dow, count(*) AS n FROM weekdays GROUP BY 1)
SELECT CASE dow WHEN 1 THEN 'Monday' WHEN 2 THEN 'Tuesday' WHEN 3 THEN 'Wednesday' WHEN 4 THEN 'Thursday' WHEN 5 THEN 'Friday' WHEN 6 THEN 'Saturday' ELSE 'Sunday' END weekday,
       c.crashes, o.n occurrences, round(c.crashes::DOUBLE/o.n, 2) avg_per_occurrence,
       round(100.0*c.crashes/sum(c.crashes) OVER(), 2) share_pct
FROM counts c JOIN occurrences o USING (dow) ORDER BY dow
""").fetchdf().to_string(index=False))
PY
# bash
python - <<'PY'
from pathlib import Path
import duckdb
import matplotlib.pyplot as plt

out = Path('out')
out.mkdir(exist_ok=True)
con = duckdb.connect()
con.execute("CREATE VIEW crashes AS SELECT * FROM read_parquet('data/crashes.parquet')")
rows = con.execute("""
WITH weekdays AS (
  SELECT d::DATE AS day, strftime(d::DATE, '%w')::INT AS dow
  FROM generate_series(DATE '2013-01-01', DATE '2025-12-31', INTERVAL 1 DAY) AS t(d)
), counts AS (
  SELECT strftime(crash_date, '%w')::INT AS dow, count(*) AS crashes
  FROM crashes
  WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
  GROUP BY 1
), occurrences AS (
  SELECT dow, count(*) AS weekday_dates FROM weekdays GROUP BY 1
)
SELECT c.dow,
  CASE c.dow WHEN 1 THEN 'Monday' WHEN 2 THEN 'Tuesday' WHEN 3 THEN 'Wednesday'
    WHEN 4 THEN 'Thursday' WHEN 5 THEN 'Friday' WHEN 6 THEN 'Saturday' ELSE 'Sunday' END AS weekday,
  c.crashes, o.weekday_dates,
  c.crashes::DOUBLE / o.weekday_dates AS mean_crashes_per_occurrence,
  100.0 * c.crashes / sum(c.crashes) OVER () AS share_pct
FROM counts c JOIN occurrences o USING (dow)
ORDER BY CASE c.dow WHEN 0 THEN 7 ELSE c.dow END
""").fetchdf()

count_data = rows[['weekday', 'crashes', 'share_pct']].rename(columns={
    'crashes': 'crash_count', 'share_pct': 'share_of_period_crashes_pct'})
count_data.to_csv(out / 'values_1.csv', index=False, float_format='%.4f')
mean_data = rows[['weekday', 'weekday_dates', 'crashes', 'mean_crashes_per_occurrence']].rename(columns={
    'crashes': 'crash_count_in_period'})
mean_data.to_csv(out / 'values_2.csv', index=False, float_format='%.4f')

plt.figure(figsize=(10, 5.8))
bars = plt.bar(rows['weekday'], rows['crashes'], color='#3977a8')
plt.title('NYC police-reported crashes by weekday, 2013–2025')
plt.xlabel('Day of week')
plt.ylabel('Crash count')
plt.grid(axis='y', alpha=0.25)
plt.bar_label(bars, labels=[f'{int(x):,}' for x in rows['crashes']], padding=3, fontsize=8)
plt.ylim(0, rows['crashes'].max() * 1.14)
plt.tight_layout()
plt.savefig(out / 'option_1.png', dpi=180)
plt.close()

plt.figure(figsize=(10, 5.8))
bars = plt.bar(rows['weekday'], rows['mean_crashes_per_occurrence'], color='#c87935')
plt.title('Average NYC crashes per calendar weekday, 2013–2025')
plt.xlabel('Day of week')
plt.ylabel('Mean crashes per occurrence of weekday')
plt.grid(axis='y', alpha=0.25)
plt.bar_label(bars, labels=[f'{x:.1f}' for x in rows['mean_crashes_per_occurrence']], padding=3, fontsize=9)
plt.ylim(0, rows['mean_crashes_per_occurrence'].max() * 1.14)
plt.tight_layout()
plt.savefig(out / 'option_2.png', dpi=180)
plt.close()
print(rows.to_string(index=False))
print('Total qualifying crashes:', int(rows['crashes'].sum()))
PY
# bash
python -c "import json; p=json.load(open('out/options.json')); print('options:', len(p['options']), 'probability_sum:', sum(x['probability'] for x in p['options'])); print([(x['id'], x['answer']) for x in p['options']])"

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_DAYCOUNT: If per-day averages or 'X% fewer on <day>' comparisons are given, the arithmetic is right (e.g. Sunday has 24% fewer than the mean weekday, Friday 32% more) and unequal day counts (678/679) are handled or noted.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.