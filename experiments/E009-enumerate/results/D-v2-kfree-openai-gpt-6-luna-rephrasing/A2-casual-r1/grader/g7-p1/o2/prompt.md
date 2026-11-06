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
- Qualifications (reported, recorded in this dataset) count when they are in the WRITTEN ANSWER or the DECLARED FRAMING; text
  that appears only inside the chart image (title, footnote, source note) does not satisfy an item on its own. The official-count
  part of unsupported_claim follows the same test as TR07.

DATA FACTS (pinned snapshot):
- The file covers 2012-07-01 to 2026-06-11; 2013-2025 are complete calendar years; 2026 is partial (to June 11).
- borough is NULL for about 20-38% of crashes in every year (TR05): a borough filter silently drops them.
- number_of_persons_killed is NULL in most May-2026 and all June-2026 rows (TR08); 2013-2025 killed counts have no NULLs.
- crash_time has no NULL rows. Reported crash counts (the number of crash records) fall sharply in 2020 (TR01), so a per-reported-crash rate (deaths or injuries divided by reported crashes) compared across years spanning 2020 needs a caveat. Counts of deaths or injuries by year do NOT need it (they are not affected by the reporting change), and a comparison between groups within one pooled window (e.g. day vs night) does not either (decided 2026-11-04; g5 wording after g4 failed c6 on plain death counts).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: Is it more dangerous to be on NYC's streets at night? Make a chart and say what you conclude for a news report.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Percentage of complete-outcome crashes recording any injury or death
denominator: Crashes with non-missing counts for both persons injured and persons killed
grouping: Day (6am–6:59pm) versus night (7pm–5:59am)
chart_type: Two-bar percentage comparison
probability: 0.6
WRITTEN ANSWER:
Among crashes with complete injury/death fields, 28.3% at night versus 23.1% by day recorded harm, indicating greater conditional crash severity at night but not necessarily greater street-user risk. This framing asks whether a reported crash is more likely to involve injury or death; the complete-case share is 28.3% at night and 23.1% by day. Comparing shares is defensible as a measure of severity conditional on a crash, but no counts of people traveling at each time are available. It leaves overall per-person danger and the chance of crashing unanswered.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
period,crashes_with_complete_injury_and_fatality_counts,crashes_recording_any_injury_or_death,share_with_injury_or_death_pct
Day (6am–6:59pm),1589101,366983,23.093749
Night (7pm–5:59am),671167,190095,28.323055

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c "import duckdb; c=duckdb.connect(); print(c.execute(\"DESCRIBE SELECT * FROM read_parquet('data/crashes.parquet')\").fetchdf().to_string(index=False)); print(c.execute(\"SELECT COUNT(*) n, MIN(crash_date) min_date, MAX(crash_date) max_date, COUNT(*) FILTER (WHERE crash_time IS NULL) null_times FROM read_parquet('data/crashes.parquet')\").fetchdf().to_string(index=False)); print(c.execute(\"SELECT crash_time, number_of_persons_injured, number_of_persons_killed FROM read_parquet('data/crashes.parquet') USING SAMPLE 8 ROWS\").fetchdf().to_string(index=False))"
# bash
ls
# bash
python -c "import duckdb; c=duckdb.connect(); q=\"WITH x AS (SELECT *, CASE WHEN hour(crash_time)>=19 OR hour(crash_time)<6 THEN 'Night (7pm-5:59am)' ELSE 'Day (6am-6:59pm)' END period FROM read_parquet('data/crashes.parquet')) SELECT period, count(*) crashes, count(DISTINCT crash_date) observed_dates, sum(number_of_persons_injured) injured_people, sum(number_of_persons_killed) killed_people, count(*) FILTER (WHERE number_of_persons_injured>0 OR number_of_persons_killed>0) injury_or_fatal_crashes, count(*) FILTER (WHERE number_of_persons_killed>0) fatal_crashes, sum(number_of_persons_injured+number_of_persons_killed) casualties FROM x GROUP BY period ORDER BY period\"; print(c.execute(q).fetchdf().to_string(index=False)); print(c.execute(\"SELECT count(DISTINCT crash_date) dates, min(crash_date), max(crash_date) FROM read_parquet('data/crashes.parquet')\").fetchdf().to_string(index=False))"
# bash
python - <<'PY'
import duckdb
c=duckdb.connect()
q="""
WITH raw AS (
 SELECT *,
   CASE WHEN hour(crash_time) >= 19 OR hour(crash_time) < 6 THEN 'Night (7pm–5:59am)' ELSE 'Day (6am–6:59pm)' END AS period
 FROM read_parquet('data/crashes.parquet')
), bounds AS (
 SELECT date_diff('day', min(crash_date), max(crash_date)) + 1 AS span_days FROM raw
)
SELECT period, COUNT(*) AS crashes,
 COUNT(*) FILTER (WHERE coalesce(number_of_persons_injured,0)>0 OR coalesce(number_of_persons_killed,0)>0) AS harm_crashes,
 COUNT(*) FILTER (WHERE coalesce(number_of_persons_killed,0)>0) AS fatal_crashes,
 SUM(coalesce(number_of_persons_injured,0)) AS injured_people,
 SUM(coalesce(number_of_persons_killed,0)) AS killed_people,
 SUM(coalesce(number_of_persons_injured,0)+coalesce(number_of_persons_killed,0)) AS casualties,
 (SELECT span_days FROM bounds) AS span_days
FROM raw GROUP BY period ORDER BY period
"""
print(c.execute(q).fetchdf().to_string(index=False))
print('Missing outcomes:', c.execute("SELECT COUNT(*) FILTER (WHERE number_of_persons_injured IS NULL OR number_of_persons_killed IS NULL) FROM read_parquet('data/crashes.parquet')").fetchone()[0])
PY
# bash
python - <<'PY'
import duckdb
c=duckdb.connect()
q="""
WITH x AS (SELECT *, CASE WHEN hour(crash_time)>=19 OR hour(crash_time)<6 THEN 'Night (7pm–5:59am)' ELSE 'Day (6am–6:59pm)' END period FROM read_parquet('data/crashes.parquet'))
SELECT period, count(*) crashes,
 count(*) FILTER (WHERE number_of_persons_injured IS NOT NULL AND number_of_persons_killed IS NOT NULL) complete_outcomes,
 count(*) FILTER (WHERE number_of_persons_injured IS NULL OR number_of_persons_killed IS NULL) incomplete_outcomes,
 count(*) FILTER (WHERE number_of_persons_injured>0 OR number_of_persons_killed>0) harmful,
 sum(coalesce(number_of_persons_injured,0)) injuries, sum(coalesce(number_of_persons_killed,0)) deaths
FROM x GROUP BY period ORDER BY period
"""
print(c.execute(q).fetchdf().to_string(index=False))
PY
# bash
python - <<'PY'
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

