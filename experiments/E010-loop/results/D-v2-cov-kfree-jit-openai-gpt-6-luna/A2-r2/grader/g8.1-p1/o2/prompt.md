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
metric: Share of crashes with at least one person injured or killed
denominator: Crashes with non-NULL number_of_persons_injured and number_of_persons_killed
grouping: Night (8 pm–5:59 am) versus day (6 am–7:59 pm)
chart_type: Two-bar column chart
probability: 0.5
WRITTEN ANSWER:
Among crashes with known injury and fatality counts, 28.44% at night versus 23.41% by day involved an injury or death, a 5.03-percentage-point nighttime excess. This framing answers whether a larger share of crashes at night involve reported harm: 28.44% of nighttime crashes versus 23.41% of daytime crashes with known outcomes involved an injury or death. It is defensible as a crash-severity comparison because each period's harm-involving crashes are divided by its crashes with known injury and death counts. It leaves unanswered the risk per trip or mile and the number of people harmed per crash, because the file contains neither travel exposure nor a person-level rate comparison. Rows with either injury or killed count NULL are left out (8,919/2,269,187, 0.393%); the file includes only Jul–Dec 2012, leaving Jan–Jun out (182/366 calendar days, 49.7%), and Jan 1–Jun 11 2026, leaving Jun 12–Dec 31 out (203/365 days, 55.6%).

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
period,known_harm_crashes,injury_or_fatal_crashes,missing_harm,injury_or_fatal_crash_share_pct,known_harm_crashes_share_of_all,file_total_crashes,file_start_date,file_end_date,2012_absent_calendar_days,2012_calendar_days,2012_absent_calendar_day_share,2026_absent_calendar_days,2026_calendar_days,2026_absent_calendar_day_share,file_rows_missing_required_outcome,file_share_missing_required_outcome
Night (8 pm–5:59 am),556333,158211,2671,28.438183605861955,0.9952218588775752,2269187,2012-07-01,2026-06-11,182,366,0.4972677595628415,203,365,0.5561643835616439,8919,0.003930482591342185
Day (6 am–7:59 pm),1703935,398867,6248,23.408580726377473,0.9963465898093948,2269187,2012-07-01,2026-06-11,182,366,0.4972677595628415,203,365,0.5561643835616439,8919,0.003930482591342185

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python3 -c "import duckdb; c=duckdb.connect(); print(c.execute(\"DESCRIBE SELECT * FROM read_parquet('data/crashes.parquet')\").fetchdf().to_string(index=False)); print(c.execute(\"SELECT COUNT(*) rows, MIN(crash_date) min_date, MAX(crash_date) max_date, COUNT(*) FILTER (WHERE crash_time IS NULL) null_time FROM read_parquet('data/crashes.parquet')\").fetchdf().to_string(index=False))"
# bash
python3 - <<'PY'
import duckdb
con=duckdb.connect()
p='data/crashes.parquet'
print(con.execute(f"""
SELECT count(*) AS n, min(crash_date) AS min_date, max(crash_date) AS max_date,
 count(*) FILTER (WHERE crash_time IS NULL) AS null_time,
 count(*) FILTER (WHERE number_of_persons_injured IS NULL) AS null_injured,
 count(*) FILTER (WHERE number_of_persons_killed IS NULL) AS null_killed,
 count(*) FILTER (WHERE number_of_persons_injured IS NULL OR number_of_persons_killed IS NULL) AS null_any_outcome
FROM read_parquet('{p}')
""").fetchdf().to_string(index=False))
print(con.execute(f"""
SELECT year(crash_date) AS yr, count(*) n, min(crash_date) min_date, max(crash_date) max_date
FROM read_parquet('{p}') GROUP BY yr ORDER BY yr
""").fetchdf().to_string(index=False))
print(con.execute(f"""
SELECT count(*) total,
 count(*) FILTER (WHERE crash_time IS NOT NULL AND (hour(crash_time)>=20 OR hour(crash_time)<6)) AS night,
 count(*) FILTER (WHERE crash_time IS NOT NULL AND hour(crash_time)>=6 AND hour(crash_time)<20) AS day
FROM read_parquet('{p}')
""").fetchdf().to_string(index=False))
PY
# bash
ls
# bash
python3 - <<'PY'
import os, json
import duckdb
import pandas as pd
import matplotlib.pyplot as plt

