You are grading ONE output of a data-analysis agent against a written standard. The chart is attached as an image.
Judge from the materials below only. Do not fix anything, do not redo the analysis. For each item answer PASS or FAIL
(NA if the item does not apply to this output) and quote the sentence, number or chart element that decides it.
Be strict: a limitation that matters but is not stated is a FAIL on the item that asks for it.

QUESTION ASKED: K2
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Annual police-reported crash count
denominator: None; raw counts within each calendar year
grouping: Calendar year × weekday (2013–2025)
chart_type: Heatmap
probability: 0.25
WRITTEN ANSWER:
Friday had the most crashes in each of the 13 years from 2013 through 2025, and Sunday had the fewest in each year.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,weekday,crash_count
2013,Monday,29454
2014,Monday,29963
2015,Monday,31061
2016,Monday,32291
2017,Monday,33049
2018,Monday,33594
2019,Monday,30478
2020,Monday,15846
2021,Monday,15567
2022,Monday,14362
2023,Monday,13665
2024,Monday,13120
2025,Monday,12068
2013,Tuesday,30216
2014,Tuesday,30791
2015,Tuesday,32685
2016,Tuesday,34314
2017,Tuesday,33721
2018,Tuesday,34469
2019,Tuesday,31833
2020,Tuesday,16184
2021,Tuesday,15674
2022,Tuesday,14547
2023,Tuesday,13653
2024,Tuesday,13270
2025,Tuesday,12131
2013,Wednesday,29395
2014,Wednesday,30588
2015,Wednesday,32405
2016,Wednesday,34236
2017,Wednesday,33856
2018,Wednesday,33916
2019,Wednesday,30932
2020,Wednesday,16258
2021,Wednesday,15794
2022,Wednesday,14791
2023,Wednesday,13691
2024,Wednesday,12925
2025,Wednesday,12324
2013,Thursday,29727
2014,Thursday,30778
2015,Thursday,32909
2016,Thursday,34682
2017,Thursday,35356
2018,Thursday,35585
2019,Thursday,31693
2020,Thursday,16817
2021,Thursday,16078
2022,Thursday,15069
2023,Thursday,14001
2024,Thursday,13135
2025,Thursday,12546
2013,Friday,33111
2014,Friday,32417
2015,Friday,34408
2016,Friday,37147
2017,Friday,36921
2018,Friday,36928
2019,Friday,33724
2020,Friday,18104
... (truncated)

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c "import duckdb; p='data/crashes.parquet'; c=duckdb.connect(); print(c.execute(\"select min(crash_date), max(crash_date), count(*) from read_parquet(?)\", [p]).fetchall()); print(c.execute(\"select dayname(crash_date), count(*) from read_parquet(?) where crash_date >= date '2013-01-01' and crash_date < date '2026-01-01' group by 1 order by count(*) desc\", [p]).fetchall()); print(c.execute(\"select min(crash_date), max(crash_date), count(*) from read_parquet(?) where crash_date >= date '2013-01-01' and crash_date < date '2026-01-01'\", [p]).fetchall())"
# bash
ls .
# bash
python - <<'PY'
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

out = Path('out')
out.mkdir(exist_ok=True)
con = duckdb.connect()
source = 'data/crashes.parquet'
weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
base = con.execute("""
    SELECT crash_date,
           strftime(crash_date, '%A') AS weekday,
           count(*) AS crash_count
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY crash_date, weekday
""", [source]).df()
# Add zero-crash calendar days to ensure the per-weekday averages use the full calendar denominator.
calendar = pd.DataFrame({'crash_date': pd.date_range('2013-01-01', '2025-12-31', freq='D')})
calendar['weekday'] = calendar['crash_date'].dt.day_name()
daily = calendar.merge(base, on=['crash_date', 'weekday'], how='left').fillna({'crash_count': 0})
daily['year'] = daily['crash_date'].dt.year

counts = daily.groupby('weekday')['crash_count'].sum().reindex(weekdays).astype(int)
summary = pd.DataFrame({'weekday': weekdays, 'crash_count': counts.values})
summary.to_csv(out / 'values_1.csv', index=False)

