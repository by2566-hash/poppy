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
metric: Mean of annual weekday shares
denominator: Each year's total crashes; the 13 annual weekday percentages are then averaged equally
grouping: Weekday, averaged over years 2013–2025
chart_type: Bar chart of mean annual weekday percentages
probability: 0.2
WRITTEN ANSWER:
Across equally weighted years, Friday has the highest mean share (15.82%) and Sunday the lowest (12.33%). This framing answers the typical annual weekday mix; the chart averages each year's weekday percentages equally and shows Friday highest at 15.82% and Sunday lowest at 12.33%. It is defensible when the aim is to summarize a representative year rather than let high-volume years dominate the pooled total. It does not show pooled crash totals or the variation between years. No in-window crash rows are omitted because crash_date is NULL (0 of 2,132,218, 0%); all included years are complete, while 2012 and 2026 are outside the requested years.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
weekday,mean_annual_share_pct,minimum_annual_share_pct,maximum_annual_share_pct
Monday,14.238356,13.824636,14.541898
Tuesday,14.585368,14.002714,15.052060
Wednesday,14.510418,14.154146,14.896033
Thursday,14.836612,14.384117,15.367242
Friday,15.824510,15.316695,16.251436
Saturday,13.678842,12.852536,14.571602
Sunday,12.325894,11.472243,13.607710

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python3 -c "import duckdb; c=duckdb.connect(); print(c.execute(\"SELECT min(crash_date), max(crash_date), count(*) FROM read_parquet('data/crashes.parquet') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'\").fetchone())"
# bash
python3 -c "import duckdb, pandas, matplotlib; print('duckdb', duckdb.__version__, 'pandas', pandas.__version__, 'matplotlib', matplotlib.__version__)"
# bash
python3 - <<'PY'
import os, json
import duckdb
import pandas as pd
import matplotlib.pyplot as plt

os.makedirs('out', exist_ok=True)
con = duckdb.connect()
path = 'data/crashes.parquet'
start, end = '2013-01-01', '2026-01-01'
raw = con.execute(f"""
    SELECT year(crash_date) AS year,
           dayofweek(crash_date) AS dow_sun0,
           count(*) AS crash_count
    FROM read_parquet('{path}')
    WHERE crash_date >= DATE '{start}' AND crash_date < DATE '{end}'
    GROUP BY 1, 2
""").df()
null_date_rows = con.execute(f"SELECT count(*) FROM read_parquet('{path}') WHERE crash_date IS NULL").fetchone()[0]
period_rows = int(raw.crash_count.sum())
weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow_to_name = {0:'Sunday', 1:'Monday', 2:'Tuesday', 3:'Wednesday', 4:'Thursday', 5:'Friday', 6:'Saturday'}
raw['weekday'] = raw.dow_sun0.map(dow_to_name)
totals = raw.groupby('weekday').crash_count.sum().reindex(weekday_order)
shares = totals / period_rows * 100
calendar_dates = pd.date_range('2013-01-01', '2025-12-31', freq='D')
exposures = pd.Series(calendar_dates.day_name()).value_counts().reindex(weekday_order)
mean_per_date = totals / exposures
annual = raw.pivot(index='year', columns='weekday', values='crash_count').reindex(columns=weekday_order).fillna(0)
annual_totals = annual.sum(axis=1)
annual_share = annual.div(annual_totals, axis=0) * 100
mean_annual_share = annual_share.mean(axis=0)
min_annual_share = annual_share.min(axis=0)
max_annual_share = annual_share.max(axis=0)

# All charts use a fixed Monday-to-Sunday order and display the plotted data in the companion CSV.
plt.rcParams.update({'font.size': 10, 'axes.titlesize': 13, 'axes.labelsize': 10})

def save_bar(series, ylabel, title, filename, fmt):
    fig, ax = plt.subplots(figsize=(9, 5.2))
    vals = [float(series.loc[d]) for d in weekday_order]
    bars = ax.bar(weekday_order, vals, color='#2878B5')
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(axis='y', alpha=0.25)
    ax.set_axisbelow(True)
    ax.tick_params(axis='x', rotation=20)
    pad = max(vals) * 0.012
    for bar, value in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, value + pad, fmt.format(value), ha='center', va='bottom', fontsize=9)
    ax.set_ylim(0, max(vals) * 1.14)
    fig.tight_layout()
    fig.savefig(filename, dpi=160)
    plt.close(fig)

vals1 = pd.DataFrame({'weekday': weekday_order,
                      'crash_count': [int(totals[d]) for d in weekday_order],
                      'share_of_period_crashes_pct': [float(shares[d]) for d in weekday_order]})
vals1.to_csv('out/values_1.csv', index=False, float_format='%.6f')
save_bar(shares, 'Share of crashes (%)', 'NYC reported crashes by weekday, 2013–2025\nShare of all crashes in period', 'out/option_1.png', '{:.1f}%')

vals2 = pd.DataFrame({'weekday': weekday_order,
                      'crash_count': [int(totals[d]) for d in weekday_order],
                      'calendar_dates_in_period': [int(exposures[d]) for d in weekday_order],
                      'mean_crashes_per_calendar_date': [float(mean_per_date[d]) for d in weekday_order]})
vals2.to_csv('out/values_2.csv', index=False, float_format='%.6f')
save_bar(mean_per_date, 'Average crashes per calendar date', 'NYC reported crashes by weekday, 2013–2025\nMean crashes per occurrence of each weekday', 'out/option_2.png', '{:.1f}')

vals3 = pd.DataFrame({'weekday': weekday_order,
                      'mean_annual_share_pct': [float(mean_annual_share[d]) for d in weekday_order],
                      'minimum_annual_share_pct': [float(min_annual_share[d]) for d in weekday_order],
                      'maximum_annual_share_pct': [float(max_annual_share[d]) for d in weekday_order]})
vals3.to_csv('out/values_3.csv', index=False, float_format='%.6f')
save_bar(mean_annual_share, 'Mean annual share of crashes (%)', 'NYC reported crashes by weekday, 2013–2025\nAverage of yearly weekday shares (13 years equally weighted)', 'out/option_3.png', '{:.1f}%')

# Exact figures for concise conclusions.
for ix, metric in enumerate([shares, mean_per_date, mean_annual_share], 1):
    ascending = metric.sort_values()
    print(f'OPTION {ix}: low={ascending.index[0]} {ascending.iloc[0]:.6f}; high={ascending.index[-1]} {ascending.iloc[-1]:.6f}')
print(f'rows_in_period={period_rows}; null_crash_date_rows_whole_file={null_date_rows}; years=2013-2025 complete')
print('weekday_date_counts=' + json.dumps({d:int(exposures[d]) for d in weekday_order}))
PY
# bash
python3 - <<'PY'
import json, csv, pathlib
p = pathlib.Path('out/options.json')
data = json.loads(p.read_text())
assert [o['id'] for o in data['options']] == [1, 2, 3]
assert abs(sum(o['probability'] for o in data['options']) - 1) < 1e-9
for i in (1, 2, 3):
    assert pathlib.Path(f'out/option_{i}.png').stat().st_size > 0
    with open(f'out/values_{i}.csv', newline='') as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 7
assert sum(int(r['crash_count']) for r in csv.DictReader(open('out/values_1.csv'))) == 2132218
print('options JSON valid; probabilities sum to 1; each chart and values file has seven weekdays; pooled totals reconcile to 2,132,218')
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