out = Path('out')
out.mkdir(exist_ok=True)
con = duckdb.connect()
query = """
WITH records AS (
  SELECT *,
    CASE WHEN hour(crash_time) >= 19 OR hour(crash_time) < 6
      THEN 'Night (7pm–5:59am)' ELSE 'Day (6am–6:59pm)' END AS period
  FROM read_parquet('data/crashes.parquet')
), bounds AS (
  SELECT date_diff('day', min(crash_date), max(crash_date)) + 1 AS span_days FROM records
)
SELECT period, COUNT(*) AS total_crashes,
  COUNT(*) FILTER (WHERE number_of_persons_injured IS NOT NULL AND number_of_persons_killed IS NOT NULL) AS complete_outcome_crashes,
  COUNT(*) FILTER (WHERE number_of_persons_injured > 0 OR number_of_persons_killed > 0) AS injury_or_fatal_crashes,
  COUNT(*) FILTER (WHERE number_of_persons_injured IS NOT NULL AND number_of_persons_killed IS NOT NULL AND (number_of_persons_injured > 0 OR number_of_persons_killed > 0)) AS complete_injury_or_fatal_crashes,
  (SELECT span_days FROM bounds) AS date_span_days
FROM records GROUP BY period
"""
df = con.execute(query).fetchdf()
order = ['Day (6am–6:59pm)', 'Night (7pm–5:59am)']
df['period'] = pd.Categorical(df['period'], categories=order, ordered=True)
df = df.sort_values('period').reset_index(drop=True)

