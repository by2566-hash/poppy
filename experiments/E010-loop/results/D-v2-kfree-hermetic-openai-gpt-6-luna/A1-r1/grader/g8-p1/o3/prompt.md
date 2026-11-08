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

QUESTION ASKED: Has road safety for pedestrians in Brooklyn gotten better since 2013? Make a chart suitable for a local news story and summarize the findings.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Annual pedestrian injuries plus pedestrian deaths
denominator: No exposure denominator; sum of reported pedestrian injuries and deaths
grouping: Brooklyn crash borough by calendar year, 2013–2025
chart_type: Line chart
probability: 0.2
WRITTEN ANSWER:
Combined reported pedestrian injuries and deaths fell 22%, from 3,671 in 2013 to 2,874 in 2025, but the total masks the rise in deaths. This answers whether the combined annual count of pedestrians injured or killed in Brooklyn crashes changed, and it shows a 22% decline from 2013 to 2025. It is a defensible summary of the total reported pedestrian casualties, but because injuries dominate the total it can hide a different fatality trend and it is not an exposure-adjusted risk measure.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,count
2013,3671
2014,3391
2015,3075
2016,2937
2017,2683
2018,2808
2019,2733
2020,1798
2021,1937
2022,2298
2023,2407
2024,2676
2025,2874

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python -c 'import duckdb; p="data/crashes.parquet"; print(duckdb.sql(f"describe select * from read_parquet(\"{p}\")").df().to_string(index=False)); print(duckdb.sql(f"select min(crash_date), max(crash_date), count(*) from read_parquet(\"{p}\")").fetchall()); print(duckdb.sql(f"select year(crash_date) y, count(*) crashes, sum(number_of_pedestrians_injured) ped_injured, sum(number_of_pedestrians_killed) ped_killed from read_parquet(\"{p}\") where borough ilike \'BROOKLYN\' group by y order by y").df().to_string(index=False))'
# bash
python -c "import duckdb; p='data/crashes.parquet'; print(duckdb.sql('describe select * from read_parquet(?)', params=[p]).df().to_string(index=False)); print(duckdb.sql('select min(crash_date), max(crash_date), count(*) from read_parquet(?)', params=[p]).fetchall()); print(duckdb.sql(\"select year(crash_date) y, count(*) crashes, sum(number_of_pedestrians_injured) ped_injured, sum(number_of_pedestrians_killed) ped_killed from read_parquet(?) where borough ilike 'BROOKLYN' group by y order by y\", params=[p]).df().to_string(index=False))"
# bash
python - <<'PY'
import duckdb
import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

out = Path('out')
out.mkdir(exist_ok=True)
source = 'data/crashes.parquet'
query = """
SELECT year(crash_date) AS year,
       COALESCE(SUM(number_of_pedestrians_injured), 0)::BIGINT AS pedestrian_injuries,
       COALESCE(SUM(number_of_pedestrians_killed), 0)::BIGINT AS pedestrian_deaths
FROM read_parquet(?)
WHERE upper(borough) = 'BROOKLYN'
  AND crash_date >= DATE '2013-01-01'
  AND crash_date < DATE '2026-01-01'
GROUP BY year
ORDER BY year
"""
df = duckdb.sql(query, params=[source]).df()
# Retain every calendar year in the comparison window, representing missing years as zero only if absent.
years = pd.DataFrame({'year': range(2013, 2026)})
df = years.merge(df, how='left', on='year').fillna(0)
for col in ['pedestrian_injuries', 'pedestrian_deaths']:
    df[col] = df[col].astype('int64')
df['pedestrian_casualties'] = df['pedestrian_injuries'] + df['pedestrian_deaths']

metrics = [
    (1, 'pedestrian_injuries', 'Pedestrian injuries', '#1769aa',
     'Pedestrians injured in Brooklyn crashes',
     'Reported pedestrian injuries fell 22%, from 3,641 in 2013 to 2,835 in 2025; this outcome count does not measure risk per pedestrian.'),
    (2, 'pedestrian_deaths', 'Pedestrian deaths', '#b42318',
     'Pedestrians killed in Brooklyn crashes',
     'Reported pedestrian deaths rose 30%, from 30 in 2013 to 39 in 2025, so safety did not improve on this severe-outcome measure.'),
    (3, 'pedestrian_casualties', 'Pedestrian injuries and deaths', '#5b4b9a',
     'Pedestrians injured or killed in Brooklyn crashes',
     'Combined reported pedestrian injuries and deaths fell 22%, from 3,671 in 2013 to 2,874 in 2025, but the total masks the rise in deaths.'),
]

