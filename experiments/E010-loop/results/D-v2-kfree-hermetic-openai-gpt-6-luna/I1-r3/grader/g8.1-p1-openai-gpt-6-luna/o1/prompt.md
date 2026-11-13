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

QUESTION ASKED: Did the risk of a motorist being killed per mile driven in NYC decline from 2013 to 2025? Make a chart and answer based on this crash data.
QUESTION TYPE: insufficient
DECLARED FRAMING:
metric: Annual number of motorist deaths recorded in crashes
denominator: None; annual total
grouping: Calendar year (2013–2025)
chart_type: Line chart
probability: 0.25
WRITTEN ANSWER:
Recorded motorist deaths fell from 110 in 2013 to 81 in 2025 (26.4% lower), but this crash file cannot determine whether deaths per mile driven declined. This framing answers whether the annual count of motorist deaths in reported NYC crashes declined: it fell between the endpoints, despite substantial year-to-year variation. It is defensible as a measure of fatality burden, but not as a measure of risk because it has no miles-driven denominator; it therefore leaves the per-mile question unanswered.

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,motorist_deaths
2013,110.0
2014,109.0
2015,95.0
2016,72.0
2017,107.0
2018,98.0
2019,82.0
2020,139.0
2021,134.0
2022,116.0
2023,123.0
2024,111.0
2025,81.0

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
pwd && ls
# bash
ls
# bash
python3 -c "import duckdb; p='data/crashes.parquet'; con=duckdb.connect(); print(con.execute(f\"SELECT min(crash_date), max(crash_date), count(*) FROM read_parquet('{p}')\").fetchall()); print(con.execute(f\"DESCRIBE SELECT * FROM read_parquet('{p}')\").fetchall())"
# bash
python3 -c "import duckdb; con=duckdb.connect(); p='data/crashes.parquet'; q=f\"SELECT year(crash_date) y, count(*) crashes, sum(coalesce(number_of_motorist_killed,0)) motorist_deaths, sum(CASE WHEN coalesce(number_of_motorist_killed,0)>0 THEN 1 ELSE 0 END) fatal_crashes, min(crash_date) first_date, max(crash_date) last_date FROM read_parquet('{p}') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY y ORDER BY y\"; print(con.execute(q).df().to_string(index=False)); print('MONTHLY'); print(con.execute(f\"SELECT year(crash_date) y, month(crash_date) m, count(*) n FROM read_parquet('{p}') WHERE crash_date >= DATE '2024-01-01' GROUP BY y,m ORDER BY y,m\").df().to_string(index=False))"
# bash
python3 - <<'PY'
from pathlib import Path
import duckdb
import pandas as pd
import matplotlib.pyplot as plt

out = Path('out')
out.mkdir(exist_ok=True)
con = duckdb.connect()
rows = con.execute("""
    SELECT year(crash_date) AS year,
           count(*) AS reported_crashes,
           sum(coalesce(number_of_motorist_killed, 0)) AS motorist_deaths,
           sum(CASE WHEN coalesce(number_of_motorist_killed, 0) > 0 THEN 1 ELSE 0 END) AS crashes_with_motorist_death
    FROM read_parquet('data/crashes.parquet')
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY year
    ORDER BY year
""").df()
rows['motorist_deaths_per_100k_crashes'] = rows['motorist_deaths'] / rows['reported_crashes'] * 100000
rows['fatal_crashes_per_100k_crashes'] = rows['crashes_with_motorist_death'] / rows['reported_crashes'] * 100000

plt.rcParams.update({'font.size': 10, 'axes.titlesize': 13, 'axes.labelsize': 10})

def line_chart(column, ylabel, title, filename, decimals=1):
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    ax.plot(rows['year'], rows[column], color='#176B87', marker='o', linewidth=2.2, markersize=5)
    ax.set_xticks(rows['year'])
    ax.tick_params(axis='x', rotation=45)
    ax.set_ylabel(ylabel)
    ax.set_xlabel('Crash year')
    ax.set_title(title, loc='left', pad=13, weight='bold')
    ax.grid(axis='y', alpha=.25)
    ax.spines[['top', 'right']].set_visible(False)
    start, end = rows.iloc[0], rows.iloc[-1]
    fmt = f'{{:.{decimals}f}}'
    ax.annotate(fmt.format(start[column]), (start['year'], start[column]), xytext=(5, 9), textcoords='offset points', color='#174A5B', weight='bold')
    ax.annotate(fmt.format(end[column]), (end['year'], end[column]), xytext=(5, 9), textcoords='offset points', color='#174A5B', weight='bold')
    fig.text(.01, .01, 'Source: NYC police-reported crash records. Crash records do not include miles driven.', color='#555555', fontsize=8)
    fig.tight_layout(rect=(0, .045, 1, 1))
    fig.savefig(out / filename, dpi=180, bbox_inches='tight')
    plt.close(fig)

rows[['year', 'motorist_deaths']].to_csv(out / 'values_1.csv', index=False)
line_chart('motorist_deaths', 'Motorist deaths (count)', 'Motorist deaths recorded in NYC crashes, 2013–2025', 'option_1.png', 0)