os.makedirs('out', exist_ok=True)
con = duckdb.connect()
p = 'data/crashes.parquet'
query = f"""
WITH base AS (
  SELECT *, CASE WHEN hour(crash_time) >= 20 OR hour(crash_time) < 6 THEN 'Night (8 pm–5:59 am)' ELSE 'Day (6 am–7:59 pm)' END AS period
  FROM read_parquet('{p}')
), bounds AS (
  SELECT min(crash_date) AS min_date, max(crash_date) AS max_date,
         date_diff('day', min(crash_date), max(crash_date)) + 1 AS calendar_days
  FROM base
), agg AS (
  SELECT period, count(*) AS crash_count,
    count(*) FILTER (WHERE number_of_persons_injured IS NOT NULL AND number_of_persons_killed IS NOT NULL) AS known_harm_crashes,
    count(*) FILTER (WHERE number_of_persons_injured IS NOT NULL AND number_of_persons_killed IS NOT NULL AND (number_of_persons_injured > 0 OR number_of_persons_killed > 0)) AS injury_or_fatal_crashes,
    count(*) FILTER (WHERE number_of_persons_killed IS NOT NULL) AS known_fatality_crashes,
    count(*) FILTER (WHERE number_of_persons_killed IS NOT NULL AND number_of_persons_killed > 0) AS fatal_crashes,
    count(*) FILTER (WHERE number_of_persons_injured IS NULL OR number_of_persons_killed IS NULL) AS missing_harm,
    count(*) FILTER (WHERE number_of_persons_killed IS NULL) AS missing_killed
  FROM base GROUP BY period
)
SELECT agg.*, bounds.min_date, bounds.max_date, bounds.calendar_days,
  CASE WHEN period LIKE 'Night%' THEN calendar_days * 10 ELSE calendar_days * 14 END AS clock_hours
FROM agg CROSS JOIN bounds
ORDER BY CASE WHEN period LIKE 'Night%' THEN 1 ELSE 2 END
"""
df = con.execute(query).fetchdf()

# Coverage exclusions are calendar days outside the file's partial endpoint years.
partial = {
    2012: {'absent_days': 182, 'days_in_year': 366},
    2026: {'absent_days': 203, 'days_in_year': 365},
}
for v in partial.values():
    v['share_absent'] = v['absent_days'] / v['days_in_year']

period_order = ['Night (8 pm–5:59 am)', 'Day (6 am–7:59 pm)']
colors = ['#d95f02', '#2878b5']
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.titleweight': 'bold'})

def save_bar(frame, metric_col, ylabel, title, subtitle, filename, fmt, color='#2878b5'):
    frame = frame.set_index('period').loc[period_order].reset_index()
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    bars = ax.bar(['Night\n8 pm–5:59 am', 'Day\n6 am–7:59 pm'], frame[metric_col], color=colors, width=.56)
    ax.bar_label(bars, labels=[fmt.format(v) for v in frame[metric_col]], padding=5, fontsize=11, fontweight='bold')
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc='left', fontsize=15, pad=23)
    ax.text(0, 1.015, subtitle, transform=ax.transAxes, ha='left', va='bottom', fontsize=9, color='#555555')
    ax.spines[['top','right']].set_visible(False)
    ax.grid(axis='y', color='#dddddd', linewidth=.7)
    ax.set_axisbelow(True)
    ax.set_ylim(0, max(frame[metric_col]) * 1.22 if max(frame[metric_col]) else 1)
    fig.tight_layout()
    fig.savefig(filename, dpi=180, bbox_inches='tight')
    plt.close(fig)

# Option 1: collisions per available clock-hour, balancing unequal lengths of night/day windows.
d1 = df[['period','crash_count','clock_hours']].copy()
d1['crashes_per_1000_clock_hours'] = d1['crash_count'] / d1['clock_hours'] * 1000
d1.to_csv('out/values_1.csv', index=False)
save_bar(d1, 'crashes_per_1000_clock_hours', 'Reported crashes per 1,000 clock-hours',
         'More crashes per hour occur overnight',
         'NYC police-reported crashes; night = 8 pm–5:59 am, day = 6 am–7:59 pm',
         'out/option_1.png', '{:.1f}')

# Option 2: share of crashes with at least one reported injury or death; require both outcome fields.
d2 = df[['period','known_harm_crashes','injury_or_fatal_crashes','missing_harm']].copy()
d2['injury_or_fatal_crash_share_pct'] = d2['injury_or_fatal_crashes'] / d2['known_harm_crashes'] * 100
d2['known_harm_crashes_share_of_all'] = d2['known_harm_crashes'] / df['crash_count']
d2.to_csv('out/values_2.csv', index=False)
save_bar(d2, 'injury_or_fatal_crash_share_pct', 'Crashes with ≥1 person injured or killed (%)',
         'A larger share of night crashes involve injury or death',
         'Among crashes with non-missing injury and death counts',
         'out/option_2.png', '{:.2f}%')