fig, ax = plt.subplots(figsize=(10, 5.6))
bars = ax.bar(weekdays, counts.values, color='#4472C4')
ax.bar_label(bars, labels=[f'{v:,.0f}' for v in counts.values], padding=3, fontsize=8)
ax.set_title('NYC police-reported crashes by weekday, 2013–2025')
ax.set_ylabel('Crashes')
ax.set_xlabel('Day of week')
ax.set_ylim(0, max(counts.values) * 1.14)
ax.grid(axis='y', alpha=.25)
fig.tight_layout()
fig.savefig(out / 'option_1.png', dpi=180)
plt.close(fig)

share = counts / counts.sum() * 100
share_df = pd.DataFrame({'weekday': weekdays, 'crash_count': counts.values, 'share_percent': share.values})
share_df.to_csv(out / 'values_2.csv', index=False)
fig, ax = plt.subplots(figsize=(8.5, 7))
wedges, texts, autotexts = ax.pie(share.values, labels=weekdays, autopct='%1.1f%%', startangle=90,
                                   counterclock=False, pctdistance=.76,
                                   colors=sns.color_palette('pastel', 7),
                                   wedgeprops={'linewidth': 1, 'edgecolor': 'white'})
ax.set_title('Share of NYC police-reported crashes by weekday, 2013–2025')
ax.axis('equal')
fig.tight_layout()
fig.savefig(out / 'option_2.png', dpi=180)
plt.close(fig)

annual = daily.groupby(['year', 'weekday'])['crash_count'].sum().unstack(fill_value=0).reindex(columns=weekdays)
annual_long = annual.reset_index().melt(id_vars='year', var_name='weekday', value_name='crash_count')
annual_long.to_csv(out / 'values_3.csv', index=False)
fig, ax = plt.subplots(figsize=(10, 7))
sns.heatmap(annual[weekdays], cmap='YlOrRd', linewidths=.25, linecolor='white',
            cbar_kws={'label': 'Crashes in year'}, ax=ax)
ax.set_title('NYC crashes by weekday and year, 2013–2025')
ax.set_xlabel('Day of week')
ax.set_ylabel('Year')
ax.set_xticklabels(weekdays, rotation=35, ha='right')
ax.set_yticklabels(annual.index.astype(str), rotation=0)
fig.tight_layout()
fig.savefig(out / 'option_3.png', dpi=180)
plt.close(fig)

max_days = annual.idxmax(axis=1)
print('weekday_totals=', counts.to_dict())
print('total=', int(counts.sum()))
print('shares_percent=', share.round(3).to_dict())
print('annual_winner_counts=', max_days.value_counts().reindex(weekdays, fill_value=0).to_dict())
print('annual_winners=', max_days.to_dict())
print('daily_means=', (counts / calendar['weekday'].value_counts().reindex(weekdays)).round(1).to_dict())
PY
# bash
python - <<'PY'
import json
from pathlib import Path
import pandas as pd
out=Path('out')
opts=json.loads((out/'options.json').read_text())['options']
assert len(opts)==3
assert abs(sum(x['probability'] for x in opts)-1)<1e-9
for i in range(1,4):
    assert (out/f'option_{i}.png').is_file() and (out/f'values_{i}.csv').is_file()
v1=pd.read_csv(out/'values_1.csv')
v2=pd.read_csv(out/'values_2.csv')
v3=pd.read_csv(out/'values_3.csv')
assert int(v1.crash_count.sum())==2132218
assert v1.loc[v1.crash_count.idxmax(),'weekday']=='Friday'
assert v1.loc[v1.crash_count.idxmin(),'weekday']=='Sunday'
assert abs(v2.loc[v2.weekday.eq('Friday'),'share_percent'].iloc[0]-15.889557259154552)<1e-9
assert v3.groupby('year').apply(lambda g:g.loc[g.crash_count.idxmax(),'weekday'], include_groups=False).eq('Friday').all()
assert v3.groupby('year').apply(lambda g:g.loc[g.crash_count.idxmin(),'weekday'], include_groups=False).eq('Sunday').all()
print('JSON valid; probabilities sum to',sum(x['probability'] for x in opts))
print('All three chart/value pairs exist; total, share, and annual claims validated.')
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
- tr_TR01: If counts are pooled over 2013–2025, the output says that pre-2020 years dominate or that crash reporting changed in 2020.
- tr_DAYCOUNT: If per-day averages or 'X% fewer on <day>' comparisons are given, the arithmetic is right (e.g. Sunday has 24% fewer than the mean weekday, Friday 32% more) and unequal day counts (678/679) are handled or noted.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.