for ident, col, label, color, title, _ in metrics:
    plotted = df[['year', col]].rename(columns={col: 'count'})
    plotted.to_csv(out / f'values_{ident}.csv', index=False)
    fig, ax = plt.subplots(figsize=(10.5, 6.2))
    ax.plot(plotted['year'], plotted['count'], color=color, linewidth=3, marker='o', markersize=6)
    ax.fill_between(plotted['year'], plotted['count'], color=color, alpha=0.09)
    ax.set_title(title, loc='left', fontsize=19, weight='bold', pad=18)
    ax.text(0, 1.02, 'Annual totals • Brooklyn • 2013–2025', transform=ax.transAxes,
            fontsize=11, color='#4b5563')
    ax.set_xlabel('Year', fontsize=11)
    ax.set_ylabel(label + ' (people)', fontsize=11)
    ax.set_xticks(plotted['year'])
    ax.tick_params(axis='x', rotation=45, labelsize=9)
    ax.yaxis.set_major_locator(mtick.MaxNLocator(integer=True, nbins=7))
    ax.grid(axis='y', color='#d9dee5', linewidth=0.8)
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.spines['bottom'].set_color('#9ca3af')
    ax.tick_params(axis='y', length=0, pad=7)
    first = int(plotted.iloc[0]['count'])
    last = int(plotted.iloc[-1]['count'])
    pct = (last / first - 1) * 100 if first else float('nan')
    sign = '+' if pct > 0 else '−'
    ax.annotate(f'{first:,}', (2013, first), xytext=(5, 12), textcoords='offset points',
                color=color, fontsize=10, weight='bold')
    ax.annotate(f'{last:,}  ({sign}{abs(pct):.0f}%)', (2025, last), xytext=(-5, 12),
                textcoords='offset points', ha='right', color=color, fontsize=10, weight='bold')
    fig.text(0.01, 0.015, 'Source: NYC police-reported motor vehicle crashes. 2026 excluded as a partial year. Counts are not adjusted for walking volume.',
             fontsize=8.5, color='#4b5563')
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(out / f'option_{ident}.png', dpi=180, bbox_inches='tight')
    plt.close(fig)

options = [
    {
      'id': 1,
      'metric': 'Annual number of pedestrians injured in police-reported crashes',
      'denominator': 'No exposure denominator; raw annual count of pedestrian injuries',
      'grouping': 'Brooklyn crash borough by calendar year, 2013–2025',
      'chart_type': 'Line chart',
      'reason': 'Injury counts capture the most frequent direct harm to pedestrians and make annual changes easy to see.',
      'probability': 0.4,
      'answer': metrics[0][5],
      'interpretation': 'This answers whether the annual number of pedestrians injured in Brooklyn crashes changed, and the chart shows a 22% decline from 2013 to 2025. Injury counts are a direct, interpretable safety outcome, but this framing does not show deaths or risk adjusted for how much people walked.'
    },
    {
      'id': 2,
      'metric': 'Annual number of pedestrians killed in police-reported crashes',
      'denominator': 'No exposure denominator; raw annual count of pedestrian deaths',
      'grouping': 'Brooklyn crash borough by calendar year, 2013–2025',
      'chart_type': 'Line chart',
      'reason': 'Fatalities are the most severe pedestrian outcome and can reveal a trend that injury totals alone obscure.',
      'probability': 0.4,
      'answer': metrics[1][5],
      'interpretation': 'This answers whether the annual number of pedestrians killed in Brooklyn crashes changed, and the chart shows an increase from 30 to 39. Fatality counts are a direct measure of the gravest harm, but this framing excludes nonfatal injuries and does not adjust for walking volume.'
    },
    {
      'id': 3,
      'metric': 'Annual pedestrian injuries plus pedestrian deaths',
      'denominator': 'No exposure denominator; sum of reported pedestrian injuries and deaths',
      'grouping': 'Brooklyn crash borough by calendar year, 2013–2025',
      'chart_type': 'Line chart',
      'reason': 'A combined casualty count gives a compact view of the total number of reported pedestrian victims across both outcome categories.',
      'probability': 0.2,
      'answer': metrics[2][5],
      'interpretation': 'This answers whether the combined annual count of pedestrians injured or killed in Brooklyn crashes changed, and it shows a 22% decline from 2013 to 2025. It is a defensible summary of the total reported pedestrian casualties, but because injuries dominate the total it can hide a different fatality trend and it is not an exposure-adjusted risk measure.'
    }
]
with (out / 'options.json').open('w') as f:
    json.dump({'options': options}, f, indent=2)
    f.write('\n')
print(df.to_string(index=False))
print('\nEndpoints and changes:')
for ident, col, *_ in metrics:
    start, end = int(df.iloc[0][col]), int(df.iloc[-1][col])
    print(ident, col, start, end, round((end / start - 1) * 100, 1))
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
- tr_TR05: If a borough filter (borough = 'BROOKLYN') is used, the output discloses that crashes with no borough recorded (19.9–38.1% per year) are excluded.
- tr_TR11: The output does not call Brooklyn 'safer' or 'less safe' from counts alone without saying that there is no pedestrian exposure measure.
- tr_TR01: If a per-crash rate spanning 2020 is shown, the output caveats the 2020 change in crash recording.
- tr_TR15: Claims about pedestrian deaths changing are qualified by the small counts (about 30–39 per year).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.