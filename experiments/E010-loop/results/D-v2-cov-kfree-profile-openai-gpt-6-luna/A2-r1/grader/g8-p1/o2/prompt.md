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
metric: Share of crashes with at least one person injured
denominator: Crashes in each period with a non-NULL number_of_persons_injured
grouping: Day 06:00–18:59 versus night 19:00–05:59
chart_type: Two-bar comparison
probability: 0.5
WRITTEN ANSWER:
Among crashes with a reported injury count, 28.20% at night involved at least one injury versus 23.10% during daytime, indicating greater injury involvement at night conditional on a reported crash. This addresses whether a reported crash is more likely to involve an injury at night, conditional on a crash being reported. The share is 28.20% at night and 23.10% by day. Comparing injury involvement among crashes is a defensible severity proxy, but it does not establish the risk of crashing or being injured per trip or mile. It excludes 18 rows with NULL injury counts (14 of 1,594,921 daytime crashes, 0.0009%, and 4 of 674,266 nighttime crashes, 0.0006%); the included partial years leave 49.73% of 2012 and 55.62% of 2026 calendar days outside the file.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
period,crashes_with_reported_injury_count,crashes_with_one_or_more_injuries,crashes_with_null_injury_count_excluded,all_crashes_in_period,injury_crash_share_percent,excluded_share_of_period_percent
Day (06:00–18:59),1594907,368455,14,1594921,23.10197397,0.00087779
Night (19:00–05:59),674262,190148,4,674266,28.20090707,0.00059324

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
ls out
# bash
python - <<'PY'
import duckdb, pandas as pd, matplotlib.pyplot as plt
from pathlib import Path
from datetime import date

base = Path('.')
out = base / 'out'
out.mkdir(exist_ok=True)
con = duckdb.connect()
path = str(base / 'data' / 'crashes.parquet')

# Partitions are based on the recorded crash clock time: night 19:00–05:59; day 06:00–18:59.
raw = con.execute(f"""
    SELECT crash_date, EXTRACT(hour FROM crash_time)::INTEGER AS hour,
           number_of_persons_injured
    FROM read_parquet('{path}')
""").df()
raw['period'] = raw['hour'].map(lambda h: 'Night (19:00–05:59)' if h >= 19 or h < 6 else 'Day (06:00–18:59)')
order = ['Day (06:00–18:59)', 'Night (19:00–05:59)']
raw['period'] = pd.Categorical(raw['period'], categories=order, ordered=True)

n_dates = (raw['crash_date'].max() - raw['crash_date'].min()).days + 1
hours_per_period = {'Day (06:00–18:59)': 13, 'Night (19:00–05:59)': 11}

# Option 1: average reported crashes per available clock-hour across the observed calendar span.
crash_counts = raw.groupby('period', observed=False).size().reindex(order, fill_value=0)
values1 = pd.DataFrame({'period': order})
values1['crashes'] = [int(crash_counts[p]) for p in order]
values1['observed_calendar_days'] = n_dates
values1['clock_hours_per_day'] = [hours_per_period[p] for p in order]
values1['observed_clock_hours'] = values1['observed_calendar_days'] * values1['clock_hours_per_day']
values1['average_crashes_per_clock_hour'] = values1['crashes'] / values1['observed_clock_hours']
values1.to_csv(out / 'values_1.csv', index=False, float_format='%.8f')

fig, ax = plt.subplots(figsize=(8, 5))
colors = ['#4C78A8', '#F58518']
bars = ax.bar(['Day\n06:00–18:59', 'Night\n19:00–05:59'], values1['average_crashes_per_clock_hour'], color=colors, width=.58)
ax.bar_label(bars, fmt='%.2f', padding=5, fontsize=11)
ax.set_ylabel('Average police-reported crashes per clock-hour')
ax.set_title('NYC crash reports by time of day')
ax.text(.5, -.22, 'Average over all calendar dates in the file; clock-hours are not adjusted for traffic volume.', transform=ax.transAxes, ha='center', fontsize=9, color='#555555')
ax.spines[['top', 'right']].set_visible(False)
ax.set_ylim(0, max(values1['average_crashes_per_clock_hour']) * 1.2)
fig.tight_layout()
fig.savefig(out / 'option_1.png', dpi=180, bbox_inches='tight')
plt.close(fig)

