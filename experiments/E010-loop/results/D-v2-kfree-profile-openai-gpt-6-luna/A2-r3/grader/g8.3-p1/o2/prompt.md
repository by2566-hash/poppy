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
metric: Share of crashes with at least one person killed
denominator: All police-reported crashes in the time period
grouping: Night (8pm–5:59am) versus day (6am–7:59pm)
chart_type: Bar chart
probability: 0.35
WRITTEN ANSWER:
The data cannot determine per-trip nighttime danger, but fatal crashes made up 0.290% of night crashes versus 0.108% of daytime crashes. This framing answers whether a reported crash was more likely to be fatal at night, and the chart shows a larger fatal-crash share at night. Fatality is a clear severe outcome and the denominator is all reported crashes in each period, but the comparison does not measure risk per trip or mile without exposure data.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
period,crashes,fatal_crashes,fatal_crash_percent
Day (6am–7:59pm),1710183,1847,0.10800014
Night (8pm–5:59am),559004,1622,0.29015893

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
ls out
# bash
python3 -c "import duckdb, pandas, matplotlib; print('duckdb', duckdb.__version__)"
# bash
python3 - <<'PY'
import duckdb
p='data/crashes.parquet'
c=duckdb.connect()
print(c.execute(f"""
WITH x AS (
 SELECT CASE WHEN hour(crash_time) >= 20 OR hour(crash_time) < 6 THEN 'Night (8pm–5:59am)' ELSE 'Day (6am–7:59pm)' END AS period,
        number_of_persons_injured > 0 OR number_of_persons_killed > 0 AS any_casualty,
        number_of_persons_killed > 0 AS fatal
 FROM read_parquet('{p}')
)
SELECT period, count(*) crashes,
       count(*) FILTER (WHERE any_casualty) casualty_crashes,
       round(100.0 * count(*) FILTER (WHERE any_casualty) / count(*), 3) casualty_pct,
       count(*) FILTER (WHERE fatal) fatal_crashes,
       round(100.0 * count(*) FILTER (WHERE fatal) / count(*), 4) fatal_pct
FROM x GROUP BY period ORDER BY period
""").df().to_string(index=False))
print('\nhourly')
print(c.execute(f"""
SELECT hour(crash_time) hour,
       count(*) crashes,
       round(count(*)::DOUBLE / (SELECT count(DISTINCT crash_date) FROM read_parquet('{p}')), 3) avg_crashes_per_calendar_day
FROM read_parquet('{p}') GROUP BY hour ORDER BY hour
""").df().to_string(index=False))
print('\ndates', c.execute(f"SELECT min(crash_date), max(crash_date), count(distinct crash_date) FROM read_parquet('{p}')").fetchone())
PY
# bash
python3 - <<'PY'
import duckdb
p='data/crashes.parquet'
c=duckdb.connect()
print(c.execute(f"""
SELECT hour(crash_time) AS hour_of_day,
       count(*) AS crashes,
       round(count(*)::DOUBLE / (SELECT count(DISTINCT crash_date) FROM read_parquet('{p}')), 3) AS avg_crashes_per_calendar_day
FROM read_parquet('{p}') GROUP BY hour_of_day ORDER BY hour_of_day
""").df().to_string(index=False))
print('dates', c.execute(f"SELECT min(crash_date), max(crash_date), count(distinct crash_date) FROM read_parquet('{p}')").fetchone())
PY
# bash
python3 - <<'PY'
from pathlib import Path
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

base = Path('.')
out = base / 'out'
out.mkdir(exist_ok=True)
source = (base / 'data' / 'crashes.parquet').as_posix()
con = duckdb.connect()
periods = con.execute(f"""
WITH crashes AS (
  SELECT CASE WHEN hour(crash_time) >= 20 OR hour(crash_time) < 6
              THEN 'Night (8pm–5:59am)' ELSE 'Day (6am–7:59pm)' END AS period,
         number_of_persons_injured > 0 OR number_of_persons_killed > 0 AS any_casualty,
         number_of_persons_killed > 0 AS fatal
  FROM read_parquet('{source}')
)
SELECT period, count(*) AS crashes,
       count(*) FILTER (WHERE any_casualty) AS casualty_crashes,
       count(*) FILTER (WHERE fatal) AS fatal_crashes
FROM crashes GROUP BY period
""").df()
periods['period'] = pd.Categorical(periods['period'], ['Day (6am–7:59pm)', 'Night (8pm–5:59am)'], ordered=True)
periods = periods.sort_values('period').reset_index(drop=True)
periods['casualty_crash_percent'] = periods['casualty_crashes'] / periods['crashes'] * 100
periods['fatal_crash_percent'] = periods['fatal_crashes'] / periods['crashes'] * 100

