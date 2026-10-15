import duckdb, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

con = duckdb.connect()
q = """
SELECT CAST(extract(isodow from crash_date) AS INT) AS dow_num,
       CASE extract(isodow from crash_date)
         WHEN 1 THEN 'Mon' WHEN 2 THEN 'Tue' WHEN 3 THEN 'Wed'
         WHEN 4 THEN 'Thu' WHEN 5 THEN 'Fri' WHEN 6 THEN 'Sat' WHEN 7 THEN 'Sun'
       END AS day_of_week,
       count(*) AS crashes
FROM './data/crashes.parquet'
WHERE crash_date BETWEEN DATE '2013-01-01' AND DATE '2025-12-31'
  AND crash_date IS NOT NULL
GROUP BY 1, 2
"""
df = con.sql(q).df().sort_values('dow_num').reset_index(drop=True)
total = int(df['crashes'].sum())
df['share_pct'] = (df['crashes']/total*100).round(2)

occ = con.sql("""
SELECT extract(isodow from CAST(d AS DATE))::INT AS dow, count(*) AS n
FROM generate_series(DATE '2013-01-01', DATE '2025-12-31', INTERVAL 1 DAY) AS t(d)
GROUP BY 1 ORDER BY 1
""").df().rename(columns={'dow':'dow_num','n':'days_with_this_weekday'})
df = df.merge(occ, on='dow_num', how='left')
df['avg_crashes_per_day'] = (df['crashes']/df['days_with_this_weekday']).round(1)
df = df[['day_of_week','dow_num','crashes','share_pct','days_with_this_weekday','avg_crashes_per_day']]
print(df.to_string(index=False))
print('total', total)
df.to_csv('./out/revised_values.csv', index=False)

fri = int(df.loc[df.day_of_week == 'Fri', 'crashes'].iloc[0])
sun = int(df.loc[df.day_of_week == 'Sun', 'crashes'].iloc[0])
print('Sun fewer than Fri %:', round((fri-sun)/fri*100, 1),
      '| Fri more than Sun %:', round((fri-sun)/sun*100, 1))

fig, ax = plt.subplots(figsize=(10, 6))
colors = ['#4C72B0']*5 + ['#DD8452']*2
bars = ax.bar(df['day_of_week'].astype(str), df['crashes'], color=colors,
              edgecolor='black', linewidth=0.6)
for b, v, p in zip(bars, df['crashes'], df['share_pct']):
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+max(df['crashes'])*0.012,
            f'{v:,.0f}\n({p:.1f}%)', ha='center', va='bottom', fontsize=9)
ax.set_title('NYC motor vehicle crashes by day of the week, 2013–2025',
             fontsize=14, fontweight='bold')
ax.set_xlabel('Day of week')
ax.set_ylabel('Number of crashes')
ax.set_ylim(0, max(df['crashes'])*1.20)
ax.grid(axis='y', alpha=0.3)
ax.set_axisbelow(True)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(facecolor='#4C72B0', edgecolor='black', label='Weekdays (Mon–Fri)'),
                   Patch(facecolor='#DD8452', edgecolor='black', label='Weekend (Sat–Sun)')],
          loc='upper left', frameon=False)
ax.annotate(f'Total crashes 2013–2025: {total:,}', xy=(0.99, 0.97),
            xycoords='axes fraction', ha='right', va='top', fontsize=9, color='#444444')
fig.tight_layout()
fig.savefig('./out/revised.png', dpi=150)
print('saved')
