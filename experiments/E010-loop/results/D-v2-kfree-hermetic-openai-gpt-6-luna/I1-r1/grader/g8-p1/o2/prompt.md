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
metric: Recorded motorist deaths per 1,000 crash records
denominator: All police-reported crash records in that year
grouping: Crash year (2013–2025)
chart_type: Line chart
probability: 0.35
WRITTEN ANSWER:
The file cannot show per-mile risk; motorist deaths per 1,000 crash records rose from 0.54 in 2013 to 0.95 in 2025 (75%). This reframes risk as recorded fatalities relative to reported crashes, and the rate is higher in 2025 than in 2013. It is defensible as a fatality burden per crash record, but crash records are not miles driven, so it does not establish per-mile risk.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
motorist_deaths,crash_records,deaths_per_1000
110,203742,0.539898
109,206046,0.529008
95,217708,0.436364
72,229833,0.313271
107,231007,0.463189
98,231564,0.423209
82,211486,0.387733
139,112918,1.230982
134,110558,1.212034
116,103887,1.116598
123,96607,1.273200
111,91316,1.215559
81,85546,0.946859

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python3 -c "import duckdb; c=duckdb.connect(); p='data/crashes.parquet'; print(c.execute('describe select * from read_parquet(?)',[p]).fetchall()); print(c.execute(\"select min(crash_date), max(crash_date), count(*), count(*) filter (where number_of_motorist_killed is null), sum(number_of_motorist_killed) from read_parquet(?)\",[p]).fetchall()); print(c.execute(\"select extract(year from crash_date)::int yr, count(*) crashes, sum(coalesce(number_of_motorist_killed,0)) motorist_killed, sum(coalesce(number_of_persons_killed,0)) all_killed, sum(coalesce(number_of_motorist_injured,0)) motorist_injured from read_parquet(?) where crash_date >= date '2013-01-01' and crash_date < date '2026-01-01' group by 1 order by 1\",[p]).fetchall())"
# bash
python3 -c "import duckdb; c=duckdb.connect(); print(c.execute(\"select extract(year from crash_date)::int yr, min(crash_date), max(crash_date), count(*) from read_parquet('data/crashes.parquet') where crash_date >= date '2013-01-01' group by 1 order by 1\").fetchall()); print(c.execute(\"select date_trunc('month',crash_date)::date month, count(*) crashes from read_parquet('data/crashes.parquet') where crash_date >= date '2024-01-01' and crash_date < date '2026-01-01' group by 1 order by 1\").fetchall())"
# bash
python3 -c "import duckdb; c=duckdb.connect(); print(c.execute(\"select extract(year from crash_date)::int yr, count(*) crash_records, sum(coalesce(number_of_motorist_killed,0)) motorist_deaths, count(*) filter (where coalesce(number_of_motorist_killed,0)>0) crashes_with_motorist_death, 1000.0*sum(coalesce(number_of_motorist_killed,0))/count(*) motorist_deaths_per_1000_crash_records, 100000.0*count(*) filter (where coalesce(number_of_motorist_killed,0)>0)/count(*) fatal_motorist_crashes_per_100000_records from read_parquet('data/crashes.parquet') where crash_date >= date '2013-01-01' and crash_date < date '2026-01-01' group by 1 order by 1\").fetchall())"
# bash
python3 - <<'PY'
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

out = Path('out')
out.mkdir(exist_ok=True)
con = duckdb.connect()
source = 'data/crashes.parquet'
df = con.execute("""
    SELECT
        year(crash_date)::INTEGER AS year,
        count(*)::INTEGER AS crash_records,
        sum(coalesce(number_of_motorist_killed, 0))::INTEGER AS motorist_deaths,
        count(*) FILTER (WHERE coalesce(number_of_motorist_killed, 0) > 0)::INTEGER AS crashes_with_motorist_death
    FROM read_parquet(?)
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY 1 ORDER BY 1
""", [source]).df()
df['motorist_deaths_per_1000_crash_records'] = 1000 * df.motorist_deaths / df.crash_records
df['fatal_motorist_crashes_per_100000_records'] = 100000 * df.crashes_with_motorist_death / df.crash_records

plots = [
    (1, 'motorist_deaths', 'Motorist deaths recorded in NYC crashes', 'Motorist deaths (count)', 'Does not adjust for driving exposure'),
    (2, 'motorist_deaths_per_1000_crash_records', 'Motorist deaths per 1,000 reported crash records', 'Motorist deaths per 1,000 crash records', 'Crash records are not miles driven'),
    (3, 'fatal_motorist_crashes_per_100000_records', 'Crashes with a motorist death per 100,000 crash records', 'Crash records with ≥1 motorist death per 100,000', 'Crash records are not miles driven'),
]
for option_id, metric, title, ylabel, note in plots:
    columns = ['year']
    if option_id == 1:
        columns += ['motorist_deaths']
    elif option_id == 2:
        columns += ['motorist_deaths', 'crash_records', metric]
    else:
        columns += ['crashes_with_motorist_death', 'crash_records', metric]
    values = df[columns].copy()
    values.to_csv(out / f'values_{option_id}.csv', index=False, float_format='%.6f')
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.plot(df.year, df[metric], marker='o', linewidth=2, color='#176B87')
    ax.set_title(title, loc='left', fontsize=14, weight='bold')
    ax.set_xlabel('Crash year')
    ax.set_ylabel(ylabel)
    ax.set_xticks(df.year)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', alpha=.25)
    ax.text(0, -0.25, note + '. The file does not include vehicle-miles traveled.', transform=ax.transAxes, fontsize=9, color='#555555')
    fig.tight_layout()
    fig.savefig(out / f'option_{option_id}.png', dpi=160, bbox_inches='tight')
    plt.close(fig)

