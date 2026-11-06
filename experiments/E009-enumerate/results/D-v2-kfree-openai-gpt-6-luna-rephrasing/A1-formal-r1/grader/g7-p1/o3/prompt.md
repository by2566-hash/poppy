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
- Qualifications (reported, recorded in this dataset) count when they are in the WRITTEN ANSWER or the DECLARED FRAMING; text
  that appears only inside the chart image (title, footnote, source note) does not satisfy an item on its own. The official-count
  part of unsupported_claim follows the same test as TR07.

DATA FACTS (pinned snapshot):
- The file covers 2012-07-01 to 2026-06-11; 2013-2025 are complete calendar years; 2026 is partial (to June 11).
- borough is NULL for about 20-38% of crashes in every year (TR05): a borough filter silently drops them.
- number_of_persons_killed is NULL in most May-2026 and all June-2026 rows (TR08); 2013-2025 killed counts have no NULLs.
- crash_time has no NULL rows. Reported crash counts (the number of crash records) fall sharply in 2020 (TR01), so a per-reported-crash rate (deaths or injuries divided by reported crashes) compared across years spanning 2020 needs a caveat. Counts of deaths or injuries by year do NOT need it (they are not affected by the reporting change), and a comparison between groups within one pooled window (e.g. day vs night) does not either (decided 2026-11-04; g5 wording after g4 failed c6 on plain death counts).
- No exposure measure exists (no traffic volume, trips, miles): counts and per-crash rates are not risk (TR11).

QUESTION ASKED: Has pedestrian road safety in Brooklyn improved since 2013? Produce a chart appropriate for a local news story and summarize the findings.
QUESTION TYPE: ambiguous
DECLARED FRAMING:
metric: Annual number of crashes with at least one pedestrian injured or killed
denominator: None; absolute count of Brooklyn police-reported crashes with at least one pedestrian casualty per calendar year
grouping: Calendar year (Brooklyn)
chart_type: Line chart
probability: 0.2
WRITTEN ANSWER:
These counts cannot establish whether pedestrian road-safety risk improved, but Brooklyn had 2,766 crashes involving a pedestrian injury or death in 2025 versus 3,498 in 2013 (21% fewer), with a substantial rise since 2020. This chart answers how often a Brooklyn crash involved pedestrian harm, showing fewer such crashes in 2025 than in 2013 but a marked increase after 2020. Crash counts offer a distinct frequency measure, but they do not account for pedestrian exposure or how many people were injured in each crash.

VALUES TABLE(S) BEHIND THE CHART:
[values_3.csv]
year,count
2013,3498
2014,3234
2015,2962
2016,2797
2017,2550
2018,2697
2019,2623
2020,1724
2021,1856
2022,2185
2023,2310
2024,2576
2025,2766

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
ls
# bash
python3 -c 'import duckdb; p="data/crashes.parquet"; con=duckdb.connect(); print(con.execute("describe select * from read_parquet(?)", [p]).fetchdf().to_string(index=False)); print(con.execute("select min(crash_date), max(crash_date), count(*), count(*) filter (where borough = '\''BROOKLYN'\'') from read_parquet(?)", [p]).fetchall())'
# bash
python3 -c 'import duckdb; q="""SELECT year(crash_date) AS year, sum(coalesce(number_of_pedestrians_injured,0))::BIGINT AS injured, sum(coalesce(number_of_pedestrians_killed,0))::BIGINT AS killed, count(*) FILTER (WHERE coalesce(number_of_pedestrians_injured,0)>0 OR coalesce(number_of_pedestrians_killed,0)>0)::BIGINT AS crashes_with_pedestrian_casualty FROM read_parquet(\"data/crashes.parquet\") WHERE borough=\"BROOKLYN\" AND crash_date >= DATE \"2013-01-01\" AND crash_date < DATE \"2026-01-01\" GROUP BY 1 ORDER BY 1"; print(duckdb.sql(q).df().to_string(index=False))'
# bash
python3 - <<'PY'
import duckdb
q = """
SELECT year(crash_date) AS year,
       sum(coalesce(number_of_pedestrians_injured,0))::BIGINT AS injured,
       sum(coalesce(number_of_pedestrians_killed,0))::BIGINT AS killed,
       count(*) FILTER (WHERE coalesce(number_of_pedestrians_injured,0)>0 OR coalesce(number_of_pedestrians_killed,0)>0)::BIGINT AS crashes_with_pedestrian_casualty
FROM read_parquet('data/crashes.parquet')
WHERE borough='BROOKLYN' AND crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
GROUP BY 1 ORDER BY 1
"""
print(duckdb.sql(q).df().to_string(index=False))
PY
# bash
python3 - <<'PY'
from pathlib import Path
import json
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

