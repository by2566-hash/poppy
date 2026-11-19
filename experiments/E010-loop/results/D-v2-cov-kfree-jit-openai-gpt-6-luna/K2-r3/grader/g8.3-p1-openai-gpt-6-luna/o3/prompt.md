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
metric: Mean police-reported crashes per calendar date
denominator: All calendar dates of the corresponding weekday in 2013–2025 (678 or 679 dates)
grouping: Day of week (Sunday through Saturday)
chart_type: Bar chart
probability: 0.3
WRITTEN ANSWER:
The average was highest on Fridays at 499.7 crashes per date and lowest on Sundays at 379.9. This framing answers how many reported crashes occurred on an average calendar date of each weekday and shows 499.7 per Friday versus 379.9 per Sunday. It is defensible because it accounts for the slightly different numbers of each weekday's calendar dates in 2013–2025, including zero-crash dates if any. It leaves unanswered whether the average pattern holds year by year or varies by season. Rows outside 2013–2025 (2012 and 2026) are excluded, representing 6.04% of all file rows; no in-period row has a NULL crash date (0.00% left out for a missing required value), and no included year is partial.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
weekday,calendar_dates,avg_crashes_per_date
Sunday,678,379.858407080
Monday,678,449.141592920
Tuesday,679,461.690721649
Wednesday,679,458.189985272
Thursday,678,469.581120944
Friday,678,499.705014749
Saturday,678,425.340707965

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("SELECT COUNT(*) n, MIN(crash_date) min_date, MAX(crash_date) max_date, COUNT(*) FILTER (WHERE crash_date IS NULL) null_date FROM read_parquet(?)", [p]).df().to_string(index=False)); print(c.execute("SELECT YEAR(crash_date) year, COUNT(*) crashes, MIN(crash_date) min_date, MAX(crash_date) max_date FROM read_parquet(?) GROUP BY year ORDER BY year", [p]).df().to_string(index=False)); print(c.execute("SELECT COUNT(DISTINCT crash_date) unique_dates FROM read_parquet(?)", [p]).fetchall())'
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; c=duckdb.connect(); print(c.execute("SELECT YEAR(crash_date) AS yr, COUNT(*) AS crashes, MIN(crash_date) AS min_date, MAX(crash_date) AS max_date FROM read_parquet(?) GROUP BY yr ORDER BY yr", [p]).df().to_string(index=False)); print(c.execute("SELECT COUNT(*) AS rows_2013_2025, COUNT(*) FILTER (WHERE crash_date IS NULL) AS null_dates FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'", [p]).df().to_string(index=False))'
# bash
ls -la .
# bash
python3 - <<'PY'
import duckdb
p = 'data/crashes.parquet'
c = duckdb.connect()
start, end = '2013-01-01', '2025-12-31'
q = """SELECT COUNT(*) AS all_rows,
COUNT(*) FILTER (WHERE crash_date BETWEEN ? AND ?) AS target_rows,
COUNT(*) FILTER (WHERE crash_date IS NULL) AS null_dates,
COUNT(DISTINCT crash_date) FILTER (WHERE crash_date BETWEEN ? AND ?) AS target_observed_dates
FROM read_parquet(?)"""
print(c.execute(q, [start,end,start,end,p]).df().to_string(index=False))
print(c.execute("""WITH days AS (
 SELECT CAST(d AS DATE) AS dt FROM generate_series(DATE '2013-01-01', DATE '2025-12-31', INTERVAL 1 DAY) AS t(d)
), crashes AS (
 SELECT crash_date AS dt, COUNT(*) AS n FROM read_parquet(?) WHERE crash_date BETWEEN ? AND ? GROUP BY 1
)
SELECT strftime(days.dt, '%w') AS dow, CASE strftime(days.dt, '%w') WHEN '0' THEN 'Sunday' WHEN '1' THEN 'Monday' WHEN '2' THEN 'Tuesday' WHEN '3' THEN 'Wednesday' WHEN '4' THEN 'Thursday' WHEN '5' THEN 'Friday' ELSE 'Saturday' END AS weekday,
COUNT(*) AS calendar_dates, SUM(COALESCE(crashes.n,0)) AS total_crashes,
AVG(COALESCE(crashes.n,0)) AS mean_crashes_per_date
FROM days LEFT JOIN crashes USING (dt) GROUP BY dow ORDER BY CAST(dow AS INTEGER)""", [p,start,end]).df().to_string(index=False))
PY
# bash
python3 - <<'PY'
import os
import duckdb
import pandas as pd
import matplotlib.pyplot as plt