rows[['year', 'crashes_with_motorist_death', 'reported_crashes', 'fatal_crashes_per_100k_crashes']].to_csv(out / 'values_2.csv', index=False)
line_chart('fatal_crashes_per_100k_crashes', 'Crashes with ≥1 motorist death per 100,000 reported crashes', 'Motorist-fatal crashes per 100,000 reported crashes, 2013–2025', 'option_2.png', 1)

rows[['year', 'motorist_deaths', 'reported_crashes', 'motorist_deaths_per_100k_crashes']].to_csv(out / 'values_3.csv', index=False)
line_chart('motorist_deaths_per_100k_crashes', 'Motorist deaths per 100,000 reported crashes', 'Motorist deaths per 100,000 reported crashes, 2013–2025', 'option_3.png', 1)

print(rows.to_string(index=False, formatters={
    'motorist_deaths_per_100k_crashes': '{:.3f}'.format,
    'fatal_crashes_per_100k_crashes': '{:.3f}'.format,
}))
PY
# bash
python3 - <<'PY'
from pathlib import Path
import duckdb
import matplotlib.pyplot as plt

out = Path('out')
con = duckdb.connect()
rows = con.execute("""
    SELECT year(crash_date) AS year,
           count(*) AS reported_crashes,
           sum(coalesce(number_of_motorist_killed, 0)) AS motorist_deaths,
           sum(CASE WHEN coalesce(number_of_motorist_killed, 0) > 0 THEN 1 ELSE 0 END) AS crashes_with_motorist_death
    FROM read_parquet('data/crashes.parquet')
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY year ORDER BY year
""").df()
rows['motorist_deaths_per_100k_crashes'] = rows['motorist_deaths'] / rows['reported_crashes'] * 100000
rows['fatal_crashes_per_100k_crashes'] = rows['crashes_with_motorist_death'] / rows['reported_crashes'] * 100000

def line_chart(column, ylabel, title, filename, decimals=1):
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    ax.plot(rows['year'], rows[column], color='#176B87', marker='o', linewidth=2.2, markersize=5)
    ax.set_xticks(rows['year'])
    ax.tick_params(axis='x', rotation=45)
    ax.set_ylim(bottom=0)
    ax.set_ylabel(ylabel)
    ax.set_xlabel('Crash year')
    ax.set_title(title, loc='left', pad=13, weight='bold')
    ax.grid(axis='y', alpha=.25)
    ax.spines[['top', 'right']].set_visible(False)
    for ix in (0, len(rows) - 1):
        point = rows.iloc[ix]
        ax.annotate(f"{point[column]:.{decimals}f}", (point['year'], point[column]), xytext=(5, 9), textcoords='offset points', color='#174A5B', weight='bold')
    fig.text(.01, .01, 'Source: NYC police-reported crash records. Crash records do not include miles driven.', color='#555555', fontsize=8)
    fig.tight_layout(rect=(0, .045, 1, 1))
    fig.savefig(out / filename, dpi=180, bbox_inches='tight')
    plt.close(fig)

rows[['year', 'motorist_deaths']].to_csv(out / 'values_1.csv', index=False)
line_chart('motorist_deaths', 'Motorist deaths (count)', 'Motorist deaths recorded in NYC crashes, 2013–2025', 'option_1.png', 0)
rows[['year', 'crashes_with_motorist_death', 'reported_crashes', 'fatal_crashes_per_100k_crashes']].to_csv(out / 'values_2.csv', index=False)
line_chart('fatal_crashes_per_100k_crashes', 'Crashes with ≥1 motorist death per 100,000 reported crashes', 'Motorist-fatal crashes per 100,000 reported crashes, 2013–2025', 'option_2.png', 1)
rows[['year', 'motorist_deaths', 'reported_crashes', 'motorist_deaths_per_100k_crashes']].to_csv(out / 'values_3.csv', index=False)
line_chart('motorist_deaths_per_100k_crashes', 'Motorist deaths per 100,000 reported crashes', 'Motorist deaths per 100,000 reported crashes, 2013–2025', 'option_3.png', 1)
for metric in ['motorist_deaths', 'fatal_crashes_per_100k_crashes', 'motorist_deaths_per_100k_crashes']:
    a, b = rows.iloc[0][metric], rows.iloc[-1][metric]
    print(metric, a, b, (b / a - 1) * 100)
PY
# bash
python3 -c "import json; from pathlib import Path; p=Path('out'); o=json.loads((p/'options.json').read_text()); print('options',len(o['options']),'probability_sum',sum(x['probability'] for x in o['options'])); print({f.name:f.stat().st_size for f in sorted(p.iterdir()) if f.name in ['options.json','option_1.png','option_2.png','option_3.png','values_1.csv','values_2.csv','values_3.csv']})"

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR01: If a per-reported-crash rate spanning 2020 is shown, the output says that the number of recorded crashes changes sharply around 2020 and that this affects comparing the per-crash rate across years (naming the cause, the 2020 recording change, is not required: it is not in the data or the dictionary).
- tr_PERMILE: A per-reported-crash rate, if shown, is not presented as a substitute for per-mile risk.
- tr_VMT: No vehicle-miles figure is imported, assumed or estimated from outside the data.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence
- required_statement: PASS if the output states, in its own words: Per-mile (per vehicle-mile) risk cannot be determined from this data because it has no vehicle-miles or traffic volume.

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.