out = Path('out')
out.mkdir(exist_ok=True)
query = """
SELECT year(crash_date)::INTEGER AS year,
       sum(coalesce(number_of_pedestrians_injured, 0))::BIGINT AS pedestrians_injured,
       sum(coalesce(number_of_pedestrians_killed, 0))::BIGINT AS pedestrians_killed,
       count(*) FILTER (
           WHERE coalesce(number_of_pedestrians_injured, 0) > 0
              OR coalesce(number_of_pedestrians_killed, 0) > 0
       )::BIGINT AS crashes_with_pedestrian_casualty
FROM read_parquet('data/crashes.parquet')
WHERE borough = 'BROOKLYN'
  AND crash_date >= DATE '2013-01-01'
  AND crash_date < DATE '2026-01-01'
GROUP BY 1 ORDER BY 1
"""
df = duckdb.sql(query).df()

options_meta = [
    {
        'id': 1, 'col': 'pedestrians_injured', 'label': 'Pedestrians injured',
        'ylabel': 'People injured', 'color': '#1769aa', 'metric': 'Annual number of pedestrians injured',
        'denominator': 'None; absolute count of injured pedestrians in Brooklyn police-reported crashes per calendar year',
        'grouping': 'Calendar year (Brooklyn)', 'chart_type': 'Line chart',
        'reason': 'Injury counts capture the most frequent direct harm to pedestrians and make the long-term trend easy to compare.',
        'probability': 0.4,
        'answer_template': 'Brooklyn recorded {end:,} pedestrian injuries in 2025 versus {start:,} in 2013 ({change}%); injuries fell through 2020 but then rose, so the count is lower than in 2013 but had not returned to its low.'
    },
    {
        'id': 2, 'col': 'pedestrians_killed', 'label': 'Pedestrians killed',
        'ylabel': 'People killed', 'color': '#b3261e', 'metric': 'Annual number of pedestrians killed',
        'denominator': 'None; absolute count of pedestrians killed in Brooklyn police-reported crashes per calendar year',
        'grouping': 'Calendar year (Brooklyn)', 'chart_type': 'Line chart',
        'reason': 'Fatalities are the most severe pedestrian outcome and should be examined separately from much more numerous injuries.',
        'probability': 0.4,
        'answer_template': 'Brooklyn recorded {end:,} pedestrian deaths in 2025 versus {start:,} in 2013 ({change}%); annual fatalities fluctuated and the 2025 count was higher, so this fatality indicator does not show improvement from 2013.'
    },
    {
        'id': 3, 'col': 'crashes_with_pedestrian_casualty', 'label': 'Crashes with pedestrian injuries or deaths',
        'ylabel': 'Crashes', 'color': '#147d64', 'metric': 'Annual number of crashes with at least one pedestrian injured or killed',
        'denominator': 'None; absolute count of Brooklyn police-reported crashes with at least one pedestrian casualty per calendar year',
        'grouping': 'Calendar year (Brooklyn)', 'chart_type': 'Line chart',
        'reason': 'Counting affected crashes provides a complementary view of how often a police-reported crash resulted in pedestrian harm, independent of the number of people hurt per crash.',
        'probability': 0.2,
        'answer_template': 'Brooklyn had {end:,} crashes involving a pedestrian injury or death in 2025 versus {start:,} in 2013 ({change}%); the count is lower than in 2013 but has risen substantially since 2020.'
    }
]

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
answers = []
for opt in options_meta:
    data = df[['year', opt['col']]].rename(columns={opt['col']: 'count'})
    data.to_csv(out / f"values_{opt['id']}.csv", index=False)
    fig, ax = plt.subplots(figsize=(9.2, 5.2), constrained_layout=True)
    ax.plot(data['year'], data['count'], color=opt['color'], marker='o', linewidth=2.8, markersize=5.5)
    ax.fill_between(data['year'], data['count'], color=opt['color'], alpha=0.08)
    first, last = data.iloc[0], data.iloc[-1]
    ax.annotate(f"{int(first['count']):,}", (first['year'], first['count']), xytext=(0, 11), textcoords='offset points', ha='center', color=opt['color'], fontweight='bold')
    ax.annotate(f"{int(last['count']):,}", (last['year'], last['count']), xytext=(0, 11), textcoords='offset points', ha='center', color=opt['color'], fontweight='bold')
    ax.set_title(f"{opt['label']} in Brooklyn", loc='left', fontsize=17, fontweight='bold', pad=24)
    ax.text(0, 1.02, 'Annual totals • 2013–2025', transform=ax.transAxes, color='#555555', fontsize=11)
    ax.set_ylabel(opt['ylabel'])
    ax.set_xlabel('Calendar year')
    ax.set_xticks(data['year'])
    ax.tick_params(axis='x', rotation=0)
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
    ax.grid(axis='y', color='#d9dee5', linewidth=0.8)
    ax.spines[['top', 'right']].set_visible(False)
    ax.spines[['left', 'bottom']].set_color('#aab2bd')
    ax.text(0, -0.22, 'Source: NYC police-reported crash records. Counts are not adjusted for walking exposure; 2026 excluded as incomplete.', transform=ax.transAxes, fontsize=8.5, color='#555555')
    fig.savefig(out / f"option_{opt['id']}.png", dpi=180, facecolor='white')
    plt.close(fig)
    start, end = int(data.iloc[0]['count']), int(data.iloc[-1]['count'])
    change = round((end - start) / start * 100)
    answer = opt['answer_template'].format(start=start, end=end, change=f'{change:+d}%')
    answers.append(answer)
    opt['answer'] = answer
    if opt['id'] == 1:
        opt['interpretation'] = 'This chart answers whether the number of pedestrians injured each year is lower than in 2013: it shows a lower 2025 count, after a sharp 2020 dip and a subsequent rise. Injury totals are a defensible direct-harm measure, but without pedestrian exposure or population data they do not show the risk per trip or establish an overall safety improvement.'
    elif opt['id'] == 2:
        opt['interpretation'] = 'This chart focuses on the most severe outcome and shows that pedestrian deaths were higher in 2025 than in 2013, with considerable year-to-year variation. Fatality counts are directly relevant to safety, but this small annual count does not describe injury burden or risk per pedestrian trip.'
    else:
        opt['interpretation'] = 'This chart answers how often a Brooklyn crash involved pedestrian harm, showing fewer such crashes in 2025 than in 2013 but a marked increase after 2020. Crash counts offer a distinct frequency measure, but they do not account for pedestrian exposure or how many people were injured in each crash.'

options = {'options': [{k: v for k, v in opt.items() if k in {'id','metric','denominator','grouping','chart_type','reason','probability','answer','interpretation'}} for opt in options_meta]}
(out / 'options.json').write_text(json.dumps(options, indent=2) + '\n')
print(df.to_string(index=False))
print('\nAnswers:')
for answer in answers:
    print(answer)
PY
# bash
git status --short
# bash
python3 - <<'PY'
import json
from pathlib import Path
p = Path('out')
data = json.loads((p / 'options.json').read_text())
assert [o['id'] for o in data['options']] == [1, 2, 3]
assert abs(sum(o['probability'] for o in data['options']) - 1) < 1e-9
for option in data['options']:
    assert (p / f"option_{option['id']}.png").is_file()
    assert (p / f"values_{option['id']}.csv").is_file()
    assert len(option['interpretation'].split('. ')) >= 2
    assert '%' in option['answer']
print('Validated JSON, probabilities, chart/data files, and final answers.')
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