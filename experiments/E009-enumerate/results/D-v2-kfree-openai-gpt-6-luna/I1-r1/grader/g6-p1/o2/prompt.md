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

DATA FACTS (pinned snapshot):
- The file covers 2012-07-01 to 2026-06-11; 2013-2025 are complete calendar years; 2026 is partial (to June 11).
- borough is NULL for about 20-38% of crashes in every year (TR05): a borough filter silently drops them.
- number_of_persons_killed is NULL in most May-2026 and all June-2026 rows (TR08); 2013-2025 killed counts have no NULLs.
- crash_time has no NULL rows. Reported crash counts (the number of crash records) fall sharply in 2020 (TR01), so a per-reported-crash rate (deaths or injuries divided by reported crashes) compared across years spanning 2020 needs a caveat. Counts of deaths or injuries by year do NOT need it (they are not affected by the reporting change), and a comparison between groups within one pooled window (e.g. day vs night) does not either (decided 2026-11-04; g5 wording after g4 failed c6 on plain death counts).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: Did the risk of a motorist being killed per mile driven in NYC decline from 2013 to 2025? Make a chart and answer based on this crash data.
QUESTION TYPE: insufficient
DECLARED FRAMING:
metric: Motorist deaths per 100,000 police-reported crash reports
denominator: All police-reported crash rows in the year, scaled to 100,000
grouping: Calendar year, 2013–2025
chart_type: Line chart
probability: 0.7
WRITTEN ANSWER:
Per-mile risk is unmeasured; motorist deaths per 100,000 crash reports rose from 54.0 in 2013 to 94.7 in 2025. This framing compares motorist deaths with annual crash-report volume, and the chart shows an increase from 54.0 deaths per 100,000 reports in 2013 to 94.7 in 2025. It is a defensible crash-normalized measure because each row is a reported crash, but it leaves the per-mile risk question unanswered because the data contain no miles driven.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,motorist_deaths,crash_reports,motorist_deaths_per_100k_crash_reports
2013,110,203742,53.989850
2014,109,206046,52.900809
2015,95,217708,43.636430
2016,72,229833,31.327094
2017,107,231007,46.318943
2018,98,231564,42.320913
2019,82,211486,38.773252
2020,139,112918,123.098177
2021,134,110558,121.203350
2022,116,103887,111.659784
2023,123,96607,127.319966
2024,111,91316,121.555916
2025,81,85546,94.685900

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c "import duckdb; c=duckdb.connect(); print(c.execute(\"SELECT count(*) n, min(crash_date), max(crash_date) FROM read_parquet('data/crashes.parquet')\").fetchdf().to_string(index=False)); print(c.execute(\"SELECT * FROM read_parquet('data/crashes.parquet') LIMIT 2\").fetchdf().to_string(index=False))"
# bash
python -c "import duckdb; c=duckdb.connect(); print(c.execute(\"SELECT year(crash_date) y, count(*) crash_rows, sum(coalesce(number_of_motorist_killed,0)) motorist_deaths, sum(coalesce(number_of_motorist_injured,0)) motorist_injuries, count(*) FILTER (WHERE coalesce(number_of_motorist_killed,0)>0) crashes_with_motorist_death FROM read_parquet('data/crashes.parquet') WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY y ORDER BY y\").fetchdf().to_string(index=False))"
# bash
ls
# bash
python -c "import duckdb; print(duckdb.connect().execute(\"SELECT min(crash_date), max(crash_date), count(DISTINCT crash_date), count(*) FROM read_parquet('data/crashes.parquet') WHERE crash_date >= DATE '2025-01-01' AND crash_date < DATE '2026-01-01'\").fetchall())"
# bash
python - <<'PY'
import duckdb
import matplotlib.pyplot as plt
from pathlib import Path

out = Path('out')
out.mkdir(exist_ok=True)
con = duckdb.connect()
df = con.execute("""
    SELECT year(crash_date) AS year,
           count(*) AS crash_reports,
           sum(coalesce(number_of_motorist_killed, 0))::BIGINT AS motorist_deaths
    FROM read_parquet('data/crashes.parquet')
    WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
    GROUP BY year ORDER BY year
""").fetchdf()
assert df['year'].tolist() == list(range(2013, 2026))
df['motorist_deaths_per_100k_crash_reports'] = df['motorist_deaths'] / df['crash_reports'] * 100_000

# Option 1: annual total deaths, an absolute burden measure.
values1 = df[['year', 'motorist_deaths']]
values1.to_csv(out / 'values_1.csv', index=False)
fig, ax = plt.subplots(figsize=(10, 5.8))
ax.plot(df['year'], df['motorist_deaths'], marker='o', linewidth=2.2, color='#245b8f')
ax.set(title='Motorist deaths in NYC police-reported crashes, 2013–2025',
       xlabel='Year', ylabel='Motorist deaths (people)')
ax.set_xticks(df['year'])
ax.tick_params(axis='x', rotation=45)
ax.grid(axis='y', alpha=.25)
ax.text(.01, -.24, 'Annual death counts do not adjust for miles driven or other exposure.',
        transform=ax.transAxes, fontsize=9, color='#444')
fig.tight_layout()
fig.savefig(out / 'option_1.png', dpi=180, bbox_inches='tight')
plt.close(fig)

# Option 2: annual motorist deaths relative to the number of reported crashes.
values2 = df[['year', 'motorist_deaths', 'crash_reports', 'motorist_deaths_per_100k_crash_reports']]
values2.to_csv(out / 'values_2.csv', index=False, float_format='%.6f')
fig, ax = plt.subplots(figsize=(10, 5.8))
ax.plot(df['year'], df['motorist_deaths_per_100k_crash_reports'], marker='o', linewidth=2.2, color='#a64b32')
ax.set(title='Motorist deaths per 100,000 NYC crash reports, 2013–2025',
       xlabel='Year', ylabel='Motorist deaths per 100,000 crash reports')
ax.set_xticks(df['year'])
ax.tick_params(axis='x', rotation=45)
ax.grid(axis='y', alpha=.25)
ax.text(.01, -.24, 'Crash-report denominator; this is not a per-mile risk rate.',
        transform=ax.transAxes, fontsize=9, color='#444')
fig.tight_layout()
fig.savefig(out / 'option_2.png', dpi=180, bbox_inches='tight')
plt.close(fig)

print(df.to_string(index=False, formatters={'motorist_deaths_per_100k_crash_reports': '{:.2f}'.format}))
PY
# bash
python -c "import json, pathlib, pandas as pd; o=json.loads(pathlib.Path('out/options.json').read_text()); assert abs(sum(x['probability'] for x in o['options'])-1)<1e-9; assert len(o['options'])==2; [print(p, pathlib.Path('out',p).stat().st_size) for p in ['option_1.png','values_1.csv','option_2.png','values_2.csv','options.json']]; a=pd.read_csv('out/values_1.csv'); b=pd.read_csv('out/values_2.csv'); assert a.iloc[0].motorist_deaths==110 and a.iloc[-1].motorist_deaths==81; assert round(b.iloc[0].motorist_deaths_per_100k_crash_reports,1)==54.0 and round(b.iloc[-1].motorist_deaths_per_100k_crash_reports,1)==94.7; print('JSON and endpoint values verified')"

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