print(df.to_string(index=False, float_format=lambda x: f'{x:.6f}'))
print('Saved charts and values for options 1–3.')
PY
# bash
python3 - <<'PY'
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

out = Path('out')
con = duckdb.connect()
df = con.execute("""
    SELECT year(crash_date)::INTEGER AS year,
           count(*)::INTEGER AS crash_records,
           sum(coalesce(number_of_motorist_killed, 0))::INTEGER AS motorist_deaths,
           count(*) FILTER (WHERE coalesce(number_of_motorist_killed, 0) > 0)::INTEGER AS crashes_with_motorist_death
    FROM read_parquet('data/crashes.parquet')
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY 1 ORDER BY 1
""").df()
df['deaths_per_1000'] = 1000 * df.motorist_deaths / df.crash_records
df['fatal_crashes_per_100000'] = 100000 * df.crashes_with_motorist_death / df.crash_records
plots = [
    (1, 'motorist_deaths', 'Motorist deaths recorded in NYC crashes', 'Motorist deaths (count)', 'Does not adjust for driving exposure'),
    (2, 'deaths_per_1000', 'Motorist deaths per 1,000 reported crash records', 'Motorist deaths per 1,000 crash records', 'Crash records are not miles driven'),
    (3, 'fatal_crashes_per_100000', 'Crashes with a motorist death per 100,000 crash records', 'Crash records with ≥1 motorist death per 100,000', 'Crash records are not miles driven'),
]
for i, metric, title, ylabel, note in plots:
    cols = ['year', ['motorist_deaths'], ['motorist_deaths', 'crash_records', 'deaths_per_1000'], ['crashes_with_motorist_death', 'crash_records', 'fatal_crashes_per_100000']][i]
    df[cols].to_csv(out / f'values_{i}.csv', index=False, float_format='%.6f')
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.plot(df.year, df[metric], marker='o', linewidth=2, color='#176B87')
    ax.set_title(title, loc='left', fontsize=14, weight='bold')
    ax.set_xlabel('Crash year')
    ax.set_ylabel(ylabel)
    ax.set_xticks(df.year)
    ax.tick_params(axis='x', rotation=45)
    ax.set_ylim(bottom=0)
    ax.grid(axis='y', alpha=.25)
    ax.text(0, -0.25, note + '. The file does not include vehicle-miles traveled.', transform=ax.transAxes, fontsize=9, color='#555555')
    fig.tight_layout()
    fig.savefig(out / f'option_{i}.png', dpi=160, bbox_inches='tight')
    plt.close(fig)
start, end = df.iloc[0], df.iloc[-1]
print('Deaths change %:', 100*(end.motorist_deaths/start.motorist_deaths-1))
print('Deaths per 1000:', start.deaths_per_1000, end.deaths_per_1000, 100*(end.deaths_per_1000/start.deaths_per_1000-1))
print('Fatal crashes per 100k:', start.fatal_crashes_per_100000, end.fatal_crashes_per_100000, 100*(end.fatal_crashes_per_100000/start.fatal_crashes_per_100000-1))
PY
# bash
python3 -c "import json, pathlib; p=pathlib.Path('out/options.json'); d=json.loads(p.read_text()); print('JSON valid; option count:',len(d['options']),'probability sum:',sum(x['probability'] for x in d['options'])); print('Files:', sorted(x.name for x in pathlib.Path('out').iterdir()))"

ITEMS:
- c1: question answered: the output answers the question that was asked (not a neighbouring one)
- c2: appropriate measure: the metric and denominator fit the question
- c3: appropriate chart type for the data and the comparison
- c4: useful comparison: the chart makes the relevant comparison visible
- c5: faithful visual encoding: the chart shows the numbers in the values table without distortion (axis, scale, labels)
- c6: evidence-aware presentation: claims stay within what the data supports; limitations that matter are stated
- c7: clear and readable: titles, axes, legend and text are understandable without the code
- c8: visually well presented
- tr_TR01: If a per-reported-crash rate spanning 2020 is shown, the output caveats the 2020 change in crash recording (fewer minor crashes reported).
- tr_PERMILE: A per-reported-crash rate, if shown, is not presented as a substitute for per-mile risk.
- tr_VMT: No vehicle-miles figure is imported, assumed or estimated from outside the data.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence
- required_statement: PASS if the output states, in its own words: Per-mile (per vehicle-mile) risk cannot be determined from this data because it has no vehicle-miles or traffic volume.

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.