path = 'data/crashes.parquet'
out = 'out'
os.makedirs(out, exist_ok=True)
start, end = '2013-01-01', '2025-12-31'
con = duckdb.connect()
query = """WITH calendar AS (
  SELECT CAST(d AS DATE) AS crash_date
  FROM generate_series(DATE '2013-01-01', DATE '2025-12-31', INTERVAL 1 DAY) AS t(d)
), daily AS (
  SELECT crash_date, COUNT(*) AS crashes
  FROM read_parquet(?)
  WHERE crash_date BETWEEN ? AND ?
  GROUP BY crash_date
)
SELECT CAST(strftime(calendar.crash_date, '%w') AS INTEGER) AS weekday_num,
       CASE strftime(calendar.crash_date, '%w')
         WHEN '0' THEN 'Sunday' WHEN '1' THEN 'Monday' WHEN '2' THEN 'Tuesday'
         WHEN '3' THEN 'Wednesday' WHEN '4' THEN 'Thursday'
         WHEN '5' THEN 'Friday' ELSE 'Saturday' END AS weekday,
       COUNT(*) AS calendar_dates,
       SUM(COALESCE(daily.crashes, 0)) AS crashes,
       AVG(COALESCE(daily.crashes, 0)) AS avg_crashes_per_date
FROM calendar LEFT JOIN daily USING (crash_date)
GROUP BY weekday_num, weekday
ORDER BY weekday_num"""
df = con.execute(query, [path, start, end]).df()
period_total = int(df['crashes'].sum())
df['crash_share_percent'] = df['crashes'] / period_total * 100

options = [
    (1, 'crashes', 'values_1.csv', 'option_1.png', 'NYC reported crashes by weekday, 2013–2025', 'Number of reported crashes'),
    (2, 'crash_share_percent', 'values_2.csv', 'option_2.png', 'Share of NYC reported crashes by weekday, 2013–2025', 'Share of all reported crashes (%)'),
    (3, 'avg_crashes_per_date', 'values_3.csv', 'option_3.png', 'Average reported crashes per calendar date by weekday, 2013–2025', 'Average crashes per weekday date'),
]
for option_id, value_col, csv_name, png_name, title, ylabel in options:
    columns = ['weekday', value_col]
    if option_id == 3:
        columns.insert(1, 'calendar_dates')
    plotted = df[columns].copy()
    plotted.to_csv(os.path.join(out, csv_name), index=False, float_format='%.9f')
    fig, ax = plt.subplots(figsize=(9, 5.2))
    bars = ax.bar(df['weekday'], df[value_col], color='#3572A5')
    ax.set_title(title, pad=14)
    ax.set_ylabel(ylabel)
    ax.set_xlabel('Day of week')
    ax.grid(axis='y', alpha=0.25)
    ax.set_axisbelow(True)
    ax.spines[['top', 'right']].set_visible(False)
    if option_id == 1:
        ax.set_ylim(0, df[value_col].max() * 1.13)
        for bar, value in zip(bars, df[value_col]):
            ax.annotate(f'{int(value):,}', (bar.get_x() + bar.get_width()/2, bar.get_height()), xytext=(0, 4), textcoords='offset points', ha='center', fontsize=8)
    elif option_id == 2:
        ax.set_ylim(0, df[value_col].max() * 1.14)
        for bar, value in zip(bars, df[value_col]):
            ax.annotate(f'{value:.2f}%', (bar.get_x() + bar.get_width()/2, bar.get_height()), xytext=(0, 4), textcoords='offset points', ha='center', fontsize=8)
    else:
        ax.set_ylim(0, df[value_col].max() * 1.13)
        for bar, value in zip(bars, df[value_col]):
            ax.annotate(f'{value:.1f}', (bar.get_x() + bar.get_width()/2, bar.get_height()), xytext=(0, 4), textcoords='offset points', ha='center', fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(out, png_name), dpi=160, bbox_inches='tight')
    plt.close(fig)

all_rows = con.execute('SELECT COUNT(*) FROM read_parquet(?)', [path]).fetchone()[0]
target_rows = con.execute('SELECT COUNT(*) FROM read_parquet(?) WHERE crash_date BETWEEN ? AND ?', [path, start, end]).fetchone()[0]
null_target_dates = con.execute('SELECT COUNT(*) FROM read_parquet(?) WHERE crash_date BETWEEN ? AND ? AND crash_date IS NULL', [path, start, end]).fetchone()[0]
print(df[['weekday','calendar_dates','crashes','crash_share_percent','avg_crashes_per_date']].to_string(index=False, formatters={'crash_share_percent':'{:.6f}'.format,'avg_crashes_per_date':'{:.6f}'.format}))
print(f'period_total={period_total}; total_rows={all_rows}; target_rows={target_rows}; outside_rows={all_rows-target_rows}; outside_share_percent={(all_rows-target_rows)/all_rows*100:.6f}; null_target_dates={null_target_dates}; target_share_percent={target_rows/all_rows*100:.6f}')
PY
# bash
python3 - <<'PY'
import json, pathlib, pandas as pd
out=pathlib.Path('out')
data=json.loads((out/'options.json').read_text())
assert len(data['options']) == 3
assert abs(sum(o['probability'] for o in data['options'])-1) < 1e-12
for i in range(1,4):
    chart=out/f'option_{i}.png'
    values=out/f'values_{i}.csv'
    assert chart.is_file() and chart.stat().st_size > 0
    df=pd.read_csv(values)
    assert len(df)==7
    print(f'option {i}: chart={chart.stat().st_size} bytes, values={values.name}, rows={len(df)}')
print('options JSON valid; probabilities sum to', sum(o['probability'] for o in data['options']))
print('weekday share sum =', pd.read_csv(out/'values_2.csv')['crash_share_percent'].sum())
print('weekday count sum =', pd.read_csv(out/'values_1.csv')['crashes'].sum())
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