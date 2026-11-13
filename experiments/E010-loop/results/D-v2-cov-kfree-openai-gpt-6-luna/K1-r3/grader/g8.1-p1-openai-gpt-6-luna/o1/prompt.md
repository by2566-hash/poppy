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

QUESTION ASKED: How many pedestrians were killed in NYC motor vehicle crashes each year from 2013 to 2025?
QUESTION TYPE: clear
DECLARED FRAMING:
metric: Sum of pedestrians killed
denominator: None (annual count)
grouping: Crash year, 2013–2025
chart_type: Bar chart
probability: 0.65
WRITTEN ANSWER:
The annual totals were 2013: 176, 2014: 133, 2015: 133, 2016: 149, 2017: 127, 2018: 123, 2019: 131, 2020: 101, 2021: 132, 2022: 135, 2023: 107, 2024: 124, 2025: 119; the highest was 176 in 2013 and the lowest was 101 in 2020. This framing answers the question with the annual count of pedestrians killed, summing the pedestrian-fatality field across crashes in each crash year. It shows 176 deaths in 2013, a low of 101 in 2020, and 119 in 2025, with year-to-year variation in between. Grouping the requested counts by calendar year is a defensible way to report how many pedestrians were killed, but it does not identify causes, locations, or individual crash circumstances. It excludes crashes dated outside 2013–2025; among selected-year rows, 0 of 2132218 (0%) are omitted for a NULL crash date or pedestrian-killed value, and each included year is complete in the file (0% omitted for partial-year coverage).

VALUES TABLE(S) BEHIND THE CHART:
[values_1.csv]
year,pedestrian_deaths
2013,176
2014,133
2015,133
2016,149
2017,127
2018,123
2019,131
2020,101
2021,132
2022,135
2023,107
2024,124
2025,119

CODE LINES THE AGENT RAN (for filters, windows, denominators):
# bash
python3 -c "import duckdb, pandas, matplotlib; print('duckdb', duckdb.__version__, 'pandas', pandas.__version__, 'matplotlib', matplotlib.__version__)"
# bash
python3 -c "import duckdb; p='data/crashes.parquet'; c=duckdb.connect(); print(c.execute(\"SELECT min(crash_date), max(crash_date), count(*), count(*) FILTER (WHERE crash_date IS NULL) FROM read_parquet(?)\", [p]).fetchdf().to_string(index=False)); print(c.execute(\"SELECT year(crash_date) AS yr, count(*) AS crash_rows, count(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS null_ped_killed, sum(number_of_pedestrians_killed) AS pedestrian_deaths, min(crash_date) AS first_date, max(crash_date) AS last_date FROM read_parquet(?) WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01' GROUP BY yr ORDER BY yr\", [p]).fetchdf().to_string(index=False)); print('null date pedestrian count:',c.execute(\"SELECT count(*) FROM read_parquet(?) WHERE crash_date IS NULL AND number_of_pedestrians_killed IS NULL\", [p]).fetchone()[0])"
# bash
ls -ld .
# bash
python3 - <<'PY'
import json
from pathlib import Path
import duckdb
import matplotlib.pyplot as plt

source = 'data/crashes.parquet'
out = Path('out')
out.mkdir(exist_ok=True)
con = duckdb.connect()
query = """
SELECT
    year(crash_date) AS year,
    SUM(number_of_pedestrians_killed)::BIGINT AS pedestrian_deaths,
    COUNT(*) AS crash_rows,
    COUNT(*) FILTER (WHERE number_of_pedestrians_killed IS NULL) AS null_death_rows,
    MIN(crash_date) AS first_date,
    MAX(crash_date) AS last_date
FROM read_parquet(?)
WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
GROUP BY year
ORDER BY year
"""
df = con.execute(query, [source]).fetchdf()
assert df['year'].tolist() == list(range(2013, 2026))

# The required measures and grouping field are present in every selected row.
selected_rows = int(df['crash_rows'].sum())
null_death_rows = int(df['null_death_rows'].sum())
all_stats = con.execute(
    "SELECT min(crash_date) AS first_date, max(crash_date) AS last_date, count(*) AS n FROM read_parquet(?)",
    [source],
).fetchone()
full_years = all(
    str(row.first_date) == f'{int(row.year)}-01-01' and str(row.last_date) == f'{int(row.year)}-12-31'
    for row in df.itertuples()
)
assert null_death_rows == 0 and full_years

values = df[['year', 'pedestrian_deaths']].copy()
values['year'] = values['year'].astype(int)
values['pedestrian_deaths'] = values['pedestrian_deaths'].astype(int)

