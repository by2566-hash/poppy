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

QUESTION ASKED: How are NYC crashes distributed across the days of the week, 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Number of police-reported crashes
denominator: No denominator for counts; total in-scope crashes for percentage share
grouping: Day of week, Monday through Sunday
chart_type: Bar chart
probability: 0.65
WRITTEN ANSWER:
Friday had the most crashes (338,800; 15.89% of the total), while Sunday had the fewest (257,544; 12.08%). This answers how the total number of reported crashes is distributed across weekdays, and the chart shows Friday highest and Sunday lowest. Raw totals are defensible because each row represents one crash and every requested year is complete. It does not adjust for how many dates of each weekday occur or explain why crashes differ. The filter leaves out 136,969 rows (6.04% of the file) from 2012 and partial 2026; no in-scope row has a NULL crash_date, and no included year is partial.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
weekday,crash_count,share_of_crashes_pct
Monday,304518,14.281748
Tuesday,313488,14.702437
Wednesday,311111,14.590956
Thursday,318376,14.931681
Friday,338800,15.889557
Saturday,288381,13.524930
Sunday,257544,12.078690

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; print(c.execute("SELECT COUNT(*) n, MIN(crash_date), MAX(crash_date), COUNT(*) FILTER (WHERE crash_date IS NULL) null_dates, COUNT(DISTINCT YEAR(crash_date)) years FROM read_parquet(?)", [p]).fetchdf().to_string(index=False)); print(c.execute("SELECT YEAR(crash_date) yr, MIN(crash_date) first_day, MAX(crash_date) last_day, COUNT(*) n FROM read_parquet(?) GROUP BY 1 ORDER BY 1", [p]).fetchdf().to_string(index=False)); print(c.execute("SELECT DAYNAME(crash_date) weekday, COUNT(*) n FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY CASE DAYNAME(crash_date) WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3 WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6 ELSE 7 END", [p]).fetchdf().to_string(index=False))'
# bash
python3 -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; q="SELECT COUNT(*) AS n, MIN(crash_date) AS min_date, MAX(crash_date) AS max_date, COUNT(*) FILTER (WHERE crash_date IS NULL) AS null_dates FROM read_parquet(?)"; print(c.execute(q,[p]).fetchdf().to_string(index=False)); q="SELECT YEAR(crash_date) AS yr, MIN(crash_date) AS first_day, MAX(crash_date) AS last_day, COUNT(*) AS n FROM read_parquet(?) GROUP BY 1 ORDER BY 1"; print(c.execute(q,[p]).fetchdf().to_string(index=False)); q="SELECT DAYNAME(crash_date) AS weekday, COUNT(*) AS n FROM read_parquet(?) WHERE crash_date >= ? AND crash_date < ? GROUP BY 1 ORDER BY CASE DAYOFWEEK(crash_date) WHEN 1 THEN 7 ELSE DAYOFWEEK(crash_date)-1 END"; print(c.execute(q,[p,"2013-01-01","2026-01-01"]).fetchdf().to_string(index=False))'
# bash
python3 - <<'PY'
import os, json, calendar
from datetime import date, timedelta
import duckdb
import pandas as pd
import matplotlib.pyplot as plt

path = 'data/crashes.parquet'
out = 'out'
os.makedirs(out, exist_ok=True)
con = duckdb.connect()
full = con.execute("""
    SELECT COUNT(*) AS total_rows,
           COUNT(*) FILTER (WHERE crash_date IS NULL) AS null_dates,
           COUNT(*) FILTER (WHERE crash_date < DATE '2013-01-01' OR crash_date >= DATE '2026-01-01') AS outside_rows,
           COUNT(*) FILTER (WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01') AS in_scope_rows
    FROM read_parquet(?)
""", [path]).fetchdf().iloc[0]
counts = con.execute("""
    SELECT DAYOFWEEK(crash_date) AS dow, COUNT(*) AS crash_count
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY DAYOFWEEK(crash_date)
""", [path]).fetchdf()
weekday_names = {0:'Sunday', 1:'Monday', 2:'Tuesday', 3:'Wednesday', 4:'Thursday', 5:'Friday', 6:'Saturday'}
counts['weekday'] = counts.dow.map(weekday_names)
counts['weekday_order'] = counts.dow.map({1:0,2:1,3:2,4:3,5:4,6:5,0:6})
counts = counts.sort_values('weekday_order').reset_index(drop=True)