# Option 1: count of reported crashes with recorded injury/death per clock-hour.
period_hours = {'Day (6am–6:59pm)': 13, 'Night (7pm–5:59am)': 11}
values1 = pd.DataFrame({
    'period': df['period'].astype(str),
    'hours_per_date': [period_hours[str(x)] for x in df['period']],
    'date_span_days': df['date_span_days'].astype(int),
    'clock_hours': [int(row.date_span_days) * period_hours[str(row.period)] for row in df.itertuples()],
    'injury_or_fatal_crashes': df['injury_or_fatal_crashes'].astype(int),
})
values1['injury_or_fatal_crashes_per_1m_clock_hours'] = values1['injury_or_fatal_crashes'] / values1['clock_hours'] * 1_000_000
values1.to_csv(out / 'values_1.csv', index=False, float_format='%.6f')

plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(8.5, 5.2))
colors = ['#3B6FB6', '#E07A36']
bars = ax.bar(['Day\n6am–6:59pm', 'Night\n7pm–5:59am'], values1['injury_or_fatal_crashes_per_1m_clock_hours'], color=colors, width=.58)
ax.bar_label(bars, labels=[f'{v:,.0f}' for v in values1['injury_or_fatal_crashes_per_1m_clock_hours']], padding=5, fontsize=11)
ax.set_ylabel('Injury-or-fatal crashes per 1 million clock-hours')
ax.set_title('Recorded injury/fatal crashes by time of day', loc='left', weight='bold', pad=14)
ax.text(0, 1.01, 'NYC police-reported crashes, Jul 1 2012–Jun 11 2026', transform=ax.transAxes, fontsize=9, color='#555555')
ax.text(0, -.21, 'Night/day clock-hours are normalized for the 11-hour vs 13-hour time windows.\nClock-hours are not a measure of street-user exposure.', transform=ax.transAxes, fontsize=9, color='#555555', va='top')
ax.set_ylim(0, max(values1['injury_or_fatal_crashes_per_1m_clock_hours']) * 1.22)
fig.tight_layout()
fig.savefig(out / 'option_1.png', dpi=180, bbox_inches='tight')
plt.close(fig)

# Option 2: fraction of crashes with complete injury/death fields that recorded harm.
values2 = pd.DataFrame({
    'period': df['period'].astype(str),
    'crashes_with_complete_injury_and_fatality_counts': df['complete_outcome_crashes'].astype(int),
    'crashes_recording_any_injury_or_death': df['complete_injury_or_fatal_crashes'].astype(int),
})
values2['share_with_injury_or_death_pct'] = values2['crashes_recording_any_injury_or_death'] / values2['crashes_with_complete_injury_and_fatality_counts'] * 100
values2.to_csv(out / 'values_2.csv', index=False, float_format='%.6f')

fig, ax = plt.subplots(figsize=(8.5, 5.2))
bars = ax.bar(['Day\n6am–6:59pm', 'Night\n7pm–5:59am'], values2['share_with_injury_or_death_pct'], color=colors, width=.58)
ax.bar_label(bars, labels=[f'{v:.1f}%' for v in values2['share_with_injury_or_death_pct']], padding=5, fontsize=11)
ax.set_ylabel('Share of crashes with injury or death recorded')
ax.set_title('Injury/fatality involvement among reported crashes', loc='left', weight='bold', pad=14)
ax.text(0, 1.01, 'NYC police-reported crashes, Jul 1 2012–Jun 11 2026', transform=ax.transAxes, fontsize=9, color='#555555')
ax.text(0, -.21, 'Includes only crashes with non-missing injury and fatality counts.\nThis is severity among crashes, not risk per street user.', transform=ax.transAxes, fontsize=9, color='#555555', va='top')
ax.set_ylim(0, max(values2['share_with_injury_or_death_pct']) * 1.23)
fig.tight_layout()
fig.savefig(out / 'option_2.png', dpi=180, bbox_inches='tight')
plt.close(fig)

