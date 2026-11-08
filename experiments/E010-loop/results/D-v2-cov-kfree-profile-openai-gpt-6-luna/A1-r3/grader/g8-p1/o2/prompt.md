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
metric: Annual number of pedestrians killed
denominator: None (annual count)
grouping: Calendar year, Brooklyn crashes
chart_type: Line chart
probability: 0.3
WRITTEN ANSWER:
Pedestrian deaths increased from 30 in 2013 to 39 in 2025 (30.0% up), with a peak of 46 in 2015. Deaths rose from 30 in 2013 to 39 in 2025 (30.0% higher), reaching a peak of 46 in 2015. Fatality counts spotlight the gravest outcome, but they do not measure nonfatal injuries or risk per pedestrian, trip, or distance walked. The borough filter excludes rows with NULL borough, 30.9% of all records pooled across 2013–2025; no Brooklyn rows with NULL in this metric’s required fields were dropped. The trend excludes 2012 and 2026 entirely (100% of the rows in each year omitted); the file covers only July 1–December 31, 2012 and January 1–June 11, 2026, respectively.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,pedestrian_deaths
2013,30
2014,42
2015,46
2016,20
2017,20
2018,23
2019,33
2020,17
2021,32
2022,23
2023,22
2024,31
2025,39

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls -la && ls -la data
# bash
ls -la data && ls -la out
# bash
python - <<'PY'
import duckdb
p='data/crashes.parquet'
con=duckdb.connect()
q="""
SELECT year(crash_date) AS year,
       count(*) AS all_rows,
       count(*) FILTER (WHERE borough IS NULL) AS borough_null,
       count(*) FILTER (WHERE borough = 'BROOKLYN') AS brooklyn_rows,
       sum(number_of_pedestrians_injured) FILTER (WHERE borough = 'BROOKLYN') AS ped_injured,
       sum(number_of_pedestrians_killed) FILTER (WHERE borough = 'BROOKLYN') AS ped_killed,
       count(*) FILTER (WHERE borough = 'BROOKLYN' AND (number_of_pedestrians_injured > 0 OR number_of_pedestrians_killed > 0)) AS ped_casualty_crashes,
       count(*) FILTER (WHERE borough = 'BROOKLYN' AND (number_of_pedestrians_injured IS NULL OR number_of_pedestrians_killed IS NULL)) AS brooklyn_metric_null
FROM read_parquet(?) GROUP BY 1 ORDER BY 1
"""
print(con.execute(q,[p]).fetchdf().to_string(index=False))
PY
# bash
python - <<'PY'
import json
from pathlib import Path
import duckdb
import matplotlib.pyplot as plt
import pandas as pd

base = Path('.')
out = base / 'out'
out.mkdir(exist_ok=True)
con = duckdb.connect()
query = """
WITH yearly AS (
  SELECT year(crash_date)::INTEGER AS year,
         count(*) AS all_rows,
         count(*) FILTER (WHERE borough IS NULL) AS borough_null_rows,
         count(*) FILTER (WHERE borough = 'BROOKLYN') AS brooklyn_rows,
         sum(number_of_pedestrians_injured) FILTER (WHERE borough = 'BROOKLYN') AS pedestrian_injuries,
         sum(number_of_pedestrians_killed) FILTER (WHERE borough = 'BROOKLYN') AS pedestrian_deaths,
         count(*) FILTER (WHERE borough = 'BROOKLYN' AND (number_of_pedestrians_injured > 0 OR number_of_pedestrians_killed > 0)) AS pedestrian_casualty_crashes,
         count(*) FILTER (WHERE borough = 'BROOKLYN' AND (number_of_pedestrians_injured IS NULL OR number_of_pedestrians_killed IS NULL)) AS metric_null_rows
  FROM read_parquet('data/crashes.parquet')
  GROUP BY 1
)
SELECT * FROM yearly ORDER BY year
"""
df = con.execute(query).fetchdf()
full = df[df.year.between(2013, 2025)].copy()
null_pct = 100 * full.borough_null_rows.sum() / full.all_rows.sum()
null_brooklyn_metric_rows = int(full.metric_null_rows.sum())