# Option 2: among crashes with a reported injury count, share with at least one person injured.
valid = raw[raw['number_of_persons_injured'].notna()].copy()
rows = []
for p in order:
    allp = raw[raw['period'] == p]
    vp = valid[valid['period'] == p]
    rows.append({
        'period': p,
        'crashes_with_reported_injury_count': int(len(vp)),
        'crashes_with_one_or_more_injuries': int((vp['number_of_persons_injured'] > 0).sum()),
        'crashes_with_null_injury_count_excluded': int(allp['number_of_persons_injured'].isna().sum()),
        'all_crashes_in_period': int(len(allp)),
        'injury_crash_share_percent': float((vp['number_of_persons_injured'] > 0).mean() * 100),
        'excluded_share_of_period_percent': float(allp['number_of_persons_injured'].isna().mean() * 100),
    })
values2 = pd.DataFrame(rows)
values2.to_csv(out / 'values_2.csv', index=False, float_format='%.8f')

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(['Day\n06:00–18:59', 'Night\n19:00–05:59'], values2['injury_crash_share_percent'], color=colors, width=.58)
ax.bar_label(bars, fmt='%.2f%%', padding=5, fontsize=11)
ax.set_ylabel('Crashes with ≥1 person injured (%)')
ax.set_title('Injury involvement among NYC crash reports')
ax.text(.5, -.22, 'Denominator: crashes with a non-NULL persons-injured count; not adjusted for traffic exposure.', transform=ax.transAxes, ha='center', fontsize=9, color='#555555')
ax.spines[['top', 'right']].set_visible(False)
ax.set_ylim(0, max(values2['injury_crash_share_percent']) * 1.2)
fig.tight_layout()
fig.savefig(out / 'option_2.png', dpi=180, bbox_inches='tight')
plt.close(fig)

print('date_min', raw['crash_date'].min(), 'date_max', raw['crash_date'].max(), 'dates', n_dates, 'rows', len(raw))
print('option 1')
print(values1.to_string(index=False))
print('option 2')
print(values2.to_string(index=False))
print('injury null overall', int(raw['number_of_persons_injured'].isna().sum()), 'share percent', raw['number_of_persons_injured'].isna().mean()*100)
for yr in [2012, 2026]:
    y = raw[raw.crash_date.map(lambda d: d.year == yr)]
    print('injury null by year', yr, int(y.number_of_persons_injured.isna().sum()), len(y), y.number_of_persons_injured.isna().mean()*100)

# Calendar share outside the supplied range for the only partial years.
for yr, first, last in [(2012, date(2012,7,1), date(2012,12,31)), (2026, date(2026,1,1), date(2026,6,11))]:
    total = (date(yr,12,31) - date(yr,1,1)).days + 1
    covered = (last - first).days + 1
    print('calendar coverage', yr, 'covered_days', covered, 'year_days', total, 'left_out_percent', (1-covered/total)*100)
PY
# bash
python - <<'PY'
import json
from pathlib import Path
p = Path('out')
obj = json.loads((p / 'options.json').read_text())
assert [x['id'] for x in obj['options']] == [1, 2]
assert abs(sum(x['probability'] for x in obj['options']) - 1) < 1e-9
for name in ['option_1.png', 'values_1.csv', 'option_2.png', 'values_2.csv', 'options.json']:
    q = p / name
    assert q.exists() and q.stat().st_size > 0, name
    print(name, q.stat().st_size)
print('options JSON valid; probabilities sum to', sum(x['probability'] for x in obj['options']))
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