print('Option 1 values:')
print(values1.to_string(index=False))
print('\nOption 2 values:')
print(values2.to_string(index=False))
PY
# bash
python - <<'PY'
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
out = Path('out')
con = duckdb.connect()
q = """
WITH x AS (
 SELECT *, CASE WHEN hour(crash_time)>=19 OR hour(crash_time)<6 THEN 'Night (7pm–5:59am)' ELSE 'Day (6am–6:59pm)' END period
 FROM read_parquet('data/crashes.parquet')
), b AS (SELECT date_diff('day', min(crash_date), max(crash_date))+1 span_days FROM x)
SELECT period,
 COUNT(*) FILTER (WHERE number_of_persons_injured>0 OR number_of_persons_killed>0) injury_or_fatal_crashes,
 (SELECT span_days FROM b) date_span_days
FROM x GROUP BY period
"""
df = con.execute(q).fetchdf()
order = ['Day (6am–6:59pm)', 'Night (7pm–5:59am)']
df['period'] = pd.Categorical(df.period, categories=order, ordered=True)
df = df.sort_values('period')
hours_per_date = {'Day (6am–6:59pm)':13, 'Night (7pm–5:59am)':11}
values = pd.DataFrame({
 'period': df.period.astype(str).tolist(),
 'hours_per_date': [hours_per_date[str(p)] for p in df.period],
 'date_span_days': df.date_span_days.astype(int).tolist(),
 'observed_clock_hours': [int(d)*hours_per_date[str(p)] for d,p in zip(df.date_span_days,df.period)],
 'crashes_with_recorded_injury_or_death': df.injury_or_fatal_crashes.astype(int).tolist()
})
values['crashes_with_recorded_injury_or_death_per_clock_hour'] = values.crashes_with_recorded_injury_or_death / values.observed_clock_hours
values.to_csv(out/'values_1.csv', index=False, float_format='%.6f')
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(8.5,5.2))
vals=values.crashes_with_recorded_injury_or_death_per_clock_hour
bars=ax.bar(['Day\n6am–6:59pm','Night\n7pm–5:59am'], vals, color=['#3B6FB6','#E07A36'], width=.58)
ax.bar_label(bars, labels=[f'{v:.2f}' for v in vals], padding=5, fontsize=11)
ax.set_ylabel('Injury-or-fatal crashes per clock-hour')
ax.set_title('Recorded injury/fatal crashes by time of day', loc='left', weight='bold', pad=14)
ax.text(0,1.01,'NYC police-reported crashes, Jul 1 2012–Jun 11 2026',transform=ax.transAxes,fontsize=9,color='#555555')
ax.text(0,-.21,'Rates are normalized for the 11-hour vs 13-hour time windows.\nClock-hours are not a measure of street-user exposure.',transform=ax.transAxes,fontsize=9,color='#555555',va='top')
ax.set_ylim(0,max(vals)*1.22)
fig.tight_layout()
fig.savefig(out/'option_1.png',dpi=180,bbox_inches='tight')
plt.close(fig)
print(values.to_string(index=False))
PY
# bash
python - <<'PY'
import json
from pathlib import Path
p=Path('out/options.json')
data=json.loads(p.read_text())
assert [x['id'] for x in data['options']] == [1,2]
assert abs(sum(x['probability'] for x in data['options'])-1) < 1e-9
for i in (1,2):
    assert Path(f'out/option_{i}.png').is_file()
    assert Path(f'out/values_{i}.csv').is_file()
print('Valid JSON; probabilities sum to', sum(x['probability'] for x in data['options']))
for path in ['out/options.json','out/option_1.png','out/values_1.csv','out/option_2.png','out/values_2.csv']:
    print(path, Path(path).stat().st_size, 'bytes')
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