metrics = [
    {
        'id': 1,
        'column': 'pedestrians_injured_or_killed',
        'values': (full.pedestrian_injuries + full.pedestrian_deaths).astype(int),
        'label': 'Pedestrians injured or killed',
        'unit': 'people per year',
        'color': '#176B87',
        'headline': 'Brooklyn’s pedestrian toll is lower than in 2013',
        'reason': 'It captures the annual human toll by combining pedestrian injuries and deaths into one burden measure.',
        'metric': 'Annual number of pedestrians injured or killed (injuries + deaths)',
        'denominator': 'None (annual count)',
        'grouping': 'Calendar year, Brooklyn crashes',
        'chart_type': 'Line chart',
        'answer': None,
        'interpretation': None,
    },
    {
        'id': 2,
        'column': 'pedestrian_deaths',
        'values': full.pedestrian_deaths.astype(int),
        'label': 'Pedestrians killed',
        'unit': 'deaths per year',
        'color': '#B23A48',
        'headline': 'Brooklyn pedestrian deaths rose from 2013',
        'reason': 'Fatalities isolate the most severe outcome, which can move differently from the total injury burden.',
        'metric': 'Annual number of pedestrians killed',
        'denominator': 'None (annual count)',
        'grouping': 'Calendar year, Brooklyn crashes',
        'chart_type': 'Line chart',
        'answer': None,
        'interpretation': None,
    },
    {
        'id': 3,
        'column': 'pedestrian_casualty_crashes',
        'values': full.pedestrian_casualty_crashes.astype(int),
        'label': 'Crashes with a pedestrian injured or killed',
        'unit': 'crashes per year',
        'color': '#497A43',
        'headline': 'Fewer Brooklyn crashes harmed pedestrians than in 2013',
        'reason': 'It counts collision events with at least one pedestrian casualty, without allowing multi-victim crashes to count as multiple events.',
        'metric': 'Annual crashes with at least one pedestrian injured or killed',
        'denominator': 'None (annual crash count)',
        'grouping': 'Calendar year, Brooklyn crashes',
        'chart_type': 'Line chart',
        'answer': None,
        'interpretation': None,
    },
]

