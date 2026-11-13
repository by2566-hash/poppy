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
metric: Annual count of pedestrians killed in police-reported crashes
denominator: No denominator; count of pedestrian deaths
grouping: Calendar year, Brooklyn
chart_type: Line chart
probability: 0.5
WRITTEN ANSWER:
Brooklyn recorded 39 pedestrian deaths in 2025, 30% more than the 30 deaths in 2013, despite year-to-year fluctuations. This framing answers whether the annual number of pedestrian deaths has improved: it was higher in 2025 than in 2013, with substantial variation between years. Fatality counts capture the most severe reported outcome, but without pedestrian exposure they cannot establish whether an individual pedestrian’s risk changed.

VALUES TABLE(S) BEHIND THE CHART:
[values_2.csv]
year,count
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
python -c 'import duckdb; c=duckdb.connect(); p="data/crashes.parquet"; print(c.execute(f"DESCRIBE SELECT * FROM read_parquet(\"{p}\")").fetchall()); print(c.execute(f"SELECT min(crash_date), max(crash_date), count(*) FROM read_parquet(\"{p}\")").fetchall()); print(c.execute(f"SELECT year(crash_date), count(*), sum(number_of_pedestrians_injured), sum(number_of_pedestrians_killed) FROM read_parquet(\"{p}\") WHERE borough = \'BROOKLYN\' GROUP BY 1 ORDER BY 1").fetchall())'
# bash
python - <<'PY'
import duckdb
c=duckdb.connect()
p='data/crashes.parquet'
print(c.execute(f'DESCRIBE SELECT * FROM read_parquet(\'{p}\')').fetchall())
print(c.execute(f'SELECT min(crash_date), max(crash_date), count(*) FROM read_parquet(\'{p}\')').fetchall())
print(c.execute(f"SELECT year(crash_date), count(*), sum(number_of_pedestrians_injured), sum(number_of_pedestrians_killed) FROM read_parquet('{p}') WHERE borough = 'BROOKLYN' GROUP BY 1 ORDER BY 1").fetchall())
PY
# bash
python - <<'PY'
import duckdb
c=duckdb.connect()
p='data/crashes.parquet'
print(c.execute(f"SELECT year(crash_date) AS yr, min(crash_date), max(crash_date), sum(number_of_pedestrians_injured), sum(number_of_pedestrians_killed), sum(number_of_pedestrians_injured + number_of_pedestrians_killed) FROM read_parquet('{p}') WHERE borough='BROOKLYN' AND crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY 1 ORDER BY 1").fetchdf().to_string(index=False))
PY
# bash
ls
# bash
python - <<'PY'
from pathlib import Path
import json
import duckdb
import pandas as pd
import matplotlib.pyplot as plt

out = Path('out')
out.mkdir(exist_ok=True)
con = duckdb.connect()
df = con.execute("""
    SELECT year(crash_date) AS year,
           SUM(number_of_pedestrians_injured)::INTEGER AS pedestrians_injured,
           SUM(number_of_pedestrians_killed)::INTEGER AS pedestrians_killed
    FROM read_parquet('data/crashes.parquet')
    WHERE borough = 'BROOKLYN'
      AND crash_date >= DATE '2013-01-01'
      AND crash_date < DATE '2026-01-01'
    GROUP BY 1
    ORDER BY 1
""").df()
assert df['year'].tolist() == list(range(2013, 2026))

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'axes.titlesize': 17,
    'axes.titleweight': 'bold',
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
})
charts = [
    {
        'id': 1,
        'column': 'pedestrians_injured',
        'label': 'Pedestrians injured',
        'title': 'Brooklyn pedestrian injuries have fallen since 2013',
        'color': '#176B87',
        'metric': 'Annual count of pedestrians injured in police-reported crashes',
        'denominator': 'No denominator; count of injured pedestrians',
        'grouping': 'Calendar year, Brooklyn',
        'chart_type': 'Line chart',
        'reason': 'Injury counts show how many pedestrians were hurt each year, a direct and widely understood measure of harm.',
        'probability': 0.5,
        'answer': 'Brooklyn recorded 2,835 pedestrians injured in 2025, down 22.1% from 3,641 in 2013, though injuries have risen from the 2020 low.',
        'interpretation': 'This framing answers whether the number of pedestrians hurt each year has improved: the count was lower in 2025 than in 2013, but it has climbed since 2020. Annual injury counts are a direct measure of reported harm; they do not show injury risk per pedestrian or account for changes in walking volume.'
    },
    {
        'id': 2,
        'column': 'pedestrians_killed',
        'label': 'Pedestrians killed',
        'title': 'Brooklyn pedestrian deaths are higher than in 2013',
        'color': '#B23A48',
        'metric': 'Annual count of pedestrians killed in police-reported crashes',
        'denominator': 'No denominator; count of pedestrian deaths',
        'grouping': 'Calendar year, Brooklyn',
        'chart_type': 'Line chart',
        'reason': 'Fatality counts isolate the most severe outcome and prevent it from being obscured by the larger number of nonfatal injuries.',
        'probability': 0.5,
        'answer': 'Brooklyn recorded 39 pedestrian deaths in 2025, 30% more than the 30 deaths in 2013, despite year-to-year fluctuations.',
        'interpretation': 'This framing answers whether the annual number of pedestrian deaths has improved: it was higher in 2025 than in 2013, with substantial variation between years. Fatality counts capture the most severe reported outcome, but without pedestrian exposure they cannot establish whether an individual pedestrian’s risk changed.'
    }
]