# Framing 1: crash-level incidence of any reported injury or death.
periods.to_csv(out / 'values_1.csv', index=False, float_format='%.8f')
fig, ax = plt.subplots(figsize=(8.2, 5.2))
bars = ax.bar(['Day\n6am–7:59pm', 'Night\n8pm–5:59am'], periods['casualty_crash_percent'], color=['#4C78A8', '#F58518'], width=.58)
ax.set_ylabel('Crashes with ≥1 person injured or killed (%)')
ax.set_title('A larger share of reported crashes involved casualties at night')
ax.set_ylim(0, 34)
ax.grid(axis='y', alpha=.25)
ax.set_axisbelow(True)
for bar, (_, row) in zip(bars, periods.iterrows()):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+.65,
            f"{row.casualty_crash_percent:.1f}%\n{int(row.casualty_crashes):,} / {int(row.crashes):,} crashes",
            ha='center', va='bottom', fontsize=9)
fig.text(.5, .015, 'NYC police-reported crashes, Jul 2012–Jun 11, 2026. Night defined as 8pm–5:59am; day as 6am–7:59pm.', ha='center', fontsize=8)
fig.tight_layout(rect=[0, .055, 1, 1])
fig.savefig(out / 'option_1.png', dpi=180, bbox_inches='tight')
plt.close(fig)

# Framing 2: crash-level incidence of a fatal outcome.
fig, ax = plt.subplots(figsize=(8.2, 5.2))
bars = ax.bar(['Day\n6am–7:59pm', 'Night\n8pm–5:59am'], periods['fatal_crash_percent'], color=['#4C78A8', '#F58518'], width=.58)
ax.set_ylabel('Crashes with ≥1 person killed (%)')
ax.set_title('Fatal crashes were a larger share of reported crashes at night')
ax.set_ylim(0, .36)
ax.grid(axis='y', alpha=.25)
ax.set_axisbelow(True)
for bar, (_, row) in zip(bars, periods.iterrows()):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+.008,
            f"{row.fatal_crash_percent:.3f}%\n{int(row.fatal_crashes):,} / {int(row.crashes):,} crashes",
            ha='center', va='bottom', fontsize=9)
fig.text(.5, .015, 'NYC police-reported crashes, Jul 2012–Jun 11, 2026. Night defined as 8pm–5:59am; day as 6am–7:59pm.', ha='center', fontsize=8)
fig.tight_layout(rect=[0, .055, 1, 1])
fig.savefig(out / 'option_2.png', dpi=180, bbox_inches='tight')
plt.close(fig)

# Framing 3: reported crash volume by clock hour, normalized per observed date.
hourly = con.execute(f"""
WITH total_dates AS (
  SELECT count(DISTINCT crash_date) AS n FROM read_parquet('{source}')
)
SELECT hour(crash_time) AS hour_of_day, count(*) AS crashes,
       (SELECT n FROM total_dates) AS observed_dates,
       count(*)::DOUBLE / (SELECT n FROM total_dates) AS avg_crashes_per_date
FROM read_parquet('{source}')
GROUP BY hour_of_day ORDER BY hour_of_day
""").df()
hourly.to_csv(out / 'values_3.csv', index=False, float_format='%.8f')
fig, ax = plt.subplots(figsize=(10.5, 5.5))
colors = ['#F58518' if h >= 20 or h < 6 else '#4C78A8' for h in hourly['hour_of_day']]
bars = ax.bar(hourly['hour_of_day'], hourly['avg_crashes_per_date'], color=colors, width=.78)
ax.set_xticks(range(24), [f'{h%12 or 12}'+('a' if h < 12 else 'p') for h in range(24)])
ax.set_xlabel('Clock hour when crash was reported')
ax.set_ylabel('Average reported crashes per clock hour, per observed date')
ax.set_title('Reported crash volume is lower overnight and peaks in the late afternoon')
ax.grid(axis='y', alpha=.25)
ax.set_axisbelow(True)
ax.set_xlim(-.6, 23.6)
ax.annotate(f"Peak: {hourly.loc[hourly.avg_crashes_per_date.idxmax(), 'avg_crashes_per_date']:.1f}/date at 4pm",
            xy=(16, hourly.loc[hourly.hour_of_day.eq(16), 'avg_crashes_per_date'].iloc[0]),
            xytext=(13.2, 36), arrowprops={'arrowstyle':'->', 'color':'#555'}, fontsize=9)
fig.text(.5, .015, 'NYC police-reported crashes, Jul 2012–Jun 11, 2026; 5,094 observed dates. Orange marks 8pm–5:59am.', ha='center', fontsize=8)
fig.tight_layout(rect=[0, .055, 1, 1])
fig.savefig(out / 'option_3.png', dpi=180, bbox_inches='tight')
plt.close(fig)