for item in metrics:
    values = pd.DataFrame({'year': full.year.astype(int), item['column']: item['values'].to_numpy(dtype=int)})
    values.to_csv(out / f"values_{item['id']}.csv", index=False)
    first = int(values.iloc[0, 1])
    last = int(values.iloc[-1, 1])
    pct = (last / first - 1) * 100
    low_idx = values.iloc[:, 1].idxmin()
    low_year = int(values.loc[low_idx, 'year'])
    low_val = int(values.loc[low_idx, item['column']])
    direction = 'down' if pct < 0 else 'up'
    if item['id'] == 1:
        item['answer'] = f"Brooklyn recorded {first:,} pedestrians injured or killed in 2013 and {last:,} in 2025 ({abs(pct):.1f}% {direction}), but the count rose from a {low_val:,} low in {low_year}."
        answer_core = f"The annual count fell from {first:,} people injured or killed in 2013 to {last:,} in 2025 ({abs(pct):.1f}% lower), after a low of {low_val:,} in {low_year}."
        defensible = 'This total is a direct count of the human harm recorded in crashes, but it does not measure risk per pedestrian, trip, or distance walked.'
    elif item['id'] == 2:
        item['answer'] = f"Pedestrian deaths increased from {first} in 2013 to {last} in 2025 ({abs(pct):.1f}% {direction}), with a peak of {int(values.iloc[:,1].max())} in {int(values.loc[values.iloc[:,1].idxmax(), 'year'])}."
        answer_core = f"Deaths rose from {first} in 2013 to {last} in 2025 ({abs(pct):.1f}% higher), reaching a peak of {int(values.iloc[:,1].max())} in {int(values.loc[values.iloc[:,1].idxmax(), 'year'])}."
        defensible = 'Fatality counts spotlight the gravest outcome, but they do not measure nonfatal injuries or risk per pedestrian, trip, or distance walked.'
    else:
        item['answer'] = f"Crashes with at least one pedestrian injured or killed declined from {first:,} in 2013 to {last:,} in 2025 ({abs(pct):.1f}% {direction}), though they rose from a {low_val:,} low in {low_year}."
        answer_core = f"Crashes with at least one pedestrian injured or killed declined from {first:,} in 2013 to {last:,} in 2025 ({abs(pct):.1f}% lower), after a low of {low_val:,} in {low_year}."
        defensible = 'Counting casualty crashes measures the frequency of harmful collision events rather than the number of people hurt, but it does not measure exposure-adjusted risk.'
    item['interpretation'] = (
        f"{answer_core} {defensible} "
        f"The borough filter excludes rows with NULL borough, {null_pct:.1f}% of all records pooled across 2013–2025; no Brooklyn rows with NULL in this metric’s required fields were dropped. "
        "The trend excludes 2012 and 2026 entirely (100% of the rows in each year omitted); the file covers only July 1–December 31, 2012 and January 1–June 11, 2026, respectively."
    )

    fig, ax = plt.subplots(figsize=(10.8, 6.2), dpi=160)
    years = values.year.to_numpy()
    counts = values.iloc[:, 1].to_numpy()
    ax.plot(years, counts, color=item['color'], linewidth=3, marker='o', markersize=5.5, markerfacecolor='white', markeredgewidth=2)
    ax.fill_between(years, counts, 0, color=item['color'], alpha=0.08)
    ax.set_title(item['headline'], loc='left', fontsize=18, fontweight='bold', pad=24)
    ax.text(0, 1.025, f"{item['label']} in Brooklyn · complete calendar years 2013–2025", transform=ax.transAxes, fontsize=10.5, color='#4B5563')
    ax.set_ylabel(item['unit'], fontsize=10)
    ax.set_xticks(years)
    ax.tick_params(axis='x', labelrotation=0, labelsize=8.5)
    ax.grid(axis='y', color='#D9DEE3', linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.spines['bottom'].set_color('#AEB7C0')
    ax.tick_params(axis='y', length=0, labelsize=9)
    ax.margins(x=0.04)
    ax.set_ylim(bottom=0, top=max(counts) * 1.18 if max(counts) else 1)
    for idx in (0, len(counts)-1):
        ax.annotate(f'{counts[idx]:,}', (years[idx], counts[idx]), xytext=(0, 10), textcoords='offset points', ha='center', fontsize=9, fontweight='bold', color=item['color'])
    ax.text(0, -0.20, 'Counts, not exposure-adjusted rates. Partial years 2012 and 2026 are excluded.  Source: NYC police-reported motor vehicle crash records.', transform=ax.transAxes, fontsize=8.2, color='#58616B')
    fig.subplots_adjust(left=0.09, right=0.98, top=0.84, bottom=0.22)
    fig.savefig(out / f"option_{item['id']}.png", bbox_inches='tight', facecolor='white')
    plt.close(fig)

options = [{k: item[k] for k in ('id','metric','denominator','grouping','chart_type','reason','answer','interpretation')} for item in metrics]
probabilities = [0.40, 0.30, 0.30]
for option, probability in zip(options, probabilities):
    option['probability'] = probability
with (out / 'options.json').open('w', encoding='utf-8') as f:
    json.dump({'options': options}, f, ensure_ascii=False, indent=2)
    f.write('\n')

print(f'Pooled 2013-2025 borough-null share: {null_pct:.4f}%')
print(f'Brooklyn rows missing required pedestrian metric columns, 2013-2025: {null_brooklyn_metric_rows}')
for item in metrics:
    v = pd.read_csv(out / f"values_{item['id']}.csv")
    pct = (v.iloc[-1,1] / v.iloc[0,1] - 1) * 100
    print(f"option {item['id']}: {int(v.iloc[0,1])} ({int(v.iloc[0,0])}) -> {int(v.iloc[-1,1])} ({int(v.iloc[-1,0])}), {pct:+.2f}%")
print(f'Wrote {len(metrics)} PNG charts, CSV values, and options.json to {out}')
PY
# bash
python - <<'PY'
import json
from pathlib import Path
import pandas as pd
out=Path('out')
data=json.loads((out/'options.json').read_text())
assert [o['id'] for o in data['options']] == [1,2,3]
assert abs(sum(o['probability'] for o in data['options'])-1) < 1e-12
for option in data['options']:
    chart=out/f"option_{option['id']}.png"
    values=out/f"values_{option['id']}.csv"
    assert chart.is_file() and chart.stat().st_size > 0
    df=pd.read_csv(values)
    assert df.year.tolist() == list(range(2013,2026))
    assert len(df.columns) == 2
    assert option['answer'].endswith('.')
    assert len([s for s in option['interpretation'].split('. ') if s]) == 4
    print(f"option {option['id']}: {chart.stat().st_size:,} bytes; {len(df)} plotted annual rows; answer/interpretation present")
print('JSON valid; probabilities sum to', sum(o['probability'] for o in data['options']))
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