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
metric: Crash count
denominator: None; total crash records for each weekday from 2013 through 2025
grouping: Day of week
chart_type: Vertical bar chart
probability: 0.55
WRITTEN ANSWER:
Friday had the most reported crashes (338,800) and Sunday the fewest (257,544) among 2,132,218 crashes. This directly answers how recorded crashes are distributed across weekdays: Friday is highest and Sunday is lowest. Total counts describe the observed crash burden in the period, but do not adjust for the small differences in how many times each weekday occurred or explain why the distribution differs.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
weekday,crash_count
Monday,304518
Tuesday,313488
Wednesday,311111
Thursday,318376
Friday,338800
Saturday,288381
Sunday,257544

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python3 -c "import duckdb, pandas, matplotlib; print('duckdb', duckdb.__version__); print('pandas', pandas.__version__); print('matplotlib', matplotlib.__version__)"
# bash
ls -la
# bash
python3 - <<'PY'
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

out = Path('out')
out.mkdir(exist_ok=True)
con = duckdb.connect()
path = str(Path('data/crashes.parquet').resolve()).replace("'", "''")
crashes = con.execute(f"""
    SELECT isodow(crash_date) AS weekday_num,
           dayname(crash_date) AS weekday,
           count(*)::BIGINT AS crash_count
    FROM read_parquet('{path}')
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY 1, 2
    ORDER BY 1
""").df()
calendar_days = con.execute("""
    SELECT isodow(d)::INTEGER AS weekday_num, count(*)::INTEGER AS weekday_occurrences
    FROM generate_series(DATE '2013-01-01', DATE '2025-12-31', INTERVAL 1 DAY) AS t(d)
    GROUP BY 1 ORDER BY 1
""").df()
df = crashes.merge(calendar_days, on='weekday_num', validate='one_to_one')
df['crash_share_pct'] = df['crash_count'] / df['crash_count'].sum() * 100
labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
df['weekday'] = pd.Categorical(df['weekday'], categories=labels, ordered=True)
df = df.sort_values('weekday_num').reset_index(drop=True)
df['weekday'] = df['weekday'].astype(str)

total = int(df['crash_count'].sum())
assert len(df) == 7 and total > 0
assert int(df['weekday_occurrences'].sum()) == 4748

# Framing 1: absolute crash counts, grouped by weekday.
values1 = df[['weekday', 'crash_count']].copy()
values1.to_csv(out / 'values_1.csv', index=False)
fig, ax = plt.subplots(figsize=(9, 5.5))
bars = ax.bar(values1['weekday'], values1['crash_count'], color='#2878B5')
ax.bar_label(bars, labels=[f'{v:,.0f}' for v in values1['crash_count']], padding=3, fontsize=9)
ax.set_title('NYC police-reported crashes by weekday, 2013–2025')
ax.set_ylabel('Number of crashes')
ax.set_xlabel('Day of week')
ax.set_ylim(0, max(values1['crash_count']) * 1.13)
ax.grid(axis='y', alpha=.22)
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout()
fig.savefig(out / 'option_1.png', dpi=160, bbox_inches='tight')
plt.close(fig)

# Framing 2: percentage of all crashes, grouped by weekday.
values2 = df[['weekday', 'crash_share_pct']].copy()
values2.to_csv(out / 'values_2.csv', index=False, float_format='%.6f')
fig, ax = plt.subplots(figsize=(9, 5.5))
bars = ax.bar(values2['weekday'], values2['crash_share_pct'], color='#E07A3F')
ax.bar_label(bars, labels=[f'{v:.2f}%' for v in values2['crash_share_pct']], padding=3, fontsize=9)
ax.set_title('Share of NYC police-reported crashes by weekday, 2013–2025')
ax.set_ylabel('Share of crashes (%)')
ax.set_xlabel('Day of week')
ax.set_ylim(0, max(values2['crash_share_pct']) * 1.13)
ax.grid(axis='y', alpha=.22)
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout()
fig.savefig(out / 'option_2.png', dpi=160, bbox_inches='tight')
plt.close(fig)

print('Total crashes:', total)
print(df[['weekday', 'crash_count', 'weekday_occurrences', 'crash_share_pct']].to_string(index=False))
print('Total share:', values2['crash_share_pct'].sum())
PY
# bash
python3 - <<'PY'
import json
from pathlib import Path
import pandas as pd
p = Path('out')
opts = json.loads((p / 'options.json').read_text())['options']
assert [o['id'] for o in opts] == [1, 2]
assert abs(sum(o['probability'] for o in opts) - 1) < 1e-12
for i in (1, 2):
    assert (p / f'option_{i}.png').is_file() and (p / f'option_{i}.png').stat().st_size > 0
v1 = pd.read_csv(p / 'values_1.csv')
v2 = pd.read_csv(p / 'values_2.csv')
assert v1.weekday.tolist() == v2.weekday.tolist()
assert int(v1.crash_count.sum()) == 2_132_218
assert abs(v2.crash_share_pct.sum() - 100) < 1e-5
assert int(v1.loc[v1.crash_count.idxmax(), 'crash_count']) == 338_800
assert v1.loc[v1.crash_count.idxmax(), 'weekday'] == 'Friday'
assert v1.loc[v1.crash_count.idxmin(), 'weekday'] == 'Sunday'
assert round(v2.loc[v2.crash_share_pct.idxmax(), 'crash_share_pct'], 2) == 15.89
assert round(v2.loc[v2.crash_share_pct.idxmin(), 'crash_share_pct'], 2) == 12.08
print('JSON, chart files, CSV totals, weekday ordering, maxima/minima, and displayed percentages validated.')
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