print('period metrics:')
print(periods.to_string(index=False))
print('\nhourly extremes:')
print(hourly.loc[[hourly.avg_crashes_per_date.idxmin(), hourly.avg_crashes_per_date.idxmax()]].to_string(index=False))
print('\ncreated:', ', '.join(p.name for p in sorted(out.glob('option_*.png'))), ', '.join(p.name for p in sorted(out.glob('values_*.csv'))))
PY
# bash
python3 - <<'PY'
from pathlib import Path
import duckdb
import pandas as pd
source='data/crashes.parquet'
out=Path('out')
df=duckdb.connect().execute(f"""
WITH x AS (
 SELECT CASE WHEN hour(crash_time) >= 20 OR hour(crash_time) < 6
             THEN 'Night (8pm–5:59am)' ELSE 'Day (6am–7:59pm)' END AS period,
        number_of_persons_killed > 0 AS fatal
 FROM read_parquet('{source}')
)
SELECT period, count(*) AS crashes,
       count(*) FILTER (WHERE fatal) AS fatal_crashes,
       count(*) FILTER (WHERE fatal)::DOUBLE / count(*) * 100 AS fatal_crash_percent
FROM x GROUP BY period
""").df()
df['period'] = pd.Categorical(df['period'], ['Day (6am–7:59pm)', 'Night (8pm–5:59am)'], ordered=True)
df.sort_values('period').to_csv(out/'values_2.csv', index=False, float_format='%.8f')
print('saved out/values_2.csv')
PY
# bash
python3 - <<'PY'
from pathlib import Path
import duckdb
import matplotlib.pyplot as plt
source='data/crashes.parquet'
out=Path('out')
hourly=duckdb.connect().execute(f"""
WITH total_dates AS (SELECT count(DISTINCT crash_date) AS n FROM read_parquet('{source}'))
SELECT hour(crash_time) AS hour_of_day, count(*) AS crashes,
       (SELECT n FROM total_dates) AS observed_dates,
       count(*)::DOUBLE / (SELECT n FROM total_dates) AS avg_crashes_per_date
FROM read_parquet('{source}') GROUP BY hour_of_day ORDER BY hour_of_day
""").df()
fig, ax=plt.subplots(figsize=(10.5,5.5))
colors=['#F58518' if h >= 20 or h < 6 else '#4C78A8' for h in hourly['hour_of_day']]
ax.bar(hourly['hour_of_day'],hourly['avg_crashes_per_date'],color=colors,width=.78)
ax.set_xticks(range(24),[f'{h%12 or 12}'+('a' if h<12 else 'p') for h in range(24)])
ax.set_xlabel('Clock hour when crash was reported')
ax.set_ylabel('Average reported crashes per clock hour, per observed date')
ax.set_title('Reported crash volume is lower overnight and peaks in the late afternoon')
ax.grid(axis='y',alpha=.25); ax.set_axisbelow(True); ax.set_xlim(-.6,23.6); ax.set_ylim(0,36)
peak=hourly.loc[hourly.avg_crashes_per_date.idxmax()]
ax.annotate(f"Peak: {peak.avg_crashes_per_date:.1f}/date at 4pm",xy=(int(peak.hour_of_day),peak.avg_crashes_per_date),xytext=(12.8,34),arrowprops={'arrowstyle':'->','color':'#555'},fontsize=9)
fig.text(.5,.015,'NYC police-reported crashes, Jul 2012–Jun 11, 2026; 5,094 observed dates. Orange marks 8pm–5:59am.',ha='center',fontsize=8)
fig.tight_layout(rect=[0,.055,1,1]); fig.savefig(out/'option_3.png',dpi=180,bbox_inches='tight'); plt.close(fig)
PY
# bash
python3 -c "import json, pathlib; p=pathlib.Path('out/options.json'); d=json.loads(p.read_text()); print('valid JSON; options:', len(d['options']), '; probability sum:', sum(x['probability'] for x in d['options'])); print('artifacts:', sorted(x.name for x in pathlib.Path('out').iterdir()))"
# bash
python3 -c "import pandas as pd; a=pd.read_csv('out/values_1.csv'); b=pd.read_csv('out/values_2.csv'); c=pd.read_csv('out/values_3.csv'); print(round(a.loc[1,'casualty_crash_percent'],1), round(a.loc[0,'casualty_crash_percent'],1), round(b.loc[1,'fatal_crash_percent'],3), round(b.loc[0,'fatal_crash_percent'],3), c.loc[c.avg_crashes_per_date.idxmin(),'hour_of_day'], round(c.avg_crashes_per_date.min(),1), c.loc[c.avg_crashes_per_date.idxmax(),'hour_of_day'], round(c.avg_crashes_per_date.max(),1))"

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