for spec in charts:
    data = df[['year', spec['column']]].rename(columns={spec['column']: 'count'})
    data.to_csv(out / f"values_{spec['id']}.csv", index=False)
    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    ax.plot(data['year'], data['count'], color=spec['color'], linewidth=3,
            marker='o', markersize=6.5, markeredgecolor='white', markeredgewidth=1.2)
    ax.scatter([2013, 2025], [data.iloc[0]['count'], data.iloc[-1]['count']],
               color=spec['color'], s=78, zorder=4, edgecolor='white', linewidth=1.2)
    ax.annotate(f"{int(data.iloc[0]['count']):,}", (2013, data.iloc[0]['count']),
                xytext=(0, 13), textcoords='offset points', ha='center',
                color=spec['color'], fontsize=11, fontweight='bold')
    ax.annotate(f"{int(data.iloc[-1]['count']):,}", (2025, data.iloc[-1]['count']),
                xytext=(0, 13), textcoords='offset points', ha='center',
                color=spec['color'], fontsize=11, fontweight='bold')
    ax.set_title(spec['title'], loc='left', pad=17)
    ax.set_ylabel(f"{spec['label']} (people)", labelpad=9)
    ax.set_xlabel('Calendar year', labelpad=9)
    ax.set_xticks(list(range(2013, 2026)))
    ax.tick_params(axis='x', rotation=0, length=0, pad=8)
    ax.tick_params(axis='y', length=0, pad=8)
    ax.set_xlim(2012.65, 2025.35)
    ymax = max(data['count'])
    ax.set_ylim(0, ymax * (1.18 if ymax > 100 else 1.28))
    ax.grid(axis='y', color='#DCE3E8', linewidth=0.9)
    ax.set_axisbelow(True)
    for side in ['top', 'right', 'left']:
        ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color('#BCC7CE')
    fig.text(0.105, 0.035,
             'Source: NYC police-reported motor vehicle crashes, Brooklyn. Annual counts; not adjusted for walking volume.',
             fontsize=9, color='#4B5963')
    fig.tight_layout(rect=(0.04, 0.09, 0.99, 0.98))
    fig.savefig(out / f"option_{spec['id']}.png", dpi=180, bbox_inches='tight')
    plt.close(fig)

options = {'options': [{k: spec[k] for k in ('id', 'metric', 'denominator', 'grouping', 'chart_type', 'reason', 'probability', 'answer', 'interpretation')} for spec in charts]}
(out / 'options.json').write_text(json.dumps(options, ensure_ascii=False, indent=2) + '\n')
print(df.to_string(index=False))
print('Saved charts, values, and options.json in out/')
PY
# bash
python - <<'PY'
from pathlib import Path
import json
import pandas as pd
out = Path('out')
opts = json.loads((out / 'options.json').read_text())['options']
assert [x['id'] for x in opts] == [1, 2]
assert abs(sum(x['probability'] for x in opts) - 1) < 1e-9
for option in opts:
    csv_path = out / f"values_{option['id']}.csv"
    png_path = out / f"option_{option['id']}.png"
    data = pd.read_csv(csv_path)
    assert data.year.tolist() == list(range(2013, 2026))
    assert png_path.exists() and png_path.stat().st_size > 10_000
    print(f"option {option['id']}: {len(data)} annual values; chart {png_path.stat().st_size:,} bytes; 2013={data.iloc[0]['count']}, 2025={data.iloc[-1]['count']}")
print('options.json valid; probabilities sum to 1; all outputs present.')
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
- tr_TR01: If a per-reported-crash rate spanning 2020 is shown, the output says that the number of recorded crashes changes sharply around 2020 and that this affects comparing the per-crash rate across years (naming the cause, the 2020 recording change, is not required: it is not in the data or the dictionary).
- tr_TR15: Claims about pedestrian deaths changing are qualified by the small counts (about 30–39 per year).
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.