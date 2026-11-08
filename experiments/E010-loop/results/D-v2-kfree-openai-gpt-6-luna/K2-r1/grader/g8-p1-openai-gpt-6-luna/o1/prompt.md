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
metric: Total number of police-reported crashes
denominator: None; raw counts pooled across 2013–2025
grouping: Day of week, Monday through Sunday
chart_type: Bar chart
probability: 0.5
WRITTEN ANSWER:
Friday had the most reported crashes (338,800) and Sunday the fewest (257,544) from 2013 through 2025. This framing answers how the total number of crashes is distributed across weekdays over the full 13 years, and its bars show Friday at the top and Sunday at the bottom. Raw totals are a direct measure of recorded crash burden, but they do not normalize for the number of dates of each weekday.

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
python -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(f\"DESCRIBE SELECT * FROM read_parquet('{p}')\").fetchall()); print(c.execute(f\"SELECT MIN(crash_date), MAX(crash_date), COUNT(*) FROM read_parquet('{p}')\").fetchall()); print(c.execute(f\"SELECT EXTRACT(year FROM crash_date) yr, COUNT(*) n FROM read_parquet('{p}') GROUP BY yr ORDER BY yr\").fetchall())"
# bash
ls
# bash
python -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute(f\"SELECT year(crash_date), min(crash_date), max(crash_date), count(*) FROM read_parquet('{p}') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1\").fetchall()); print(c.execute(f\"SELECT dayofweek(crash_date) dow, count(*) crashes, count(DISTINCT crash_date) dates FROM read_parquet('{p}') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1\").fetchall())"
# bash
python - <<'PY'
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import json
from pathlib import Path

out = Path('out')
out.mkdir(exist_ok=True)
con = duckdb.connect()
rows = con.execute("""
    WITH day_counts AS (
        SELECT dayofweek(crash_date) AS dow, COUNT(*) AS crash_count
        FROM read_parquet('data/crashes.parquet')
        WHERE crash_date >= DATE '2013-01-01'
          AND crash_date < DATE '2026-01-01'
        GROUP BY dow
    ), date_counts AS (
        SELECT dayofweek(d) AS dow, COUNT(*) AS dates_observed
        FROM generate_series(DATE '2013-01-01', DATE '2025-12-31', INTERVAL 1 DAY) AS t(d)
        GROUP BY dow
    )
    SELECT dc.dow, dc.crash_count, date_counts.dates_observed
    FROM day_counts dc JOIN date_counts USING (dow)
    ORDER BY CASE dc.dow WHEN 1 THEN 1 WHEN 2 THEN 2 WHEN 3 THEN 3
                         WHEN 4 THEN 4 WHEN 5 THEN 5 WHEN 6 THEN 6 ELSE 7 END
""").fetchdf()
labels = {1:'Monday', 2:'Tuesday', 3:'Wednesday', 4:'Thursday', 5:'Friday', 6:'Saturday', 0:'Sunday'}
rows['weekday'] = rows['dow'].map(labels)
rows['average_crashes_per_date'] = rows['crash_count'] / rows['dates_observed']
rows['share_of_crashes_pct'] = rows['crash_count'] / rows['crash_count'].sum() * 100

counts = rows[['weekday', 'crash_count', 'share_of_crashes_pct']].copy()
counts.to_csv(out / 'values_1.csv', index=False, float_format='%.6f')
means = rows[['weekday', 'crash_count', 'dates_observed', 'average_crashes_per_date']].copy()
means.to_csv(out / 'values_2.csv', index=False, float_format='%.6f')

plt.rcParams.update({'font.size': 10, 'axes.titlesize': 15, 'axes.labelsize': 11})
for idx, (data, value_col, ylabel, title, fmt) in enumerate([
    (counts, 'crash_count', 'Reported crashes', 'NYC motor vehicle crashes by weekday, 2013–2025', '{:,.0f}'),
    (means, 'average_crashes_per_date', 'Average reported crashes per calendar date', 'Average NYC crashes per weekday date, 2013–2025', '{:,.1f}')
], start=1):
    fig, ax = plt.subplots(figsize=(9, 5.4))
    bars = ax.bar(data['weekday'], data[value_col], color='#2676a8', width=0.72)
    ax.set_title(title, pad=14)
    ax.set_ylabel(ylabel)
    ax.set_xlabel('Day of week')
    ax.grid(axis='y', color='#d9e0e5', linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(axis='x', rotation=0)
    ax.bar_label(bars, labels=[fmt.format(x) for x in data[value_col]], padding=4, fontsize=9)
    ax.margins(y=0.12)
    fig.text(0.01, 0.01, 'Source: NYC police-reported crash records; calendar years 2013–2025.', color='#555555', fontsize=8)
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    fig.savefig(out / f'option_{idx}.png', dpi=180, bbox_inches='tight')
    plt.close(fig)

count_max = rows.loc[rows.crash_count.idxmax()]
count_min = rows.loc[rows.crash_count.idxmin()]
mean_max = rows.loc[rows.average_crashes_per_date.idxmax()]
mean_min = rows.loc[rows.average_crashes_per_date.idxmin()]
options = {
    'options': [
        {
            'id': 1,
            'metric': 'Total number of police-reported crashes',
            'denominator': 'None; raw counts pooled across 2013–2025',
            'grouping': 'Day of week, Monday through Sunday',
            'chart_type': 'Bar chart',
            'reason': 'Pooled counts directly show how many recorded crashes fell on each weekday over the full period.',
            'probability': 0.5,
            'answer': f"Friday had the most reported crashes ({int(count_max.crash_count):,}) and Sunday the fewest ({int(count_min.crash_count):,}) from 2013 through 2025.",
            'interpretation': 'This framing answers how the total number of crashes is distributed across weekdays over the full 13 years, and its bars show Friday at the top and Sunday at the bottom. Raw totals are a direct measure of recorded crash burden, but they do not normalize for the number of dates of each weekday.'
        },
        {
            'id': 2,
            'metric': 'Mean number of police-reported crashes per calendar date',
            'denominator': 'Number of calendar dates for each weekday in 2013–2025',
            'grouping': 'Day of week, Monday through Sunday',
            'chart_type': 'Bar chart',
            'reason': 'Per-date averages account for the small differences in how often each weekday occurred during the 13-year window.',
            'probability': 0.5,
            'answer': f"Friday averaged {mean_max.average_crashes_per_date:,.1f} crashes per date, the highest weekday average, while Sunday averaged {mean_min.average_crashes_per_date:,.1f}, the lowest.",
            'interpretation': 'This framing answers how crash frequency differs on a typical calendar date for each weekday, with Friday highest and Sunday lowest in the period. Dividing each weekday’s count by the number of dates of that weekday makes the comparison account for unequal weekday counts, but it does not describe totals alone or adjust for traffic volume, population, or exposure.'
        }
    ]
}
(out / 'options.json').write_text(json.dumps(options, indent=2) + '\n')
print(rows[['weekday','crash_count','dates_observed','average_crashes_per_date','share_of_crashes_pct']].to_string(index=False))
PY
# bash
python - <<'PY'
from pathlib import Path
import json
import pandas as pd
from PIL import Image

out = Path('out')
options = json.loads((out / 'options.json').read_text())['options']
assert len(options) == 2
assert abs(sum(option['probability'] for option in options) - 1) < 1e-12
for i in (1, 2):
    values = pd.read_csv(out / f'values_{i}.csv')
    image = Image.open(out / f'option_{i}.png')
    assert len(values) == 7 and image.width > 0 and image.height > 0
    assert list(values.weekday) == ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
first = pd.read_csv(out / 'values_1.csv')
second = pd.read_csv(out / 'values_2.csv')
assert first.crash_count.sum() == 2_141_218
assert round(first.share_of_crashes_pct.sum(), 4) == 100.0
assert (first.crash_count.to_list() == second.crash_count.to_list())
assert second.loc[second.average_crashes_per_date.idxmax(), 'weekday'] == 'Friday'
assert second.loc[second.average_crashes_per_date.idxmin(), 'weekday'] == 'Sunday'
print('Reviewed: JSON valid, probabilities sum to 1, both charts and 7-row CSVs exist, values agree across options, totals and weekday extrema verified.')
PY
# bash
python - <<'PY'
import pandas as pd
x=pd.read_csv('out/values_1.csv')
print(x.crash_count.sum(), x.share_of_crashes_pct.sum())
PY
# bash
python - <<'PY'
from pathlib import Path
import json
import pandas as pd
from PIL import Image

out = Path('out')
options = json.loads((out / 'options.json').read_text())['options']
assert len(options) == 2
assert abs(sum(option['probability'] for option in options) - 1) < 1e-12
for i in (1, 2):
    values = pd.read_csv(out / f'values_{i}.csv')
    image = Image.open(out / f'option_{i}.png')
    assert len(values) == 7 and image.width > 0 and image.height > 0
    assert list(values.weekday) == ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
first = pd.read_csv(out / 'values_1.csv')
second = pd.read_csv(out / 'values_2.csv')
assert first.crash_count.sum() == 2_132_218
assert round(first.share_of_crashes_pct.sum(), 4) == 100.0
assert first.crash_count.to_list() == second.crash_count.to_list()
assert second.loc[second.average_crashes_per_date.idxmax(), 'weekday'] == 'Friday'
assert second.loc[second.average_crashes_per_date.idxmin(), 'weekday'] == 'Sunday'
print('Reviewed: JSON valid, probabilities sum to 1, both charts and 7-row CSVs exist, values agree across options, totals and weekday extrema verified.')
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