for option_id, kind in [(1, 'bar'), (2, 'line')]:
    values.to_csv(out / f'values_{option_id}.csv', index=False)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    if kind == 'bar':
        ax.bar(values['year'], values['pedestrian_deaths'], color='#2f6b9a', width=0.72)
    else:
        ax.plot(values['year'], values['pedestrian_deaths'], color='#2f6b9a', marker='o', linewidth=2)
    ax.set_title('Pedestrians killed in NYC motor vehicle crashes, 2013–2025')
    ax.set_xlabel('Crash year')
    ax.set_ylabel('Pedestrians killed')
    ax.set_xticks(values['year'])
    ax.set_ylim(0, max(values['pedestrian_deaths']) * 1.12)
    ax.grid(axis='y', alpha=0.25)
    fig.tight_layout()
    fig.savefig(out / f'option_{option_id}.png', dpi=160)
    plt.close(fig)

numbers = ', '.join(f"{int(r.year)}: {int(r.pedestrian_deaths)}" for r in values.itertuples())
answer = f"The annual totals were {numbers}; the highest was 176 in 2013 and the lowest was 101 in 2020."
common_interpretation = (
    'This framing answers the question with the annual count of pedestrians killed, summing the pedestrian-fatality field across crashes in each crash year. '
    'It shows 176 deaths in 2013, a low of 101 in 2020, and 119 in 2025, with year-to-year variation in between. '
    'Grouping the requested counts by calendar year is a defensible way to report how many pedestrians were killed, but it does not identify causes, locations, or individual crash circumstances. '
    'It excludes crashes dated outside 2013–2025; among selected-year rows, 0 of 2,246,678 (0%) are omitted for a NULL crash date or pedestrian-killed value, and each included year is complete in the file (0% omitted for partial-year coverage).'
)
options = {
    'options': [
        {
            'id': 1,
            'metric': 'Sum of pedestrians killed',
            'denominator': 'None (annual count)',
            'grouping': 'Crash year, 2013–2025',
            'chart_type': 'Bar chart',
            'reason': 'Bars make it easy to compare the discrete annual totals requested.',
            'probability': 0.65,
            'answer': answer,
            'interpretation': common_interpretation,
        },
        {
            'id': 2,
            'metric': 'Sum of pedestrians killed',
            'denominator': 'None (annual count)',
            'grouping': 'Crash year, 2013–2025',
            'chart_type': 'Line chart',
            'reason': 'A line chart emphasizes the year-to-year trend while preserving each annual count.',
            'probability': 0.35,
            'answer': answer,
            'interpretation': common_interpretation,
        },
    ]
}
(out / 'options.json').write_text(json.dumps(options, indent=2) + '\n')
print('selected rows', selected_rows, 'null required rows', null_death_rows, 'full file coverage', all_stats)
print(values.to_string(index=False))
print('outputs saved to', out.resolve())
PY
# bash
python3 - <<'PY'
import json
from pathlib import Path
import duckdb
import matplotlib.pyplot as plt

source = 'data/crashes.parquet'
out = Path('out')
out.mkdir(exist_ok=True)
con = duckdb.connect()
df = con.execute("""
SELECT year(crash_date) AS year,
       SUM(number_of_pedestrians_killed)::BIGINT AS pedestrian_deaths,
       COUNT(*) AS crash_rows,
       COUNT(*) FILTER (WHERE crash_date IS NULL OR number_of_pedestrians_killed IS NULL) AS null_required_rows,
       MIN(crash_date) AS first_date,
       MAX(crash_date) AS last_date
FROM read_parquet(?)
WHERE crash_date >= DATE '2013-01-01' AND crash_date < DATE '2026-01-01'
GROUP BY year ORDER BY year
""", [source]).fetchdf()
assert df['year'].tolist() == list(range(2013, 2026))
selected_rows = int(df['crash_rows'].sum())
null_required_rows = int(df['null_required_rows'].sum())
full_years = all(
    row.first_date.date().isoformat() == f'{int(row.year)}-01-01'
    and row.last_date.date().isoformat() == f'{int(row.year)}-12-31'
    for row in df.itertuples()
)
assert null_required_rows == 0 and full_years
values = df[['year', 'pedestrian_deaths']].copy()
values['year'] = values['year'].astype(int)
values['pedestrian_deaths'] = values['pedestrian_deaths'].astype(int)

