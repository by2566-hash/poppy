Revise an analysis based on a reviewer's numbered issues.

Question:
How are NYC crashes distributed across the days of the week, 2013 to 2025?

Data description:
Data file: ./data/crashes.parquet (one row per police-reported motor vehicle crash in New York City; read it with DuckDB or pandas).
Columns: crash_date (DATE), crash_time (TIME), borough (VARCHAR, may be NULL), zip_code, latitude, longitude,
on_street_name, cross_street_name, number_of_persons_injured (INT), number_of_persons_killed (INT),
number_of_pedestrians_injured, number_of_pedestrians_killed, number_of_cyclist_injured, number_of_cyclist_killed,
number_of_motorist_injured, number_of_motorist_killed, contributing_factor_vehicle_1 ... contributing_factor_vehicle_5 (VARCHAR),
collision_id (BIGINT), vehicle_type_code1 ... vehicle_type_code5 (VARCHAR).
Python 3 with duckdb, pandas and matplotlib is available.

Current code:
python3 -c "import duckdb, pandas, matplotlib; print(duckdb.__version__, pandas.__version__, matplotlib.__version__)"

python3 -c "
import duckdb
con = duckdb.connect()
print(con.sql(\"DESCRIBE SELECT * FROM './data/crashes.parquet'\").df().to_string())
print(con.sql(\"SELECT COUNT(*) n, MIN(crash_date) mn, MAX(crash_date) mx FROM './data/crashes.parquet'\").df())
"

mkdir -p ./out && python3 << 'EOF'
import duckdb, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

con = duckdb.connect()
q = """
SELECT strftime(crash_date, '%w') AS dow_num,
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
df = con.sql(q).df()
order = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
df['dow_num'] = df['dow_num'].astype(int)
df = df.sort_values('dow_num').reset_index(drop=True)
df['day_of_week'] = pd.Categorical(df['day_of_week'], categories=order, ordered=True)
df = df.sort_values('dow_num').reset_index(drop=True)
total = df['crashes'].sum()
df['share_pct'] = (df['crashes']/total*100).round(2)
# average per day of week occurrence over the period
n_days = con.sql("""SELECT count(DISTINCT crash_date) FROM './data/crashes.parquet'
                    WHERE crash_date BETWEEN DATE '2013-01-01' AND DATE '2025-12-31'""").fetchone()[0]
# count occurrences of each weekday in range
occ = con.sql("""
SELECT extract(isodow from d)::INT AS dow, count(*) AS n
FROM (SELECT generate_date(DATE '2013-01-01', DATE '2025-12-31', 1) AS d)
GROUP BY 1 ORDER BY 1
""").df()
df = df.merge(occ.rename(columns={'dow':'dow_num','n':'days_with_this_weekday'}), on='dow_num', how='left')
df['avg_crashes_per_day'] = (df['crashes']/df['days_with_this_weekday']).round(1)
df = df[['day_of_week','dow_num','crashes','share_pct','days_with_this_weekday','avg_crashes_per_day']]
print(df.to_string(index=False))
print('total', total, 'distinct dates', n_days)
df.to_csv('./out/values.csv', index=False)

fig, ax = plt.subplots(figsize=(10,6))
colors = ['#4C72B0']*5 + ['#DD8452']*2
bars = ax.bar(df['day_of_week'].astype(str), df['crashes'], color=colors, edgecolor='black', linewidth=0.6)
for b, v, p in zip(bars, df['crashes'], df['share_pct']):
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+ max(df['crashes'])*0.012,
            f'{v:,.0f}\n({p:.1f}%)', ha='center', va='bottom', fontsize=9)
ax.set_title('NYC motor vehicle crashes by day of the week, 2013–2025', fontsize=14, fontweight='bold')
ax.set_xlabel('Day of week')
ax.set_ylabel('Number of crashes')
ax.set_ylim(0, max(df['crashes'])*1.18)
ax.grid(axis='y', alpha=0.3)
ax.set_axisbelow(True)
# legend for color groups
from matplotlib.patches import Patch
ax.legend(handles=[Patch(facecolor='#4C72B0', edgecolor='black', label='Weekdays (Mon–Fri)'),
                   Patch(facecolor='#DD8452', edgecolor='black', label='Weekend (Sat–Sun)')],
          loc='upper left', frameon=False)
ax.annotate(f'Total crashes 2013–2025: {total:,}', xy=(0.99, 0.97), xycoords='axes fraction',
            ha='right', va='top', fontsize=9, color='#444444')
fig.tight_layout()
fig.savefig('./out/initial.png', dpi=150)
print('saved')
EOF

python3 << 'EOF'
import duckdb, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

con = duckdb.connect()
q = """
SELECT CAST(strftime(crash_date, '%w') AS INT) AS dow_num,
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
df.to_csv('./out/values.csv', index=False)

fig, ax = plt.subplots(figsize=(10,6))
colors = ['#4C72B0']*5 + ['#DD8452']*2
bars = ax.bar(df['day_of_week'].astype(str), df['crashes'], color=colors, edgecolor='black', linewidth=0.6)
for b, v, p in zip(bars, df['crashes'], df['share_pct']):
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+max(df['crashes'])*0.012,
            f'{v:,.0f}\n({p:.1f}%)', ha='center', va='bottom', fontsize=9)
ax.set_title('NYC motor vehicle crashes by day of the week, 2013–2025', fontsize=14, fontweight='bold')
ax.set_xlabel('Day of week')
ax.set_ylabel('Number of crashes')
ax.set_ylim(0, max(df['crashes'])*1.20)
ax.grid(axis='y', alpha=0.3); ax.set_axisbelow(True)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(facecolor='#4C72B0', edgecolor='black', label='Weekdays (Mon–Fri)'),
                   Patch(facecolor='#DD8452', edgecolor='black', label='Weekend (Sat–Sun)')],
          loc='upper left', frameon=False)
ax.annotate(f'Total crashes 2013–2025: {total:,}', xy=(0.99, 0.97), xycoords='axes fraction',
            ha='right', va='top', fontsize=9, color='#444444')
fig.tight_layout()
fig.savefig('./out/initial.png', dpi=150)
print('saved')
EOF
ls -la ./out

python3 << 'EOF'
import duckdb, pandas as pd, matplotlib
... [truncated, 2660 more characters]

Current plotted values (values.csv):
day_of_week,dow_num,crashes,share_pct,days_with_this_weekday,avg_crashes_per_day
Mon,1,304518,14.28,678,449.1
Tue,2,313488,14.7,679,461.7
Wed,3,311111,14.59,679,458.2
Thu,4,318376,14.93,678,469.6
Fri,5,338800,15.89,678,499.7
Sat,6,288381,13.52,678,425.3
Sun,7,257544,12.08,678,379.9


Current written answer:
Across 2013–2025 NYC logged 2,132,218 crashes, and they are not evenly spread over the week — weekday volume is consistently higher than weekend. Friday is the peak day (338,800 crashes, 15.9% of the total, ~500/day), followed by Thursday (318,376; 14.9%), Tuesday (313,488; 14.7%), Wednesday (311,111; 14.6%) and Monday (304,518; 14.3%); Monday–Friday together account for 74.4% of all crashes. Saturday falls to 288,381 (13.5%, ~425/day) and Sunday is the lowest at 257,544 (12.1%, ~380/day) — about 32% fewer crashes on Sundays than Fridays, consistent with lighter traffic and fewer commuters on weekends.

Reviewer's issues:
1. Written answer: "about 32% fewer crashes on Sundays than Fridays" is wrong arithmetic. Friday − Sunday = 338,800 − 257,544 = 81,256, which is 24.0% of Friday's 338,800, so Sundays have about 24% fewer crashes than Fridays. (32% is roughly the reverse comparison: Fridays have ~31.5% more than Sundays; that is not what the sentence says.)
2. Written answer: "consistent with lighter traffic and fewer commuters on weekends" asserts a cause (traffic volume, commuter counts) that the allowed data (one row per crash) contains no variable for; it cannot support this explanation. Remove it or mark it explicitly as speculation.

Instructions:
- Go through the issues one by one. For each, either fix it, or check it and keep the original if the reviewer was wrong, or state that it cannot be addressed with this data.
- Change nothing the reviewer did not flag: same data, filters, numbers, chart type and wording of the written answer, unless fixing an issue requires it.
- Write and run the revised code yourself. Save the chart to ./out/revised.png and the plotted data to ./out/revised_values.csv, even if only the written answer changes.
- When finished, reply in exactly this format, with one line per issue in the reviewer's numbering:
CHANGES:
1. <fixed | kept | cannot address>: <what you changed, or why you kept it or could not address it>
2. ...
ANSWER: <the revised short written answer, based on the numbers you computed>
