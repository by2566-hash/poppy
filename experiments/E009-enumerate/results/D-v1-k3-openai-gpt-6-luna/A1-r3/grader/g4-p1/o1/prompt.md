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

DATA FACTS (pinned snapshot):
- The file covers 2012-07-01 to 2026-06-11; 2013-2025 are complete calendar years; 2026 is partial (to June 11).
- borough is NULL for about 20-38% of crashes in every year (TR05): a borough filter silently drops them.
- number_of_persons_killed is NULL in most May-2026 and all June-2026 rows (TR08); 2013-2025 killed counts have no NULLs.
- crash_time has no NULL rows. Reported crash counts fall sharply in 2020 (TR01): a per-reported-crash rate or a pooled count COMPARED ACROSS YEARS spanning 2020 needs a caveat; a comparison between groups within one pooled window (e.g. day vs night) does not (decided 2026-11-04).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: Has road safety for pedestrians in Brooklyn gotten better since 2013? Make a chart suitable for a local news story and summarize the findings.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Annual count of pedestrians injured in reported crashes
denominator: None; count
grouping: Brooklyn by calendar year (2013–2025)
chart_type: Line chart
probability: 0.4
WRITTEN ANSWER:
Reported pedestrian injuries were lower in 2025 than in 2013 (2,835 vs. 3,641; down 22%), although they rose from 1,781 in 2020. The data cannot establish whether risk per walking trip improved because it contains no pedestrian-exposure measure.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,pedestrians_injured
2013,3641.0
2014,3349.0
2015,3029.0
2016,2917.0
2017,2663.0
2018,2785.0
2019,2700.0
2020,1781.0
2021,1905.0
2022,2275.0
2023,2385.0
2024,2645.0
2025,2835.0

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python -c 'import duckdb; p="data/crashes.parquet"; print(duckdb.sql(f"SELECT min(crash_date), max(crash_date), count(*) FROM read_parquet(\u0027{p}\u0027)").fetchall()); print(duckdb.sql(f"SELECT borough, count(*) FROM read_parquet(\u0027{p}\u0027) GROUP BY borough ORDER BY count(*) DESC LIMIT 10").fetchall())'
# bash
python -c 'import duckdb; con=duckdb.connect(); con.execute("CREATE VIEW crashes AS SELECT * FROM read_parquet(\u0027data/crashes.parquet\u0027)"); print(con.execute("SELECT year(crash_date) AS year, count(*) AS crashes, sum(number_of_pedestrians_injured) AS ped_injured, sum(number_of_pedestrians_killed) AS ped_killed, sum(number_of_pedestrians_injured + number_of_pedestrians_killed) AS ped_casualties, count(*) FILTER (WHERE number_of_pedestrians_injured > 0 OR number_of_pedestrians_killed > 0) AS ped_casualty_crashes FROM crashes WHERE borough = \u0027BROOKLYN\u0027 AND crash_date >= DATE \u00272013-01-01\u0027 AND crash_date < DATE \u00272026-01-01\u0027 GROUP BY year ORDER BY year").fetchdf().to_string(index=False))'
# bash
python -c 'import duckdb; print(duckdb.sql("SELECT count(*) FILTER (WHERE number_of_pedestrians_injured IS NULL) AS missing_injured, count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS missing_killed FROM read_parquet(\u0027data/crashes.parquet\u0027) WHERE borough=\u0027BROOKLYN\u0027 AND crash_date >= DATE \u00272013-01-01\u0027 AND crash_date < DATE \u00272026-01-01\u0027").fetchall())'
# bash
python - <<'PY'
import os
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

os.makedirs('out', exist_ok=True)
con = duckdb.connect()
query = """
SELECT year(crash_date) AS year,
       count(*) AS brooklyn_crashes,
       sum(number_of_pedestrians_injured) AS pedestrians_injured,
       sum(number_of_pedestrians_killed) AS pedestrians_killed,
       sum(number_of_pedestrians_injured + number_of_pedestrians_killed) AS pedestrian_casualties,
       count(*) FILTER (WHERE number_of_pedestrians_injured > 0 OR number_of_pedestrians_killed > 0) AS pedestrian_casualty_crashes
FROM read_parquet('data/crashes.parquet')
WHERE borough = 'BROOKLYN'
  AND crash_date >= DATE '2013-01-01'
  AND crash_date < DATE '2026-01-01'
GROUP BY year
ORDER BY year
"""
df = con.execute(query).fetchdf()
df['pedestrian_casualty_crash_pct'] = 100 * df['pedestrian_casualty_crashes'] / df['brooklyn_crashes']

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.titleweight': 'bold'})
navy, teal, orange = '#17324d', '#168c8c', '#d35d35'
source = 'Source: NYC police-reported motor vehicle crashes | Brooklyn | complete years 2013–2025'
foot = 'Crash records do not measure walking trips or pedestrian volume.'

def frame(title, ylabel, filename, note, color=teal):
    fig, ax = plt.subplots(figsize=(10, 5.6), constrained_layout=True)
    ax.set_facecolor('#f7f8fa')
    fig.patch.set_facecolor('white')
    ax.set_title(title, loc='left', fontsize=16, color=navy, pad=17)
    ax.set_ylabel(ylabel, color=navy)
    ax.set_xlabel('Calendar year', color=navy)
    ax.set_xticks(df['year'])
    ax.tick_params(axis='x', rotation=0, labelsize=9)
    ax.grid(axis='y', color='#d9dfe5', linewidth=.8)
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.spines['bottom'].set_color('#9aa7b2')
    ax.tick_params(axis='y', length=0, colors=navy)
    ax.tick_params(axis='x', length=0, colors=navy)
    fig.text(.01, -.015, source + '\n' + note + ' ' + foot, fontsize=8, color='#4b5965')
    return fig, ax