for option_id, kind in [(1, 'bar'), (2, 'line')]:
    values.to_csv(out / f'values_{option_id}.csv', index=False)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    if kind == 'bar':
        ax.bar(values['year'], values['pedestrian_deaths'], color='#2f6b9a', width=0.72)
    else:
        ax.plot(values['year'], values['pedestrian_deaths'], color='#2f6b9a', marker='o', linewidth=2)
    ax.set_title('Pedestrians killed in NYC motor vehicle crashes, 2013–2025')
    ax.set_xlabel('Crash year')
    ax.set_ylabel('Pedestrians killed')
    ax.set_xticks(values['year'])
    ax.set_ylim(0, max(values['pedestrian_deaths']) * 1.12)
    ax.grid(axis='y', alpha=0.25)
    fig.tight_layout()
    fig.savefig(out / f'option_{option_id}.png', dpi=160)
    plt.close(fig)

numbers = ', '.join(f'{int(r.year)}: {int(r.pedestrian_deaths)}' for r in values.itertuples())
maximum = values.loc[values['pedestrian_deaths'].idxmax()]
minimum = values.loc[values['pedestrian_deaths'].idxmin()]
answer = (f"The annual totals were {numbers}; the highest was {int(maximum.pedestrian_deaths)} in "
          f"{int(maximum.year)} and the lowest was {int(minimum.pedestrian_deaths)} in {int(minimum.year)}.")
common_interpretation = (
    'This framing answers the question with the annual count of pedestrians killed, summing the pedestrian-fatality field across crashes in each crash year. '
    f"It shows {int(maximum.pedestrian_deaths)} deaths in {int(maximum.year)}, a low of {int(minimum.pedestrian_deaths)} in {int(minimum.year)}, and {int(values.iloc[-1]['pedestrian_deaths'])} in 2025, with year-to-year variation in between. "
    'Grouping the requested counts by calendar year is a defensible way to report how many pedestrians were killed, but it does not identify causes, locations, or individual crash circumstances. '
    f'It excludes crashes dated outside 2013–2025; among selected-year rows, {null_required_rows} of {selected_rows} ({100 * null_required_rows / selected_rows:.0f}%) are omitted for a NULL crash date or pedestrian-killed value, and each included year is complete in the file (0% omitted for partial-year coverage).'
)
options = {'options': [
    {'id': 1, 'metric': 'Sum of pedestrians killed', 'denominator': 'None (annual count)',
     'grouping': 'Crash year, 2013–2025', 'chart_type': 'Bar chart',
     'reason': 'Bars make it easy to compare the discrete annual totals requested.',
     'probability': 0.65, 'answer': answer, 'interpretation': common_interpretation},
    {'id': 2, 'metric': 'Sum of pedestrians killed', 'denominator': 'None (annual count)',
     'grouping': 'Crash year, 2013–2025', 'chart_type': 'Line chart',
     'reason': 'A line chart emphasizes the year-to-year trend while preserving each annual count.',
     'probability': 0.35, 'answer': answer, 'interpretation': common_interpretation},
]}
(out / 'options.json').write_text(json.dumps(options, indent=2) + '\n')
print('selected rows:', selected_rows, '| NULL required rows:', null_required_rows, '| all years complete:', full_years)
print(values.to_string(index=False))
print('saved:', ', '.join(str(p) for p in sorted(out.iterdir())))
PY
# bash
python3 - <<'PY'
import csv, json
from pathlib import Path
out = Path('out')
data = json.loads((out / 'options.json').read_text())
assert len(data['options']) == 2
assert abs(sum(o['probability'] for o in data['options']) - 1) < 1e-9
for o in data['options']:
    with (out / f"values_{o['id']}.csv").open(newline='') as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 13 and rows[0]['year'] == '2013' and rows[-1]['year'] == '2025'
    for row in rows:
        assert f"{row['year']}: {row['pedestrian_deaths']}" in o['answer']
    assert (out / f"option_{o['id']}.png").is_file()
print('JSON, probabilities, chart/value artifacts, and answer-to-CSV totals verified.')
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
- tr_TR07: The output does not present the open-data death counts as the official NYC toll. The counts are qualified when the written output (answer, interpretation or declared framing fields) ties them to this data in any wording: reported, recorded, police-reported crashes, in this dataset (e.g. 'pedestrians killed in reported motor vehicle crashes' qualifies). A qualification or source note that appears only inside the chart image does not count, and a chart title without one is fine when the written output has it. FAIL only when no such qualification appears in the written output (Bo 2026-11-04, refined 2026-11-06).
- tr_CAUSAL: The output makes no causal attribution (e.g. 'because of the pandemic') that the data cannot support.
- unsupported_claim: PASS if no sentence makes a causal claim, a risk-per-exposure claim, an official-count claim, or uses a number from outside the data; FAIL otherwise, quoting the sentence

Reply with exactly one JSON object and nothing else:
{"<item>": {"verdict": "PASS|FAIL|NA", "evidence": "<short quote>"}, ...} with one entry per item above.