# Option 3: fatal crashes per 10,000 crashes with non-missing killed count.
d3 = df[['period','known_fatality_crashes','fatal_crashes','missing_killed']].copy()
d3['fatal_crashes_per_10000_known_crashes'] = d3['fatal_crashes'] / d3['known_fatality_crashes'] * 10000
d3['known_fatality_crashes_share_of_all'] = d3['known_fatality_crashes'] / df['crash_count']
d3.to_csv('out/values_3.csv', index=False)
save_bar(d3, 'fatal_crashes_per_10000_known_crashes', 'Fatal crashes per 10,000 crashes with known death count',
         'Fatal crashes are more frequent per reported crash at night',
         'Crashes with missing number of persons killed are excluded',
         'out/option_3.png', '{:.1f}')

# Print exact, auditable values for review and options.json drafting.
print('coverage dates', df[['min_date','max_date','calendar_days']].iloc[0].to_dict())
print('partial-year absent calendar-day shares', {y: v['share_absent'] for y,v in partial.items()})
print(df.to_string(index=False))
print('\nOption 1\n', d1.to_string(index=False))
print('\nOption 2\n', d2.to_string(index=False))
print('\nOption 3\n', d3.to_string(index=False))
PY
# bash
python3 - <<'PY'
import pandas as pd
import matplotlib.pyplot as plt
p = pd.read_csv('out/values_1.csv')
order = ['Night (8 pm–5:59 am)', 'Day (6 am–7:59 pm)']
p = p.set_index('period').loc[order].reset_index()
fig, ax = plt.subplots(figsize=(8.4, 5.0))
bars = ax.bar(['Night\n8 pm–5:59 am', 'Day\n6 am–7:59 pm'], p['crashes_per_1000_clock_hours'], color=['#d95f02','#2878b5'], width=.56)
ax.bar_label(bars, labels=[f'{v:,.0f}' for v in p['crashes_per_1000_clock_hours']], padding=5, fontsize=11, fontweight='bold')
ax.set_ylabel('Reported crashes per 1,000 clock-hours')
ax.set_title('Reported crash frequency per clock-hour is lower overnight', loc='left', fontsize=15, fontweight='bold', pad=23)
ax.text(0, 1.015, 'NYC police-reported crashes; night = 8 pm–5:59 am, day = 6 am–7:59 pm', transform=ax.transAxes, ha='left', va='bottom', fontsize=9, color='#555555')
ax.spines[['top','right']].set_visible(False)
ax.grid(axis='y', color='#dddddd', linewidth=.7)
ax.set_axisbelow(True)
ax.set_ylim(0, p['crashes_per_1000_clock_hours'].max()*1.22)
fig.tight_layout()
fig.savefig('out/option_1.png', dpi=180, bbox_inches='tight')
plt.close(fig)
PY
# bash
python3 - <<'PY'
import duckdb
c=duckdb.connect()
p='data/crashes.parquet'
print(c.execute(f"SELECT count(*) AS total, count(*) FILTER (WHERE crash_date IS NULL) AS null_date, count(*) FILTER (WHERE crash_time IS NULL) AS null_time, count(*) FILTER (WHERE number_of_persons_injured IS NULL OR number_of_persons_killed IS NULL) AS null_either, count(*) FILTER (WHERE number_of_persons_killed IS NULL) AS null_killed FROM read_parquet('{p}')").fetchdf().to_string(index=False))
print('excluded shares:', 8919/2269187*100, 8913/2269187*100)
PY
# bash
python3 - <<'PY'
import pandas as pd
for i, miss_col in [(1, None), (2, 'missing_harm'), (3, 'missing_killed')]:
    path=f'out/values_{i}.csv'
    d=pd.read_csv(path)
    d['file_total_crashes']=2269187
    d['file_start_date']='2012-07-01'
    d['file_end_date']='2026-06-11'
    d['2012_absent_calendar_days']=182
    d['2012_calendar_days']=366
    d['2012_absent_calendar_day_share']=182/366
    d['2026_absent_calendar_days']=203
    d['2026_calendar_days']=365
    d['2026_absent_calendar_day_share']=203/365
    if i == 1:
        d['missing_crash_time']=0
        d['missing_crash_time_share']=0.0
    else:
        n=int(d[miss_col].sum())
        d['file_rows_missing_required_outcome']=n
        d['file_share_missing_required_outcome']=n/2269187
    d.to_csv(path,index=False)
PY
python3 -m json.tool out/options.json >/dev/null
python3 - <<'PY'
import pandas as pd
for i in (1,2,3):
    print(f'values_{i}:')
    print(pd.read_csv(f'out/values_{i}.csv').to_string(index=False))
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
- tr_TR11: Severity per crash (deaths or injuries per crash) is described as such, not as the risk of being on the street at night (no traffic volume by hour exists).
- tr_TR08: NA if the option uses no killed or injured counts. Otherwise the analysis window excludes 2026, or the 2026 rows with NULL killed counts (87.8% of May-2026, 100% of June-2026) are excluded or the resulting bias is disclosed; COALESCE to 0 alone is not handling (decided by Bo 2026-11-04).
- tr_NIGHTDEF: The definition of 'night' (hours) is stated.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.