# Option 1: annual pedestrian injury count
fig, ax = frame('Pedestrian injuries fell from 2013, then rose', 'Pedestrians injured (count)', 'option_1.png', 'Annual count of pedestrians recorded injured.')
y = df['pedestrians_injured']
ax.plot(df['year'], y, color=teal, linewidth=3, marker='o', markersize=5)
ax.set_ylim(0, 4200)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{int(v):,}'))
ax.annotate(f'{int(y.iloc[0]):,}', (df['year'].iloc[0], y.iloc[0]), xytext=(5, 10), textcoords='offset points', color=navy, fontweight='bold')
ax.annotate(f'{int(y.iloc[-1]):,}', (df['year'].iloc[-1], y.iloc[-1]), xytext=(-35, 10), textcoords='offset points', color=navy, fontweight='bold')
fig.savefig('out/option_1.png', dpi=180, bbox_inches='tight')
plt.close(fig)
df[['year', 'pedestrians_injured']].to_csv('out/values_1.csv', index=False)

# Option 2: annual pedestrian fatality count
fig, ax = frame('Pedestrian deaths remain volatile—and above 2013', 'Pedestrians killed (count)', 'option_2.png', 'Annual count of pedestrians recorded killed.', color=orange)
y = df['pedestrians_killed']
ax.bar(df['year'], y, color=orange, width=.68)
ax.set_ylim(0, 55)
ax.set_yticks([0, 10, 20, 30, 40, 50])
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{int(v)}'))
ax.annotate(f'{int(y.iloc[0])}', (df['year'].iloc[0], y.iloc[0]), xytext=(0, 7), textcoords='offset points', ha='center', color=navy, fontweight='bold')
ax.annotate(f'{int(y.iloc[-1])}', (df['year'].iloc[-1], y.iloc[-1]), xytext=(0, 7), textcoords='offset points', ha='center', color=navy, fontweight='bold')
fig.savefig('out/option_2.png', dpi=180, bbox_inches='tight')
plt.close(fig)
df[['year', 'pedestrians_killed']].to_csv('out/values_2.csv', index=False)

# Option 3: share of all police-reported Brooklyn crashes with a pedestrian casualty
fig, ax = frame('A larger share of Brooklyn crashes involved a pedestrian casualty', 'Crashes with pedestrian injury or death (% of Brooklyn crashes)', 'option_3.png', 'Share = crashes with ≥1 pedestrian injured or killed ÷ all Brooklyn crash records.', color=navy)
y = df['pedestrian_casualty_crash_pct']
ax.plot(df['year'], y, color=navy, linewidth=3, marker='o', markersize=5)
ax.set_ylim(0, 14)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f'{v:.0f}%'))
ax.annotate(f'{y.iloc[0]:.1f}%', (df['year'].iloc[0], y.iloc[0]), xytext=(5, 10), textcoords='offset points', color=navy, fontweight='bold')
ax.annotate(f'{y.iloc[-1]:.1f}%', (df['year'].iloc[-1], y.iloc[-1]), xytext=(-35, 10), textcoords='offset points', color=navy, fontweight='bold')
fig.savefig('out/option_3.png', dpi=180, bbox_inches='tight')
plt.close(fig)
df[['year', 'pedestrian_casualty_crashes', 'brooklyn_crashes', 'pedestrian_casualty_crash_pct']].to_csv('out/values_3.csv', index=False, float_format='%.4f')

print(df.to_string(index=False))
print('\nEndpoint changes:')
for col in ['pedestrians_injured', 'pedestrians_killed', 'pedestrian_casualty_crash_pct']:
    a, b = df[col].iloc[0], df[col].iloc[-1]
    print(f'{col}: 2013={a:.4f}, 2025={b:.4f}, change={(b-a)/a*100:.1f}%')
PY
# bash
python -c 'import json, pathlib; p=pathlib.Path("out"); d=json.loads((p/"options.json").read_text()); assert [o["id"] for o in d["options"]] == [1,2,3]; assert abs(sum(o["probability"] for o in d["options"])-1)<1e-9; files=[p/f"option_{i}.png" for i in range(1,4)]+[p/f"values_{i}.csv" for i in range(1,4)]; assert all(f.is_file() and f.stat().st_size for f in files); print("JSON valid; probabilities sum to", sum(o["probability"] for o in d["options"])); print("All six chart/value outputs exist and are nonempty.")'

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR05: If a borough filter (borough = 'BROOKLYN') is used, the output discloses that crashes with no borough recorded (19.9–38.1% per year) are excluded.
- tr_TR11: The output does not call Brooklyn 'safer' or 'less safe' from counts alone without saying that there is no pedestrian exposure measure.
- tr_TR01: If a per-crash rate spanning 2020 is shown, the output caveats the 2020 change in crash recording.
- tr_TR15: Claims about pedestrian deaths changing are qualified by the small counts (about 30–39 per year).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.