# Exposure is the number of calendar dates of each weekday in the complete requested period.
start, end = date(2013, 1, 1), date(2025, 12, 31)
exposure = {i: 0 for i in range(7)}
d = start
while d <= end:
    exposure[(d.weekday() + 1) % 7] += 1  # Python Monday=0; DuckDB Sunday=0
    d += timedelta(days=1)
counts['calendar_days'] = counts.dow.map(exposure)
counts['share_of_crashes_pct'] = counts.crash_count / int(full.in_scope_rows) * 100
counts['crashes_per_calendar_day'] = counts.crash_count / counts.calendar_days

v1 = counts[['weekday','crash_count','share_of_crashes_pct']].copy()
v1.to_csv(f'{out}/values_1.csv', index=False, float_format='%.6f')
v2 = counts[['weekday','crash_count','calendar_days','crashes_per_calendar_day']].copy()
v2.to_csv(f'{out}/values_2.csv', index=False, float_format='%.6f')

plt.figure(figsize=(9,5.3))
plt.bar(v1.weekday, v1.crash_count, color='#3B78A1')
plt.ylabel('Police-reported crashes')
plt.xlabel('Day of week')
plt.title('NYC crashes by weekday, 2013–2025')
plt.xticks(rotation=25, ha='right')
plt.grid(axis='y', alpha=.25)
plt.tight_layout()
plt.savefig(f'{out}/option_1.png', dpi=160)
plt.close()

plt.figure(figsize=(9,5.3))
plt.bar(v2.weekday, v2.crashes_per_calendar_day, color='#D27B3C')
plt.ylabel('Crashes per calendar date')
plt.xlabel('Day of week')
plt.title('Average NYC crashes per weekday date, 2013–2025')
plt.xticks(rotation=25, ha='right')
plt.grid(axis='y', alpha=.25)
plt.tight_layout()
plt.savefig(f'{out}/option_2.png', dpi=160)
plt.close()

print('coverage:', full.to_dict())
print(counts[['weekday','crash_count','calendar_days','share_of_crashes_pct','crashes_per_calendar_day']].to_string(index=False))
print('weekday date exposure:', exposure)
print('outside share pct:', float(full.outside_rows)/float(full.total_rows)*100)
PY
# bash
python3 - <<'PY'
import json, pandas as pd
with open('out/options.json') as f:
    doc = json.load(f)
assert abs(sum(o['probability'] for o in doc['options']) - 1) < 1e-9
v1 = pd.read_csv('out/values_1.csv')
v2 = pd.read_csv('out/values_2.csv')
assert v1.loc[v1.crash_count.idxmax(), 'weekday'] == 'Friday'
assert v1.loc[v1.crash_count.idxmin(), 'weekday'] == 'Sunday'
assert v2.loc[v2.crashes_per_calendar_day.idxmax(), 'weekday'] == 'Friday'
assert v2.loc[v2.crashes_per_calendar_day.idxmin(), 'weekday'] == 'Sunday'
assert round(v1.loc[v1.weekday.eq('Friday'), 'share_of_crashes_pct'].iloc[0], 2) == 15.89
assert round(v2.loc[v2.weekday.eq('Friday'), 'crashes_per_calendar_day'].iloc[0], 1) == 499.7
print('Validated options JSON, totals, high/low weekdays, and answer figures.')
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
- tr_DAYCOUNT: If per-day averages or 'X% fewer on <day>' comparisons are given, the arithmetic is right (e.g. Sunday has 24% fewer than the mean weekday, Friday 32% more) and unequal day counts (678/679) are handled or noted.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.